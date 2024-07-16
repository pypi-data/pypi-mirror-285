import numpy as np
import pandas as pd
import anndata as ad
import scipy.sparse
from numba import njit, prange
import gc

from .. import utils
from .. import preprocessing
from .. import tools

# This function is based on scanpy.preprocessing._simple._downsample_array:
# https://github.com/theislab/scanpy/blob/8fe1cf9cb6309fa0e91aa5cfd9ed7580e9d5b2ad/scanpy/preprocessing/_simple.py#L1043
@njit(cache=True)
def _sample(
    arr,
    target,
    replace=True,
    seed=42,
):
    np.random.seed(seed)
    
    cumcounts = arr.cumsum()

    arr[:] = 0

    total = cumcounts[-1]
    sample = np.random.choice(int(total), int(target), replace=replace)
    sample.sort()
    j_gene = 0
    for count in sample:
        while count >= cumcounts[j_gene]:
            j_gene += 1
        arr[j_gene] += 1

@njit(cache=True, parallel=True)
def _sample_dense_counts(
    X,
    counts_per_cell,
    seed=42,
    replace=True,
):
    n_cell = X.shape[0]
    
    for i_cell in prange(n_cell):
        
        _sample(X[i_cell,:], target=counts_per_cell[i_cell], replace=replace, seed=seed+i_cell)
    
@njit(cache=True, parallel=True)
def _sample_sparse_counts(
    X_indptr,
    X_data,
    counts_per_cell,
    seed=42,
    replace=True,
):  
    n_cell = X_indptr.shape[0] - 1
    
    for i_cell in prange(n_cell):
        
        i0 = X_indptr[i_cell]
        i1 = X_indptr[i_cell+1]
        if i0 >= i1:
            continue
        
        _sample(X_data[i0:i1], target=counts_per_cell[i_cell], replace=replace, seed=seed+i_cell)

def sample_counts(
    X,
    replace=False,
    fraction=1,
    seed=42,
):
    """\
    Sample counts from count matrix by sampling from each observation/row
    separately. This sampling basically assumes a multinomial count model with
    column probabilities given by the counts.
    
    Parameters
    ----------
    X
        A 2D :class:`~np.ndarray` or scipy sparse matrix.
    replace
        Whether to sample the counts with replacement.
    fraction
        The fraction of counts to sample per observation. If `replace==False`,
        `fraction` must be smaller than or equal to `1`.
    seed
        Random seed for sampling.
        
    Returns
    -------
    Returns the sampled count matrix.
    
    """
    
    preprocessing.check_counts_validity(X)
    
    counts_per_cell = utils.get_sum(X, axis=1)
    if fraction != 1:
        counts_per_cell = (counts_per_cell * fraction).astype(int)
    elif fraction > 1 and not replace:
        raise ValueError(f'`fraction` can only be larger than 1 if `replace==True`!')

    n_obs = X.shape[0]
    
    if scipy.sparse.issparse(X):
        if not isinstance(X, scipy.sparse.csr_matrix):
            X = X.tocsr()
        else:
            X = X.copy()
        _sample_sparse_counts(X.indptr, X.data, counts_per_cell, seed=seed, replace=replace)
    else:
        X = X.copy()
        _sample_dense_counts(X, counts_per_cell, seed=seed, replace=replace)
    return X

def _flatten_variations(variations):
    if isinstance(variations, dict):
        variations = [variations]
    all_variations = []
    for variation in variations:
        old_variations = [{}]
        new_variations = []
        for arg, options in variation.items():
            for option in options:
                for old_variation in old_variations:
                    new_variation = old_variation.copy()
                    new_variation[arg] = option
                    new_variations.append(new_variation)
            old_variations = new_variations
            new_variations = []
        all_variations.extend(old_variations)
    return all_variations

def wrap_uncertainty(
    adata,
    function,
    variations={},
    nResampling=20,
    mode='simultaneous',
    stat_error=False,
    syst_error=False,
    seed=42,
    verbose=1,
    **kw_args,
):
    """\
    Evaluates any numeric function of an :class:`~anndata.AnnData` and
    generates statistical and systematical error estimates for it.
    
    Parameters
    ----------
    adata
        An :class:`~anndata.AnnData` including count data in `.X`.
    function
        A function taking an :class:`~anndata.AnnData` as first argument and an
        arbitrary number of keyword arguments. The function has to return
        :class:`~numpy.ndarray` of the same size for every call, or a
        :class:`~pandas.Series` or :class:`~pandas.DataFrame`, all containing
        only numeric values.
    variations
        A dictionary containing pairs of keyword parameter names and iterables
        defining the sweep over parameters to include in the systematic
        variations. Can also be a list of such dictionaries.
    nResampling
        The number of resampling rounds for statistical error estimation. The
        statistical error estimation gets more accurate for higher values, but
        the computing time is directly proportional to this value, except for
        `mode=='simultaneous'`, see below. If `None` or smaller than `2`, only
        systematic errors are considered.
    mode
        The mode of estimation of statistical errors. Available are:
        
        - 'bootstrap': Resample the counts per bead with a standard
          bootstrap; This evaluates the function for every systematic variation
          `nResampling` times.
        - 'jackknife': Resample the counts per bead with a blocked jackknife;
          This evaluates the function for every systematic variation
          `nResampling` times. This uses all data equally and gives a more
          accurate error estimation for fixed `nResampling` than 'bootstrap'
          due to less sampling error. This works only if the function is linear
          enough, see e.g. https://arxiv.org/pdf/1606.00497v1.pdf.
        - 'simultaneous': Uses a different bootstrap resampled count matrix for
          every systematic variation and thus uses less function evaluations.
          In this mode it is not possible to give a separate statistical and
          systematical error estimate. If the number of systematic variations
          is less than `nResampling`, runs as many full sets of systematic
          variations until at least `nResampling` runs have been made.
        - `None`: Only systematic errors are considered.
        
    stat_error
        Whether to return a separate statistical error estimate.
    syst_error
        Whether to return a separate systematical error estimate.
    seed
        The random seed to use for the statistical resampling.
    verbose
        Level of verbosity, with `0` (no output), `1` (some output), ...
    **kw_args
        Additional keyword arguments are forwarded to every `function` call.
        
    Returns
    -------
    Returns the result of the function call with error estimates as a tuple of\
    result instances in the order: mean, total error, statistical error (if\
    available), systematical error (if available).
    
    """

    all_variations = _flatten_variations(variations)
    nVariations = len(all_variations)
    original_adata = adata
    working_adata = original_adata.copy()
    if nResampling is None or nResampling < 2:
        mode = None
        nResampling = 1
        stat_error = False
    if mode is None:
        pass
    elif mode == 'simultaneous':
        nResampling = ((nResampling + nVariations - 1) // nVariations) * nVariations
        stat_error = False
        syst_error = False
    elif mode == 'jackknife':
        used_counts = original_adata.X.copy()
        if scipy.sparse.issparse(used_counts):
            used_counts.data[:] = 0
        else:
            used_counts[:] = 0
        too_small_observations = (utils.get_sum(original_adata.X, axis=1) < nResampling).sum()
        if too_small_observations > 0 and verbose > 0:
            print(f'{too_small_observations} of {original_adata.shape[0]} observations have not enough counts (i.e. less than {nResampling}) for a proper jackknife with `nResampling=={nResampling}`! For the other observables it should work fine, so continuing anyway...')
    elif mode == 'bootstrap':
        pass
    else:
        raise ValueError(f'`mode` is {mode!r}, but can only be one of {["bootstrap","jackknife","simultaneous",None]!r}')
        
    results = [[] for iResampling in range(nResampling)]
    common_index = None
    common_columns = None
    for iResampling in range(nResampling):
        if verbose > 0:
            print(f'Running resampling {iResampling+1} of {nResampling}')
        if mode is None:
            pass
        elif mode == 'jackknife':
            # determine the Jackknife block of counts to remove in this round
            working_adata.X = original_adata.X - used_counts
            working_adata.X = sample_counts(working_adata.X, fraction=1.0/(nResampling-iResampling), seed=seed+iResampling, replace=False)
            # keep track of all the used counts
            used_counts = used_counts + working_adata.X
            # construct the count matrix to use for this round
            working_adata.X = original_adata.X - working_adata.X
        else: # if mode == 'bootstrap' or mode == 'simultaneous':
            working_adata.X = sample_counts(original_adata.X.copy(), fraction=1.0, seed=seed+iResampling, replace=True)

        _all_variations = [all_variations[iResampling % nVariations]] if mode == 'simultaneous' else all_variations
        for iVariation,variation in enumerate(_all_variations):
            if verbose > 0:
                print(f'+ Running variation {iVariation+1} of {len(_all_variations)}')
            result = function(working_adata, **kw_args, **variation)
            results[iResampling].append(result)
            if isinstance(result, (pd.DataFrame, pd.Series)):
                # use only the intersection of results: for others it is not straightforward to define the error as some systematics or statistics are not represented
                if common_index is None:
                    common_index = result.index
                    if isinstance(result, pd.DataFrame):
                        common_columns = result.columns
                else:
                    common_index = common_index.intersection(result.index)
                    if isinstance(result, pd.DataFrame):
                        common_columns = common_columns.intersection(result.columns)
    
    del working_adata
    gc.collect() # anndata copies are not well garbage collected and accumulate in memory
    
    if common_columns is not None:
        results = np.array([ [ result.reindex(index=common_index, columns=common_columns).to_numpy() for result in results[iResampling] ] for iResampling in range(nResampling) ])
    elif common_index is not None:
        results = np.array([ [ result.reindex(index=common_index).to_numpy() for result in results[iResampling] ] for iResampling in range(nResampling) ])
    else:
        results = np.array(results)

    if mode == 'jackknife': # scale the variability in Jackknife direction correctly
        meanResampling = results.mean(axis=0)
        results = (results - meanResampling) * np.sqrt(nResampling - 1) + meanResampling
        del meanResampling

    def _wrap(result):
        if common_columns is not None:
            return pd.DataFrame(result, index=common_index, columns=common_columns)
        elif common_index is not None:
            return pd.Series(result, index=common_index)
        else:
            return result
    mean = _wrap(np.mean(results, axis=(0,1)))
    total = _wrap(np.std(results, axis=(0,1)))
    stat = _wrap(np.std(np.mean(results, axis=1), axis=0)) if stat_error else None
    syst = _wrap(np.std(np.mean(results, axis=0), axis=0)) if syst_error else None
    
    if stat is None and syst is None:
        return (mean, total)
    elif syst is None:
        return (mean, total, stat)
    elif stat is None:
        return (mean, total, syst)
    else:
        return (mean, total, stat, syst)

def annotate_uncertainty(
    adata,
    reference,
    annotation_key=None,
    variations={},
    nResampling=20,
    mode='simultaneous',
    result_key=None,
    error_key=None,
    stat_error_key=False,
    syst_error_key=False,
    seed=42,
    verbose=1,
    **kw_args,
):
    """\
    Annotates an :class:`~anndata.AnnData` using reference data.
    
    Parameters
    ----------
    adata
        An :class:`~anndata.AnnData` including count data in `.X` and
        profiles in `.varm` and/or annotation in `.obs` or `.obsm`.
    reference
        Reference data to get the annotation definition from.
    annotation_key
        The `.obs`, `.obsm`, and/or `.varm` key where the annotation and
        profiles are stored in the `reference`. If `None`, it is inferred from
        `reference`, if possible.
    variations
        A dictionary containing pairs of keyword parameter names and iterables
        defining the sweep over parameters to include in the systematic
        variations. Can also be a list of such dictionaries.
    nResampling
        The number of resampling rounds for statistical error estimation. The
        statistical error estimation gets more accurate for higher values, but
        the computing time is directly proportional to this value, except for
        `mode=='simultaneous'`, see below. If `None` or smaller than `2`, only
        systematic errors are considered.
    mode
        The mode of estimation of statistical errors. Available are:
        
        - 'bootstrap': Resample the counts per bead with a standard
          bootstrap; This evaluates the function for every systematic variation
          `nResampling` times.
        - 'simultaneous': Uses a different bootstrap resampled count matrix for
          every systematic variation and thus uses less function evaluations.
          In this mode it is not possible to give a separate statistical and
          systematical error estimate. If the number of systematic variations
          is less than `nResampling`, runs as many full sets of systematic
          variations until at least `nResampling` runs have been made.
        - `None`: Only systematic errors are considered.
        
    result_key
        The `.obsm` key of `adata` where to store the mean annotation. If
        `None`, do not write to `adata` and return result instead.
    error_key
        The `.obsm` key of `adata` where to store the total error estimate. If
        `None`, uses `"{result_key}_err"`.
    stat_error_key
        The `.obsm` key of `adata` where to store the statistical error
        estimate. If `None`, uses `"{result_key}_err_stat"`. If `False`, do not
        include a separate statistical error estimate in any result. If
        `mode=='simultaneous'`, statistical error estimates are not available.
    syst_error_key
        The `.obsm` key of `adata` where to store the systematical error
        estimate. If `None`, uses `"{result_key}_err_syst"`. If `False`, do not
        include a separate systematical error estimate in any result. If
        `mode=='simultaneous'`, systematical error estimates are not available.
    seed
        The random seed to use for the statistical resampling.
    verbose
        Level of verbosity, with `0` (no output), `1` (some output), ...
    **kw_args
        Additional keyword arguments are forwarded to every annotation run as
        keyword arguments to :func:`~tacco.tools.annotate`. See
        :func:`~tacco.tools.annotate` for details.
        
    Returns
    -------
    Depending on `result_key`, either returns the original `adata` with\
    annotation and error estimates written in the corresponding `.obsm` keys,\
    or just the annotation and error estimates as a tuple of\
    :class:`~pandas.DataFrame` instances in the order: mean, total error,\
    statistical error (if available), systematical error (if available).
    
    """
    
    if mode == 'jackknife':
        print('Annotation is a very nonlinear process, so statistical errors derived from the jackknife procedure are not really reliable. So unless you know exactly what you are doing, use a different `mode`!')
    
    def annotation_function(adata, **kw_args):
    
        result = tools.annotate(adata, **kw_args)
        
        if 'result_key' in kw_args:
            result = result[kw_args['result_key']]
        
        return result
    
    stat_error = (mode is not None and mode != 'simultaneous' and (~isinstance(stat_error_key, bool) or not stat_error_key))
    syst_error = (mode != 'simultaneous' and (~isinstance(syst_error_key, bool) or not syst_error_key))
    result = wrap_uncertainty(
        adata,
        function=annotation_function,
        variations=variations,
        nResampling=nResampling,
        mode=mode,
        stat_error=stat_error,
        syst_error=syst_error,
        seed=seed,
        verbose=verbose,
        **kw_args,
        reference=reference,
        annotation_key=annotation_key,
    )
    
    (mean, total, stat, syst) = (None, None, None, None)
    if stat_error and syst_error:
        (mean, total, stat, syst) = result
    elif stat_error:
        (mean, total, stat) = result
    elif syst_error:
        (mean, total, syst) = result
    else:
        (mean, total) = result

    if result_key is None:
        if stat is None and syst is None:
            return (mean, total)
        elif syst is None:
            return (mean, total, stat)
        elif stat is None:
            return (mean, total, syst)
        else:
            return (mean, total, stat, syst)
        
    adata.obsm[result_key] = mean.reindex(index=adata.obs.index)
    if error_key is None:
        error_key = f'{result_key}_err'
    adata.obsm[error_key] = total.reindex(index=adata.obs.index)
    if stat is not None:
        if stat_error_key is None:
            stat_error_key = f'{result_key}_err_stat'
        adata.obsm[stat_error_key] = stat.reindex(index=adata.obs.index)
    if syst is not None:
        if syst_error_key is None:
            syst_error_key = f'{result_key}_err_syst'
        adata.obsm[syst_error_key] = syst.reindex(index=adata.obs.index)
    
    return adata
