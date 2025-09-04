from typing import Dict
from ar_analytics import ArUtils
from ar_analytics.legacy_breakout import BreakoutAnalysis
import pandas as pd
from analysis_class_overrides.insurance_utilities import InsuranceSharedFn
from ar_analytics.helpers.utils import OldDimensionHierarchy

class InsuranceLegacyBreakout(BreakoutAnalysis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = InsuranceSharedFn()
        self.ar_utils = ArUtils()

    def _create_breakout_chart_vars(self, raw_b_df: pd.DataFrame, dim: str, metric: str):

        categories = raw_b_df[dim].tolist()
        formatter = self.ar_utils.python_to_highcharts_format(self.format_dict[metric])

        y_axis = [{
            "title": "",
            "labels": {
                "format": formatter.get('value_format')
            }
        }]

        data = [{
            "name": metric,
            "data": self.helper.replace_nans_with_string_nan(raw_b_df[metric].tolist()),
            "dataLabels": {
                "enabled": False,
                "format": formatter.get('point_y_format')
            },
            "tooltip": {
                "pointFormat": "<b>{series.name}</b>: " + formatter.get('point_y_format')
            }
        }]

        return {
            "chart_categories": categories,
            "chart_y_axis": y_axis,
            "chart_title": "",
            "chart_data": data
        }
    
    def get_display_tables(self):
        df = self._df.copy()
        col_order = [col for col in df.columns if col not in self.metric_cols] + self.metric_cols
        df = df[col_order]
        tables = {}
        dims = list(df["dim"].unique())

        if self.dim_hierarchy:
            # display according to the dim hierarchy ordering
            ordering_dict = {value: index for index, value in
                             enumerate(OldDimensionHierarchy(self.dim_hierarchy).get_hierarchy_ordering())}
            # rename cols to dim labels
            ordering_dict = {self.helper.get_dimension_prop(k, self.dim_props).get("label", k): v for k, v in
                             ordering_dict.items()}
            # sort dims by hierarchy order
            dims.sort(key=lambda x: (ordering_dict.get(x, len(ordering_dict)), x))

        for ix, dim_name in enumerate(dims):
            dim_df = df[df["dim"] == dim_name]
            chart_dim_df = dim_df.copy()
            if ix == 0:
                self.row_count = len(dim_df)
            col_rename = {"dim_member": dim_name}
            if "rank" in dim_df:
                col_rename["rank"] = self.rank_col_map.get(dim_name, "rank")

            # renaming column to be used for highlighting to is_subject for consistency with other skills
            col_rename["filtered_dim"] = "is_subject"
            dim_df = dim_df.rename(columns=col_rename)
            dim_df.drop(columns=["dim"], inplace=True)

            for metric in self.metric_cols:
                if metric in dim_df.columns:
                    dim_df[metric] = dim_df[metric].apply(lambda x: self.helper.get_formatted_num(x, self.format_dict[metric]))

            dim_df.max_metadata.set_filters(self.env.breakout_parameters.get("query_filters", []))
            dim_df.max_metadata.set_measures(self.metric_cols)
            dim_df.max_metadata.set_description(f"{', '.join(self.metric_cols)} broken out by {dim_name}")
            tables[dim_name] = {
                "df": dim_df,
                "chart_vars": self._create_breakout_chart_vars(chart_dim_df, "dim_member", self.metric_cols[0])
            }

        return tables