import numpy as np
from sklearn.neighbors import NearestNeighbors


def knn_weights(k, m, n):
    w = np.ones(k - 1) / np.arange(n, n + k - 1)
    w *= (1 - m) / sum(w)

    return np.append(m, w)


def knn_blur(arr, k=5, m=0.6, n=7, return_neighbors=False):
    knn = NearestNeighbors(n_neighbors=k).fit(arr)
    neighbors = knn.kneighbors(arr, return_distance=False)

    w = knn_weights(k, m, n)

    out = np.sum(arr[neighbors] * w[:, None], axis=1)

    if return_neighbors:
        return out, neighbors

    return out


def gaussian_kernel(distance, bandwidth):
    return np.exp(-0.5 * (distance / bandwidth) ** 2)


def gaussian_blur(arr, k=5, bandwidth=None, return_neighbors=False):
    arr = arr.T
    knn = NearestNeighbors(n_neighbors=k).fit(arr)
    distance, neighbors = knn.kneighbors(arr)

    if bandwidth is None:
        bandwidth = np.percentile(distance, 95, axis=1, keepdims=True)

    w = gaussian_kernel(distance, bandwidth)
    w /= np.sum(w, axis=1)[:, None]

    out = np.sum(arr[neighbors] * w[..., None], axis=1).T

    if return_neighbors:
        return out, neighbors

    return out
