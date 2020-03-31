"""
Rank-biased overlap. (RBO)

Implementation of RBO as defined in [1]_.
The current implementation handles uneven lists but not ties.

.. [1] William Webber, Alistair Moffat, and Justin Zobel. 2010. A similarity measure for indefinite rankings.
   ACM Trans. Inf. Syst. 28, 4, Article 20 (November 2010), 38 pages. DOI:https://doi.org/10.1145/1852102.1852106
"""

import math


def overlap(S, T, d):
    return len(set(S[:d]) & set(T[:d]))


def agreement(S, T, d):
    return overlap(S, T, d) / d


def rbo_min(S, T, p, k=None):
    """Minimum value of RBO as defined in equation (11).
    """
    if not k:
        k = min(len(S), len(T))
    xk = overlap(S, T, k)
    sum1 = sum((overlap(S, T, d) - xk) * p ** d / d for d in range(1, k + 1))

    return (1 - p) / p * (sum1 - xk * math.log(1 - p))


def rbo_res(S, T, p):
    """Residual RBO value as defined in equation (30).

    Implementation handles uneven lists but not ties.
    """
    if len(S) > len(T):
        L, S = S, T
    else:
        L, S = T, S
    l, s = len(L), len(S)

    xl = overlap(L, S, l)
    f = l + s - xl
    sum1 = sum(p ** d / d for d in range(s + 1, f + 1))
    sum2 = sum(p ** d / d for d in range(l + 1, f + 1))
    sum3 = sum(p ** d / d for d in range(1, f + 1))
    return p ** s + p ** l - p ** f - ((1 - p) / p * (s * sum1 + l * sum2 + xl * (math.log(1 / (1 - p)) - sum3)))


def rbo_ext(S, T, p):
    """Extrapolated RBO value as defined in equation (30).

    Implementation handles uneven lists but not ties.
    """
    if len(S) > len(T):
        L, S = S, T
    else:
        L, S = T, S
    l, s = len(L), len(S)

    xl = overlap(L, S, l)
    xs = overlap(L, S, s)
    sum1 = sum(overlap(L, S, d) / d * p ** d for d in range(1, l + 1))
    sum2 = sum(xs * (d - s) / (s * d) * p ** d for d in range(s + 1, l + 1))
    return (1 - p) / p * (sum1 + sum2) + ((xl - xs) / l + xs / s) * p ** l


def rbo(S, T, p):
    """Returns a tuple containing RBO_min, RBO_res and RBO_ext.
    """
    return rbo_min(S, T, p), rbo_res(S, T, p), rbo_ext(S, T, p)
