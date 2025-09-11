from ar_analytics.trend import AdvanceTrend
from analysis_class_overrides.insurance_utilities import InsuranceSharedFn
import pandas as pd
import logging
import math

class InsuranceAdvanceTrend(AdvanceTrend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = InsuranceSharedFn()
        self.logger = logging.getLogger(__name__)
    
    def get_dynamic_layout_chart_vars(self):
        """Override to add M/K/B formatting to trend charts"""
        from genpact_formatting import genpact_format_number
        
        # Get the original chart vars from parent
        chart_vars = super().get_dynamic_layout_chart_vars()
        
        self.logger.info(f"DEBUG** Starting trend chart formatting enhancement for {list(chart_vars.keys())}")
        
        # Process each chart configuration
        for chart_name, chart_config in chart_vars.items():
            self.logger.info(f"DEBUG** Processing chart: {chart_name}")
            
            # Quick check for available env metrics
            env_metrics = getattr(self.env, 'metrics', None) if hasattr(self, 'env') else None
            self.logger.info(f"DEBUG** Available metrics from env: {env_metrics}")
                
            # Handle trend-specific chart structure with prefixes
            prefixes = ["absolute_", "growth_", "difference_"]
            processed_any = False
            
            for prefix in prefixes:
                series_key = f"{prefix}series"
                y_axis_key = f"{prefix}y_axis"
                
                if series_key in chart_config:
                    self.logger.info(f"DEBUG** Found {series_key} in chart {chart_name}")
                    
                    # Determine if this is currency or percentage by checking chart name or metric
                    is_currency = False
                    is_percentage = False
                    
                    # Try multiple ways to determine metric format
                    # Method 1: Check chart name for currency indicators
                    chart_name_lower = chart_name.lower()
                    if any(word in chart_name_lower for word in ['premium', 'revenue', 'sales', 'cost', 'expense', 'loss']):
                        is_currency = True
                        self.logger.info(f"DEBUG** Detected currency from chart name: {chart_name}")
                    elif any(word in chart_name_lower for word in ['rate', 'ratio', 'percent', '%']):
                        is_percentage = True  
                        self.logger.info(f"DEBUG** Detected percentage from chart name: {chart_name}")
                        
                    # Method 2: Check metric name if available
                    metric_name_key = f"{prefix}metric_name"
                    if metric_name_key in chart_config:
                        metric_name = str(chart_config[metric_name_key]).lower()
                        if any(word in metric_name for word in ['premium', 'revenue', 'sales', 'cost', 'expense', 'loss']):
                            is_currency = True
                            self.logger.info(f"DEBUG** Detected currency from metric name: {chart_config[metric_name_key]}")
                        elif any(word in metric_name for word in ['rate', 'ratio', 'percent', '%']):
                            is_percentage = True
                            self.logger.info(f"DEBUG** Detected percentage from metric name: {chart_config[metric_name_key]}")
                    
                    # Method 3: Try to get format from available attributes
                    try:
                        if hasattr(self, 'metric_cols'):
                            for metric in self.metric_cols:
                                if hasattr(self, 'format_dict') and metric in self.format_dict:
                                    metric_format = self.format_dict.get(metric, "")
                                    if "$" in metric_format:
                                        is_currency = True
                                    if "%" in metric_format:
                                        is_percentage = True
                    except Exception as e:
                        self.logger.info(f"DEBUG** Error checking metric formats: {e}")
                    
                    self.logger.info(f"DEBUG** Chart {chart_name} ({prefix}): is_currency={is_currency}, is_percentage={is_percentage}")
                    
                    # Get all data values to determine range from trend series
                    all_values = []
                    series_data = chart_config[series_key]
                    if isinstance(series_data, list):
                        for series in series_data:
                            if isinstance(series, dict) and "data" in series:
                                for point in series["data"]:
                                    if isinstance(point, dict) and "y" in point:
                                        val = point["y"]
                                    elif isinstance(point, (int, float)):
                                        val = point
                                    else:
                                        continue
                                    if pd.notna(val) and isinstance(val, (int, float)):
                                        all_values.append(val)
                    
                    self.logger.info(f"DEBUG** Found {len(all_values)} data values for {prefix} in chart {chart_name}")
                    if all_values:
                        self.logger.info(f"DEBUG** Value range: {min(all_values)} to {max(all_values)}")
                        
                        max_value = max(all_values)
                        min_value = min(all_values)
                        
                        # Apply formatting based on data type
                        if is_percentage:
                            self.logger.info(f"DEBUG** Applying percentage formatting for {prefix}")
                            # For percentages, check if values are decimals that need conversion
                            if max_value <= 1:  # Values like 0.6312 need to be converted to 63.12
                                # Scale the data and update y-axis
                                series_data = chart_config[series_key]
                                if isinstance(series_data, list):
                                    for series in series_data:
                                        if isinstance(series, dict) and "data" in series:
                                            for i, point in enumerate(series["data"]):
                                                if isinstance(point, dict) and "y" in point:
                                                    series["data"][i]["y"] = point["y"] * 100
                                                    if "formatted" not in series["data"][i]:
                                                        series["data"][i]["formatted"] = f"{point['y'] * 100:.2f}%"
                                                elif isinstance(point, (int, float)):
                                                    series["data"][i] = point * 100
                            
                            chart_config[y_axis_key] = [{
                                "title": {"text": ""},
                                "labels": {"format": "{value:.1f}%"}
                            }]
                            self.logger.info(f"DEBUG** Applied percentage formatting to {y_axis_key}")
                        
                        elif is_currency and max_value >= 1000:
                            self.logger.info(f"DEBUG** Applying currency M/K/B formatting for {prefix}")
                            # Apply M/K/B formatting for large currency values
                            scaled_max = max_value / 1000000  # Convert to millions
                            scaled_min = min_value / 1000000  # Convert to millions
                            
                            # For difference charts, allow negative values
                            if prefix == "difference_":
                                # Calculate symmetric range around zero for difference charts
                                abs_max = max(abs(scaled_max), abs(scaled_min))
                                if abs_max <= 500:
                                    axis_max = math.ceil(abs_max / 100) * 100
                                    y_axis_config = {
                                        "title": {"text": ""},
                                        "min": -axis_max,
                                        "max": axis_max,
                                        "tickInterval": 100,
                                        "labels": {"format": "${value}M"}
                                    }
                                else:
                                    axis_max = math.ceil(abs_max / 200) * 200
                                    y_axis_config = {
                                        "title": {"text": ""},
                                        "min": -axis_max,
                                        "max": axis_max,
                                        "tickInterval": 200,
                                        "labels": {"format": "${value}M"}
                                    }
                                self.logger.info(f"DEBUG** Applied symmetric Y-axis for difference chart: -{axis_max}M to {axis_max}M")
                            else:
                                # For absolute and growth charts, use dynamic range instead of starting from 0
                                # This prevents charts from looking flat when values are high (e.g., 1.9B-2.0B range)
                                data_range = scaled_max - scaled_min
                                
                                # Add padding above and below the data range (10% padding)
                                padding = data_range * 0.1
                                axis_min = max(0, scaled_min - padding)  # Don't go below 0 for absolute values
                                axis_max = scaled_max + padding
                                
                                # Round to nice intervals
                                if axis_max <= 500:
                                    axis_max = math.ceil(axis_max / 100) * 100
                                    axis_min = math.floor(axis_min / 100) * 100
                                    tick_interval = 100
                                else:
                                    axis_max = math.ceil(axis_max / 200) * 200
                                    axis_min = math.floor(axis_min / 200) * 200
                                    tick_interval = 200
                                
                                y_axis_config = {
                                    "title": {"text": ""},
                                    "min": axis_min,
                                    "max": axis_max,
                                    "tickInterval": tick_interval,
                                    "labels": {"format": "${value}M"}
                                }
                                self.logger.info(f"DEBUG** Applied dynamic Y-axis for {prefix} chart: ${axis_min}M to ${axis_max}M")
                            
                            # Scale the data to millions
                            series_data = chart_config[series_key]
                            if isinstance(series_data, list):
                                for series in series_data:
                                    if isinstance(series, dict) and "data" in series:
                                        for i, point in enumerate(series["data"]):
                                            if isinstance(point, dict) and "y" in point:
                                                orig_value = point["y"]
                                                series["data"][i]["y"] = orig_value / 1000000
                                                if "formatted" not in series["data"][i]:
                                                    series["data"][i]["formatted"] = f"${genpact_format_number(orig_value)}"
                                            elif isinstance(point, (int, float)):
                                                series["data"][i] = point / 1000000
                            
                            chart_config[y_axis_key] = [y_axis_config]
                            self.logger.info(f"DEBUG** Applied M/K/B formatting to {y_axis_key}")
                            processed_any = True
                        else:
                            self.logger.info(f"DEBUG** Skipping formatting for {prefix} - not currency or small currency values")
                    else:
                        self.logger.info(f"DEBUG** No data values found for {prefix}")
            
            if not processed_any:
                self.logger.info(f"DEBUG** No formatting applied to chart {chart_name}")
        
        return chart_vars