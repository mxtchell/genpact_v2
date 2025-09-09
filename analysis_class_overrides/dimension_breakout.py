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
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"DEBUG** Starting _create_breakout_chart_vars for metric: {metric}")
        logger.info(f"DEBUG** DataFrame shape: {raw_b_df.shape}")
        logger.info(f"DEBUG** DataFrame columns: {raw_b_df.columns.tolist()}")
        logger.info(f"DEBUG** Dim column: {dim}")
        
        categories = raw_b_df[dim].tolist()
        logger.info(f"DEBUG** Categories: {categories}")
        
        # Get the metric format to determine if it's a percentage
        metric_format = self.format_dict.get(metric, "")
        is_percentage = "%" in metric_format
        is_currency = "$" in metric_format
        logger.info(f"DEBUG** Metric format: {metric_format}, is_percentage: {is_percentage}, is_currency: {is_currency}")
        
        # Prepare data with proper formatting like the working skills
        raw_values = raw_b_df[metric].tolist()
        logger.info(f"DEBUG** Raw values: {raw_values}")
        chart_data = []
        
        for i, (category, raw_value) in enumerate(zip(categories, raw_values)):
            try:
                logger.info(f"DEBUG** Processing item {i}: category='{category}', raw_value='{raw_value}', type={type(raw_value)}")
                
                # Handle NaN values
                if pd.isna(raw_value):
                    logger.info(f"DEBUG** Item {i}: NaN value, using 0")
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
                    y_value = float(raw_value) if isinstance(raw_value, (int, float)) else 0
                    logger.info(f"DEBUG** Item {i}: Percentage - formatted='{formatted_value}', y={y_value}")
                    chart_data.append({
                        "name": category,
                        "y": y_value,
                        "formatted": formatted_value
                    })
                else:
                    # For currency and regular numbers, use genpact formatting
                    if is_currency:
                        formatted_value = f"${genpact_format_number(raw_value)}"
                    else:
                        formatted_value = genpact_format_number(raw_value)
                    
                    y_value = float(raw_value) if isinstance(raw_value, (int, float)) else 0
                    logger.info(f"DEBUG** Item {i}: Number - formatted='{formatted_value}', y={y_value}")
                    chart_data.append({
                        "name": category,
                        "y": y_value,
                        "formatted": formatted_value
                    })
                    
            except Exception as e:
                logger.error(f"DEBUG** Error processing item {i}: {e}")
                # Fallback for any conversion issues
                chart_data.append({
                    "name": category,
                    "y": 0,
                    "formatted": "0"
                })

        logger.info(f"DEBUG** Final chart_data length: {len(chart_data)}")
        logger.info(f"DEBUG** Sample chart_data (first 3): {chart_data[:3]}")

        # Create Y-axis with M/K/B formatting by calculating ticks and labels
        max_value = max([item.get('y', 0) for item in chart_data if isinstance(item.get('y'), (int, float))]) if chart_data else 0
        min_value = min([item.get('y', 0) for item in chart_data if isinstance(item.get('y'), (int, float))]) if chart_data else 0
        
        logger.info(f"DEBUG** Y-axis range: {min_value} to {max_value}")
        
        if is_percentage:
            y_axis = [{"title": "", "labels": {"format": "{value:.1f}%"}}]
        elif is_currency and max_value >= 1000:
            # For currency values with large numbers, create custom tick positions and labels
            import math
            
            # Calculate better tick interval for 5-6 ticks total
            value_range = max_value - min_value
            target_ticks = 5
            raw_interval = value_range / target_ticks
            
            # Round interval to nice numbers
            if max_value >= 1000000000:
                # For billions, use 200M intervals
                tick_interval = 200000000  # 200M
            elif max_value >= 500000000:  
                # For 500M+, use 100M intervals
                tick_interval = 100000000  # 100M
            elif max_value >= 100000000:
                # For 100M+, use 50M intervals  
                tick_interval = 50000000   # 50M
            elif max_value >= 10000000:
                # For 10M+, use 10M intervals
                tick_interval = 10000000   # 10M
            elif max_value >= 1000000:
                # For 1M+, use 1M intervals
                tick_interval = 1000000    # 1M
            else:
                # For smaller values, use reasonable intervals
                tick_interval = max(1000, math.ceil(raw_interval / 1000) * 1000)
            
            # Create tick positions from 0 to a bit above max_value
            tick_positions = []
            tick_labels = []
            current_tick = 0
            max_tick = math.ceil(max_value / tick_interval) * tick_interval
            
            while current_tick <= max_tick:
                tick_positions.append(current_tick)
                if current_tick >= 1000000000:
                    tick_labels.append(f"${current_tick / 1000000000:.1f}B")
                elif current_tick >= 1000000:
                    tick_labels.append(f"${current_tick / 1000000:.0f}M")
                elif current_tick >= 100000:
                    tick_labels.append(f"${current_tick / 1000:.0f}K")
                elif current_tick >= 1000:
                    tick_labels.append(f"${current_tick / 1000:.0f}K")
                else:
                    tick_labels.append(f"${current_tick:.0f}")
                current_tick += tick_interval
            
            logger.info(f"DEBUG** Tick interval: {tick_interval}")
            logger.info(f"DEBUG** Tick positions: {tick_positions}")
            logger.info(f"DEBUG** Tick labels: {tick_labels}")
            
            y_axis = [{
                "title": "",
                "tickPositions": tick_positions,
                "categories": tick_labels,
                "labels": {"enabled": True}
            }]
        else:
            # For other values, use simple formatting
            if is_currency:
                y_axis = [{"title": "", "labels": {"format": "${value:.0f}"}}]
            else:
                y_axis = [{"title": "", "labels": {"format": "{value:.0f}"}}]
        
        # Build series data with better color palette - remove JS formatters
        data = [{
            "name": metric,
            "data": chart_data,
            "dataLabels": {
                "enabled": False
            },
            "tooltip": {
                "pointFormat": "<b>{series.name}</b>: {point.formatted}"
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

        chart_result = {
            "chart_categories": categories,
            "chart_y_axis": y_axis,
            "chart_title": "",
            "chart_data": data
        }
        
        logger.info(f"DEBUG** Final chart result keys: {chart_result.keys()}")
        logger.info(f"DEBUG** Chart categories count: {len(categories)}")
        logger.info(f"DEBUG** Chart data series count: {len(data)}")
        logger.info(f"DEBUG** Y-axis config: {y_axis}")
        logger.info(f"DEBUG** Full chart_data structure: {data}")
        logger.info(f"DEBUG** Chart data first point: {data[0]['data'][0] if data and data[0]['data'] else 'NO DATA'}")
        logger.info(f"DEBUG** Colors config: {data[0].get('colors', 'NO COLORS') if data else 'NO DATA ARRAY'}")
        logger.info(f"DEBUG** ColorByPoint: {data[0].get('colorByPoint', 'NOT SET') if data else 'NO DATA ARRAY'}")
        logger.info(f"DEBUG** Finished _create_breakout_chart_vars successfully")
        
        return chart_result
    
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