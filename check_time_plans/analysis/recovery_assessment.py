# temporay is stop both of the recoverly classes maybe in the futue I will be implenting them


from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SleepQualityInsight(BaseModel):
    """Detailed insight about sleep quality and patterns."""
    pattern_type: str = Field(..., description="Type of sleep pattern identified")
    description: str = Field(..., description="Description of the sleep pattern")
    impact_on_recovery: str = Field(..., description="Impact on overall recovery")
    physiological_explanation: str = Field(..., description="Physiological explanation of the pattern's impact")
    optimization_suggestions: List[str] = Field(..., description="Suggestions for optimizing this aspect of sleep")

class StressRecoveryInsight(BaseModel):
    """Insight about stress management and recovery relationship."""
    stress_pattern: str = Field(..., description="Identified stress pattern")
    recovery_impact: str = Field(..., description="Impact on recovery processes")
    physiological_pathway: str = Field(..., description="Physiological pathway of impact")
    adaptation_implications: str = Field(..., description="Implications for training adaptation")
    management_strategies: List[str] = Field(..., description="Stress management strategies")

class RecoveryCapacityAssessment(BaseModel):
    """Assessment of overall recovery capacity and limitations."""
    recovery_capacity_rating: float = Field(..., description="Overall recovery capacity rating (0-100)")
    limiting_factors: List[str] = Field(..., description="Primary factors limiting recovery capacity")
    hormonal_indicators: List[str] = Field(..., description="Potential hormonal indicators from recovery patterns")
    nervous_system_status: str = Field(..., description="Assessment of nervous system recovery status")
    metabolic_recovery_status: str = Field(..., description="Assessment of metabolic recovery status")
    recovery_reserve: str = Field(..., description="Assessment of recovery reserve capacity")

class RecoveryDeepAnalysis(BaseModel):
    """Comprehensive recovery analysis with physiological insights."""
    overall_recovery_score: float = Field(..., description="Overall recovery effectiveness score (0-100)")
    recovery_trend: str = Field(..., description="Trend in recovery metrics over time")
    sleep_quality_insights: List[SleepQualityInsight] = Field(..., description="Detailed insights about sleep quality")
    stress_recovery_insights: List[StressRecoveryInsight] = Field(..., description="Insights about stress-recovery relationship")
    recovery_capacity: RecoveryCapacityAssessment = Field(..., description="Assessment of recovery capacity")
    recovery_balance: str = Field(..., description="Assessment of balance between stress and recovery")
    recovery_consistency: str = Field(..., description="Assessment of day-to-day recovery consistency")


