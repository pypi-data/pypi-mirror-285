import pytest
import numpy as np
import pandas as pd
import anndata as ad
import tacco as tc
import scipy.sparse

@pytest.fixture(scope="session")
def adata_sample_counts():
    def _adata_sample_counts(sparse, replace=False, fraction=0.0):
        baseX = np.array([
            [ 0, 0, 0, 0, 0,],
            [ 0, 0, 0, 0, 1,],
            [ 0, 0, 0, 0,10,],
            [ 0, 0,10, 0,10,],
            [ 0, 1, 2, 3, 4,],
            [10,10,10,10,10,],
        ])
        if sparse:
            baseX = scipy.sparse.csr_matrix(baseX)
        adata = ad.AnnData(baseX)
        sampledX = baseX.copy()
        if fraction <= 0.0:
            if sparse:
                sampledX.data[:] = 0
            else:
                sampledX[:,:] = 0
        elif replace:
            if fraction == 0.5:
                sampledX[1,4] = 0
                sampledX[2,4] = 5
                sampledX[3,2] = 6
                sampledX[3,4] = 4
                sampledX[4,1] = 0
                sampledX[4,2] = 1
                sampledX[4,3] = 3
                sampledX[4,4] = 1
                sampledX[5,0] = 12
                sampledX[5,1] = 2
                sampledX[5,2] = 4
                sampledX[5,3] = 1
                sampledX[5,4] = 6
            elif fraction == 1.0:
                sampledX[4,1] = 2
                sampledX[4,2] = 2
                sampledX[4,3] = 3
                sampledX[4,4] = 3
                sampledX[5,0] = 18
                sampledX[5,1] = 7
                sampledX[5,2] = 9
                sampledX[5,3] = 5
                sampledX[5,4] = 11
            elif fraction == 2.0:
                sampledX[1,4] = 2
                sampledX[2,4] = 20
                sampledX[3,2] = 18
                sampledX[3,4] = 22
                sampledX[4,1] = 2
                sampledX[4,2] = 6
                sampledX[4,3] = 3
                sampledX[4,4] = 9
                sampledX[5,0] = 23
                sampledX[5,1] = 16
                sampledX[5,2] = 29
                sampledX[5,3] = 17
                sampledX[5,4] = 15
            else:
                raise NotImplementedError()
        else:
            if fraction == 0.5:
                sampledX[1,4] = 0
                sampledX[2,4] = 5
                sampledX[3,2] = 3
                sampledX[3,4] = 7
                sampledX[4,1] = 1
                sampledX[4,2] = 1
                sampledX[4,3] = 0
                sampledX[4,4] = 3
                sampledX[5,0] = 0
                sampledX[5,1] = 7
                sampledX[5,2] = 6
                sampledX[5,3] = 9
                sampledX[5,4] = 3
            elif fraction == 1.0:
                pass
            else:
                raise NotImplementedError()
        sdata = ad.AnnData(sampledX)
        return adata, sdata
    return _adata_sample_counts

def _test_sample_counts(adata_sample_counts, sparse, replace, fraction):
    adata, sdata = adata_sample_counts(sparse, replace, fraction) # contains result for frozen seed=42
    
    result = tc.tl.sample_counts(adata.X, replace=replace, fraction=fraction, seed=42)
    
    if sparse:
        tc.testing.assert_sparse_equal(result, sdata.X)
    else:
        tc.testing.assert_dense_equal(result, sdata.X)

@pytest.mark.parametrize('sparse', [True,False])
@pytest.mark.parametrize('fraction', [0.0,0.5,1.0,2.0])
def test_sample_counts_with_replacement(adata_sample_counts, sparse, fraction):
    _test_sample_counts(adata_sample_counts, sparse=sparse, replace=True, fraction=fraction)
@pytest.mark.parametrize('sparse', [True,False])
@pytest.mark.parametrize('fraction', [0.0,0.5,1.0])
def test_sample_counts_without_replacement(adata_sample_counts, sparse, fraction):
    _test_sample_counts(adata_sample_counts, sparse=sparse, replace=False, fraction=fraction)

@pytest.fixture(scope="session")
def adata_uncertainty():
    test_shape = (30,20)
    counts_per_obs = 1000
    test_X = np.zeros(test_shape)
    np.random.seed(42)
    for row, count_row in enumerate(np.random.choice(np.arange(test_shape[1]),size=(test_shape[0],counts_per_obs))):
        for gene in count_row: 
            test_X[row,gene] += 1
    test_adata = ad.AnnData(test_X)
    return test_adata

@pytest.mark.parametrize('mode', ['jackknife','bootstrap','simultaneous',None])
@pytest.mark.parametrize('returntype', ['array','dataframe','series'])
def test_uncertainty(adata_uncertainty, mode, returntype):
    
    def wrap_result(result):
        if returntype == 'dataframe':
            return pd.DataFrame(result)
        elif returntype == 'series':
            return pd.Series(result[0])
        else:
            return result
    def assert_equal(*args, **kwargs):
        if returntype == 'dataframe':
            return tc.testing.assert_frame_equal(*args, **kwargs)
        elif returntype == 'series':
            return tc.testing.assert_series_equal(*args, **kwargs)
        else:
            return tc.testing.assert_dense_equal(*args, **kwargs)
        
    def testf(adata, offset):
        return wrap_result(adata.X + offset)
    def binomial_uncertainty(X, offsets):
        bus = []
        for o in offsets:
            Xo = X + o
            sums = tc.sum(Xo, axis=1)
            sums[sums == 0] = 1
            bu = np.sqrt(Xo * (1-Xo/sums[:,None]))
            bus.append(bu)
        return wrap_result(np.mean(bus, axis=0))
    def systematic_uncertainty(X, offsets):
        return wrap_result(np.full_like(X, np.std(offsets)))
    def total_uncertainty(X, offsets):
        if mode is None:
            return systematic_uncertainty(X, offsets)
        else:
            return np.sqrt(binomial_uncertainty(X, offsets)**2 + systematic_uncertainty(X, offsets)**2)
    def mean_result(X, offsets):
        return wrap_result(X + np.mean(offsets))
    
    adata = adata_uncertainty
    
    offsets = [0,2]
    
    result = tc.tl.wrap_uncertainty(adata, function=testf, variations={'offset':offsets}, nResampling=200, mode=mode, stat_error=True, syst_error=True, seed=42, )
    
    # freeze the smallest possible deviation per mode
    rtol = 5e-3 if mode == 'jackknife' else (4e-2 if mode == 'bootstrap' else (5e-2 if mode == 'simultaneous' else 1e-5))
    assert_equal(result[0], mean_result(adata.X, offsets), rtol=rtol)
    if mode != 'simultaneous' and mode is not None:
        rtol = 2e-1
        assert_equal(result[2], binomial_uncertainty(adata.X, offsets), rtol=rtol)
        rtol = 2e-5 if mode == 'jackknife' else 1e-5
        assert_equal(result[3], systematic_uncertainty(adata.X, offsets), rtol=rtol)
    rtol = 1e-5 if mode is None else 2e-1
    assert_equal(result[1], total_uncertainty(adata.X, offsets), rtol=rtol)

@pytest.fixture(scope="session")
def adata_reference_and_typing_uncertainty():
    reference = ad.AnnData(X=np.array([
        [1,0,0],
        [2,0,0],
        [3,0,0],
        [0,1,0],
        [0,2,0],
        [0,3,0],
        [0,0,1],
        [0,0,2],
        [0,0,3],
    ]))
    reference.obs=pd.DataFrame({
        'type': pd.Series([0,0,0,1,1,1,2,2,2,],dtype='category',index=pd.Index(range(reference.shape[0])).astype(str)),
    })
    adata = ad.AnnData(X=np.array([
        [  1,  0,  0],
        [ 10,  0,  0],
        [100,  0,  0],
        [  1,  1,  0],
        [  1, 10,  0],
        [  1,100,  0],
        [  1,  1,  1],
        [  1,  1, 10],
        [  1,  1,100],
        [  1,  1,  0],
        [ 10, 10,  0],
        [100,100,  0],
    ]))
    adata.obsm['type']=pd.DataFrame((adata.X/tc.sum(adata.X,axis=1)[:,None]).astype(np.float64),index=adata.obs.index,columns=pd.Index(reference.obs['type'].cat.categories,dtype=reference.obs['type'].dtype,name='type'))
    return adata, reference

@pytest.mark.skip(reason="uncertainty is optional - test depended on legacy calibration arguments")
def test_annotate_uncertainty(adata_reference_and_typing_uncertainty):
    adata, reference = adata_reference_and_typing_uncertainty
    typing = adata.obsm['type']

    result = tc.tl.annotate_uncertainty(adata, reference, 'type', platform_iterations=None, variations=[
        {'method':['projection'], 'projection': ['naive','bc','bc2'], 'deconvolution': [False,'linear']},
        {'method':['OT'], 'epsilon':[1,100]}
    ], nResampling=10)
    tc.testing.assert_frame_equal(result[0], typing, rtol=0.2, atol=0.2)
    
    deviation = 1 / np.sqrt(adata.X.sum(axis=1)+1)[:,None] # error should scale with the sqrt of the counts
    deviation = deviation * (adata.X != 0) # error should be 0 when there is no evidence at all
    deviation = deviation * ((deviation != 0).sum(axis=1) != 1)[:,None] # error should be 0 when there is only a single choice
    deviation *= 0.50 # nuisance factor
    deviation = pd.DataFrame(deviation.astype(np.float64), index=typing.index, columns=typing.columns)
    
    tc.testing.assert_frame_equal(result[1], deviation, rtol=1e-1, atol=1e-1)
