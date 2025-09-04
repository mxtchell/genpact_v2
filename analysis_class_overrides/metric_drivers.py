from ar_analytics.driver_analysis import DriverAnalysis
from ar_analytics.metric_tree import MetricTreeAnalysis
from ar_analytics.breakout_drivers import BreakoutDrivers
from ar_analytics.helpers.utils import Connector
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

class InsuranceMetricTreeAnalysis(MetricTreeAnalysis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = InsuranceSharedFn()

class InsuranceBreakoutDrivers(BreakoutDrivers):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = InsuranceSharedFn()