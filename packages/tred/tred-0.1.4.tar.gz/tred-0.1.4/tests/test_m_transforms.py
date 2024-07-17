import numpy as np
import pytest
from scipy.stats import special_ortho_group
from numpy.testing import assert_allclose

from tred import (
    generate_transform_pair_from_matrix,
    generate_dctii_m_transform_pair,
    generate_dstii_m_transform_pair,
)

GLOBAL_SEED = 1

TENSOR_SHAPES = [(4, 3, 2), (5, 7, 6), (2, 2, 6)]
MATRIX_SHAPES = [(4, 6), (7, 3)]
VECTOR_SHAPES = [(4,)]

SCIPY_GENERATORS = [
    generate_dctii_m_transform_pair,
    generate_dstii_m_transform_pair,
]


@pytest.mark.parametrize("shape", TENSOR_SHAPES + MATRIX_SHAPES + VECTOR_SHAPES)
def test_matrix_defined_transforms(shape):
    """Compare implementation with (slower) mathematically clear version"""
    # scaling constant (arbitrary)
    C = 5

    rng = np.random.default_rng(seed=GLOBAL_SEED)

    # tensors of various sizes with uniformly distributed elements within [-0.5*C, 0.5*C)
    X = rng.random(size=shape) * C - 0.5 * C
    M_mat = special_ortho_group.rvs(shape[-1], random_state=rng)

    if len(X.shape) == 3:
        n, p, t = shape
        # apply across tensor tubes
        hatX_expected = np.zeros(shape=(n, p, t))
        for i in range(n):
            for j in range(p):
                hatX_expected[i, j, :] = M_mat @ X[i, j, :]
    elif len(X.shape) == 2:
        k, t = shape
        hatX_expected = np.zeros(shape=(k, t))
        for i in range(k):
            hatX_expected[i, :] = M_mat @ X[i, :]
    elif len(X.shape) == 1:
        hatX_expected = M_mat @ X
    else:
        raise RuntimeError("Unexpected shape passed in testing module")

    # compare with our optimized implementation
    M, Minv = generate_transform_pair_from_matrix(M_mat)
    assert_allclose(hatX_expected, M(X))

    # test inverse transform working as expected
    assert_allclose(X, Minv(M(X)))


@pytest.mark.parametrize("shape", TENSOR_SHAPES + MATRIX_SHAPES)
@pytest.mark.parametrize("transform_generator", SCIPY_GENERATORS)
def test_scipy_fft_wrapper_transforms(shape, transform_generator):
    # scaling constant (arbitrary)
    C = 5

    rng = np.random.default_rng(seed=GLOBAL_SEED)

    # tensors of various sizes with uniformly distributed elements within [-0.5*C, 0.5*C)
    X = rng.random(size=shape) * C - 0.5 * C
    M, Minv = transform_generator(shape[-1])

    if len(X.shape) == 3:
        n, p, t = shape
        # apply across tensor tubes
        hatX_expected = np.zeros(shape=(n, p, t))
        for i in range(n):
            for j in range(p):
                hatX_expected[i, j:] = M(X[i, j, :])
    elif len(X.shape) == 2:
        k, t = shape
        hatX_expected = np.zeros(shape=(k, t))
        for i in range(k):
            hatX_expected[i, :] = M(X[i, :])
    else:
        raise RuntimeError("Unexpected shape passed in testing module")

    assert_allclose(hatX_expected, M(X))

    # test inverse transform working as expected
    assert_allclose(X, Minv(M(X)))
