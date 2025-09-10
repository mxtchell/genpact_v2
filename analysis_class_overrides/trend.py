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
        
        self.logger.info(f"DEBUG** Starting trend chart formatting enhancement")
        
        # Process each chart configuration
        for chart_name, chart_config in chart_vars.items():
            if "chart_y_axis" in chart_config:
                # Determine if this is currency or percentage
                is_currency = False
                is_percentage = False
                
                # Check the metric format
                for metric in self.metrics:
                    metric_format = self.format_dict.get(metric, "")
                    if "$" in metric_format:
                        is_currency = True
                    if "%" in metric_format:
                        is_percentage = True
                
                self.logger.info(f"DEBUG** Chart {chart_name}: is_currency={is_currency}, is_percentage={is_percentage}")
                
                # Get all data values to determine range
                all_values = []
                if "chart_data" in chart_config:
                    for series in chart_config["chart_data"]:
                        if "data" in series:
                            for point in series["data"]:
                                if isinstance(point, dict) and "y" in point:
                                    val = point["y"]
                                elif isinstance(point, (int, float)):
                                    val = point
                                else:
                                    continue
                                if pd.notna(val) and isinstance(val, (int, float)):
                                    all_values.append(val)
                
                if all_values:
                    max_value = max(all_values)
                    min_value = min(all_values)
                    self.logger.info(f"DEBUG** Chart {chart_name} Y-axis range: {min_value} to {max_value}")
                    
                    # Apply formatting based on data type
                    if is_percentage:
                        # For percentages, check if values are decimals that need conversion
                        if max_value <= 1:  # Values like 0.6312 need to be converted to 63.12
                            # Scale the data and update y-axis
                            if "chart_data" in chart_config:
                                for series in chart_config["chart_data"]:
                                    if "data" in series:
                                        for i, point in enumerate(series["data"]):
                                            if isinstance(point, dict) and "y" in point:
                                                series["data"][i]["y"] = point["y"] * 100
                                                if "formatted" not in series["data"][i]:
                                                    series["data"][i]["formatted"] = f"{point['y'] * 100:.2f}%"
                                            elif isinstance(point, (int, float)):
                                                series["data"][i] = point * 100
                        
                        chart_config["chart_y_axis"] = [{
                            "title": {"text": ""},
                            "labels": {"format": "{value:.1f}%"}
                        }]
                    
                    elif is_currency and max_value >= 1000:
                        # Apply M/K/B formatting for large currency values
                        scaled_max = max_value / 1000000  # Convert to millions
                        
                        if scaled_max <= 500:
                            y_axis_config = {
                                "title": {"text": ""},
                                "min": 0,
                                "max": math.ceil(scaled_max / 100) * 100,
                                "tickInterval": 100,
                                "labels": {"format": "${value}M"}
                            }
                        else:
                            y_axis_config = {
                                "title": {"text": ""},
                                "min": 0,
                                "max": math.ceil(scaled_max / 200) * 200,
                                "tickInterval": 200,
                                "labels": {"format": "${value}M"}
                            }
                        
                        # Scale the data to millions
                        if "chart_data" in chart_config:
                            for series in chart_config["chart_data"]:
                                if "data" in series:
                                    for i, point in enumerate(series["data"]):
                                        if isinstance(point, dict) and "y" in point:
                                            orig_value = point["y"]
                                            series["data"][i]["y"] = orig_value / 1000000
                                            if "formatted" not in series["data"][i]:
                                                series["data"][i]["formatted"] = f"${genpact_format_number(orig_value)}"
                                        elif isinstance(point, (int, float)):
                                            series["data"][i] = point / 1000000
                        
                        chart_config["chart_y_axis"] = [y_axis_config]
                        self.logger.info(f"DEBUG** Applied M/K/B formatting to chart {chart_name}")
        
        return chart_vars