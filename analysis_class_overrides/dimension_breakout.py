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
        from genpact_formatting import genpact_format_number
        
        categories = raw_b_df[dim].tolist()
        
        # Get the metric format to determine if it's a percentage
        metric_format = self.format_dict.get(metric, "")
        is_percentage = "%" in metric_format
        is_currency = "$" in metric_format
        
        # Prepare data with proper formatting like the working skills
        raw_values = raw_b_df[metric].tolist()
        chart_data = []
        
        for i, (category, raw_value) in enumerate(zip(categories, raw_values)):
            try:
                # Handle NaN values
                if pd.isna(raw_value):
                    chart_data.append({
                        "name": category,
                        "y": 0,
                        "formatted": "N/A"
                    })
                    continue
                
                # Format the value using genpact_format_number like working skills
                if is_percentage:
                    # For percentages, keep original formatting
                    formatted_value = f"{raw_value:.1f}%" if isinstance(raw_value, (int, float)) else str(raw_value)
                    chart_data.append({
                        "name": category,
                        "y": float(raw_value) if isinstance(raw_value, (int, float)) else 0,
                        "formatted": formatted_value
                    })
                else:
                    # For currency and regular numbers, use genpact formatting
                    if is_currency:
                        formatted_value = f"${genpact_format_number(raw_value)}"
                    else:
                        formatted_value = genpact_format_number(raw_value)
                    
                    chart_data.append({
                        "name": category,
                        "y": float(raw_value) if isinstance(raw_value, (int, float)) else 0,
                        "formatted": formatted_value
                    })
                    
            except Exception as e:
                # Fallback for any conversion issues
                chart_data.append({
                    "name": category,
                    "y": 0,
                    "formatted": "0"
                })

        # Use the proven chart configuration from working skills
        y_axis = [{
            "title": "",
            "labels": {
                "formatter": "function() { return this.axis.defaultLabelFormatter.call(this); }"
            }
        }]
        
        # Build series data with better color palette
        data = [{
            "name": metric,
            "data": chart_data,
            "dataLabels": {
                "enabled": False,
                "formatter": "function() { return this.point.formatted || this.y; }"
            },
            "tooltip": {
                "pointFormatter": "function() { return '<b>' + this.series.name + '</b>: ' + (this.formatted || this.y); }"
            },
            # Use a vibrant color palette instead of dark blue/black
            "colorByPoint": True,
            "colors": [
                "#2E86C1",  # Professional blue (like working skills)
                "#28B463",  # Green
                "#F39C12",  # Orange
                "#E74C3C",  # Red  
                "#8E44AD",  # Purple (like working skills)
                "#17A2B8",  # Teal
                "#FFC107",  # Amber
                "#DC3545",  # Crimson
                "#20C997",  # Success green
                "#6F42C1",  # Indigo
                "#FD7E14",  # Bright orange
                "#198754"   # Forest green
            ]
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