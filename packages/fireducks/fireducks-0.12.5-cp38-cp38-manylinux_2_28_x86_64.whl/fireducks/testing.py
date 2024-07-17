# Copyright (c) 2023 NEC Corporation. All Rights Reserved.


import fireducks.pandas as pd
import pandas


def assert_range_index_equal(left, right):
    assert left.start == right.start
    assert left.stop == right.stop
    assert left.step == right.step


def assert_index_equal(left, right):
    assert left.equals(right)
    assert type(left) == type(right)

    # left.equal(right) return true when both range indexes are empty with
    # different start/stop/step. Ex:
    #   - RangeIndex(6, 6, 1)
    #   - RangeIndex(3, 0, 5)
    # To check pandas compatibility, we check more strictly.
    #
    # To use this assert for pandas, allow pandas.RangeIndex. It does not mean
    # that we want to test fireducks's index with pandas's index.
    if isinstance(left, pd.wrappers.RangeIndex) or isinstance(
        left, pandas.RangeIndex
    ):
        assert_range_index_equal(left, right)

    assert left.names == right.names


def assert_frame_equal(left, right):
    assert left.equals(right)
    assert left.columns.names == right.columns.names
    assert_index_equal(left.index, right.index)


def assert_series_equal(left, right):
    assert left.equals(right)
    assert left.name == right.name
    assert_index_equal(left.index, right.index)
