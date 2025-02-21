from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class NutrientTimingWindow(BaseModel):
    """Specific timing window for nutrient intake."""
    window_name: str = Field(..., description="Name of this timing window (e.g., 'Pre-workout', 'Post-workout')")
    timing_description: str = Field(..., description="When this window occurs relative to training")
    duration: str = Field(..., description="Duration of this timing window")
    primary_purpose: str = Field(..., description="Physiological purpose of this timing window")
    protein_recommendation: str = Field(..., description="Protein intake recommendation during this window")
    carb_recommendation: str = Field(..., description="Carbohydrate intake recommendation during this window")
    fat_recommendation: str = Field(..., description="Fat intake recommendation during this window")
    hydration_recommendation: str = Field(..., description="Hydration recommendation during this window")
    ideal_food_sources: List[str] = Field(..., description="Optimal food choices for this window")
    scientific_rationale: str = Field(..., description="Research-based explanation for these recommendations")

class ScheduledMeal(BaseModel):
    """Details for a specific scheduled meal."""
    meal_name: str = Field(..., description="Name of the meal (e.g., 'Breakfast', 'Lunch')")
    recommended_timing: str = Field(..., description="Recommended time of day for this meal")
    purpose: str = Field(..., description="Primary nutritional purpose of this meal")
    macronutrient_composition: Dict[str, Any] = Field(..., description="Macronutrient targets for this meal")
    caloric_content: int = Field(..., description="Caloric target for this meal")
    meal_size_classification: str = Field(..., description="Size classification (Major/Minor)")
    hydration_recommendation: str = Field(..., description="Water intake with this meal")
    sample_meal_ideas: List[str] = Field(..., description="Example meal compositions that meet requirements")
    timing_flexibility: str = Field(..., description="How flexible the timing can be for this meal")

class TrainingDayMealPlan(BaseModel):
    """Complete meal plan for a training day."""
    day_type: str = Field(..., description="Type of training day (e.g., 'Upper Body', 'Lower Body', 'Rest')")
    training_time: str = Field(..., description="Time of day when training occurs")
    total_meals: int = Field(..., description="Total number of meals/snacks for this day")
    caloric_distribution: Dict[str, float] = Field(..., description="Percentage of calories at each meal")
    scheduled_meals: List[ScheduledMeal] = Field(..., description="Detailed plan for each meal")
    nutrient_timing_windows: List[NutrientTimingWindow] = Field(..., description="Critical nutrient timing windows")
    hydration_schedule: Dict[str, str] = Field(..., description="Timing and amounts for fluid intake")
    supplement_timing: Dict[str, str] = Field(..., description="Timing for any recommended supplements")

class MealTimingRecommendation(BaseModel):
    """Complete meal timing recommendation plan."""
    client_name: str = Field(..., description="Client's name")
    primary_goal: str = Field(..., description="Client's primary nutritional goal")
    training_day_plans: List[TrainingDayMealPlan] = Field(..., description="Meal plans for different training days")
    rest_day_plan: TrainingDayMealPlan = Field(..., description="Meal plan for rest days")
    meal_timing_principles: List[str] = Field(..., description="Key scientific principles guiding the timing recommendations")
    circadian_rhythm_considerations: str = Field(..., description="How the plan accounts for circadian biology")
    sleep_optimization_strategy: str = Field(..., description="Nutrition timing to support sleep quality")
    schedule_adaptation_guidelines: str = Field(..., description="How to adapt timing for schedule changes")
    meal_preparation_strategies: List[str] = Field(..., description="Practical implementation strategies")
    consistency_recommendations: str = Field(..., description="Guidance on maintaining consistent meal timing")

class MealTimingDecisionNode:
    """
    Determines optimal meal timing and nutrient distribution throughout the day
    based on the client's training schedule, macronutrient targets, and lifestyle.
    
    This class uses an LLM-driven decision process to establish precise meal timing
    recommendations that maximize nutrient utilization, training performance, and
    recovery while accommodating the client's daily schedule and preferences.
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
        macro_distribution: Dict[str, Any],
        split_recommendation: Dict[str, Any],
        profile_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal meal timing and nutrient distribution.
        
        This method integrates data from previous analysis modules to establish
        detailed meal timing recommendations considering:
        - Training schedule and workout timing
        - Macronutrient distribution requirements
        - Sleep schedule and circadian rhythm
        - Work/school schedule constraints
        - Digestive tolerance and preferences
        - Recovery capacity and needs
        
        Args:
            macro_distribution: Macronutrient distribution plan from previous node
            split_recommendation: Recommended training split and schedule
            profile_analysis: Client demographic and metrics analysis
            goal_analysis: Goal clarification analysis
            recovery_analysis: Recovery capacity and lifestyle analysis
            
        Returns:
            A dictionary containing structured meal timing recommendations
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_meal_timing_schema(
                macro_distribution, split_recommendation, profile_analysis, 
                goal_analysis, recovery_analysis
            )
            
            return {
                "meal_timing_recommendation": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining meal timing: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in meal timing decision-making.
        
        The system message establishes the context and criteria for determining
        optimal meal timing according to scientific principles of nutrient timing,
        chronobiology, and performance nutrition.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a nutrient timing specialist with expertise in sports nutrition, chronobiology, "
            "and performance optimization. Your task is to determine optimal meal timing and nutrient "
            "distribution throughout the day based on the client's training schedule, macronutrient targets, "
            "recovery capacity, and lifestyle factors.\n\n"
            
            "Apply these scientific principles when determining meal timing:\n"
            "1. **Peri-workout Nutrition**: Optimize pre-, intra-, and post-workout nutrition windows "
            "to maximize performance, minimize muscle protein breakdown, and enhance recovery.\n"
            "2. **Protein Distribution**: Distribute protein intake evenly across meals to maximize "
            "muscle protein synthesis, with appropriate leucine thresholds (~2.5-3g) per meal.\n"
            "3. **Carbohydrate Timing**: Prioritize carbohydrate intake around training sessions for "
            "glycogen replenishment and performance, with consideration for training intensity and duration.\n"
            "4. **Circadian Biology**: Align meal timing with circadian rhythm for optimal metabolic "
            "function, considering time-restricted feeding windows if appropriate.\n"
            "5. **Sleep Optimization**: Limit food intake 2-3 hours before sleep, with consideration "
            "for sleep-promoting nutrients if needed (e.g., casein protein, tryptophan-rich foods).\n"
            "6. **Gastric Emptying**: Account for gastric emptying rates of different macronutrients "
            "when timing meals around workouts and throughout the day.\n"
            "7. **Practical Adherence**: Balance physiological optimality with lifestyle factors and "
            "preferences to ensure long-term consistency.\n\n"
            
            "Your meal timing recommendations should include specific timing windows for each meal, "
            "nutrient composition for each meal, critical timing windows around workouts, and strategies "
            "for adapting the plan to accommodate schedule variations."
        )

    def _determine_meal_timing_schema(
        self,
        macro_distribution: Dict[str, Any],
        split_recommendation: Dict[str, Any],
        profile_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine meal timing using Pydantic schema validation.
        
        Args:
            macro_distribution: Macronutrient distribution plan
            split_recommendation: Recommended training split and schedule
            profile_analysis: Client demographic and metrics analysis
            goal_analysis: Goal clarification analysis
            recovery_analysis: Recovery capacity and lifestyle analysis
            
        Returns:
            Structured meal timing recommendation as a Pydantic model
        """
        # Extract relevant data from macro distribution
        macro_plan = macro_distribution.get("macro_distribution_plan", {})
        total_calories = macro_plan.get("total_daily_calories", 0)
        protein_strategy = macro_plan.get("protein_strategy", "")
        carb_strategy = macro_plan.get("carbohydrate_strategy", "")
        fat_strategy = macro_plan.get("fat_strategy", "")
        
        # Extract training split information
        split_schema = split_recommendation.get("split_recommendation_schema", {})
        split_name = split_schema.get("split_name", "")
        weekly_schedule = split_schema.get("weekly_schedule", {})
        
        # Extract client profile information
        standardized_profile = {}  # This would normally come from the full standardized profile
        wake_time = standardized_profile.get("lifestyle", {}).get("data", {}).get("wakeTime", "6:00 AM")
        bed_time = standardized_profile.get("lifestyle", {}).get("data", {}).get("bedTime", "10:00 PM")
        work_hours = standardized_profile.get("lifestyle", {}).get("data", {}).get("workHours", "")
        
        # Extract recovery information
        recovery_capacity = recovery_analysis.get("recovery_capacity", {})
        stress_level = recovery_capacity.get("stress_level", "")
        sleep_quality = recovery_capacity.get("sleep_quality", "")
        
        # Extract current meal timing patterns
        current_meal_pattern = standardized_profile.get("nutrition", {}).get("data", {}).get("mealTime", "")
        
        # Extract client name and primary goal
        client_name = profile_analysis.get("client_profile", {}).get("personal_info", {}).get("name", "Client")
        primary_goal = goal_analysis.get("goals", {}).get("primary_goal", "")
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Determine the optimal meal timing and nutrient distribution throughout the day for this client "
            "based on their training schedule, macronutrient targets, recovery capacity, and lifestyle. "
            "Create comprehensive meal timing recommendations for training and rest days.\n\n"
            
            f"CLIENT PROFILE:\n"
            f"- Name: {client_name}\n"
            f"- Primary Goal: {primary_goal}\n"
            f"- Wake Time: {wake_time}\n"
            f"- Bed Time: {bed_time}\n"
            f"- Work/Study Hours: {work_hours}\n"
            f"- Current Meal Pattern: {current_meal_pattern}\n\n"
            
            f"TRAINING SPLIT: {split_name}\n"
            f"Weekly Schedule:\n{self._format_dict(weekly_schedule)}\n\n"
            
            f"MACRONUTRIENT PLAN:\n"
            f"- Total Daily Calories: {total_calories}\n"
            f"- Protein Strategy: {protein_strategy}\n"
            f"- Carbohydrate Strategy: {carb_strategy}\n"
            f"- Fat Strategy: {fat_strategy}\n\n"
            
            f"RECOVERY PROFILE:\n"
            f"- Stress Level: {stress_level}\n"
            f"- Sleep Quality: {sleep_quality}\n"
            f"- Recovery Capacity: {self._format_dict(recovery_capacity)}\n\n"
            
            "Your meal timing recommendations should include:\n"
            "1. Specific meal plans for different types of training days and rest days\n"
            "2. Optimal nutrient timing windows around workouts (pre, intra, post)\n"
            "3. Meal-by-meal macronutrient distribution throughout the day\n"
            "4. Hydration strategy integrated with meal timing\n"
            "5. Supplement timing recommendations if applicable\n"
            "6. Strategies to optimize circadian rhythm and sleep quality\n"
            "7. Practical guidelines for implementing the timing recommendations\n\n"
            
            "Consider meal timing through the lens of current sports nutrition research, particularly "
            "the International Society of Sports Nutrition position stands on nutrient timing, "
            "meal frequency, and research on time-restricted feeding and circadian biology."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=MealTimingRecommendation)
        return result
    
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