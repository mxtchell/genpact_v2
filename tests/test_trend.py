from dataclasses import dataclass
from typing import Dict, List
from trend import trend
from skill_framework import ExitFromSkillException, SkillInput
from skill_framework.preview import preview_skill
from dataset_definitions.genpact_insurance import GenpactInsuranceTestColumnNames

@dataclass
class TestTrendCommonParametersConfig:
    metric_1: str
    metric_2: str
    breakout_1: str
    breakout_2: str
    period_filter: str
    filter_1: dict
    filter_2: dict
    time_granularity_1: str = "month"
    time_granularity_2: str = "quarter"
    growth_type__yoy: str = "Y/Y"
    growth_type__pop: str = "P/P"

GenpactInsuranceTrendCommonParametersConfig = TestTrendCommonParametersConfig(
    metric_1=GenpactInsuranceTestColumnNames.CLAIMS_EXPENSE.value,
    metric_2=GenpactInsuranceTestColumnNames.COMBINED_RATIO.value,
    breakout_1=GenpactInsuranceTestColumnNames.COUNTRY.value,
    breakout_2=GenpactInsuranceTestColumnNames.DISTRIBUTION_CHANNEL.value,
    period_filter="2024",
    filter_1={"dim": GenpactInsuranceTestColumnNames.GEO.value, "op": "=", "val": GenpactInsuranceTestColumnNames.GEO__EUROPE.value},
    filter_2={"dim": GenpactInsuranceTestColumnNames.LINE_OF_BUSINESS.value, "op": "=", "val": GenpactInsuranceTestColumnNames.LINE_OF_BUSINESS__GROUP.value}
) 

@dataclass
class TestTrendGuardrailsConfig:
    """Configuration for testing guardrails and edge cases"""
    invalid_metric: str = "invalid_metric"
    invalid_growth_type: str = "invalid_growth"
    invalid_breakout: str = "invalid_breakout"
    empty_metrics: List[str] = None
    
    def __post_init__(self):
        if self.empty_metrics is None:
            self.empty_metrics = []

GenpactInsuranceTrendGuardrailsConfig = TestTrendGuardrailsConfig()

class TestTrend:

    def _run_trend(self, parameters: Dict, preview: bool = False):
        skill_input: SkillInput = trend.create_input(arguments=parameters)
        out = trend(skill_input)
        if preview or getattr(self, 'preview', False):
            preview_skill(trend, out)
        return out

    def _assert_trend_runs_with_error(self, parameters: Dict, expected_exception):
        try:
            self._run_trend(parameters, preview=False)
            assert False, f"Expected exception but skill ran successfully"
        except expected_exception as e:
            pass
        except Exception as e:
            assert False, f"Expected {expected_exception}, got {type(e).__name__}: {e}"

    def _assert_trend_runs_without_errors(self, parameters: Dict, preview: bool = False):
        self._run_trend(parameters, preview=preview)
        assert True

class TestTrendCommonParameters(TestTrend):
    """Test the trend skill with common parameters to verify functionality"""

    config = GenpactInsuranceTrendCommonParametersConfig
    preview = False

    def test_single_metric(self):
        parameters = {
            "metrics": [self.config.metric_1]
        }   
        self._assert_trend_runs_without_errors(parameters)

    def test_single_metric_with_period_and_yoy_growth_type(self):
        parameters = {
            "metrics": [self.config.metric_1],
            "periods": [self.config.period_filter],
            "growth_type": self.config.growth_type__yoy
        }
        self._assert_trend_runs_without_errors(parameters)

    def test_single_metric_with_period_and_pop_growth_type(self):
        parameters = {
            "metrics": [self.config.metric_1],
            "periods": [self.config.period_filter],
            "growth_type": self.config.growth_type__pop
        }
        self._assert_trend_runs_without_errors(parameters)

    def test_single_metric_with_period_and_breakout(self):
        parameters = {
            "metrics": [self.config.metric_1],
            "periods": [self.config.period_filter],
            "breakouts": [self.config.breakout_1]
        }
        self._assert_trend_runs_without_errors(parameters)

    def test_single_metric_with_period_and_filter(self):
        parameters = {
            "metrics": [self.config.metric_1],
            "periods": [self.config.period_filter],
            "other_filters": [self.config.filter_1]
        }
        self._assert_trend_runs_without_errors(parameters)

    def test_multiple_metrics(self):
        parameters = {
            "metrics": [self.config.metric_1, self.config.metric_2]
        }
        self._assert_trend_runs_without_errors(parameters)

    def test_multiple_metrics_with_period_and_growth_type(self):
        parameters = {
            "metrics": [self.config.metric_1, self.config.metric_2],
            "periods": [self.config.period_filter],
            "growth_type": self.config.growth_type__yoy
        }
        self._assert_trend_runs_without_errors(parameters)

    def test_complex_parameter_combination(self):
        parameters = {
            "metrics": [self.config.metric_1, self.config.metric_2],
            "periods": [self.config.period_filter],
            "breakouts": [self.config.breakout_1],
            "other_filters": [self.config.filter_1, self.config.filter_2],
            "growth_type": self.config.growth_type__yoy
        }
        self._assert_trend_runs_without_errors(parameters)

class TestTrendGuardrails(TestTrend):
    """Test guardrails and error conditions for trend skill"""

    config = GenpactInsuranceTrendCommonParametersConfig
    guardrail_config = GenpactInsuranceTrendGuardrailsConfig
    preview = False

    def test_no_metrics_provided(self):
        """Test that skill fails when no metrics are provided"""
        parameters = {}
        self._assert_trend_runs_with_error(parameters, ExitFromSkillException)

    def test_empty_metrics_list(self):
        """Test that skill fails when empty metrics list is provided"""
        parameters = {
            "metrics": self.guardrail_config.empty_metrics
        }
        self._assert_trend_runs_with_error(parameters, ExitFromSkillException)

    def test_invalid_metric_completely_unknown(self):
        """Test that skill fails with completely unknown metric"""
        parameters = {
            "metrics": [self.guardrail_config.invalid_metric]
        }
        self._assert_trend_runs_with_error(parameters, ExitFromSkillException)

    def test_invalid_growth_type_defaults_gracefully(self):
        """Test that invalid growth type either defaults or fails gracefully"""
        parameters = {
            "metrics": [self.config.metric_1],
            "periods": [self.config.period_filter],
            "growth_type": self.guardrail_config.invalid_growth_type
        }
        # This might pass if it defaults to a valid growth type, or fail - depends on implementation
        try:
            self._assert_trend_runs_without_errors(parameters)
        except AssertionError:
            self._assert_trend_runs_with_error(parameters, ExitFromSkillException)

    def test_invalid_breakout(self):
        """Test that skill fails with invalid breakout dimension"""
        parameters = {
            "metrics": [self.config.metric_1],
            "periods": [self.config.period_filter],
            "breakouts": [self.guardrail_config.invalid_breakout]
        }
        self._assert_trend_runs_with_error(parameters, ExitFromSkillException)

    def test_mixed_valid_invalid_metrics(self):
        """Test behavior with mix of valid and invalid metrics"""
        parameters = {
            "metrics": [self.config.metric_1, self.guardrail_config.invalid_metric]
        }
        self._assert_trend_runs_with_error(parameters, ExitFromSkillException)
