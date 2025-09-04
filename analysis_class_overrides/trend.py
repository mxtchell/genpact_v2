from ar_analytics.trend import AdvanceTrend
from analysis_class_overrides.insurance_utilities import InsuranceSharedFn

class InsuranceAdvanceTrend(AdvanceTrend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = InsuranceSharedFn()