from typing import Dict
from ar_analytics import ArUtils
from ar_analytics.driver_analysis import DriverAnalysis
from ar_analytics.metric_tree import MetricTreeAnalysis
from ar_analytics.breakout_drivers import BreakoutDrivers
from ar_analytics.helpers.utils import Connector, fmt_sign_num
import pandas as pd
from analysis_class_overrides.insurance_utilities import InsuranceSharedFn

class InsuranceDriverAnalysis(DriverAnalysis):
    def __init__(self, dim_hierarchy, dim_val_map={}, sql_exec:Connector=None, constrained_values={}, compare_date_warning_msg=None, df_provider=None, sp=None):
        self.mta = MetricTreeAnalysis(sql_exec, df_provider=df_provider, sp=sp)
        self.ba = BreakoutDrivers(dim_hierarchy, dim_val_map, sql_exec, df_provider=df_provider, sp=sp)
        self.helper = InsuranceSharedFn()
        self.allowed_metrics = constrained_values.get("metric", [])
        self.alloed_breakouts = constrained_values.get("breakout", [])
        self.notes = []
        self.compare_date_warning_msg = compare_date_warning_msg
        self.sp=sp
        self.ar_utils = ArUtils()

    def _create_breakout_chart_vars(self, raw_b_df: pd.DataFrame, dim: str, rename_dict: Dict[str, str]):

        categories = raw_b_df[dim].tolist()

        formatter = self.ar_utils.python_to_highcharts_format(self.ba.target_metric["fmt"])

        y_axis = [{
            "title": "",
            "labels": {
                "format": formatter.get('value_format')
            }
        }]

        data = []

        for col in ["curr", "prev"]:
            data.append({
                "name": rename_dict[col],
                "data": self.helper.replace_nans_with_string_nan(raw_b_df[col].tolist()),
                "dataLabels": {
                    "enabled": True,
                    "format": formatter.get('point_y_format')
                },
                "tooltip": {
                    "pointFormat": "<b>{series.name}</b>: " + formatter.get('point_y_format')
                }
            })

        return {
            "chart_categories": categories,
            "chart_y_axis": y_axis,
            "chart_title": "",
            "chart_data": data
        }

    def get_display_tables(self):
        metric_df = self._metric_df.copy()
        breakout_df = self._breakout_df.copy()
        breakout_chart_df = self._breakout_df.copy()

        # Define required columns for metric_df
        metric_tree_required_columns = ["curr", "prev", "diff", "growth"]
        if self.include_sparklines:
            metric_tree_required_columns.append("sparkline")

        if "impact" in metric_df.columns:
            metric_tree_required_columns.append("impact")

        # Filter metric_df to include only the required columns
        metric_df = metric_df[metric_tree_required_columns]

        # Apply formatting for metric_df
        for col in ["curr", "prev", "diff", "growth"]:
            metric_df[col] = metric_df.apply(
                lambda row: self.helper.get_formatted_num(
                    row[col],
                    self.helper.get_metric_prop(row.name, self.metric_props).get("fmt",
                                                                                 "") if col != "growth" else self.helper.get_metric_prop(
                        row.name, self.metric_props).get("growth_fmt", "")
                ), axis=1
            )

        if "impact" in metric_df.columns:
            metric_df["impact"] = metric_df.apply(
                lambda row: self.helper.get_formatted_num(row["impact"], self.mta.impact_format), axis=1
            )

        # rename columns
        metric_df = metric_df.rename(
            columns={'curr': 'Value', 'prev': 'Prev Value', 'diff': 'Change', 'growth': '% Growth'})
        
        metric_df = metric_df.reset_index()

        # rename index to metric labels
        metric_df["index"] = metric_df["index"].apply(lambda x: self.helper.get_metric_prop(x, self.metric_props).get("label", x))

        # indent non target metric
        metric_df["index"] = metric_df["index"].apply(lambda x: f"  {x}" if x != self.mta.target_metric else x)

        metric_df = metric_df.rename(columns={"index": ""})

        # Define required columns for breakout_df
        breakout_required_columns = ["curr", "prev", "diff", "diff_pct", "rank_change"]
        if self.include_sparklines:
            breakout_required_columns.append("sparkline")

        breakout_dfs = {}
        breakout_chart_vars = {}

        # Apply formatting for breakout_df
        for col in ["curr", "prev", "diff", "diff_pct"]:
            breakout_df[col] = breakout_df.apply(
                lambda row: self.helper.get_formatted_num(row[col],
                                                          self.ba.target_metric["fmt"] if col != "diff_pct" else
                                                          self.ba.target_metric["growth_fmt"]),
                axis=1
            )

        # Format rank column
        breakout_df["rank_curr"] = breakout_df["rank_curr"]
        breakout_df["rank_change"] = breakout_df.apply(lambda row: f"{int(row['rank_curr'])} ({fmt_sign_num(row['rank_change'])})"
                                                    if (row['rank_change'] and pd.notna(row['rank_change']) and row['rank_change'] != 0)
                                                    else row['rank_curr'], axis=1)
        breakout_df = breakout_df.reset_index()
        breakout_chart_df = breakout_chart_df.reset_index()

        breakout_dims = list(breakout_df["dim"].unique())
        if self.ba.dim_hier:
            # display according to the dim hierarchy ordering
            ordering_dict = {value: index for index, value in enumerate(self.ba.dim_hier.get_hierarchy_ordering())}
            # rename cols to dim labels
            ordering_dict = {self.helper.get_dimension_prop(k, self.dim_props).get("label", k): v for k, v in ordering_dict.items()}
            # sort dims by hierarchy order
            breakout_dims.sort(key=lambda x: (ordering_dict.get(x, len(ordering_dict)), x))

        comp_dim = None
        if self.ba._owner_dim:
            comp_dim = next((d for d in breakout_dims if d.lower() == self.ba._owner_dim.lower()), None)

        if comp_dim:
            breakout_dims = [comp_dim] + [x for x in breakout_dims if x != comp_dim]

        for dim in breakout_dims:
            b_df = breakout_df[breakout_df["dim"] == dim]
            raw_b_df = breakout_chart_df[breakout_chart_df["dim"] == dim]
            if str(dim).lower() == str(comp_dim).lower():
                viz_name = "Benchmark"
            else:
                viz_name = dim
            raw_b_df = raw_b_df.rename(columns={'dim_value': dim})
            b_df = b_df.rename(columns={'dim_value': dim})
            b_df = b_df[[dim] + breakout_required_columns]

            rename_dict = {'curr': 'Value', 'prev': 'Prev Value', 'diff': 'Change', 'diff_pct': '% Growth',
                         'rank_change': 'Rank Change'}

            # rename columns
            b_df = b_df.rename(
                columns=rename_dict)
            breakout_dfs[viz_name] = {
                "df": b_df,
                "chart_vars": self._create_breakout_chart_vars(raw_b_df, dim, rename_dict)
            }

        return {"viz_metric_df": metric_df, "viz_breakout_dfs": breakout_dfs}

class InsuranceMetricTreeAnalysis(MetricTreeAnalysis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = InsuranceSharedFn()

class InsuranceBreakoutDrivers(BreakoutDrivers):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = InsuranceSharedFn()