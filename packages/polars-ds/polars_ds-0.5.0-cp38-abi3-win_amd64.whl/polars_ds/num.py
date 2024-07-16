from __future__ import annotations
import math
import polars as pl
from typing import Union, Optional, List, Iterable
from .type_alias import (
    DetrendMethod,
    Distance,
    ConvMode,
    ConvMethod,
    str_to_expr,
    StrOrExpr,
    LinearRegressionMethod,
)
from ._utils import pl_plugin

__all__ = [
    "softmax",
    "query_gcd",
    "query_lcm",
    "haversine",
    "query_singular_values",
    "query_pca",
    "query_principal_components",
    "query_knn_ptwise",
    "query_knn_entropy",
    "within_dist_from",
    "is_knn_from",
    "query_radius_ptwise",
    "query_nb_cnt",
    "query_approx_entropy",
    "query_sample_entropy",
    "query_cond_entropy",
    "query_copula_entropy",
    "query_cond_indep",
    "query_transfer_entropy",
    "query_permute_entropy",
    "query_lstsq",
    "query_lstsq_report",
    "query_lempel_ziv",
    "query_jaccard_row",
    "query_jaccard_col",
    "query_psi",
    "query_psi_w_breakpoints",
    "query_psi_discrete",
    "query_woe",
    "query_woe_discrete",
    "query_iv",
    "query_iv_discrete",
    "integrate_trapz",
    "convolve",
    "list_amax",
    "gamma",
    "expit",
    "exp2",
    "expit",
    "logit",
    "trunc",
    "detrend",
    "rfft",
    "fract",
]


def softmax(x: StrOrExpr) -> pl.Expr:
    """
    Applies the softmax function to the column, which turns any real valued column into valid probability
    values. This is simply a shorthand for x.exp() / x.exp().sum() for expressions x.

    Paramters
    ---------
    x
        Either a str represeting a column name or a Polars expression
    """
    xx = str_to_expr(x)
    return xx.exp() / (xx.exp().sum())


def query_gcd(x: StrOrExpr, y: Union[int, str, pl.Expr]) -> pl.Expr:
    """
    Computes GCD of two integer columns. This will try to cast everything to int32.

    Parameters
    ----------
    x
        An integer column
    y
        Either an int, or another integer column
    """
    if isinstance(y, int):
        yy = pl.lit(y, dtype=pl.Int32)
    else:
        yy = str_to_expr(y).cast(pl.Int32)

    return pl_plugin(
        symbol="pl_gcd",
        args=[str_to_expr(x).cast(pl.Int32), yy],
        is_elementwise=True,
    )


def query_lcm(x: StrOrExpr, y: Union[int, str, pl.Expr]) -> pl.Expr:
    """
    Computes LCM of two integer columns. This will try to cast everything to int32.

    Parameters
    ----------
    x
        An integer column
    y
        Either an int, or another integer column
    """
    if isinstance(y, int):
        yy = pl.lit(y, dtype=pl.Int32)
    else:
        yy = str_to_expr(y).cast(pl.Int32)

    return pl_plugin(
        symbol="pl_lcm",
        args=[str_to_expr(x).cast(pl.Int32), yy],
        is_elementwise=True,
    )


def haversine(
    x_lat: StrOrExpr,
    x_long: StrOrExpr,
    y_lat: Union[float, str, pl.Expr],
    y_long: Union[float, str, pl.Expr],
) -> pl.Expr:
    """
    Computes haversine distance using the naive method. The output unit is km.

    Parameters
    ----------
    x_lat
        Column representing latitude in x
    x_long
        Column representing longitude in x
    y_lat
        Column representing latitude in y
    y_long
        Column representing longitude in y
    """
    xlat = str_to_expr(x_lat)
    xlong = str_to_expr(x_long)
    ylat = pl.lit(y_lat) if isinstance(y_lat, float) else str_to_expr(y_lat)
    ylong = pl.lit(y_long) if isinstance(y_long, float) else str_to_expr(y_long)
    return pl_plugin(
        symbol="pl_haversine",
        args=[xlat, xlong, ylat, ylong],
        is_elementwise=True,
        cast_to_supertype=True,
    )


def query_singular_values(
    *features: StrOrExpr,
    center: bool = True,
    as_explained_var: bool = False,
    as_ratio: bool = False,
) -> pl.Expr:
    """
    Finds all principal values (singular values) for the data matrix formed by the given features
    and returns them in descending order.

    Note: if a row has null values, it will be dropped.

    Paramters
    ---------
    features
        Feature columns
    center
        Whether to center the data or not. If you want to standard-normalize, set this to False,
        and do it for input features by hand.
    as_explained_var
        If true, return the explained variance, which is singular_value ^ 2 / (n_samples - 1)
    as_ratio
        If true, normalize output to between 0 and 1.
    """
    feats = [str_to_expr(f) for f in features]
    if center:
        actual_inputs = [f - f.mean() for f in feats]
    else:
        actual_inputs = feats

    out = pl_plugin(symbol="pl_singular_values", args=actual_inputs, returns_scalar=True)
    if as_explained_var:
        out = out.list.eval(pl.element().pow(2) / (pl.count() - 1))
    if as_ratio:
        out = out.list.eval(pl.element() / pl.element().sum())

    return out


def query_pca(
    *features: StrOrExpr,
    center: bool = True,
) -> pl.Expr:
    """
    Finds all singular values as well as the principle vectors.

    Paramters
    ---------
    features
        Feature columns
    center
        Whether to center the data or not. If you want to standard normalize, set this to False,
        and do it for input features by hand.
    """
    feats = [str_to_expr(f) for f in features]
    if center:
        actual_inputs = [f - f.mean() for f in feats]
    else:
        actual_inputs = feats

    return pl_plugin(symbol="pl_pca", args=actual_inputs, changes_length=True)


def query_principal_components(
    *features: StrOrExpr,
    k: int = 2,
    center: bool = True,
) -> pl.Expr:
    """
    Transforms the features to get the first k principal components.

    Paramters
    ---------
    features
        Feature columns
    center
        Whether to center the data or not. If you want to standard normalize, set this to False,
        and do it for input features by hand.
    """
    feats = [str_to_expr(f) for f in features]
    if k > len(feats) or k < 0:
        raise ValueError("Input `k` should be between 1 and the number of features inclusive.")

    if center:
        actual_inputs = [f - f.mean() for f in feats]
    else:
        actual_inputs = feats

    actual_inputs.insert(0, pl.lit(k, dtype=pl.UInt32).alias("principal_components"))
    return pl_plugin(symbol="pl_principal_components", args=actual_inputs, changes_length=True)


def query_knn_ptwise(
    *features: StrOrExpr,
    index: StrOrExpr,
    k: int = 5,
    leaf_size: int = 32,
    dist: Distance = "l2",
    parallel: bool = False,
    return_dist: bool = False,
    eval_mask: Optional[StrOrExpr] = None,
    data_mask: Optional[StrOrExpr] = None,
) -> pl.Expr:
    """
    Takes the index column, and uses feature columns to determine the k nearest neighbors
    to every id in the index columns. By default, this will return k + 1 neighbors, because in almost
    all cases, the point is a neighbor to itself and this returns k actual neighbors. The only exception
    is when data_mask excludes the point from being a neighbor, in which case, k + 1 distinct neighbors will
    be returned.

    Note that the index column must be convertible to u32. If you do not have a u32 column,
    you can generate one using pl.int_range(..), which should be a step before this. The index column
    must not contain nulls.

    Also note that this internally builds a kd-tree for fast querying and deallocates it once we
    are done. If you need to repeatedly run the same query on the same data, then it is not
    ideal to use this. A specialized external kd-tree structure would be better in that case.

    Parameters
    ----------
    *features : str | pl.Expr
        Other columns used as features
    index : str | pl.Expr
        The column used as index, must be castable to u32
    k : int
        Number of neighbors to query
    leaf_size : int
        Leaf size for the kd-tree. Tuning this might improve runtime performance.
    dist : Literal[`l1`, `l2`, `inf`, `h`, `cosine`]
        Note `l2` is actually squared `l2` for computational efficiency.
    parallel : bool
        Whether to run the k-nearest neighbor query in parallel. This is recommended when you
        are running only this expression, and not in group_by context.
    return_dist
        If true, return a struct with indices and distances.
    eval_mask
        Either None or a boolean expression or the name of a boolean column. If not none, this will
        only evaluate KNN for rows where this is true. This can speed up computation with K is large
        and when only results on a subset are nedded.
    data_mask
        Either None or a boolean expression or the name of a boolean column. If none, all rows can be
        neighbors. If not None, the pool of possible neighbors will be rows where this is true.
    """
    if k < 1:
        raise ValueError("Input `k` must be >= 1.")

    idx = str_to_expr(index).cast(pl.UInt32).rechunk()
    metric = str(dist).lower()
    cols = [idx]
    if eval_mask is None:
        skip_eval = False
    else:
        skip_eval = True
        cols.append(str_to_expr(eval_mask))

    if data_mask is None:
        skip_data = False
    else:
        skip_data = True
        cols.append(str_to_expr(data_mask))

    kwargs = {
        "k": k,
        "leaf_size": leaf_size,
        "metric": metric,
        "parallel": parallel,
        "skip_eval": skip_eval,
        "skip_data": skip_data,
    }

    cols.extend(str_to_expr(x) for x in features)
    if return_dist:
        return pl_plugin(
            symbol="pl_knn_ptwise_w_dist",
            args=cols,
            kwargs=kwargs,
            is_elementwise=True,
        )
    else:
        return pl_plugin(
            symbol="pl_knn_ptwise",
            args=cols,
            kwargs=kwargs,
            is_elementwise=True,
        )


def within_dist_from(
    *features: StrOrExpr,
    pt: Iterable[float],
    r: Union[float, pl.Expr],
    dist: Distance = "l2",
) -> pl.Expr:
    """
    Returns a boolean column that returns points that are within radius from the given point.

    Parameters
    ----------
    *features : str | pl.Expr
        Other columns used as features
    pt : Iterable[float]
        The point, at which we filter using the radius.
    r : either a float or an expression
        The radius to query with. If this is an expression, the radius will be applied row-wise.
    dist : Literal[`l1`, `l2`, `inf`, `h`, `cosine`]
        Note `l2` is actually squared `l2` for computational efficiency.
    """
    # For a single point, it is faster to just do it in native polars
    oth = [str_to_expr(x) for x in features]
    if len(pt) != len(oth):
        raise ValueError("Dimension does not match.")

    if dist == "l1":
        return (
            pl.sum_horizontal((e - pl.lit(xi, dtype=pl.Float64)).abs() for xi, e in zip(pt, oth))
            <= r
        )
    elif dist == "l2":
        return (
            pl.sum_horizontal((e - pl.lit(xi, dtype=pl.Float64)).pow(2) for xi, e in zip(pt, oth))
            <= r
        )
    elif dist == "inf":
        return (
            pl.max_horizontal((e - pl.lit(xi, dtype=pl.Float64)).abs() for xi, e in zip(pt, oth))
            <= r
        )
    elif dist == "cosine":
        x_list = list(pt)
        x_norm = sum(z * z for z in x_list)
        oth_norm = pl.sum_horizontal(e * e for e in oth)
        dist = (
            1.0
            - pl.sum_horizontal(xi * e for xi, e in zip(x_list, oth)) / (x_norm * oth_norm).sqrt()
        )
        return dist <= r
    elif dist in ("h", "haversine"):
        pt_as_list = list(pt)
        if (len(pt_as_list) != 2) or (len(oth) < 2):
            raise ValueError(
                "For Haversine distance, input x must have dimension 2 and 2 other columns"
                " must be provided as lat and long."
            )

        y_lat = pl.lit(pt_as_list[0], dtype=pl.Float64)
        y_long = pl.lit(pt_as_list[1], dtype=pl.Float64)
        dist = haversine(oth[0], oth[1], y_lat, y_long)
        return dist <= r
    else:
        raise ValueError(f"Unknown distance function: {dist}")


def is_knn_from(
    *features: StrOrExpr,
    pt: Iterable[float],
    k: int,
    dist: Distance = "l2",
) -> pl.Expr:
    """
    Returns a boolean column that returns points that are k nearest neighbors from the point.

    Parameters
    ----------
    *features : str | pl.Expr
        Other columns used as features
    pt : Iterable[float]
        The point, at which we filter using the radius.
    k : int
        k nearest neighbor
    dist : Literal[`l1`, `l2`, `inf`, `h`, `cosine`]
        Note `l2` is actually squared `l2` for computational efficiency.
    """
    # For a single point, it is faster to just do it in native polars
    oth = [str_to_expr(x) for x in features]
    if len(pt) != len(oth):
        raise ValueError("Dimension does not match.")

    if dist == "l1":
        dist = pl.sum_horizontal((e - pl.lit(xi, dtype=pl.Float64)).abs() for xi, e in zip(pt, oth))
        return dist <= dist.bottom_k(k=k).max()
    elif dist == "l2":
        dist = pl.sum_horizontal(
            (e - pl.lit(xi, dtype=pl.Float64)).pow(2) for xi, e in zip(pt, oth)
        )
        return dist <= dist.bottom_k(k=k).max()
    elif dist == "inf":
        dist = pl.max_horizontal((e - pl.lit(xi, dtype=pl.Float64)).abs() for xi, e in zip(pt, oth))
        return dist <= dist.bottom_k(k=k).max()
    elif dist == "cosine":
        x_list = list(pt)
        x_norm = sum(z * z for z in x_list)
        oth_norm = pl.sum_horizontal(e * e for e in oth)
        dist = (
            1.0
            - pl.sum_horizontal(xi * e for xi, e in zip(x_list, oth)) / (x_norm * oth_norm).sqrt()
        )
        return dist <= dist.bottom_k(k=k).max()
    elif dist in ("h", "haversine"):
        pt_as_list = list(pt)
        if (len(pt_as_list) != 2) or (len(oth) < 2):
            raise ValueError(
                "For Haversine distance, input x must have dimension 2 and 2 other columns"
                " must be provided as lat and long."
            )

        y_lat = pl.lit(pt_as_list[0], dtype=pl.Float64)
        y_long = pl.lit(pt_as_list[1], dtype=pl.Float64)
        dist = haversine(oth[0], oth[1], y_lat, y_long)
        return dist <= dist.bottom_k(k=k).max()
    else:
        raise ValueError(f"Unknown distance function: {dist}")


def query_radius_ptwise(
    *features: StrOrExpr,
    index: StrOrExpr,
    r: float,
    dist: Distance = "l2",
    sort: bool = True,
    parallel: bool = False,
) -> pl.Expr:
    """
    Takes the index column, and uses features columns to determine distance, and finds all neighbors
    within distance r from each id in the index column. If you only care about neighbor count, you
    should use query_nb_cnt, which supports expression for radius.

    Note that the index column must be convertible to u32. If you do not have a u32 ID column,
    you can generate one using pl.int_range(..), which should be a step before this.

    Also note that this internally builds a kd-tree for fast querying and deallocates it once we
    are done. If you need to repeatedly run the same query on the same data, then it is not
    ideal to use this. A specialized external kd-tree structure would be better in that case.

    Parameters
    ----------
    *features : str | pl.Expr
        Other columns used as features
    index : str | pl.Expr
        The column used as index, must be castable to u32
    r : float
        The radius. Must be a scalar value now.
    dist : Literal[`l1`, `l2`, `inf`, `cosine`]
        Note `l2` is actually squared `l2` for computational efficiency.
    sort
        Whether the neighbors returned should be sorted by the distance. Setting this to False can
        improve performance by 10-20%.
    parallel : bool
        Whether to run the k-nearest neighbor query in parallel. This is recommended when you
        are running only this expression, and not in group_by context.
    """
    if r <= 0.0:
        raise ValueError("Input `r` must be > 0.")
    elif isinstance(r, pl.Expr):
        raise ValueError("Input `r` must be a scalar now. Expression input is not implemented.")

    idx = str_to_expr(index).cast(pl.UInt32).rechunk()
    metric = str(dist).lower()
    cols = [idx]
    cols.extend(str_to_expr(x) for x in features)
    return pl_plugin(
        symbol="pl_query_radius_ptwise",
        args=cols,
        kwargs={"r": r, "leaf_size": 32, "metric": metric, "parallel": parallel, "sort": sort},
        is_elementwise=True,
    )


def query_nb_cnt(
    r: Union[float, str, pl.Expr, List[float], "np.ndarray", pl.Series],  # noqa: F821
    *features: StrOrExpr,
    dist: Distance = "l2",
    parallel: bool = False,
) -> pl.Expr:
    """
    Return the number of neighbors within (<=) radius r for each row under the given distance
    metric. The point itself is always a neighbor of itself.

    Parameters
    ----------
    r : float | Iterable[float] | pl.Expr | str
        If this is a scalar, then it will run the query with fixed radius for all rows. If
        this is a list, then it must have the same height as the dataframe. If
        this is an expression, it must be an expression representing radius. If this is a str,
        it must be the name of a column
    *features : str | pl.Expr
        Other columns used as features
    dist : Literal[`l1`, `l2`, `inf`, `h`, `cosine`]
        Note `l2` is actually squared `l2` for computational efficiency.
    parallel : bool
        Whether to run the distance query in parallel. This is recommended when you
        are running only this expression, and not in group_by context.
    """
    if isinstance(r, (float, int)):
        rad = pl.lit(pl.Series(values=[r], dtype=pl.Float64))
    elif isinstance(r, pl.Expr):
        rad = r
    elif isinstance(r, str):
        rad = pl.col(r)
    else:
        rad = pl.lit(pl.Series(values=r, dtype=pl.Float64))

    return pl_plugin(
        symbol="pl_nb_cnt",
        args=[rad] + [str_to_expr(x) for x in features],
        kwargs={
            "k": 0,
            "leaf_size": 32,  # useless now
            "metric": dist,
            "parallel": parallel,
            "skip_eval": False,
            "skip_data": False,
        },
        is_elementwise=True,
    )


def query_approx_entropy(
    ts: StrOrExpr,
    m: int,
    filtering_level: float,
    scale_by_std: bool = True,
    parallel: bool = True,
) -> pl.Expr:
    """
    Approximate sample entropies of a time series given the filtering level. It is highly
    recommended that the user impute nulls before calling this.

    If NaN/some error is returned/thrown, it is likely that:
    (1) Too little data, e.g. m + 1 > length
    (2) filtering_level or (filtering_level * std) is too close to 0 or std is null/NaN.

    Parameters
    ----------
    ts : str | pl.Expr
        A time series
    m : int
        Length of compared runs of data. This is `m` in the wikipedia article.
    filtering_level : float
        Filtering level, must be positive. This is `r` in the wikipedia article.
    scale_by_std : bool
        Whether to scale filter level by std of data. In most applications, this is the default
        behavior, but not in some other cases.
    parallel : bool
        Whether to run this in parallel or not. This is recommended when you
        are running only this expression, and not in group_by context.

    Reference
    ---------
    https://en.wikipedia.org/wiki/Approximate_entropy
    """

    if filtering_level <= 0:
        raise ValueError("Filter level must be positive.")

    t = str_to_expr(ts)
    if scale_by_std:
        r: pl.Expr = filtering_level * t.std()
    else:
        r: pl.Expr = pl.lit(filtering_level, dtype=pl.Float64)

    rows = t.len() - m + 1
    data = [r, t.slice(0, length=rows).cast(pl.Float64)]
    # See rust code for more comment on why I put m + 1 here.
    data.extend(
        t.shift(-i).slice(0, length=rows).cast(pl.Float64).alias(str(i)) for i in range(1, m + 1)
    )
    # More errors are handled in Rust
    return pl_plugin(
        symbol="pl_approximate_entropy",
        args=data,
        kwargs={
            "k": 0,
            "leaf_size": 32,
            "metric": "inf",
            "parallel": parallel,
            "skip_eval": False,
            "skip_data": False,
        },
        returns_scalar=True,
        pass_name_to_apply=True,
    )


def query_sample_entropy(
    ts: StrOrExpr, ratio: float = 0.2, m: int = 2, parallel: bool = False
) -> pl.Expr:
    """
    Calculate the sample entropy of this column. It is highly
    recommended that the user impute nulls before calling this.

    If NaN/some error is returned/thrown, it is likely that:
    (1) Too little data, e.g. m + 1 > length
    (2) ratio or (ratio * std) is too close to or below 0 or std is null/NaN.

    Parameters
    ----------
    ts : str | pl.Expr
        A time series
    ratio : float
        The tolerance parameter. Default is 0.2.
    m : int
        Length of a run of data. Most common run length is 2.
    parallel : bool
        Whether to run this in parallel or not. This is recommended when you
        are running only this expression, and not in group_by context.

    Reference
    ---------
    https://en.wikipedia.org/wiki/Sample_entropy
    """
    t = str_to_expr(ts)
    r = ratio * t.std(ddof=0)
    rows = t.len() - m + 1

    data = [r, t.slice(0, length=rows)]
    # See rust code for more comment on why I put m + 1 here.
    data.extend(
        t.shift(-i).slice(0, length=rows).alias(str(i)) for i in range(1, m + 1)
    )  # More errors are handled in Rust
    return pl_plugin(
        symbol="pl_sample_entropy",
        args=data,
        kwargs={
            "k": 0,
            "leaf_size": 32,
            "metric": "inf",
            "parallel": parallel,
            "skip_eval": False,
            "skip_data": False,
        },
        returns_scalar=True,
        pass_name_to_apply=True,
    )


def query_cond_entropy(x: StrOrExpr, y: StrOrExpr) -> pl.Expr:
    """
    Queries the conditional entropy of x on y, aka. H(x|y).

    Parameters
    ----------
    x
        Either a string or a polars expression
    y
        Either a string or a polars expression
    """
    return pl_plugin(
        symbol="pl_conditional_entropy",
        args=[str_to_expr(x), str_to_expr(y)],
        returns_scalar=True,
        pass_name_to_apply=True,
    )


def query_knn_entropy(
    *features: StrOrExpr,
    k: int = 3,
    dist: Distance = "l2",
    parallel: bool = False,
) -> pl.Expr:
    """
    Computes KNN entropy among all the rows.

    Note if rows <= k, NaN will be returned.

    Parameters
    ----------
    *features
        Columns used as features
    k
        The number of nearest neighbor to consider. Usually 2 or 3.
    dist : Literal[`l2`, `inf`]
        Note `l2` is actually squared `l2` for computational efficiency.
    parallel : bool
        Whether to run the distance query in parallel. This is recommended when you
        are running only this expression, and not in group_by context.

    Reference
    ---------
    https://arxiv.org/pdf/1506.06501v1.pdf
    """
    if k <= 0:
        raise ValueError("Input `k` must be > 0.")
    if dist not in ["l2", "inf"]:
        raise ValueError("Invalid metric for KNN entropy.")

    return pl_plugin(
        symbol="pl_knn_entropy",
        args=[str_to_expr(e).alias(str(i)) for i, e in enumerate(features)],
        kwargs={
            "k": k,
            "leaf_size": 32,
            "metric": dist,
            "parallel": parallel,
            "skip_eval": False,
            "skip_data": False,
        },
        returns_scalar=True,
        pass_name_to_apply=True,
    )


# def query_mutual_info(*features: StrOrExpr, k: int = 3, parallel: bool = False) -> pl.Expr:
#     """
#     Estimates Copula Entropy via rank statistics.

#     Reference
#     ---------
#     Jian Ma and Zengqi Sun. Mutual information is copula entropy. Tsinghua Science & Technology, 2011, 16(1): 51-54.
#     """
#     ranks = [x.rank(method="max") / x.len() for x in (str_to_expr(f) for f in features)]
#     return query_knn_entropy(*ranks, k=k, dist="l2", parallel=parallel)


def query_copula_entropy(*features: StrOrExpr, k: int = 3, parallel: bool = False) -> pl.Expr:
    """
    Estimates Copula Entropy via rank statistics.

    Reference
    ---------
    Jian Ma and Zengqi Sun. Mutual information is copula entropy. Tsinghua Science & Technology, 2011, 16(1): 51-54.
    """
    ranks = [x.rank() / x.len() for x in (str_to_expr(f) for f in features)]
    return -query_knn_entropy(*ranks, k=k, dist="l2", parallel=parallel)


def query_cond_indep(
    x: StrOrExpr, y: StrOrExpr, z: StrOrExpr, k: int = 3, parallel: bool = False
) -> pl.Expr:
    """
    Computes the conditional independance of `x`  and `y`, conditioned on `z`

    Reference
    ---------
    Jian Ma. Multivariate Normality Test with Copula Entropy. arXiv preprint arXiv:2206.05956, 2022.
    """
    # We can likely optimize this by going into Rust.
    # Here we are
    # (1) computing rank multiple times
    # (2) creating 3 separate kd-trees, and copying the data 3 times. Might just need to copy once.
    xyz = query_copula_entropy(x, y, z, k=k, parallel=parallel)
    yz = query_copula_entropy(y, z, k=k, parallel=parallel)
    xz = query_copula_entropy(x, z, k=k, parallel=parallel)
    return xyz - yz - xz


def query_transfer_entropy(
    x: StrOrExpr, source: StrOrExpr, lag: int = 1, k: int = 3, parallel: bool = False
) -> pl.Expr:
    """
    Estimating transfer entropy from `source` to `x` with a lag

    Reference
    ---------
    Jian Ma. Estimating Transfer Entropy via Copula Entropy. arXiv preprint arXiv:1910.04375, 2019.
    """
    if lag < 1:
        raise ValueError("Input `lag` must be >= 1.")

    xx = str_to_expr(x)
    x1 = xx.slice(0, pl.len() - lag)
    x2 = xx.slice(lag, pl.len() - lag)  # (equivalent to slice(lag, None), but will break in v1.0)
    s = str_to_expr(source).slice(0, pl.len() - lag)
    return query_cond_indep(x2, s, x1, k=k, parallel=parallel)


def query_permute_entropy(
    ts: StrOrExpr,
    tau: int = 1,
    n_dims: int = 3,
    base: float = math.e,
) -> pl.Expr:
    """
    Computes permutation entropy.

    Parameters
    ----------
    ts : str | pl.Expr
        A time series
    tau : int
        The embedding time delay which controls the number of time periods between elements
        of each of the new column vectors.
    n_dims : int, > 1
        The embedding dimension which controls the length of each of the new column vectors
    base : float
        The base for log in the entropy computation

    Reference
    ---------
    https://www.aptech.com/blog/permutation-entropy/
    """
    if n_dims <= 1:
        raise ValueError("Input `n_dims` has to be > 1.")
    if tau < 1:
        raise ValueError("Input `tau` has to be >= 1.")

    t = str_to_expr(ts)
    if tau == 1:  # Fast track the most common use case
        return (
            pl.concat_list(t, *(t.shift(-i) for i in range(1, n_dims)))
            .head(t.len() - n_dims + 1)
            .list.eval(pl.element().arg_sort())
            .value_counts()  # groupby and count, but returns a struct
            .struct.field("count")  # extract the field named "count"
            .entropy(base=base, normalize=True)
        )
    else:
        return (
            pl.concat_list(
                t.gather_every(tau),
                *(t.shift(-i).gather_every(tau) for i in range(1, n_dims)),
            )
            .slice(0, length=(t.len() // tau) + 1 - (n_dims // tau))
            .list.eval(pl.element().arg_sort())
            .value_counts()
            .struct.field("count")
            .entropy(base=base, normalize=True)
        )


def query_lstsq(
    *x: StrOrExpr,
    target: StrOrExpr,
    add_bias: bool = False,
    skip_null: bool = False,
    return_pred: bool = False,
    method: LinearRegressionMethod = "normal",
    lambda_: float = 0.0,
) -> pl.Expr:
    """
    Computes least squares solution to the equation Ax = y where y is the target.

    All positional arguments should be expressions representing predictive variables. This
    does not support composite expressions like pl.col(["a", "b"]), pl.all(), etc.

    If add_bias is true, it will be the last coefficient in the output
    and output will have len(variables) + 1.

    Note: if using bias and regularization, the bias term will also be regularized. This might be
    changed in the future.

    Parameters
    ----------
    x : str | pl.Expr
        The variables used to predict target
    target : str | pl.Expr
        The target variable
    add_bias
        Whether to add a bias term
    skip_null
        Whether to skip a row if there is a null value in row
    return_pred
        If true, return prediction and residue. If false, return coefficients. Note that
        for coefficients, it reduces to one output (like max/min), but for predictions and
        residue, it will return the same number of rows as in input.
    method
        Linear Regression method. One of "normal" (normal equation), "l2" (l2 regularized)
    lambda
        Regularization factor. Should be nonzero when method != normal.
    """
    t = str_to_expr(target).cast(pl.Float64)
    cols = [t]
    cols.extend(str_to_expr(z) for z in x)
    lr_kwargs = {"bias": add_bias, "skip_null": skip_null, "method": method, "lambda": lambda_}
    if return_pred:
        return pl_plugin(
            symbol="pl_lstsq_pred",
            args=cols,
            kwargs=lr_kwargs,
            pass_name_to_apply=True,
        )
    else:
        return pl_plugin(
            symbol="pl_lstsq",
            args=cols,
            kwargs=lr_kwargs,
            returns_scalar=True,
            pass_name_to_apply=True,
        )


def query_lstsq_report(
    *x: StrOrExpr,
    target: StrOrExpr,
    add_bias: bool = False,
    skip_null: bool = False,
) -> pl.Expr:
    """
    Creates a least square report with more stats about each coefficient.

    Note: if columns are not linearly independent, some numerical issue may occur. E.g
    you may see unrealistic coefficients in the output. It is possible to have
    `silent` numerical issue during computation. For this report, input must not
    contain nulls and there must be > # features number of records. This uses the closed
    form solution to compute the least square report.

    This functions returns a struct with the same length as the number of features used
    in the linear regression, and +1 if add_bias is true.

    Parameters
    ----------
    x : str | pl.Expr
        The variables used to predict target
    target : str | pl.Expr
        The target variable
    add_bias
        Whether to add a bias term. If bias is added, it is always the last feature.
    skip_null
        Whether to skip a row if there is a null value in row
    """
    t = str_to_expr(target).cast(pl.Float64)
    cols = [t]
    cols.extend(str_to_expr(z) for z in x)
    return pl_plugin(
        symbol="pl_lstsq_report",
        args=cols,
        kwargs={"bias": add_bias, "skip_null": skip_null, "method": "normal", "lambda": 0.0},
        changes_length=True,
        pass_name_to_apply=True,
    )


def query_lempel_ziv(b: StrOrExpr, as_ratio: bool = True) -> pl.Expr:
    """
    Computes Lempel Ziv complexity on a boolean column. Null will be mapped to False.

    Parameters
    ----------
    b
        A boolean column
    as_ratio : bool
        If true, return complexity / length.
    """
    x = str_to_expr(b)
    out = pl_plugin(
        symbol="pl_lempel_ziv_complexity",
        args=[x],
        returns_scalar=True,
    )
    if as_ratio:
        return out / x.len()
    return out


def query_jaccard_row(first: StrOrExpr, second: StrOrExpr) -> pl.Expr:
    """
    Computes jaccard similarity pairwise between this and the other column. The type of
    each column must be list and the lists must have the same inner type. The inner type
    must either be integer or string.

    Parameters
    ----------
    first
        A list column with a hashable inner type
    second
        A list column with a hashable inner type
    """
    return pl_plugin(
        symbol="pl_list_jaccard",
        args=[str_to_expr(first), str_to_expr(second)],
        is_elementwise=True,
    )


def query_jaccard_col(first: StrOrExpr, second: StrOrExpr, count_null: bool = False) -> pl.Expr:
    """
    Computes jaccard similarity column-wise. This will hash entire columns and compares the two
    hashsets. Note: only integer/str columns can be compared.

    Parameters
    ----------
    first
        A column with a hashable type
    second
        A column with a hashable type
    count_null
        Whether to count null as a distinct element.
    """
    return pl_plugin(
        symbol="pl_jaccard",
        args=[str_to_expr(first), str_to_expr(second), pl.lit(count_null, dtype=pl.Boolean)],
        returns_scalar=True,
    )


def query_psi(
    new: Union[pl.Expr, Iterable[float]],
    baseline: Union[pl.Expr, Iterable[float]],
    n_bins: int = 10,
    return_report: bool = False,
) -> pl.Expr:
    """
    Compute the Population Stability Index between x and the reference column (usually x's historical values).
    The reference column will be divided into n_bins quantile bins which will be used as basis of comparison.

    Note this assumes values in self and ref are continuous. This will also remove all infinite, null, NA.
    values.

    Also note that it will try to create `n_bins` many unique breakpoints. If input data has < n_bins
    unique breakpoints, the repeated breakpoints will be grouped together, and the computation will be done
    with < `n_bins` many bins. This happens when a single value appears too many times in data. This also
    differs from the reference implementation by treating breakpoints as right-closed intervals with -inf
    and inf being the first and last values of the intervals. This is because we need to accommodate all data
    in the case when actual data's min and the reference data's min are not the same, which is common in reality.

    Parameters
    ----------
    new
        An expression or any iterable that can be turned into a Polars series that represents newly
        arrived feature values
    baseline
        An expression or any iterable that can be turned into a Polars series. Usually this should
        be the feature's historical values
    n_bins : int, > 1
        The number of quantile bins to use
    return_report
        Whether to return a PSI report or not.

    Reference
    ---------
    https://github.com/mwburke/population-stability-index/blob/master/psi.py
    https://www.listendata.com/2015/05/population-stability-index.html
    """
    if n_bins <= 1:
        raise ValueError("Input `n_bins` must be >= 2.")

    if isinstance(new, (str, pl.Expr)):
        new_ = str_to_expr(new)
        valid_new: Union[pl.Series, pl.Expr] = new_.filter(new_.is_finite()).cast(pl.Float64)
    else:
        temp = pl.Series(values=new, dtype=pl.Float64)
        valid_new: Union[pl.Series, pl.Expr] = temp.filter(temp.is_finite())

    if isinstance(baseline, (str, pl.Expr)):
        base = str_to_expr(baseline)
        valid_ref: Union[pl.Series, pl.Expr] = base.filter(base.is_finite()).cast(pl.Float64)
    else:
        temp = pl.Series(values=baseline, dtype=pl.Float64)
        valid_ref: Union[pl.Series, pl.Expr] = temp.filter(temp.is_finite())

    vc = (
        valid_ref.qcut(n_bins, left_closed=False, allow_duplicates=True, include_breaks=True)
        .struct.rename_fields(
            ["brk", "category"]
        )  # Use "breakpoints" in the future. Skip this rename. After polars v1
        .struct.field("brk")
        .value_counts()
        .sort()
    )
    # breakpoints learned from ref
    brk = vc.struct.field("brk")  # .cast(pl.Float64)
    # counts of points in the buckets
    cnt_ref = vc.struct.field("count")  # .cast(pl.UInt32)
    psi_report = pl_plugin(
        symbol="pl_psi_report",
        args=[valid_new, brk, cnt_ref],
        changes_length=True,
    ).alias("psi_report")
    if return_report:
        return psi_report

    return psi_report.struct.field("psi_bin").sum()


def query_psi_discrete(
    new: Union[StrOrExpr, Iterable[str]],
    baseline: Union[StrOrExpr, Iterable[str]],
    return_report: bool = False,
) -> pl.Expr:
    """
    Compute the Population Stability Index between self (actual) and the reference column. The baseline
    column will be used as categories which are the basis of comparison.

    Note this assumes values in new and ref baseline discrete columns (e.g. str categories). This will
    treat each value as a distinct category and null will be treated as a category by itself. If a category
    exists in new but not in baseline, the percentage will be imputed by 0.0001. If you do not wish to include
    new distinct values in PSI calculation, you can still compute the PSI by generating the report and filtering.

    Also note that discrete columns must have the same type in order to be considered the same.

    Parameters
    ----------
    x
        The feature
    baseline
        An expression, or any iterable that can be turned into a Polars series. Usually this should
        be x's historical values
    return_report
        Whether to return a PSI report or not.

    Reference
    ---------
    https://www.listendata.com/2015/05/population-stability-index.html
    """
    if isinstance(new, (str, pl.Expr)):
        new_ = str_to_expr(new)
        temp = new_.value_counts().struct.rename_fields(["", "count"])
        new_cnt: Union[pl.Series, pl.Expr] = temp.struct.field("count")
        new_cat: Union[pl.Series, pl.Expr] = temp.struct.field("")
    else:
        temp = pl.Series(values=new)
        temp: pl.DataFrame = temp.value_counts()  # This is a df in this case
        ref_cnt: Union[pl.Series, pl.Expr] = temp.drop_in_place("count")
        ref_cat: Union[pl.Series, pl.Expr] = temp[temp.columns[0]]

    if isinstance(baseline, (str, pl.Expr)):
        base = str_to_expr(baseline)
        temp = base.value_counts().struct.rename_fields(["", "count"])
        ref_cnt: Union[pl.Series, pl.Expr] = temp.struct.field("count")
        ref_cat: Union[pl.Series, pl.Expr] = temp.struct.field("")
    else:
        temp = pl.Series(values=baseline)
        temp: pl.DataFrame = temp.value_counts()  # This is a df in this case
        ref_cnt: Union[pl.Series, pl.Expr] = temp.drop_in_place("count")
        ref_cat: Union[pl.Series, pl.Expr] = temp[temp.columns[0]]

    psi_report = pl_plugin(
        symbol="pl_psi_discrete_report",
        args=[new_cat, new_cnt, ref_cat, ref_cnt],
        changes_length=True,
    )
    if return_report:
        return psi_report

    return psi_report.struct.field("psi_bin").sum()


def query_psi_w_breakpoints(
    new: Union[StrOrExpr, Iterable[float]],
    baseline: Union[StrOrExpr, Iterable[float]],
    breakpoints: List[float],  # noqa: F821
) -> pl.Expr:
    """
    Creates a PSI report using the custom breakpoints.

    Parameters
    ----------
    baseline
        The data representing the baseline data. Any sequence of numerical values that
        can be turned into a Polars'series, or an expression representing a column will work
    actual
        The data representing the actual, observed data. Any sequence of numerical values that
        can be turned into a Polars'series, or an expression representing a column will work
    breakpoints
        The data that represents breakpoints. Input must be sorted, distinct, finite numeric values.
        This function will not cleanse the breakpoints for the user. E.g. [0.1, 0.5, 0.9] will create
        four bins: (-inf. 0.1], (0.1, 0.5], (0.5, 0.9] and (0.9, inf).
    """
    if isinstance(baseline, (str, pl.Expr)):
        x: pl.Expr = str_to_expr(baseline)
        x = x.filter(x.is_finite())
    else:
        temp = pl.Series(values=baseline)
        x: pl.Expr = pl.lit(temp.filter(temp.is_finite()))

    if isinstance(new, (str, pl.Expr)):
        y: pl.Expr = str_to_expr(new)
        y = y.filter(y.is_finite())
    else:
        temp = pl.Series(values=new)
        y: pl.Expr = pl.lit(temp.filter(temp.is_finite()))

    if len(breakpoints) == 0:
        raise ValueError("Breakpoints is empty.")

    bp = breakpoints + [float("inf")]
    return pl_plugin(
        symbol="pl_psi_w_bps",
        args=[x.rechunk(), y.rechunk(), pl.Series(values=bp)],
        changes_length=True,
    ).alias("psi_report")


def query_woe(x: StrOrExpr, target: Union[StrOrExpr, Iterable[int]], n_bins: int = 10) -> pl.Expr:
    """
    Compute the Weight of Evidence for x with respect to target. This assumes x
    is continuous. A value of 1 is added to all events/non-events
    (goods/bads) to smooth the computation.

    Currently only quantile binning strategy is implemented.

    Parameters
    ----------
    x
        The feature
    target
        The target variable. Should be 0s and 1s.
    n_bins
        The number of bins to bin the variable.

    Reference
    ---------
    https://www.listendata.com/2015/03/weight-of-evidence-woe-and-information.html
    """
    if isinstance(target, (str, pl.Expr)):
        t = str_to_expr(target)
    else:
        t = pl.Series(values=target)
    xx = str_to_expr(x)
    valid = xx.filter(xx.is_finite())
    brk = valid.qcut(n_bins, left_closed=False, allow_duplicates=True).cast(pl.String)
    return pl_plugin(symbol="pl_woe_discrete", args=[brk, t], changes_length=True)


def query_woe_discrete(
    x: StrOrExpr,
    target: Union[StrOrExpr, Iterable[int]],
) -> pl.Expr:
    """
    Compute the Weight of Evidence for x with respect to target. This assumes x
    is discrete and castable to String. A value of 1 is added to all events/non-events
    (goods/bads) to smooth the computation.

    Parameters
    ----------
    x
        The feature
    target
        The target variable. Should be 0s and 1s.

    Reference
    ---------
    https://www.listendata.com/2015/03/weight-of-evidence-woe-and-information.html
    """
    if isinstance(target, (str, pl.Expr)):
        t = str_to_expr(target)
    else:
        t = pl.Series(values=target)
    return pl_plugin(
        symbol="pl_woe_discrete",
        args=[str_to_expr(x).cast(pl.String), t],
        changes_length=True,
    )


def query_iv(
    x: StrOrExpr, target: Union[StrOrExpr, Iterable[int]], n_bins: int = 10, return_sum: bool = True
) -> pl.Expr:
    """
    Compute Information Value for x with respect to target. This assumes the variable x
    is continuous. A value of 1 is added to all events/non-events
    (goods/bads) to smooth the computation.

    Currently only quantile binning strategy is implemented.

    Parameters
    ----------
    x
        The feature. Must be numeric.
    target
        The target column. Should be 0s and 1s.
    n_bins
        The number of bins to bin x.
    return_sum
        If false, the output is a struct containing the ranges and the corresponding IVs. If true,
        it is the sum of the individual information values.

    Reference
    ---------
    https://www.listendata.com/2015/03/weight-of-evidence-woe-and-information.html
    """
    if isinstance(target, (str, pl.Expr)):
        t = str_to_expr(target)
    else:
        t = pl.Series(values=target)
    xx = str_to_expr(x)
    valid = xx.filter(xx.is_finite())
    brk = valid.qcut(n_bins, left_closed=False, allow_duplicates=True).cast(pl.String)
    out = pl_plugin(symbol="pl_iv", args=[brk, t], changes_length=True)
    return out.struct.field("iv").sum() if return_sum else out


def query_iv_discrete(
    x: StrOrExpr, target: Union[StrOrExpr, Iterable[int]], return_sum: bool = True
) -> pl.Expr:
    """
    Compute the Information Value for x with respect to target. This assumes x
    is discrete and castable to String. A value of 1 is added to all events/non-events
    (goods/bads) to smooth the computation.

    Parameters
    ----------
    x
        The feature. The column must be castable to String
    target
        The target variable. Should be 0s and 1s.
    return_sum
        If false, the output is a struct containing the categories and the corresponding IVs. If true,
        it is the sum of the individual information values.

    Reference
    ---------
    https://www.listendata.com/2015/03/weight-of-evidence-woe-and-information.html
    """
    if isinstance(target, (str, pl.Expr)):
        t = str_to_expr(target)
    else:
        t = pl.Series(values=target)
    out = pl_plugin(symbol="pl_iv", args=[str_to_expr(x).cast(pl.String), t], changes_length=True)
    return out.struct.field("iv").sum() if return_sum else out


def integrate_trapz(y: StrOrExpr, x: Union[float, pl.Expr]) -> pl.Expr:
    """
    Integrate y along x using the trapezoidal rule. If x is not a single
    value, then x should be sorted.

    Parameters
    ----------
    y
        A column of numbers
    x
        If it is a single float, it must be positive and it will represent a uniform
        distance between points. If it is an expression, it must be sorted, does not contain
        null, and have the same length as self.
    """
    yy = str_to_expr(y).cast(pl.Float64)
    if isinstance(x, float):
        xx = pl.lit(abs(x), pl.Float64)
    else:
        xx = x.cast(pl.Float64)

    return pl_plugin(
        symbol="pl_trapz",
        args=[yy, xx],
        returns_scalar=True,
    )


def convolve(
    x: StrOrExpr,
    kernel: Union[List[float], "np.ndarray", pl.Series, pl.Expr],  # noqa: F821
    fill_value: Union[float, pl.Expr] = 0.0,
    method: ConvMethod = "direct",
    mode: ConvMode = "full",
    parallel: bool = False,
) -> pl.Expr:
    """
    Performs a convolution with the filter via FFT. The current implementation's performance is worse
    than SciPy but offers parallelization within Polars.

    For large kernels (usually kernel length > 120), convolving with FFT is faster, but for smaller kernels,
    convolving with direct method is faster.

    parameters
    ----------
    x
        A column of numbers
    kernel
        The filter for the convolution. Anything that can be turned into a Polars Series will work. All non-finite
        values will be filtered out before the convolution.
    fill_value
        Fill null values in `x` with this value. Either a float or a polars's expression representing 1 element
    method
        Either `fft` or `direct`.
    mode
        Please check the reference. One of `same`, `left` (left-aligned same), `right` (right-aligned same),
        `valid` or `full`.
    parallel
        Only applies when method = direct. Whether to compute the convulition in parallel. Note that this may not
        have the expected performance when you are in group_by or other parallel context already. It is recommended
        to use this in select/with_columns context, when few expressions are being run at the same time.

    Reference
    ---------
    https://brianmcfee.net/dstbook-site/content/ch03-convolution/Modes.html
    https://en.wikipedia.org/wiki/Convolution
    """
    xx = str_to_expr(x).fill_null(fill_value).cast(pl.Float64).rechunk()  # One cont slice
    f: Union[pl.Expr, pl.Series]
    if isinstance(kernel, pl.Expr):
        f = kernel.filter(kernel.is_finite()).rechunk()  # One cont slice
    else:
        f = pl.Series(values=kernel, dtype=pl.Float64)
        f = f.filter(f.is_finite()).rechunk()  # One cont slice

    if method == "direct":
        f = f.reverse()

    return pl_plugin(
        symbol="pl_convolve",
        args=[xx, f],
        kwargs={"mode": mode, "method": method, "parallel": parallel},
        changes_length=True,
    )


def list_amax(list_col: StrOrExpr) -> pl.Expr:
    """
    Finds the argmax of the list in this column. This is useful for

    (1) Turning sparse multiclass target into dense target.
    (2) Finding the max probability class of a multiclass classification output.
    (3) As a shortcut for expr.list.eval(pl.element().arg_max()).
    """
    return str_to_expr(list_col).list.eval(pl.element().arg_max())


def gamma(x: StrOrExpr) -> pl.Expr:
    """
    Applies the gamma function to self. Note, this will return NaN for negative values and inf when x = 0,
    whereas SciPy's gamma function will return inf for all x <= 0.
    """
    return pl_plugin(
        args=[str_to_expr(x)],
        symbol="pl_gamma",
        is_elementwise=True,
    )


def expit(x: StrOrExpr) -> pl.Expr:
    """
    Applies the Expit function to self. Expit(x) = 1 / (1 + e^(-x))
    """
    return pl_plugin(
        args=[str_to_expr(x)],
        symbol="pl_expit",
        is_elementwise=True,
    )


def logit(x: StrOrExpr) -> pl.Expr:
    """
    Applies the logit function to self. Logit(x) = ln(x/(1-x)).
    Note that logit(0) = -inf, logit(1) = inf, and logit(p) for p < 0 or p > 1 yields nan.
    """
    return pl_plugin(
        args=[str_to_expr(x)],
        symbol="pl_logit",
        is_elementwise=True,
    )


def exp2(x: StrOrExpr) -> pl.Expr:
    """
    Returns 2^x.
    """
    return pl_plugin(
        args=[str_to_expr(x)],
        symbol="pl_exp2",
        is_elementwise=True,
    )


def fract(x: StrOrExpr) -> pl.Expr:
    """
    Returns the fractional part of the input values. E.g. fractional part of 1.1 is 0.1
    """
    return pl_plugin(
        args=[str_to_expr(x)],
        symbol="pl_fract",
        is_elementwise=True,
    )


def trunc(x: StrOrExpr) -> pl.Expr:
    """
    Returns the integer part of the input values. E.g. integer part of 1.1 is 1.0
    """
    return pl_plugin(
        args=[str_to_expr(x)],
        symbol="pl_trunc",
        is_elementwise=True,
    )


def sinc(x: StrOrExpr) -> pl.Expr:
    """
    Computes the sinc function normalized by pi.
    """
    xx = str_to_expr(x)
    y = math.pi * pl.when(xx == 0).then(1e-20).otherwise(xx)
    return y.sin() / y


def detrend(x: StrOrExpr, method: DetrendMethod = "linear") -> pl.Expr:
    """
    Detrends self using either linear/mean method. This does not persist.

    Parameters
    ----------
    method
        Either `linear` or `mean`
    """
    ts = str_to_expr(x)
    if method == "linear":
        N = ts.count()
        x = pl.int_range(0, N, eager=False)
        coeff = pl.cov(ts, x) / x.var()
        const = ts.mean() - coeff * (N - 1) / 2
        return ts - x * coeff - const
    elif method == "mean":
        return ts - ts.mean()
    else:
        raise ValueError(f"Unknown detrend method: {method}")


def rfft(series: StrOrExpr, n: Optional[int] = None, return_full: bool = False) -> pl.Expr:
    """
    Computes the DFT transform of a real-valued input series using FFT Algorithm. Note that
    by default a series of length (length // 2 + 1) will be returned.

    Parameters
    ----------
    series
        Input real series
    n
        The number of points to use. If n is smaller than the length of the input,
        the input is cropped. If it is larger, the input is padded with zeros.
        If n is not given, the length of the input is used.
    return_full
        If true, output will have the same length as determined by n.
    """
    if n is not None and n <= 1:
        raise ValueError("Input `n` should be > 1.")

    full = pl.lit(return_full, pl.Boolean)
    nn = pl.lit(n, pl.UInt32)
    x: pl.Expr = str_to_expr(series).cast(pl.Float64)
    return pl_plugin(symbol="pl_rfft", args=[x, nn, full], changes_length=True)


def target_encode(
    s: StrOrExpr,
    target: Union[StrOrExpr, Iterable[int]],
    min_samples_leaf: int = 20,
    smoothing: float = 10.0,
) -> pl.Expr:
    """
    Compute information necessary to target encode a string column.

    Note: nulls will be encoded as well.

    Parameters
    ----------
    s
        The string column to encode
    target
        The target column. Should be 0s and 1s.
    min_samples_leaf
        A regularization factor
    smoothing
        Smoothing effect to balance categorical average vs prior

    Reference
    ---------
    https://contrib.scikit-learn.org/category_encoders/targetencoder.html
    """
    if isinstance(target, (str, pl.Expr)):
        t = str_to_expr(target)
    else:
        t = pl.Series(values=target)
    return pl_plugin(
        symbol="pl_target_encode",
        args=[str_to_expr(s), t, t.mean()],
        kwargs={"min_samples_leaf": float(min_samples_leaf), "smoothing": smoothing},
        changes_length=True,
    )
