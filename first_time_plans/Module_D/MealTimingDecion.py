from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MealDetails(BaseModel):
    """Detailed information about a specific meal."""
    meal_name: str = Field(..., description="Name of the meal (e.g., 'Breakfast', 'Pre-workout meal')")
    timing: str = Field(..., description="Recommended timing (e.g., '7:00 AM', '1-2 hours before training')")
    calorie_allocation: int = Field(..., description="Calories allocated to this meal")
    protein: int = Field(..., description="Protein in grams")
    carbohydrates: int = Field(..., description="Carbohydrates in grams")
    fats: int = Field(..., description="Fats in grams")
    hydration: str = Field(..., description="Fluid recommendations")
    primary_purpose: str = Field(..., description="Main nutritional purpose of this meal")
    food_suggestions: List[str] = Field(..., description="Suggested food sources")
    notes: Optional[str] = Field(None, description="Additional considerations for this meal")

class TrainingDayPlan(BaseModel):
    """Complete meal timing plan for training days."""
    day_type: str = Field(..., description="Type of training day (e.g., 'Upper Body Day', 'Rest Day')")
    daily_macronutrient_targets: Dict[str, int] = Field(..., description="Daily macro targets in grams")
    meal_schedule: List[MealDetails] = Field(..., description="Detailed meal timing and composition")
    pre_workout_strategy: str = Field(..., description="Specific pre-workout nutrition approach")
    intra_workout_strategy: Optional[str] = Field(None, description="Intra-workout nutrition if applicable")
    post_workout_strategy: str = Field(..., description="Post-workout nutrition approach")
    scientific_rationale: str = Field(..., description="Scientific basis for this meal timing approach")

class NutrientTimingPrinciples(BaseModel):
    """Core scientific principles guiding the meal timing recommendations."""
    protein_distribution: str = Field(..., description="Approach to protein distribution throughout the day")
    carbohydrate_periodization: str = Field(..., description="Strategy for carbohydrate timing")
    fat_timing_considerations: str = Field(..., description="Guidelines for fat consumption timing")
    workout_nutrition_science: str = Field(..., description="Scientific basis for workout nutrition")
    circadian_considerations: str = Field(..., description="How circadian rhythms influence meal timing")

class ImplementationGuidelines(BaseModel):
    """Practical guidelines for implementing the meal timing plan."""
    meal_preparation_strategies: List[str] = Field(..., description="Strategies for meal prep and planning")
    dining_out_recommendations: List[str] = Field(..., description="Guidelines for restaurant eating")
    tracking_recommendations: str = Field(..., description="Approach to tracking nutrition")
    adherence_strategies: List[str] = Field(..., description="Strategies to improve adherence")
    adaptation_timeline: str = Field(..., description="Expected timeline for adaptation to plan")

class MealTimingRecommendation(BaseModel):
    """Complete meal timing recommendation plan."""
    client_name: str = Field(..., description="Client's name")
    caloric_targets: Dict[str, int] = Field(..., description="Daily caloric targets")
    training_day_plans: List[TrainingDayPlan] = Field(..., description="Meal timing plans for different day types")
    scientific_principles: NutrientTimingPrinciples = Field(..., description="Scientific principles behind recommendations")
    individual_adaptations: List[str] = Field(..., description="Client-specific adaptations to standard protocols")
    implementation_guidelines: ImplementationGuidelines = Field(..., description="Practical implementation guidance")
    progress_monitoring: List[str] = Field(..., description="Metrics to track for effectiveness")
    adjustment_protocols: str = Field(..., description="Protocol for adjusting the plan based on results")

class MealTimingDecisionNode:
    """
    Determines optimal meal timing strategies based on client data, training schedule, and nutritional goals.
    
    This class uses scientific principles and LLM-driven decision process to
    generate personalized meal timing recommendations that optimize nutrient partitioning,
    training performance, and recovery.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the MealTimingDecisionNode with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self,
        macro_plan: Dict[str, Any],
        split_recommendation: Dict[str, Any],
        client_data: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal meal timing strategies.
        
        This method integrates data from multiple analysis modules to develop
        appropriate meal timing recommendations, considering:
        - Macronutrient targets and distribution
        - Training split and workout timing
        - Client lifestyle and schedule
        - Recovery capacity and needs
        
        Args:
            macro_plan: Macronutrient distribution plan
            split_recommendation: Training split recommendation
            client_data: Raw client profile data
            goal_analysis: Client goals analysis
            recovery_analysis: Recovery capacity analysis
            
        Returns:
            A dictionary containing structured meal timing recommendations
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_meal_timing_schema(
                macro_plan, split_recommendation, client_data, goal_analysis, recovery_analysis
            )
            
            return {
                "meal_timing_recommendation": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining meal timing recommendations: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in meal timing determination.
        
        The system message establishes the context and criteria for determining
        optimal meal timing according to scientific principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a nutrient timing specialist with expertise in sports nutrition and chronobiology. "
            "Your task is to develop a personalized meal timing strategy that optimizes nutrient partitioning, "
            "training performance, and recovery based on the client's training schedule, goals, and lifestyle.\n\n"
            
            "Apply these scientific principles when determining meal timing strategies:\n"
            "1. **Protein Distribution**: Optimal muscle protein synthesis occurs with protein doses of ~0.3g/kg "
            "body weight distributed across 4-6 meals at 3-5 hour intervals.\n"
            "2. **Carbohydrate Timing**: Strategic carbohydrate placement around training sessions improves "
            "performance, glycogen replenishment, and recovery.\n"
            "3. **Periworkout Nutrition**: Pre-workout meals 1-3 hours before training with protein and carbs; "
            "post-workout nutrition within 30-60 minutes with focus on rapid absorption.\n"
            "4. **Rest Day Adjustments**: Modified macronutrient distribution on non-training days with reduced "
            "carbohydrate intake and maintained protein intake.\n"
            "5. **Circadian Optimization**: Alignment of meal timing with circadian rhythms for optimal metabolic "
            "function and hormone regulation.\n"
            "6. **Individual Adaptations**: Customizations based on training schedule, sleep patterns, digestion, "
            "and personal preferences.\n\n"
            
            "Your recommendation should include detailed meal-by-meal breakdowns for different training days, "
            "scientific rationale, and practical implementation guidelines that respect the client's lifestyle and preferences."
        )

    def _determine_meal_timing_schema(
        self,
        macro_plan: Dict[str, Any],
        split_recommendation: Dict[str, Any],
        client_data: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine meal timing recommendations using Pydantic schema validation.
        
        Args:
            macro_plan: Macronutrient distribution plan
            split_recommendation: Training split recommendation
            client_data: Raw client profile data
            goal_analysis: Client goals analysis
            recovery_analysis: Recovery capacity analysis
            
        Returns:
            Structured meal timing recommendation as a Pydantic model
        """
        # Extract relevant data for prompt construction
        personal_info = client_data.get("personal_info", {}).get("data", {})
        name = personal_info.get("name", "Client")
        
        nutrition_info = client_data.get("nutrition", {}).get