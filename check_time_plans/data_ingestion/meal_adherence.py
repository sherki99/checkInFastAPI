from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MealComplianceMetrics(BaseModel):
    overall_adherence_percentage: float
    protein_target_adherence: float
    carbs_target_adherence: float
    fat_target_adherence: float
    calorie_target_adherence: float
    meal_timing_adherence: float
    consistent_days: int
    inconsistent_days: int

class MealAdherenceItem(BaseModel):
    meal_name: str
    scheduled_time: str
    average_actual_time: Optional[str] = None
    compliance_rate: float
    common_substitutions: List[str]
    nutrition_impact: str

class MealPlanAdherenceAnalysis(BaseModel):
    compliance_metrics: MealComplianceMetrics
    meal_specific_adherence: List[MealAdherenceItem]
    adherence_trends: str
    practical_challenges: List[str]
    successful_strategies: List[str]

class MealAdherenceExtractor:
    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client or BaseLLM()

    def extract_meal_adherence(self, meal_plan_data: Dict[str, Any], daily_reports: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        try:
            system_message = "Analyze client's meal adherence based on reports and prescribed plan."
            prompt = self._generate_prompt(meal_plan_data, daily_reports)
            result = self.llm_client.call_llm(prompt, system_message, schema=MealPlanAdherenceAnalysis)
            return {"meal_adherence_analysis": result}
        except Exception as e:
            logger.error(f"Error analyzing meal adherence: {str(e)}")
            return {"error": "Failed to analyze meal adherence"}

    def _generate_prompt(self, meal_plan_data: Dict[str, Any], daily_reports: Optional[List[Dict[str, Any]]] = None) -> str:
        daily_reports = daily_reports or []
        return (
            f"Meal Plan: {meal_plan_data.get('name', 'Unknown')}\n"
            f"Daily Nutrition Targets: {meal_plan_data.get('totalDailyNutrition', {})}\n"
            f"Daily Reports: {len(daily_reports)} entries\n"
            "Provide an adherence analysis including compliance metrics, trends, and challenges."
        )
