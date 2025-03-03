from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MealComplianceMetrics(BaseModel):
    """Metrics for measuring meal plan compliance."""
    overall_adherence_percentage: float = Field(..., description="Overall percentage of meal plan compliance")
    protein_target_adherence: float = Field(..., description="Percentage of protein target achieved")
    carbs_target_adherence: float = Field(..., description="Percentage of carbohydrate target achieved")
    fat_target_adherence: float = Field(..., description="Percentage of fat target achieved")
    calorie_target_adherence: float = Field(..., description="Percentage of calorie target achieved")
    meal_timing_adherence: float = Field(..., description="Percentage adherence to scheduled meal times")
    consistent_days: int = Field(..., description="Number of days with high compliance")
    inconsistent_days: int = Field(..., description="Number of days with low compliance")

class MealAdherenceItem(BaseModel):
    """Analysis of adherence for an individual meal or meal component."""
    meal_name: str = Field(..., description="Name of the meal (e.g., Breakfast, Lunch, Post-Workout)")
    scheduled_time: str = Field(..., description="Scheduled time for the meal")
    average_actual_time: Optional[str] = Field(None, description="Average actual time the meal was consumed")
    compliance_rate: float = Field(..., description="Percentage compliance for this specific meal")
    common_substitutions: List[str] = Field(..., description="Frequently used food substitutions for this meal")
    nutrition_impact: str = Field(..., description="Impact of adherence/non-adherence on nutrition targets")

class MealPlanAdherenceAnalysis(BaseModel):
    """Comprehensive analysis of client's adherence to their meal plan."""
    compliance_metrics: MealComplianceMetrics = Field(..., description="Quantitative meal compliance metrics")
    meal_specific_adherence: List[MealAdherenceItem] = Field(..., description="Adherence analysis for each meal")
    training_vs_non_training_adherence: str = Field(..., description="Comparison of adherence on training vs. non-training days")
    most_challenging_meals: List[str] = Field(..., description="Meals with lowest adherence rates")
    most_consistent_meals: List[str] = Field(..., description="Meals with highest adherence rates")
    adherence_trends: str = Field(..., description="Observed trends in meal plan adherence over time")
    hunger_satiety_observations: str = Field(..., description="Observations about hunger and satiety levels")
    practical_challenges: List[str] = Field(..., description="Practical challenges affecting meal plan adherence")
    successful_strategies: List[str] = Field(..., description="Strategies that have improved adherence")

class MealAdherenceExtractor:
    """
    Extracts and analyzes client meal plan adherence data.
    
    This class processes meal plan data alongside daily reports to evaluate how well
    a client has adhered to their prescribed nutrition plan, identifying patterns,
    challenges, and successful strategies.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the MealAdherenceExtractor with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def extract_meal_adherence(self, meal_plan_data: Dict[str, Any], daily_reports: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Process meal plan data and daily reports to analyze adherence.
        
        This method evaluates how well a client has followed their prescribed meal plan
        by comparing actual reported intake from daily reports against the prescribed plan.
        
        Args:
            meal_plan_data: The client's prescribed meal plan
            daily_reports: Daily nutrition and meal timing reports from the client
            
        Returns:
            A dictionary containing structured meal adherence analysis
        """
        try:
            # Process using the schema-based approach
            schema_result = self._analyze_meal_adherence_schema(meal_plan_data, daily_reports)
            
            return {
                "meal_adherence_analysis": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error analyzing meal adherence: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in meal adherence analysis.
        
        The system message establishes the context and criteria for analyzing
        meal plan adherence according to nutritional science principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a nutrition specialist with expertise in dietary compliance analysis. "
            "Your task is to evaluate how well a client has adhered to their prescribed meal plan "
            "based on their daily reports and the original meal plan.\\n\\n"
            
            "Apply these principles when analyzing meal adherence:\\n"
            "1. **Macro Compliance**: Compare actual vs. target intake for protein, carbs, fats, and total calories.\\n"
            "2. **Timing Adherence**: Assess whether meals were consumed at prescribed times.\\n"
            "3. **Meal Composition**: Evaluate adherence to prescribed food choices and portion sizes.\\n"
            "4. **Pattern Recognition**: Identify consistent patterns of adherence or non-adherence.\\n"
            "5. **Contextual Analysis**: Consider training days vs. non-training days differences.\\n"
            "6. **Practical Challenges**: Identify logistical or lifestyle factors affecting adherence.\\n"
            "7. **Successful Strategies**: Highlight approaches that have improved adherence.\\n\\n"
            
            "Your analysis should be balanced, recognizing both areas of strong compliance "
            "and opportunities for improvement, with practical insights that can guide plan adjustments."
        )
    
    def _analyze_meal_adherence_schema(
        self,
        meal_plan_data: Dict[str, Any],
        daily_reports: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze meal adherence using Pydantic schema validation.
        
        Args:
            meal_plan_data: The client's prescribed meal plan
            daily_reports: Daily nutrition and meal timing reports from the client
            
        Returns:
            Structured meal adherence analysis as a Pydantic model
        """
        # Extract relevant data for prompt construction
        daily_reports = daily_reports or []
        
        # Extract meal plan details
        plan_name = meal_plan_data.get("name", "Unnamed Plan")
        training_day_meals = meal_plan_data.get("trainingDayMeals", [])
        non_training_day_meals = meal_plan_data.get("nonTrainingDayMeals", [])
        total_nutrition = meal_plan_data.get("totalDailyNutrition", {})
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Analyze this client's meal plan adherence based on their prescribed meal plan and daily reports. "
            "Evaluate macro compliance, meal timing, food choices, and identify patterns of adherence.\\n\\n"
            
            f"MEAL PLAN SUMMARY:\\n"
            f"- Plan name: {plan_name}\\n"
            f"- Daily target calories: {total_nutrition.get('calories', 'Unknown')}\\n"
            f"- Daily protein target: {total_nutrition.get('protein', 'Unknown')}g\\n"
            f"- Daily carbs target: {total_nutrition.get('carbohydrates', 'Unknown')}g\\n"
            f"- Daily fat target: {total_nutrition.get('fat', 'Unknown')}g\\n\\n"
            
            f"PRESCRIBED MEALS (TRAINING DAYS):\\n{self._format_meals(training_day_meals)}\\n\\n"
            f"PRESCRIBED MEALS (NON-TRAINING DAYS):\\n{self._format_meals(non_training_day_meals)}\\n\\n"
            
            f"DAILY REPORTS:\\n{self._format_daily_reports(daily_reports)}\\n\\n"
            
            "Your meal adherence analysis should include:\\n"
            "1. Overall compliance metrics for macros and timing\\n"
            "2. Specific adherence analysis for each prescribed meal\\n"
            "3. Comparison between training and non-training days\\n"
            "4. Identification of challenging and consistent meals\\n"
            "5. Practical challenges affecting adherence\\n"
            "6. Successful strategies that have improved adherence\\n\\n"
            
            "Create a complete meal adherence analysis with practical insights that can guide plan adjustments."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=MealPlanAdherenceAnalysis)
        return result
    
    def _format_meals(self, meals: List[Dict[str, Any]]) -> str:
        """
        Format meal data as a readable string for inclusion in prompts.
        
        Args:
            meals: List of meal dictionaries
            
        Returns:
            Formatted string representation
        """
        formatted = ""
        for i, meal in enumerate(meals, 1):
            name = meal.get("name", f"Meal {i}")
            time = meal.get("time", "Unspecified time")
            nutrition = meal.get("nutrition", {})
            
            formatted += f"  {name} ({time}):\\n"
            formatted += f"    - Calories: {nutrition.get('calories', 0)}\\n"
            formatted += f"    - Protein: {nutrition.get('protein', 0)}g\\n"
            formatted += f"    - Carbs: {nutrition.get('carbohydrates', 0)}g\\n"
            formatted += f"    - Fat: {nutrition.get('fat', 0)}g\\n"
            
            items = meal.get("items", [])
            if items:
                formatted += "    - Items:\\n"
                for item in items:
                    item_name = item.get("name", "Unknown item")
                    quantity = item.get("quantity", "")
                    formatted += f"      * {item_name} ({quantity})\\n"
        
        return formatted
    
    def _format_daily_reports(self, reports: List[Dict[str, Any]]) -> str:
        """
        Format daily report data as a readable string for inclusion in prompts.
        
        Args:
            reports: List of daily report dictionaries
            
        Returns:
            Formatted string representation
        """
        if not reports:
            return "No daily reports available."
        
        formatted = ""
        for report in reports:
            date = report.get("date", "Unknown date")
            day = report.get("day", "")
            formatted += f"  Day {day} ({date}):\\n"
            
            # Macro data
            macros = report.get("macros", {})
            formatted += f"    - Protein: {macros.get('proteins', 0)}g\\n"
            formatted += f"    - Carbs: {macros.get('carbs', 0)}g\\n"
            formatted += f"    - Fats: {macros.get('fats', 0)}g\\n"
            
            # Additional notes
            notes = report.get("additionalNotes", "")
            if notes:
                formatted += f"    - Notes: {notes}\\n"
            
            appetite = report.get("appetite", "")
            if appetite:
                formatted += f"    - Appetite: {appetite}\\n"
        
        return formatted
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """
        Format a dictionary as a readable string for inclusion in prompts.
        
        Args:
            data: Dictionary to format
            
        Returns:
            Formatted string representation
        """
        try:
            return json.dumps(data, indent=2)
        except:
            # Fallback for non-serializable objects
            return str(data)