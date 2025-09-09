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
        
        # Check for Previous period data to create grouped chart
        previous_metric = metric.replace("(Current)", "(Previous)")
        has_previous = previous_metric in raw_b_df.columns
        
        logger.info(f"DEBUG** Previous metric: {previous_metric}, has_previous: {has_previous}")
        
        # Prepare Current data
        current_values = raw_b_df[metric].tolist()
        logger.info(f"DEBUG** Current values: {current_values}")
        current_data = []
        
        # Prepare Previous data if available
        previous_data = []
        if has_previous:
            previous_values = raw_b_df[previous_metric].tolist()
            logger.info(f"DEBUG** Previous values: {previous_values}")
        
        for i, category in enumerate(categories):
            try:
                logger.info(f"DEBUG** Processing item {i}: category='{category}'")
                
                # Process Current values
                current_value = current_values[i]
                if pd.isna(current_value):
                    current_formatted = "N/A"
                    current_y = 0
                else:
                    if is_percentage:
                        current_formatted = f"{current_value:.1f}%" if isinstance(current_value, (int, float)) else str(current_value)
                        current_y = float(current_value) if isinstance(current_value, (int, float)) else 0
                    else:
                        if is_currency:
                            current_formatted = f"${genpact_format_number(current_value)}"
                        else:
                            current_formatted = genpact_format_number(current_value)
                        current_y = float(current_value) if isinstance(current_value, (int, float)) else 0
                
                current_data.append({
                    "name": category,
                    "y": current_y,
                    "formatted": current_formatted
                })
                
                # Process Previous values if available
                if has_previous:
                    previous_value = previous_values[i]
                    if pd.isna(previous_value):
                        previous_formatted = "N/A"  
                        previous_y = 0
                    else:
                        if is_percentage:
                            previous_formatted = f"{previous_value:.1f}%" if isinstance(previous_value, (int, float)) else str(previous_value)
                            previous_y = float(previous_value) if isinstance(previous_value, (int, float)) else 0
                        else:
                            if is_currency:
                                previous_formatted = f"${genpact_format_number(previous_value)}"
                            else:
                                previous_formatted = genpact_format_number(previous_value)
                            previous_y = float(previous_value) if isinstance(previous_value, (int, float)) else 0
                    
                    previous_data.append({
                        "name": category,
                        "y": previous_y,
                        "formatted": previous_formatted
                    })
                
                logger.info(f"DEBUG** Item {i}: current='{current_formatted}', previous='{previous_formatted if has_previous else 'N/A'}'")
                
            except Exception as e:
                logger.error(f"DEBUG** Error processing item {i}: {e}")
                # Fallback for any conversion issues
                current_data.append({
                    "name": category,
                    "y": 0,
                    "formatted": "0"
                })
                if has_previous:
                    previous_data.append({
                        "name": category, 
                        "y": 0,
                        "formatted": "0"
                    })
        
        # Use current_data for axis scaling calculations
        chart_data = current_data

        logger.info(f"DEBUG** Final chart_data length: {len(chart_data)}")
        logger.info(f"DEBUG** Sample chart_data (first 3): {chart_data[:3]}")

        # Create Y-axis with M/K/B formatting by calculating ticks and labels
        # Consider both Current and Previous data for scaling
        all_values = [item.get('y', 0) for item in current_data if isinstance(item.get('y'), (int, float))]
        if has_previous and previous_data:
            all_values.extend([item.get('y', 0) for item in previous_data if isinstance(item.get('y'), (int, float))])
        
        max_value = max(all_values) if all_values else 0
        min_value = min(all_values) if all_values else 0
        
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
            
            # Avoid JavaScript formatters - use simple axis configuration with manual scaling
            # Scale the Y values to show in millions for readability
            scaled_max = max_value / 1000000  # Convert to millions
            
            if scaled_max <= 500:
                # For values up to 500M, use 100M intervals
                y_axis = [{
                    "title": "",
                    "min": 0,
                    "max": math.ceil(scaled_max / 100) * 100,
                    "tickInterval": 100,
                    "labels": {"format": "${value}M"}
                }]
            else:
                # For values above 500M, use 200M intervals  
                y_axis = [{
                    "title": "",
                    "min": 0,
                    "max": math.ceil(scaled_max / 200) * 200, 
                    "tickInterval": 200,
                    "labels": {"format": "${value}M"}
                }]
            
            # Scale down both current and previous data to match the axis  
            for item in current_data:
                if isinstance(item.get('y'), (int, float)):
                    item['y'] = item['y'] / 1000000  # Convert to millions
            
            if has_previous and previous_data:
                for item in previous_data:
                    if isinstance(item.get('y'), (int, float)):
                        item['y'] = item['y'] / 1000000  # Convert to millions
            
            logger.info(f"DEBUG** Scaled current data (first 3): {current_data[:3]}")
            if has_previous:
                logger.info(f"DEBUG** Scaled previous data (first 3): {previous_data[:3]}")
            logger.info(f"DEBUG** Y-axis config: {y_axis}")
        else:
            # For other values, use simple formatting
            if is_currency:
                y_axis = [{"title": "", "labels": {"format": "${value:.0f}"}}]
            else:
                y_axis = [{"title": "", "labels": {"format": "{value:.0f}"}}]
        
        # Build series data - create separate series for Current and Previous
        data = []
        
        # Current series
        current_series = {
            "name": "Current",
            "data": current_data,
            "color": "#2E86C1",  # Professional blue
            "dataLabels": {
                "enabled": False
            },
            "tooltip": {
                "pointFormat": "<b>{series.name}</b>: {point.formatted}"
            }
        }
        data.append(current_series)
        
        # Previous series (if available)
        if has_previous and previous_data:
            previous_series = {
                "name": "Previous", 
                "data": previous_data,
                "color": "#95A5A6",  # Light gray for previous
                "dataLabels": {
                    "enabled": False
                },
                "tooltip": {
                    "pointFormat": "<b>{series.name}</b>: {point.formatted}"
                }
            }
            data.append(previous_series)
        
        logger.info(f"DEBUG** Created {len(data)} series: Current" + (", Previous" if has_previous else ""))

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