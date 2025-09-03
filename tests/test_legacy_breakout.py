from dataclasses import dataclass
from typing import Dict, List
from enum import Enum
from dimension_breakout import simple_breakout
from skill_framework import ExitFromSkillException, SkillInput
from skill_framework.preview import preview_skill
from dataset_definitions.genpact_insurance import GenpactInsuranceTestColumnNames


class LegacyBreakoutParameters(Enum):
    """Parameter names for legacy breakout skill with clean reference system"""
    metrics = "metrics"
    breakouts = "breakouts"
    periods = "periods"
    limit_n = "limit_n"
    growth_type = "growth_type"
    growth_trend = "growth_trend"
    other_filters = "other_filters"
    calculated_metric_filters = "calculated_metric_filters"
    max_prompt = "max_prompt"
    insight_prompt = "insight_prompt"
    table_viz_layout = "table_viz_layout"
    bridge_chart_viz_layout = "bridge_chart_viz_layout"


@dataclass
class LegacyBreakoutCommonParametersConfig:
    """Configuration for common parameter testing using pasta_v9 dataset"""
    metric_1: str
    metric_2: str
    breakout_1: str
    breakout_2: str
    period_filter: str
    filter_1: dict
    filter_2: dict
    growth_type_yoy: str = "Y/Y"
    growth_type_pop: str = "P/P"
    growth_type_none: str = "None"
    growth_trend_fastest_growing: str = "fastest growing"
    growth_trend_highest_growing: str = "highest growing"
    growth_trend_highest_declining: str = "highest declining"
    growth_trend_fastest_declining: str = "fastest declining"
    growth_trend_smallest_overall: str = "smallest overall"
    growth_trend_biggest_overall: str = "biggest overall"


GenpactInsuranceLegacyBreakoutCommonParametersConfig = LegacyBreakoutCommonParametersConfig(
    metric_1=GenpactInsuranceTestColumnNames.CLAIMS_EXPENSE.value,
    metric_2=GenpactInsuranceTestColumnNames.COMBINED_RATIO.value,
    breakout_1=GenpactInsuranceTestColumnNames.COUNTRY.value,
    breakout_2=GenpactInsuranceTestColumnNames.DISTRIBUTION_CHANNEL.value,
    period_filter="2024",
    filter_1={"dim": GenpactInsuranceTestColumnNames.GEO.value, "op": "=", "val": GenpactInsuranceTestColumnNames.GEO__EUROPE.value},
    filter_2={"dim": GenpactInsuranceTestColumnNames.LINE_OF_BUSINESS.value, "op": "=", "val": GenpactInsuranceTestColumnNames.LINE_OF_BUSINESS__GROUP.value}
)


@dataclass
class LegacyBreakoutGuardrailsConfig:
    """Configuration for testing guardrails and edge cases"""
    invalid_metric: str = "invalid_metric"
    invalid_metric_from_pasta: str = "invalid_metric"  # Not a valid metric for legacy breakout
    empty_metrics: List[str] = None
    
    def __post_init__(self):
        if self.empty_metrics is None:
            self.empty_metrics = []


GenpactInsuranceLegacyBreakoutGuardrailsConfig = LegacyBreakoutGuardrailsConfig()


class TestLegacyBreakout:
    """Base test class with helper methods for legacy breakout testing"""

    def _run_legacy_breakout(self, parameters: Dict, preview: bool = False):
        skill_input: SkillInput = simple_breakout.create_input(arguments=parameters)
        out = simple_breakout(skill_input)
        if preview or getattr(self, 'preview', False):
            preview_skill(simple_breakout, out)
        return out

    def _assert_legacy_breakout_runs_with_error(self, parameters: Dict, expected_exception):
        try:
            self._run_legacy_breakout(parameters, preview=False)
            assert False, f"Expected exception but skill ran successfully"
        except Exception as e:
            assert isinstance(e, expected_exception), f"Expected {expected_exception}, got {type(e).__name__}"

    def _assert_legacy_breakout_runs_without_errors(self, parameters: Dict, preview: bool = False):
        self._run_legacy_breakout(parameters, preview=preview)
        assert True


class TestLegacyBreakoutCommonParameters(TestLegacyBreakout):
    """Test the legacy breakout skill with common parameters to verify functionality"""

    config = GenpactInsuranceLegacyBreakoutCommonParametersConfig
    preview = False

    def test_single_metric_with_breakout(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1]
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_single_metric_with_period_and_breakout(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.periods.value: [self.config.period_filter],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1]
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_single_metric_with_growth_type_yoy(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.periods.value: [self.config.period_filter],
            LegacyBreakoutParameters.growth_type.value: self.config.growth_type_yoy
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_single_metric_with_growth_type_pop(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.periods.value: [self.config.period_filter],
            LegacyBreakoutParameters.growth_type.value: self.config.growth_type_pop
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_single_metric_with_growth_trend_fastest_growing(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.periods.value: [self.config.period_filter],
            LegacyBreakoutParameters.growth_type.value: self.config.growth_type_yoy,
            LegacyBreakoutParameters.growth_trend.value: self.config.growth_trend_fastest_growing
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_single_metric_with_growth_trend_highest_declining(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.periods.value: [self.config.period_filter],
            LegacyBreakoutParameters.growth_type.value: self.config.growth_type_yoy,
            LegacyBreakoutParameters.growth_trend.value: self.config.growth_trend_highest_declining
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_single_metric_with_filter(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.other_filters.value: [self.config.filter_1]
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_single_metric_with_limit_n(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.limit_n.value: 5
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_single_metric_with_growth_type_none(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.growth_type.value: self.config.growth_type_none
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_growth_trend_biggest_overall(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.growth_trend.value: self.config.growth_trend_biggest_overall
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_growth_trend_smallest_overall(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.growth_trend.value: self.config.growth_trend_smallest_overall
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_multiple_metrics_with_breakout(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1, self.config.metric_2],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1]
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_multiple_metrics_with_multiple_breakouts(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1, self.config.metric_2],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1, self.config.breakout_2]
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_complex_parameter_combination(self):
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1, self.config.metric_2],
            LegacyBreakoutParameters.periods.value: [self.config.period_filter],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1, self.config.breakout_2],
            LegacyBreakoutParameters.growth_type.value: self.config.growth_type_yoy,
            LegacyBreakoutParameters.growth_trend.value: self.config.growth_trend_fastest_growing,
            LegacyBreakoutParameters.other_filters.value: [self.config.filter_1],
            LegacyBreakoutParameters.limit_n.value: 15
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_calculated_metric_filters_basic(self):
        calculated_filters = [
            {
                "metric": self.config.metric_1,
                "computation": "growth",
                "operator": ">",
                "value": 0,
                "scale": "percentage"
            }
        ]
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.periods.value: [self.config.period_filter],
            LegacyBreakoutParameters.growth_type.value: self.config.growth_type_yoy,
            LegacyBreakoutParameters.calculated_metric_filters.value: calculated_filters
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)

    def test_bridge_chart_generation(self):
        """Test that bridge chart is generated with single metric, breakout, and growth comparison"""
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.periods.value: ["2022", "2021"],
            LegacyBreakoutParameters.growth_type.value: self.config.growth_type_yoy
        }
        self._assert_legacy_breakout_runs_without_errors(parameters)


class TestLegacyBreakoutGuardrails(TestLegacyBreakout):
    """Test guardrails and error conditions for legacy breakout skill"""

    config = GenpactInsuranceLegacyBreakoutCommonParametersConfig
    guardrail_config = GenpactInsuranceLegacyBreakoutGuardrailsConfig
    preview = False

    def test_no_metrics_provided(self):
        """Test that skill fails when no metrics are provided"""
        parameters = {
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1]
        }
        self._assert_legacy_breakout_runs_with_error(parameters, ExitFromSkillException)

    def test_empty_metrics_list(self):
        """Test that skill fails when empty metrics list is provided"""
        parameters = {
            LegacyBreakoutParameters.metrics.value: self.guardrail_config.empty_metrics,
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1]
        }
        self._assert_legacy_breakout_runs_with_error(parameters, ExitFromSkillException)

    def test_invalid_metric_completely_unknown(self):
        """Test that skill fails with completely unknown metric"""
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.guardrail_config.invalid_metric],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1]
        }
        self._assert_legacy_breakout_runs_with_error(parameters, ExitFromSkillException)

    def test_invalid_metric_from_pasta_dataset(self):
        """Test that skill fails with acv_share (exists in pasta but not supported by legacy breakout)"""
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.guardrail_config.invalid_metric_from_pasta],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1]
        }
        self._assert_legacy_breakout_runs_with_error(parameters, ExitFromSkillException)

    def test_growth_type_without_periods(self):
        """Test that growth_type without periods fails appropriately"""
        parameters = {
            LegacyBreakoutParameters.metrics.value: [self.config.metric_1],
            LegacyBreakoutParameters.breakouts.value: [self.config.breakout_1],
            LegacyBreakoutParameters.growth_type.value: self.config.growth_type_yoy
            # Intentionally missing periods
        }
        self._assert_legacy_breakout_runs_with_error(parameters, ExitFromSkillException)
