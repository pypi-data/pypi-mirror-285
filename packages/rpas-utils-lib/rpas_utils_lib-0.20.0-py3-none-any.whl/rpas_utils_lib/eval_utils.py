import numpy as np
import multiprocessing as mp
from joblib import Parallel, delayed
from tqdm import tqdm
from typing import Any

def _l2_squared_min(a: np.ndarray, b: np.ndarray) -> float:
    """Compute the minimum squared L2 distance from each point in a to points in b."""
    return np.min(np.sum((a - b) ** 2, axis=1))

def _l2_squared(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute the squared L2 distances from each point in a to points in b."""
    return np.sum((a - b) ** 2, axis=1)

def calc_chamfer_distance(
        T_S: Any, G: Any, progress: bool = False, parallel: bool = True) -> float:
    """
    Calculate chamfer distance/loss as defined in Section II.E of 
    [Non-Rigid Point Set Registration Networks](https://arxiv.org/abs/1904.01428).

    Parameters
    ----------
    T_S : array-like
        The transformed source 2-D points set.
    G : array-like
        The target 2-D points set.
    progress : bool
        Show progress bar.
    parallel : bool
        Run the calculation in parallel. Useful when the number of points is large.

    Returns
    -------
    float
        Chamfer distance.
    """
    T_S = np.atleast_2d(T_S).astype(np.float64)
    G = np.atleast_2d(G).astype(np.float64)
    assert T_S.shape[1] == 2 and G.shape[1] == 2
    
    if parallel:
        chamfer_distance = np.mean(Parallel(n_jobs=mp.cpu_count())(
            delayed(_l2_squared_min)(x[np.newaxis, :], G) for x in T_S))
        chamfer_distance += np.mean(Parallel(n_jobs=mp.cpu_count())(
            delayed(_l2_squared_min)(T_S, y[np.newaxis, :]) for y in G))
    else:
        cd1 = 0.0
        for x in tqdm(T_S, desc="1/2", position=3, leave=False, disable=(not progress)):
            cd1 += _l2_squared(x[np.newaxis, :], G).min()
        cd1 /= len(T_S)
        
        cd2 = 0.0
        for y in tqdm(G, desc="2/2", position=3, leave=False, disable=(not progress)):
            cd2 += _l2_squared(T_S, y[np.newaxis, :]).min()
        cd2 /= len(G)
        
        chamfer_distance = cd1 + cd2
    
    return chamfer_distance


