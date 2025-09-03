from ar_analytics.legacy_breakout import BreakoutAnalysis
from analysis_class_overrides.insurance_utilities import InsuranceSharedFn

class InsuranceLegacyBreakout(BreakoutAnalysis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = InsuranceSharedFn()