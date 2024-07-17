import numpy as np
from scipy import sparse

from typing import Literal
from numpy.typing import NDArray

from . import preprocessing


def zero_as_nan(x):
    return np.where(x, x, np.nan)


def norm_q(x: NDArray, k=0.7413) -> NDArray:
    axis = int(x.ndim != 1)
    q = np.nanquantile(zero_as_nan(x), [0.25, 0.5, 0.75], axis)[..., None]

    iqr = k * (q[2] - q[0])
    iqr[iqr == 0] = 1

    return (x - q[1]) / iqr


def norm_z(x: NDArray) -> NDArray:
    axis = int(x.ndim != 1)
    mean = np.nanmean(zero_as_nan(x), axis)

    std = np.nanstd(zero_as_nan(x), axis)
    std[std == 0] = 1

    return (x - mean[..., None]) / std[..., None]


def wstats(x, w):
    xw = x * w

    sum_weights = w @ w.T
    sum_x = xw @ w.T
    mean = sum_x / sum_weights
    sum_xy = xw @ xw.T

    return sum_weights, sum_x, mean, sum_xy


def _var(x, w, sw, s, m):
    x = (x**2 * w) @ w.T
    x -= 2 * s * m
    x += sw * m**2
    x /= sw
    return x


def wcorrcoef(x: NDArray, weights: NDArray | None = None):
    if weights is None:
        return np.corrcoef(x)

    sum_weights, sum_x, mean, sum_xy = wstats(x, weights)
    var = _var(x, weights, sum_weights, sum_x, mean)

    x = sum_x * mean.T
    x += x.T
    x -= sum_xy
    x -= sum_weights * mean * mean.T

    x /= np.sqrt(var * var.T) * sum_weights
    return -x


def weights(x, k=2.0, alpha=0.5, method: Literal["exp", "const"] = "exp") -> NDArray:
    if method == "exp":
        return np.minimum(1, k ** (x * alpha))
    elif method == "const":
        return np.where(x <= 0, alpha, 1)
    else:
        raise ValueError(f"Expected one of ('exp', 'const') as a method, got: {method}")


def norm_q_sparse(mat, k=0.7413):
    mat = sparse.csr_matrix(mat, copy=True)
    K = np.zeros(mat.shape[0])

    for i, (j, l) in enumerate(zip(mat.indptr, mat.indptr[1:])):
        if mat.data[j:l].size:
            q = np.nanquantile(mat.data[j:l], q=[0.25, 0.5, 0.75])
            K[i] = q[1]

            if iqr := (k * (q[2] - q[0])):
                mat.data[j:l] /= iqr
                K[i] /= iqr

    mat = mat.tocsc()
    return mat, K


def norm_z_sparse(mat):
    mat = sparse.csr_matrix(mat, copy=True)
    K = np.zeros(mat.shape[0])

    for i, (j, l) in enumerate(zip(mat.indptr, mat.indptr[1:])):
        if mat.data[j:l].size:
            K[i] = np.mean(mat.data[j:l])

            if sd := np.std(mat.data[j:l]):
                mat.data[j:l] /= sd
                K[i] /= sd

    mat = mat.tocsc()
    return mat, K


def odds_ratio(mat):
    mat = sparse.csr_array(mat, dtype=bool).astype(int)
    n = mat.shape[1]

    tp = mat.dot(mat.T).todense()
    fp = mat.sum(axis=1) - tp
    fn = fp.T
    tn = n - tp - fp - fn

    OR = np.log((tp * tn) / (fp * fn))
    pseudoOR = np.log(tp / np.sqrt(fp + fn))
    cosparsity = tp / n

    return OR, pseudoOR, cosparsity
