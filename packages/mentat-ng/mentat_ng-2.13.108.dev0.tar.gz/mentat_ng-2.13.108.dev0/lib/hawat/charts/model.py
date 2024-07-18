"""
This file contains data models for the charts module.
"""

from flask_babel import lazy_gettext, format_decimal
from flask_babel.speaklater import LazyString
import pandas as pd
from functools import reduce
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Union,
    Iterable
)
import typing
from abc import ABC

from mentat.stats.idea import (
    ST_SKEY_REST,
    TimelineCFG,
    DataRowType,
    DataWideType,
    DataLongType,
    StatType,
    StatisticsDataType
)
from .const import (
    ChartJSONType,
    DataComplexity,
    InputDataFormat,
)
from . import const, chart_configuration


class ChartData(ABC):
    """Class representing data required to render a chart."""

    chart: ChartJSONType
    """JSON of chart to be rendered by plotly on the frontend."""

    df: pd.DataFrame
    """Pandas DataFrame to be used for rendering a table for the chart."""

    def to_dict(self) -> Dict[str, Any]:
        """Returns json-serializable dictionary representation of the data."""
        return self.df.reset_index().to_dict('records')

    def __iter__(self) -> Iterator[Union[ChartJSONType, pd.DataFrame]]:
        """Iterate over the rows of the data frame."""
        yield from (self.chart, self.df)


class TimelineChartData(ChartData):
    timeline_cfg: TimelineCFG

    def __init__(
        self,
        data: Union[DataWideType, DataLongType],
        chsection: 'ChartSection',
        timeline_cfg: TimelineCFG,
        data_format: InputDataFormat,
        add_rest: bool = False,
        x_axis_label_override: Union[str, LazyString, None] = None,
        forced_timezone: Optional[str] = None,
    ) -> None:
        """
        Expects `data` to be sorted by bucket in ascending order.

        if add_rest is true, the data is modified so it only contains `const.MAX_VALUE_COUNT`
        columns, and the rest will be stored under `__REST__` (Useful, when the source statistics do not
        already contain `__REST__`, and need to be abridged)
        """

        if data_format == InputDataFormat.LONG_SIMPLE\
           and chsection.data_complexity != DataComplexity.NONE:
            raise ValueError('LONG_SIMPLE data format can only support data complexity of NONE')

        self.timeline_cfg = timeline_cfg

        if data_format == InputDataFormat.WIDE_SIMPLE:
            data = typing.cast(DataWideType, data)
            df = self._from_wide_simple(data, chsection)
        elif data_format == InputDataFormat.WIDE_COMPLEX:
            data = typing.cast(DataWideType, data)
            df = self._from_wide_complex(data, chsection)
        elif data_format == InputDataFormat.LONG_SIMPLE:
            data = typing.cast(DataLongType, data)
            df = self._from_long_simple(data, chsection)
        elif data_format == InputDataFormat.LONG_COMPLEX:
            data = typing.cast(DataLongType, data)
            df = self._from_long_complex(data)
        else:
            raise ValueError(f"Invalid value '{data_format}' for type InputDataFormat")

        df = self._move_rest_to_end(df)

        if add_rest:
            df = self._add_rest(df)

        if df.empty:
            self.chart = chart_configuration.get_chart_json_no_data()
        else:
            self.chart = chart_configuration.get_chart_json_timeline(
                df,
                chsection,
                timeline_cfg,
                forced_timezone=forced_timezone,
                x_axis_label_override=None if x_axis_label_override is None else str(x_axis_label_override)
            )

        df[const.KEY_SUM] = df.sum(axis=1)  # add sum of each bucket as a last column
        self.df = df

    @staticmethod
    def _from_long_simple(data: DataLongType, chsection: 'ChartSection') -> pd.DataFrame:
        """
        Converts from `InputDataFormat.LONG_SIMPLE` to a unified pandas DataFrame for timeline.
        """
        df = pd.DataFrame(data)
        df.set_index('bucket', inplace=True)
        df.rename(columns={'count': str(chsection.column_name)}, inplace=True)
        return df

    @staticmethod
    def _from_long_complex(data: DataLongType) -> pd.DataFrame:
        """
        Converts from `InputDataFormat.LONG_COMPLEX` to a unified pandas DataFrame for timeline.
        """
        df = pd.DataFrame(data)

        # Similar to:
        # df = pd.DataFrame(data).pivot(
        #     columns='set',
        #     index='bucket',
        #     values='count'
        # )
        # But retains the order of columns
        return df.groupby(
            ['bucket', 'set'],
            sort=False
        )['count'].sum().unstack()

    @staticmethod
    def _from_wide_simple(data: DataWideType, chsection: 'ChartSection') -> pd.DataFrame:
        """
        Converts from `InputDataFormat.WIDE_SIMPLE` to a unified pandas DataFrame for timeline.
        """
        df = pd.DataFrame(TimelineChartData._iter_wide_simple_data(data, chsection))
        df.set_index('bucket', inplace=True)
        return df

    @staticmethod
    def _from_wide_complex(data: DataWideType, chsection: 'ChartSection') -> pd.DataFrame:
        """
        Converts from `InputDataFormat.WIDE_COMPLEX` to a unified pandas DataFrame for timeline.
        """
        df = pd.DataFrame(TimelineChartData._iter_wide_complex_data(data, chsection))
        df.fillna(0, inplace=True)
        df.set_index('bucket', inplace=True)
        return df

    @staticmethod
    def _iter_wide_simple_data(
        data: DataWideType,
        chsection: 'ChartSection'
    ) -> Iterator[DataRowType]:
        for bucket, stat in data:
            row: DataRowType = {'bucket': bucket}
            for data_key in chsection.iter_data_keys():
                row[str(data_key.display_name)] = typing.cast(
                    Union[int, float],
                    stat.get(data_key.key, 0)
                )
            yield row

    @staticmethod
    def _iter_wide_complex_data(
        data: DataWideType,
        chsection: 'ChartSection'
    ) -> Iterator[DataRowType]:
        for bucket, stat in data:
            yield {
                'bucket': bucket,
                **typing.cast(DataRowType, stat.get(chsection.key, {}))
            }

    @staticmethod
    def _move_rest_to_end(df: pd.DataFrame) -> pd.DataFrame:
        """
        Moves the `__REST__` column to the end of the timeline dataframe.
        """
        if ST_SKEY_REST in df.columns:
            df.insert(len(df.columns) - 1, ST_SKEY_REST, df.pop(ST_SKEY_REST))
        return df

    @staticmethod
    def _add_rest(df: pd.DataFrame) -> pd.DataFrame:
        """
        Abridges the dataframe for secondary charts to contain only `const.MAX_VALUE_COUNT`
        columns, and stores the rest under `__REST__` column.
        """
        if df.shape[1] > const.MAX_VALUE_COUNT:
            kept_columns = df.iloc[:, :const.MAX_VALUE_COUNT - 1]
            df[ST_SKEY_REST] = df.iloc[:, const.MAX_VALUE_COUNT - 1:].sum(axis=1)
            return pd.concat([kept_columns, df[[ST_SKEY_REST]]], axis=1)

        return df


class SecondaryChartData(ChartData):
    def __init__(
        self,
        statistics: StatisticsDataType,
        chsection: 'ChartSection',
        data_format: InputDataFormat,
        total_count: Optional[int] = None,
        add_rest: bool = False,
        sort: bool = False,
    ) -> None:
        """
        if total count not provided, it is calculated as the sum of all counts in the data frame.

        if add_rest is true, the data is modified so it only contains `const.MAX_VALUE_COUNT`
        rows, and the rest will be stored under `__REST__` (Useful, when the source statistics do
        not already contain `__REST__`, and need to be abridged)

        sort should be set to True, if the source data is not yet sorted.
        """

        if chsection.data_complexity == DataComplexity.NONE:
            raise ValueError('Cannot generate a secondary chart for DataComplexity.NONE')

        if data_format == InputDataFormat.WIDE_SIMPLE:
            data_iter: Iterable[Dict[str, Union[str, int, float]]] = (
                {
                    'set': str(data_key.display_name),
                    'count': typing.cast(Union[int, float], statistics.get(data_key.key))
                }
                for data_key in chsection.iter_data_keys()
            )
        elif chsection.key in statistics:
            data_iter = (
                {'set': key, 'count': val}
                for key, val in typing.cast(StatType, statistics[chsection.key]).items()
            )
        else:
            data_iter = []

        df = pd.DataFrame(data_iter)

        if sort and not df.empty:
            df = df.sort_values(by='count', ascending=False)

        df = self._move_rest_to_end(df)

        if add_rest:
            df = self._add_rest(df)

        if total_count is None and 'count' in df.columns:
            total_count = df['count'].sum()

        if total_count != 0 and 'count' in df.columns:
            df[const.KEY_SHARE] = df['count'] / total_count
        else:
            df[const.KEY_SHARE] = 0.0

        if df.empty:
            self.chart = chart_configuration.get_chart_json_no_data()
        elif chsection.data_complexity == DataComplexity.SINGLE:
            self.chart = chart_configuration.get_chart_json_pie(df, chsection)
        elif chsection.data_complexity == DataComplexity.MULTI:
            self.chart = chart_configuration.get_chart_json_bar(df, chsection)

        if 'set' in df.columns:
            df.set_index('set', inplace=True)

        self.df = df

    @staticmethod
    def _move_rest_to_end(df: pd.DataFrame) -> pd.DataFrame:
        """
        Moves the `__REST__` row to the end of the secondary dataframe.
        """
        if 'set' not in df.columns:
            return df

        rest_row = df[df['set'] == ST_SKEY_REST]
        df = df[df['set'] != ST_SKEY_REST]
        return pd.concat([df, rest_row])

    @staticmethod
    def _add_rest(df: pd.DataFrame) -> pd.DataFrame:
        """
        Abridges the dataframe for secondary charts to contain only `const.MAX_VALUE_COUNT`
        rows, and stores the rest under `__REST__`.
        """
        if df.shape[0] > const.MAX_VALUE_COUNT:
            kept_rows = df.iloc[:const.MAX_VALUE_COUNT - 1]
            rest_sum = df.iloc[const.MAX_VALUE_COUNT - 1:]['count'].sum()
            sum_row = pd.DataFrame({'set': [ST_SKEY_REST], 'count': [rest_sum]})
            return pd.concat([kept_rows, sum_row])
        return df


class ChartSectionData(NamedTuple):
    """Named Tuple representing data for all charts in a single chart section."""
    timeline: Optional[TimelineChartData] = None
    secondary: Optional[SecondaryChartData] = None

    def add(self, *args: ChartData) -> 'ChartSectionData':
        return reduce(ChartSectionData._add_single, args, self)

    def _add_single(self, data: ChartData) -> 'ChartSectionData':
        if isinstance(data, TimelineChartData) and self.timeline is None:
            return self._replace(timeline=data)
        if isinstance(data, SecondaryChartData) and self.secondary is None:
            return self._replace(secondary=data)
        raise ValueError('Only one instance of each ChartData type is allowed')

    def __bool__(self) -> bool:
        return any(self)


class DataKey(NamedTuple):
    key: str
    display_name: Union[LazyString, str]


class ValueFormats(NamedTuple):
    column_name: Union[LazyString, str] = lazy_gettext('Count')
    """Name for the column containing the value. Shown in tables and charts on hover."""

    format_function: Callable = format_decimal
    """Function to be used for formatting values under 'count' in tables."""

    d3_format: Union[str, bool] = True
    """
    D3 format string to be used for formatting values in hover text for charts.
    If True, the plotly default format is used. If False, value is omitted.
    """


class ChartSection(NamedTuple):
    key: str
    """Key, under which chart and table date is expected to be stored in the response context."""

    label: Union[LazyString, str]
    """Name shown on the tab label."""

    short_description: Union[LazyString, str, None]
    """Text shown as the header of the tab."""

    description: Union[LazyString, str, None]
    """Long, descriptive text shown right under the header of the tab."""

    data_complexity: DataComplexity
    """Used to differentiate which secondary chart to use."""

    column_name: Union[LazyString, str]
    """
    Name for column containing the aggregated categories.
    Shown in charts on hover, and the rendered table.
    """

    value_formats: ValueFormats = ValueFormats()
    """Formats for the values in the tables and charts."""

    csag_group: Optional[str] = None
    """
    Context search group the aggregated categories belong to.
    If unset, `key` is used.
    """

    allow_table_aggregation: Optional[bool] = None
    """
    Enables/disables aggregation footers in the chart tables.
    If unset, timeline charts, and pie charts will contain aggregation footer,
    secondary bar charts will not.
    """

    data_keys: Optional[List[DataKey]] = None
    """
    Keys which store the data for visualization in WIDE SIMPLE data format.
    If the data format is not WIDE_SIPMLE, this is ignored.
    If None, only the single key stored in `key` will be used.
    """

    data: ChartSectionData = ChartSectionData()
    """
    Data containing all chart and table data for this section.
    Usually provided later, during request handling, using the `add_data` method.

    model for data:
    ```
    data                    ChartSectionData
      ├─.timeline           TimelineChartData
      │   ├─.chart          ChartJSONType
      │   ├─.df             pd.DataFrame
      │   └─.timeline_cfg   TimelineCFG
      └─.secondary          SecondaryChartData
          ├─.chart          ChartJSONType
          └─.df             pd.DataFrame
    ```
    """

    def add_data(self, *args: ChartData) -> 'ChartSection':
        """Add provided chart data to the chart section"""
        return self._replace(data=self.data.add(*args))

    def iter_data_keys(self) -> Iterator[DataKey]:
        """Iterate over all data keys for the chart section"""
        if self.data_keys is not None:
            yield from self.data_keys
        else:
            yield DataKey(self.key, self.column_name)

    def get_csag_group(self) -> str:
        """Get the context search group for the chart section"""
        return self.csag_group or self.key

    def get_aggregate_table(self) -> bool:
        """Get whether aggregation footers should be shown in the secondary chart tables"""
        if self.allow_table_aggregation is not None:
            return self.allow_table_aggregation
        return self.data_complexity == DataComplexity.SINGLE
