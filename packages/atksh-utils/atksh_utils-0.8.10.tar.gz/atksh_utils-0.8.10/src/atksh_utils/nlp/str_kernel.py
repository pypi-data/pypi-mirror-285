from typing import List

import numba as nb
import numpy as np
import numpy.typing as npt

__all__ = ["build_kernel"]


@nb.njit("f4(i8[:], i8[:], i8, f4)", fastmath=True, cache=True, inline="always")
def ssk_array(s: npt.NDArray, t: npt.NDArray, n: int, lam: float) -> float:
    lens = len(s)
    lent = len(t)
    k_prim = np.zeros((n, lens, lent), dtype=nb.float32)
    k_prim[0, :, :] = 1

    for i in range(1, n):
        for sj in range(i, lens):
            toret = 0.0
            for tk in range(i, lent):
                cond = s[sj - 1] == t[tk - 1]
                toret1 = lam * (toret + lam * k_prim[i - 1, sj - 1, tk - 1])
                toret2 = toret * lam
                toret = cond * toret1 + (1 - cond) * toret2

                k_prim[i, sj, tk] = toret + lam * k_prim[i, sj - 1, tk]

    k = 0.0
    for i in range(n):
        for sj in range(i, lens):
            for tk in range(i, lent):
                cond = s[sj] == t[tk]
                k += cond * lam * lam * k_prim[i, sj, tk]

    return k


@nb.njit(
    "f4[:, :](i8[:, :], i8[:], i8, f4)", parallel=True, fastmath=True, cache=True, inline="never"
)
def _build_kernel(
    tokens: npt.NDArray,
    lens: npt.NDArray,
    n: int,
    lam: float,
) -> npt.NDArray:
    b = len(tokens)
    idx_total = b * (b - 1) // 2 + b

    mat = np.zeros((b, b), dtype=nb.float32)
    idxes = [(i, j) for i in range(b) for j in range(i, b)]
    assert len(idxes) == idx_total

    for idx in nb.prange(idx_total):
        i, j = idxes[idx]
        tokens_i = tokens[i][: lens[i]]
        tokens_j = tokens[j][: lens[j]]
        tmp = ssk_array(tokens_i, tokens_j, n, lam)
        mat[i, j] = tmp
        mat[j, i] = tmp
    norm = np.diag(mat).reshape(b, 1)
    return np.divide(mat, np.sqrt(norm.T * norm))


@nb.njit("Tuple((i8[:], i8))(unicode_type, i8)", fastmath=True, cache=True, inline="always")
def str_to_int64(s: str, length: int) -> npt.NDArray:
    out = np.zeros(length, dtype=np.int64)
    for i, c in enumerate(s):
        out[i] = ord(c)
    return out, i + 1


@nb.njit(
    "Tuple((i8[:, :], i8[:]))(ListType(unicode_type))", fastmath=True, cache=True, inline="never"
)
def build_tokens_and_lens(s: List[str]) -> npt.NDArray:
    b = len(s)
    max_len = max(map(len, s))
    tokens = np.zeros((b, max_len), dtype=np.int64)
    lens = np.zeros(b, dtype=np.int64)
    for i in range(b):
        tokens[i], lens[i] = str_to_int64(s[i], max_len)
    return tokens, lens


@nb.jit(forceobj=True, cache=True, inline="always")
def to_TypedList(s: List[str]) -> nb.typed.List:
    return nb.typed.List(s)


@nb.jit(forceobj=True, cache=True, inline="never")
def build_kernel(s: List[str], n: int, lam: float) -> npt.NDArray:
    """Build a Gram matrix with string subsequence kernel."""
    ss = to_TypedList(s)
    tokens, lens = build_tokens_and_lens(ss)
    return _build_kernel(tokens, lens, n, lam)


if __name__ == "__main__":
    print(build_kernel(["abc", "ab", "a"] * 30, 5, 0.5))
