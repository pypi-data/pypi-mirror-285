import scanpy as sc
import anndata as ad
import pandas as pd
import numpy as np
from numpy.random import Generator, PCG64
from scipy.spatial import distance_matrix
from scipy.sparse import csc_matrix, issparse
from scipy import integrate
from numba import njit

from ..preprocessing._platform import _get_random_platform_factors
from .. import utils

def add_random_coordinates(df, rng):
    n = df.index.shape[0]
    df['x'] = rng.random(n)
    df['y'] = rng.random(n)

@njit(cache=True)
def _inplace_minimium(A,B):
    n0,n1 = A.shape
    assert(A.shape==B.shape)
    for i in range(n0):
        for j in range(n1):
            if B[i,j] < A[i,j]:
                A[i,j] = B[i,j]
    return A

def get_distances(sampling_df, obs_df):
    # use periodic boundaries to use all data equally 
    prime_x = sampling_df['x']
    shift_x = prime_x + (prime_x<0.5) - (prime_x>0.5)
    prime_y = sampling_df['y']
    shift_y = prime_y + (prime_y<0.5) - (prime_y>0.5)
    x_y = obs_df[['x','y']].to_numpy()
    distances = utils.dense_distance_matrix(np.array([prime_x,prime_y]).T, x_y)
    _inplace_minimium(distances, utils.dense_distance_matrix(np.array([shift_x,prime_y]).T, x_y))
    _inplace_minimium(distances, utils.dense_distance_matrix(np.array([shift_x,shift_y]).T, x_y))
    _inplace_minimium(distances, utils.dense_distance_matrix(np.array([prime_x,shift_y]).T, x_y))
    return distances

def get_weights(distances, length_scale, psf = 'gauss'):
    #psf = 0.25 # 0.001 ~ circle, 1.0 ~ gauss
    n_samples, n_cells = distances.shape
    
    # get consistently normalized weights: sum_cells int_space psf(distance)
    dV = 1 / n_cells
    if psf == 'gauss':
        norm = (length_scale * np.sqrt(2 * np.pi))**2
        weights = dV * np.exp(-0.5 * (distances/length_scale)**2) / norm
    elif psf == 'disc':
        norm = length_scale**2 * np.pi
        weights = dV * (distances < length_scale) / norm
    else:
        g_scale = 1.16 # makes width == 1.0 correspond (approximately) to the gaussian case
        psf = float(psf)
        width = psf*length_scale
        g = lambda x: (np.tanh(-(x-length_scale)/(g_scale*width))+1)*0.5
        f = lambda y, x: g(np.sqrt(x**2+y**2))
        x0 = min(1, 5 * (length_scale + g_scale*width)) # restrict numerical integration range for better convergence
        norm = integrate.dblquad(f, -x0, x0, lambda x: -x0, lambda x: x0,epsabs=1e-10)[0]
        weights = dV * g(distances) / norm

    # cutoff small weights: does not really matter, but makes the matrix sparse and calculations faster
    weights[weights < 1e-3] = 0
    weights = csc_matrix(weights)

    weight_per_cell = 1 / (n_cells*norm)
    
    print('%s weight_per_cell: %s' % (psf, weight_per_cell))
        
    return weights

def get_weights_yield(distances, length_scale, psf = 'gauss', capture_rate=1.0):
    #psf = 0.25 # 0.001 ~ circle, 1.0 ~ gauss
    n_samples, n_cells = distances.shape
    
    # get consistently normalized weights: psf(0) = capture_rate
    if psf == 'gauss':
        weights = np.exp(-0.5 * (distances/length_scale)**2)
    elif psf == 'disc':
        weights = 1.0 * (distances < length_scale)
    else:
        g_scale = 1.16 # makes width == 1.0 correspond (approximately) to the gaussian case
        psf = float(psf)
        width = psf*length_scale
        g = lambda x: (np.tanh(-(x-length_scale)/(g_scale*width))+1)*0.5
        weights = g(distances) / g(0)
    
    if capture_rate == 'normalized':
        weights /= utils.get_sum(weights,axis=1)[:,None]
    else:
        weights *= capture_rate

    # cutoff small weights: does not really matter, but makes the matrix sparse and calculations faster
    weights[weights < 1e-3] = 0
    weights = csc_matrix(weights)

    return weights

def mix_in_silico(
    adata,
    type_key=None,
    topic_key=None,
    n_samples=30000,
    bead_shape=0.1,
    bead_size=1.0,
    norm_cells=False,
    platform_log10_mean=None,
    platform_log10_std=0.6,
    seed=42,
    round=True,
    min_counts=100,
    capture_rate=1.0,
):

    """\
    Given single cell data, create an in-silico mixed dataset. The mixtures are
    generated by placing the cells randomly in space, placing measurement points
    ("beads") randomly in space, and convoluting them with some spatial profile,
    e.g. a gaussian.
    Optionally also applies a random log-laplace distributed rescaling per gene.
    
    Parameters
    ----------
    adata
        An :class:`~anndata.AnnData` with annotation in `.obs`.
    type_key
        An `.obs` key with categorical information to propagate through to the
        mixed data, e.g. cell types.
    topic_key
        An `.obsm` key with continuous information to propagate through to the
        mixed data, e.g. transciptional topics.
    n_samples
        The number of measurement points ("beads") which are put randomly in
        space. Note that depending on `min_counts` and the mixing parameters
        the number of returned measurement points is somewhat smaller than this
        value.
    bead_shape
        The shape to use for determining the contributions of cells to "beads".
        Can also be a list of shapes to save setup time wrt. isolated calls.
        Possible values:
        
        - 'gauss': weights decrease with distance like a gaussian.
        - 'disc': weights are constant until some distance and then drop to
          `0`.
        - number: weights decrease with distance according to a tanh-profile
          with the sharpness of the decrease given by this number. It can be
          used to interpolates between `0` (disc-like) and `1` (gauss-like).
    bead_size
        Scaling factor determining the effetive size of the beads/profile. A
        value of `1` corresponds to tightly packed cells and beads of the size
        of a cell.
    norm_cells
        Whether to normalize the total counts per cell in the single cell data
        prior to mixing.
    platform_log10_mean
        log10 of the mean of the Laplace distribution for Log-Laplace
        distributed per gene platform effect. The per-gene factors are
        available in `.var['platform_effect']`. If `None`, no platform factors
        are applied.
    platform_log10_std
        log10 of the standard deviation of the Laplace distribution for
        Log-Laplace distributed per gene platform effect
    seed
        The random seed to use
    round
        Whether to round the resulting expression matrix to integer counts
        after rescaling
    min_counts
        The returned adata is filtered to have at least this number of counts
        per observation. If `None`, return all observations.
    capture_rate
        The fraction of counts to keep from a cell with maximum coverage from
        the bead. If `'normalized'`, normalize weights per bead to sum to 1. If
        `None`, normalize the bead psf to 1.
        
    Returns
    -------
    Returns the mixed data as :class:`~anndata.AnnData`. If `beadshape` is a\
    list, returns a dictionary containing a :class:`~anndata.AnnData` per\
    `beadshape`.
    
    """
    
    # generate random positions for cells and sampling points (simulated beads) in the range of 0..1
    rg = Generator(PCG64(seed=seed))
    cell_pos = pd.DataFrame(index=adata.obs.index)
    add_random_coordinates(cell_pos, rg)
    sampling = pd.DataFrame(index=list(range(n_samples)))
    add_random_coordinates(sampling, rg)
    
    # determine length scale (effective bead size) which incorporates the actual bead size and the cell size (determined by assuming that the cells fill the space completely) 
    n_cells = cell_pos.index.shape[0]
    density = 1 / n_cells
    length_scale = bead_size * 0.5 * np.sqrt(density)
    
    # get distances between simulated beads and cells, matrix of shape n_samples x n_cells
    distances = get_distances(sampling, cell_pos)
    
    # get single cell annotation matrix of shape n_cells x n_types
    dummies = pd.get_dummies(adata.obs[type_key])
    
    # optionally normalize cell counts
    if norm_cells:
        adata = adata.copy()
        sc.pp.normalize_total(adata)
    
    if platform_log10_mean is None:
        rescaling_factors = np.ones(adata.shape[1], dtype=adata.X.dtype)
    else:
        rescaling_factors = _get_random_platform_factors(adata, platform_log10_mean=platform_log10_mean, platform_log10_std=platform_log10_std, seed=seed).to_numpy()
    
    # support multiple calculation for multiple bead_shapes at once as distance calculation above takes a while
    return_dict = len(np.array(bead_shape).shape) != 0
    if not return_dict:
        bead_shape = [bead_shape]
    in_silico_data = {}
    for bs in bead_shape:
        # get the weight matrix of shape n_samples x n_cells
        if capture_rate is None:
            weights = get_weights(distances, length_scale, psf=bs)
        else:
            weights = get_weights_yield(distances, length_scale, psf=bs, capture_rate=capture_rate)
        
        # get the true spatial expression and save it in the sampling data
        sample_X = (weights @ adata.X)#.astype(int)
        if platform_log10_mean is not None:
            utils.col_scale(sample_X, rescaling_factors)
        if round:
            if issparse(sample_X):
                np.around(sample_X.data, decimals=0, out=sample_X.data)
            else:
                np.around(sample_X, decimals=0, out=sample_X)
        if issparse(sample_X):
            sample_X.eliminate_zeros()
        sample_data = ad.AnnData(X=sample_X, obs=sampling, var=adata.var.copy())
        if platform_log10_mean is not None:
            sample_data.var['platform_effect'] = rescaling_factors
        
        # get the true spatial label weights and save them in the sampling data
        weighted_labels = weights @ dummies
        sample_data.obsm[type_key] = pd.DataFrame(weighted_labels, index=sample_data.obs.index, columns=dummies.columns)

        # get the true spatial label read weights and save them in the sampling data
        weighted_labels = weights @ (dummies * np.array(adata.X @ rescaling_factors).flatten()[:,None])
        sample_data.obsm['reads_'+type_key] = pd.DataFrame(weighted_labels, index=sample_data.obs.index, columns=dummies.columns)

        if platform_log10_mean is not None:
            # get the true spatial label read weights without platform factors and save them in the sampling data
            weighted_labels = weights @ (dummies * np.array(adata.X.sum(axis=1)).flatten()[:,None])
            sample_data.obsm['bare_reads_'+type_key] = pd.DataFrame(weighted_labels, index=sample_data.obs.index, columns=dummies.columns)
        
        if topic_key is not None:
            topics = adata.obsm[topic_key].copy()
            
            # normalize topics to 1 per cell
            topics /= topics.sum(axis=1)[:,None]
            weighted_topics = weights @ topics.fillna(0)
            sample_data.obsm[topic_key] = pd.DataFrame(weighted_topics, index=sample_data.obs.index, columns=topics.columns)
            
            # normalize topics to number of reads per cell
            topics *= np.array(adata.X @ rescaling_factors).flatten()[:,None]
            weighted_topics = weights @ topics.fillna(0)
            sample_data.obsm['bare_reads_'+topic_key] = pd.DataFrame(weighted_topics, index=sample_data.obs.index, columns=topics.columns)

            if platform_log10_mean is not None:
                # normalize topics to number of reads per cell without platform factors
                topics *= np.array(adata.X.sum(axis=1)).flatten()[:,None]
                weighted_topics = weights @ topics.fillna(0)
                sample_data.obsm['bare_reads_'+topic_key] = pd.DataFrame(weighted_topics, index=sample_data.obs.index, columns=topics.columns)

        if min_counts is not None:
            # remove beads with too few counts
            sample_data = sample_data[utils.get_sum(sample_data.X, axis=1) >= min_counts]
        
        in_silico_data[bs] = sample_data

    if return_dict:
        return in_silico_data
    else:
        return in_silico_data[bead_shape[0]]
