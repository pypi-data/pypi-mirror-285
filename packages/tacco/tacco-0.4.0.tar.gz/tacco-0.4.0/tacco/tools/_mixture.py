import numpy as np
import pandas as pd
import anndata as ad
import gc

from .. import get
from .. import preprocessing
from .. import utils
from . import _helper as helper
from ._annotate import annotate
from scipy.sparse import issparse, csr_matrix
import scipy.linalg
import scipy.optimize

try: # dont fail importing the whole module, just because a single annotation method is not available
    import jax
    jax.config.update("jax_enable_x64", True)
    HAVE_JAX = True
except ImportError:
    HAVE_JAX = False

def _objective_f(x, T, X, model):
    Nt,Ng = T.shape # type by gene matrix
    No,Ng2 = X.shape # obs by gene matrix
    assert(Ng == Ng2)
    
    phi = jax.numpy.reshape(x.astype(T.dtype),(No, Nt)) # obs by type matrix
    f = phi**2 # make f positive
    f /= f.sum(axis=1)[:,None] # make f sum to one
    
    fT = f @ T # obs by gene
    
    if model == 'multinomial':
        loglikelyhood = (X * jax.numpy.log(fT)).sum(axis=1) @ (1/X.sum(axis=1)) # total count weight accelerates convergence
    elif model == 'poisson':
        loglikelyhood = jax.scipy.stats.poisson.logpmf(X, X.sum(axis=1)[:,None] * fT).sum(axis=1) @ (1/X.sum(axis=1)) # total count weight accelerates convergence
    elif model == 'overlap':
        loglikelyhood = jax.numpy.sqrt(X * fT + 1e-30).sum(axis=1) @ (1/jax.numpy.sqrt(X.sum(axis=1))) # total count weight accelerates convergence
    elif model == 'overnomial':
        loglikelyhood1 = (X * jax.numpy.log(fT)).sum(axis=1) @ (1/X.sum(axis=1))
        loglikelyhood2 = jax.numpy.sqrt(X * fT + 1e-30).sum(axis=1) @ (1/jax.numpy.sqrt(X.sum(axis=1)))
        loglikelyhood = loglikelyhood1 + loglikelyhood2
    else:
        raise ValueError(f'model {model} is not available!')
    
    return -loglikelyhood
if HAVE_JAX:
    _objective_fdf_ = jax.value_and_grad(_objective_f)
else:
    def _objective_fdf_(x, T, X, model):
        raise ImportError('The module JAX could not be imported, but is required to use the annotate method "mixture"! Maybe it is not installed properly?')
def _objective_fdf(x, T, X, model):
    v,g = _objective_fdf_(x, T, X, model)
    g = np.array(g)
    print(v,np.sqrt((g**2).sum()))
    return v, g

def _annotate_mixture(
    adata,
    reference,
    annotation_key=None,
    model='multinomial',
    tol=1e-8,
    dtype=np.float32,
    ):

    """\
    Implements the functionality of :func:`~annotate_mixture` without data
    integrity checks.
    """
    average_profiles = utils.get_average_profiles(annotation_key, reference)
    
    T = average_profiles.to_numpy().T.astype(dtype)

    X = adata.X.astype(dtype)
    if scipy.sparse.issparse(X):
        X = X.A
    
    Nt,Ng = T.shape # type by gene matrix
    No,Ng2 = X.shape # obs by gene matrix
    assert(Ng == Ng2)
    T += 1e-9 / Ng # regularize type profiles
    
    guess = np.sqrt(np.ones(No*Nt,dtype=dtype) / Nt)
    
    if isinstance(model, str):
        models = [model]
    else:
        models = model
    
    for model in models:
        result = scipy.optimize.minimize(_objective_fdf, guess, args=(T,X,model), method='L-BFGS-B', jac=True, tol=tol,).x
        guess = result

    cell_type = (result**2).reshape((No, Nt))
    
    cell_type = pd.DataFrame(cell_type, columns=average_profiles.columns, index=adata.obs.index)
    
    cell_type = helper.normalize_result_format(cell_type)
    
    return cell_type

def annotate_mixture(
    adata,
    reference,
    annotation_key=None,
    counts_location=None,
    model='multinomial',
    tol=1e-8,
    ):

    """\
    Annotates an :class:`~anndata.AnnData` using reference data by fitting a
    mixture model.

    This is the direct interface to this annotation method. In practice using
    the general wrapper :func:`~tacco.tools.annotate` is recommended due to its
    higher flexibility.
    
    Parameters
    ----------
    adata
        An :class:`~anndata.AnnData` including expression data in `.X`.
    reference
        Reference data to get the annotation definition from.
    annotation_key
        The `.obs` and/or `.varm` key where the annotation and/or profiles are
        stored in the `reference`. If `None`, it is inferred from `reference`,
        if possible.
    counts_location
        A string or tuple specifying where the count matrix is stored, e.g.
        `'X'`, `('raw','X')`, `('raw','obsm','my_counts_key')`,
        `('layer','my_counts_key')`, ... For details see
        :func:`~tacco.get.counts`.
    model
        Which model to use. Available models are:
        
        - 'multinomial': MLE `X_og ~ multinomial(sum_t f_ot T_tg)`
        - 'poisson': MLE `X_og ~ poisson(sum_t f_ot T_tg sum_g X_og)`
        - 'overlap': Maximum Overlap of `X_og` and `sum_t f_ot T_tg` in
          the sense of maximal Bhattacharyya coefficient
        - 'overnomial': optimizes the sum of objective functions of
          'multinomial' and 'overlap'
        
        where `X_og` are the counts in `adata` per observation `o` and gene
        `g`, `f_ot` is the fraction of counts in observation `o` per type `t`
        normalized such that `sum_t f_ot == 1`, `T_tg` is the type profile of
        type `t` for gene `g` normalized such that `sum_g T_tg == 1`.
    tol
        Solver tolerance
        
    Returns
    -------
    Returns the annotation in a :class:`~pandas.DataFrame`.
    
    """
    
    adata, reference, annotation_key = helper.validate_annotation_args(adata, reference, annotation_key, counts_location, full_reference=False)

    # call typing without data integrity checks
    cell_type = _annotate_mixture(
        adata=adata,
        reference=reference,
        annotation_key=annotation_key,
        model=model,
        tol=tol,
    )
    
    return cell_type
