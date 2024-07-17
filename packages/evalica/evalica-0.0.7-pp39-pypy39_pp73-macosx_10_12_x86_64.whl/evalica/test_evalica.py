from __future__ import annotations

from typing import Any

import hypothesis.strategies as st
import numpy as np
import numpy.typing as npt
import pandas as pd
import pytest
from hypothesis import given
from hypothesis.extra._array_helpers import array_shapes
from hypothesis.extra.numpy import arrays
from hypothesis.extra.pandas import series
from pandas._testing import assert_series_equal

import evalica
from conftest import Example, elements


def test_version() -> None:
    assert isinstance(evalica.__version__, str)
    assert len(evalica.__version__) > 0


def test_exports() -> None:
    for attr in evalica.__all__:
        assert hasattr(evalica, attr), f"missing attribute: {attr}"


@given(example=elements())
def test_index_elements(example: Example) -> None:  # type: ignore[type-var]
    xs, ys, _ = example

    index, xs_indexed, ys_indexed = evalica.index_elements(xs, ys)

    assert len(xs_indexed) == len(xs)
    assert len(ys_indexed) == len(ys)
    assert isinstance(index, pd.Index)
    assert len(index) == len(set(xs) | set(ys))
    assert set(index.values) == (set(xs) | set(ys))


@given(example=elements())
def test_index_elements_reuse(example: Example) -> None:
    xs, ys, _ = example

    index, xs_indexed, ys_indexed = evalica.index_elements(xs, ys)
    reindex, xs_reindexed, ys_reindexed = evalica.index_elements(xs, ys, index)

    assert xs_reindexed == xs_indexed
    assert ys_reindexed == ys_indexed
    assert reindex is index


@given(example=elements())
def test_matrices(example: Example) -> None:
    xs, ys, ws = example

    index, xs_indexed, ys_indexed = evalica.index_elements(xs, ys)

    wins = sum(status in [evalica.Winner.X, evalica.Winner.Y] for status in ws)
    ties = sum(status == evalica.Winner.Draw for status in ws)

    result = evalica.matrices(xs_indexed, ys_indexed, ws, index)

    assert result.win_matrix.shape == (len(index), len(index))
    assert result.tie_matrix.shape == (len(index), len(index))
    assert result.win_matrix.sum() == wins
    assert result.tie_matrix.sum() == 2 * ties


@given(example=elements(), win_weight=st.floats(0., 10.), tie_weight=st.floats(0., 10.))
def test_counting(example: Example, win_weight: float, tie_weight: float) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.counting(
        xs, ys, ws,
        win_weight=win_weight,
        tie_weight=tie_weight,
        solver="pyo3",
    )

    result_naive = evalica.counting(
        xs, ys, ws,
        win_weight=win_weight,
        tie_weight=tie_weight,
        solver="naive",
    )

    for result in (result_pyo3, result_naive):
        assert len(result.scores) == len(set(xs) | set(ys))
        assert np.isfinite(result.scores).all()

    assert_series_equal(result_pyo3.scores, result_naive.scores)


@given(example=elements(), win_weight=st.floats(0., 10.), tie_weight=st.floats(0., 10.))
def test_bradley_terry(example: Example, win_weight: float, tie_weight: float) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.bradley_terry(
        xs, ys, ws,
        win_weight=win_weight,
        tie_weight=tie_weight,
        solver="pyo3",
    )

    result_naive = evalica.bradley_terry(
        xs, ys, ws,
        win_weight=win_weight,
        tie_weight=tie_weight,
        solver="naive",
    )

    for result in (result_pyo3, result_naive):
        assert len(result.scores) == len(set(xs) | set(ys))
        assert np.isfinite(result.scores).all()
        assert result.iterations > 0

    assert_series_equal(result_pyo3.scores, result_naive.scores, rtol=1e-4)


@given(example=elements(), v_init=st.floats())
def test_newman(example: Example, v_init: float) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.newman(xs, ys, ws, v_init=v_init, solver="pyo3")
    result_naive = evalica.newman(xs, ys, ws, v_init=v_init, solver="naive")

    for result in (result_pyo3, result_naive):
        assert len(result.scores) == len(set(xs) | set(ys))
        assert np.isfinite(result.scores).all()
        assert np.isfinite(result.v)
        assert result.iterations > 0

        if np.isfinite(v_init):
            assert result.v_init == v_init
        else:
            assert result.v_init is v_init

    assert_series_equal(result_pyo3.scores, result_naive.scores)
    assert result_pyo3.v == pytest.approx(result_naive.v)


@given(
    example=elements(),
    initial=st.floats(0., 1000.),
    base=st.floats(0., 1000.),
    scale=st.floats(0., 1000.),
    k=st.floats(0., 1000.),
)
def test_elo(
        example: Example,
        initial: float,
        base: float,
        scale: float,
        k: float,
) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.elo(
        xs, ys, ws,
        initial=initial,
        base=base,
        scale=scale,
        k=k,
        solver="pyo3",
    )

    result_naive = evalica.elo(
        xs, ys, ws,
        initial=initial,
        base=base,
        scale=scale,
        k=k,
        solver="naive",
    )

    for result in (result_pyo3, result_naive):
        assert len(result.scores) == len(set(xs) | set(ys))
        assert np.isfinite(result.scores).all()

    assert_series_equal(result_pyo3.scores, result_naive.scores)


@given(example=elements(), win_weight=st.floats(0., 10.), tie_weight=st.floats(0., 10.))
def test_eigen(example: Example, win_weight: float, tie_weight: float) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.eigen(
        xs, ys, ws,
        win_weight=win_weight,
        tie_weight=tie_weight,
        solver="pyo3",
    )

    result_naive = evalica.eigen(
        xs, ys, ws,
        win_weight=win_weight,
        tie_weight=tie_weight,
        solver="naive",
    )

    for result in (result_pyo3, result_naive):
        assert len(result.scores) == len(set(xs) | set(ys))
        assert np.isfinite(result.scores).all()
        assert not xs or result.iterations > 0

    assert_series_equal(result_pyo3.scores, result_naive.scores)


@given(
    example=elements(),
    damping=st.floats(0., 1.),
    win_weight=st.floats(0., 10.),
    tie_weight=st.floats(0., 10.),
)
def test_pagerank(example: Example, damping: float, win_weight: float, tie_weight: float) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.pagerank(
        xs, ys, ws,
        damping=damping,
        win_weight=win_weight,
        tie_weight=tie_weight,
        solver="pyo3",
    )

    result_naive = evalica.pagerank(
        xs, ys, ws,
        damping=damping,
        win_weight=win_weight,
        tie_weight=tie_weight,
        solver="naive",
    )

    for result in (result_pyo3, result_naive):
        assert len(result.scores) == len(set(xs) | set(ys))
        assert np.isfinite(result.scores).all()
        assert np.isfinite(result.damping)
        assert np.isfinite(result.win_weight)
        assert np.isfinite(result.tie_weight)
        assert not xs or result.iterations > 0

    assert_series_equal(result_pyo3.scores, result_naive.scores)


@given(example=elements(shape="bad"))
@pytest.mark.parametrize("algorithm", [
    "counting",
    "bradley_terry",
    "newman",
    "elo",
    "eigen",
    "pagerank",
])
def test_misshaped(example: Example, algorithm: str) -> None:
    with pytest.raises(evalica.LengthMismatchError):
        getattr(evalica, algorithm)(*example)


@pytest.mark.parametrize(("algorithm", "dataset"), [
    ("counting", "simple"),
    ("counting", "food"),
    ("counting", "llmfao"),
])
def test_counting_dataset(example: Example, example_golden: pd.Series[str]) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.counting(xs, ys, ws)
    result_naive = evalica.counting(xs, ys, ws)

    assert_series_equal(result_naive.scores, example_golden, check_like=True)
    assert_series_equal(result_pyo3.scores, example_golden, check_like=True)
    assert_series_equal(result_pyo3.scores, result_naive.scores, check_like=True)


@pytest.mark.parametrize(("algorithm", "dataset"), [
    ("bradley_terry", "simple"),
    ("bradley_terry", "food"),
    ("bradley_terry", "llmfao"),
])
def test_bradley_terry_dataset(example: Example, example_golden: pd.Series[str]) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.bradley_terry(xs, ys, ws, solver="pyo3")
    result_naive = evalica.bradley_terry(xs, ys, ws, solver="naive")

    assert_series_equal(result_naive.scores, example_golden, rtol=1e-4, check_like=True)
    assert_series_equal(result_pyo3.scores, example_golden, rtol=1e-4, check_like=True)
    assert_series_equal(result_pyo3.scores, result_naive.scores, check_like=True)


@pytest.mark.parametrize(("algorithm", "dataset"), [
    ("newman", "simple"),
    ("newman", "food"),
    ("newman", "llmfao"),
])
def test_newman_dataset(example: Example, example_golden: pd.Series[str]) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.newman(xs, ys, ws, solver="pyo3")
    result_naive = evalica.newman(xs, ys, ws, solver="naive")

    assert_series_equal(result_naive.scores, example_golden, rtol=1e-4, check_like=True)
    assert_series_equal(result_pyo3.scores, example_golden, rtol=1e-4, check_like=True)

    assert_series_equal(result_pyo3.scores, result_naive.scores, check_like=True)
    assert result_pyo3.v == pytest.approx(result_naive.v)


@pytest.mark.parametrize(("algorithm", "dataset"), [
    ("elo", "simple"),
    ("elo", "food"),
    ("elo", "llmfao"),
])
def test_elo_dataset(example: Example, example_golden: pd.Series[str]) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.elo(xs, ys, ws, initial=1000, k=4, scale=400, solver="pyo3")
    result_naive = evalica.elo(xs, ys, ws, initial=1000, k=4, scale=400, solver="naive")

    assert_series_equal(result_naive.scores, example_golden, check_like=True)
    assert_series_equal(result_pyo3.scores, example_golden, check_like=True)
    assert_series_equal(result_pyo3.scores, result_naive.scores, check_like=True)


@pytest.mark.parametrize(("algorithm", "dataset"), [
    ("eigen", "simple"),
    ("eigen", "food"),
    ("eigen", "llmfao"),
])
def test_eigen_dataset(example: Example, example_golden: pd.Series[str]) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.eigen(xs, ys, ws, solver="pyo3")
    result_naive = evalica.eigen(xs, ys, ws, solver="naive")

    assert_series_equal(result_naive.scores, example_golden, check_like=True)
    assert_series_equal(result_pyo3.scores, example_golden, check_like=True)
    assert_series_equal(result_pyo3.scores, result_naive.scores, check_like=True)


@pytest.mark.parametrize(("algorithm", "dataset"), [
    ("pagerank", "simple"),
    ("pagerank", "food"),
    ("pagerank", "llmfao"),
])
def test_pagerank_dataset(example: Example, example_golden: pd.Series[str]) -> None:
    xs, ys, ws = example

    result_pyo3 = evalica.pagerank(xs, ys, ws, solver="pyo3")
    result_naive = evalica.pagerank(xs, ys, ws, solver="naive")

    assert_series_equal(result_naive.scores, example_golden, check_like=True)
    assert_series_equal(result_pyo3.scores, example_golden, check_like=True)
    assert_series_equal(result_pyo3.scores, result_naive.scores, check_like=True)


@given(arrays(dtype=np.float64, shape=array_shapes(max_dims=1, min_side=0)))
def test_pairwise_scores(scores: npt.NDArray[np.float64]) -> None:
    with np.errstate(all="ignore"):
        pairwise = evalica.pairwise_scores(scores)

    assert pairwise.dtype == scores.dtype
    assert pairwise.shape == (len(scores), len(scores))

    if np.isfinite(scores).all():
        assert np.isfinite(pairwise).all()
    else:
        assert not np.isfinite(pairwise).all()


def test_pairwise_scores_empty() -> None:
    pairwise = evalica.pairwise_scores(np.zeros(0, dtype=np.float64))
    assert pairwise.dtype == np.float64
    assert pairwise.shape == (0, 0)


@given(array_shapes())
def test_pairwise_scores_shape(shape: tuple[int, ...]) -> None:
    scores = np.zeros(shape, dtype=np.int64)

    if len(shape) == 1:
        with np.errstate(all="ignore"):
            evalica.pairwise_scores(scores)
    else:
        with pytest.raises(evalica.ScoreDimensionError):
            evalica.pairwise_scores(scores)


@given(series(dtype=np.float64))
def test_pairwise_frame(scores: pd.Series[Any]) -> None:
    with np.errstate(all="ignore"):
        df_pairwise = evalica.pairwise_frame(scores)

    assert df_pairwise.shape == (len(scores), len(scores))
    assert df_pairwise.index is scores.index
    assert df_pairwise.columns is scores.index
