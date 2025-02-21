Copyfrom typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CalorieCalculation(BaseModel):
    """Breakdown of the calorie calculation process."""
    bmr_formula_used: str = Field(..., description="BMR formula used (e.g., 'Mifflin-St Jeor', 'Harris-Benedict')")
    bmr_value: float = Field(..., description="Calculated Basal Metabolic Rate in calories")
    activity_multiplier: float = Field(..., description="Activity factor applied to BMR")
    tdee_calculation: float = Field(..., description="Total Daily Energy Expenditure (BMR × activity factor)")
    exercise_adjustment: float = Field(..., description="Additional calories for exercise activity")
    non_exercise_adjustment: float = Field(..., description="Adjustment for NEAT (Non-Exercise Activity Thermogenesis)")
    goal_adjustment: float = Field(..., description="Caloric adjustment based on goals (surplus/deficit)")
    final_caloric_target: float = Field(..., description="Final recommended daily caloric intake")

class CaloriePhasing(BaseModel):
    """Caloric intake phasing recommendations."""
    initial_phase_calories: float = Field(..., description="Starting caloric target")
    initial_phase_duration: str = Field(..., description="Duration of initial phase (e.g., '2 weeks')")
    subsequent_phases: List[Dict[str, Any]] = Field(..., description="Future caloric adjustments")
    adaptation_indicators: List[str] = Field(..., description="Signs indicating need for caloric adjustment")
    plateau_strategy: str = Field(..., description="Strategy for handling plateaus")

class MealStructureGuidelines(BaseModel):
    """Guidelines for meal structure and timing."""
    recommended_meal_frequency: int = Field(..., description="Optimal number of meals per day")
    calorie_distribution: Dict[str, float] = Field(..., description="Percentage of calories per meal")
    pre_workout_guidelines: str = Field(..., description="Pre-workout nutrition recommendations")
    post_workout_guidelines: str = Field(..., description="Post-workout nutrition recommendations")
    meal_timing_rationale: str = Field(..., description="Scientific basis for meal timing recommendations")

class CaloricNeedsRecommendation(BaseModel):
    """Comprehensive caloric needs recommendation."""
    client_name: str = Field(..., description="Client's name")
    primary_goal: str = Field(..., description="Client's primary nutritional goal")
    calorie_targets: CalorieCalculation = Field(..., description="Detailed calorie calculation")
    calorie_phasing: CaloriePhasing = Field(..., description="Progressive calorie adjustment plan")
    meal_structure: MealStructureGuidelines = Field(..., description="Meal timing and structure recommendations")
    refeed_strategy: Optional[str] = Field(None, description="Refeed/diet break recommendations if applicable")
    goal_timeline_estimate: str = Field(..., description="Estimated timeline to reach nutritional goals")
    monitoring_metrics: List[str] = Field(..., description="Metrics to track for adjusting caloric intake")
    scientific_rationale: str = Field(..., description="Scientific basis for caloric recommendations")

class CaloricNeedsDecisionNode:
    """
    Determines optimal caloric intake based on client profile, body composition,
    and goal analysis.
    
    This class uses an LLM-driven decision process to calculate appropriate
    caloric targets considering metabolic rate, activity level, body composition,
    and specific goals, while incorporating scientific principles of energy balance.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the CaloricNeedsDecisionNode with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self,
        profile_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal caloric needs.
        
        This method integrates data from previous analysis modules to calculate
        appropriate caloric targets considering:
        - Basal metabolic rate based on body composition
        - Activity level and exercise expenditure
        - Specific goals (muscle gain, fat loss, performance)
        - Adaptive thermogenesis considerations
        - Progressive caloric adjustment strategy
        
        Args:
            profile_analysis: Client profile analysis
            body_analysis: Body composition analysis
            goal_analysis: Goal clarification analysis
            
        Returns:
            A dictionary containing the structured caloric needs recommendation
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_caloric_needs_schema(
                profile_analysis, body_analysis, goal_analysis
            )
            
            return {
                "caloric_needs_recommendation": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining caloric needs: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in caloric needs decision-making.
        
        The system message establishes the context and criteria for determining
        optimal caloric intake according to scientific principles of energy balance
        and nutritional science.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a nutrition specialist with expertise in energy metabolism, "
            "body composition analysis, and sports nutrition. Your task is to determine "
            "optimal caloric targets for a client based on their profile, body composition, "
            "and specific goals.\n\n"
            
            "Apply these scientific principles when calculating caloric needs:\n"
            "1. **Energy Balance Equation**: Consider the relationship between energy intake, "
            "expenditure, and storage to establish appropriate caloric targets.\n"
            "2. **Metabolic Adaptation**: Account for adaptive thermogenesis and metabolic "
            "flexibility when planning long-term caloric strategies.\n"
            "3. **Body Composition Considerations**: Use fat-free mass as a primary driver "
            "for basal metabolic rate calculations.\n"
            "4. **Goal-Specific Energy Requirements**: Adjust caloric targets based on whether "
            "the goal is muscle hypertrophy, fat loss, performance, or maintenance.\n"
            "5. **Progressive Implementation**: Design caloric phases that gradually adapt to "
            "changes in metabolism and body composition.\n"
            "6. **Individual Variability**: Account for genetic, hormonal, and lifestyle factors "
            "that influence metabolic rate and energy partitioning.\n"
            "7. **Activity Energy Expenditure**: Differentiate between exercise activity thermogenesis "
            "and non-exercise activity thermogenesis.\n\n"
            
            "Your caloric recommendations should include both immediate targets and a progressive "
            "adjustment strategy, along with meal timing considerations that align with the client's "
            "training schedule and metabolic needs."
        )

    def _determine_caloric_needs_schema(
        self,
        profile_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine caloric needs using Pydantic schema validation.
        
        Args:
            profile_analysis: Client profile analysis
            body_analysis: Body composition analysis
            goal_analysis: Goal clarification analysis
            
        Returns:
            Structured caloric needs recommendation as a Pydantic model
        """

        profile_analysis = profile_analysis.get("data")
        # Extract relevant data from profile analysis
        client_name = profile_analysis.get("name", "Client")
        age = profile_analysis.get("age", "Unknown")
        gender = profile_analysis.get("gender", "Unknown")
        activity_level = profile_analysis.get("activity_level", "Unknown")
        
        # Extract body composition data
        height = profile_analysis.get("height", "Unknown")
        weight = profile_analysis.get("weight", "Unknown")
        body_fat_percentage = body_analysis.get("body_fat_percentage", "Unknown")
        fat_free_mass = body_analysis.get("fat_free_mass", "Unknown")
        
        # Extract goal information
        primary_goal = goal_analysis.get("primary_goal", "Unknown")
        goal_timeframe = goal_analysis.get("goal_timeframe", "Unknown")
        goal_intensity = goal_analysis.get("goal_intensity", "Unknown")
        

"""
            primary_goals: List[str] = Field(
        ...,
        description="The 1-3 most important objectives that should receive the majority of programming "
        "focus. Should address the client's stated priorities while being physiologically optimal."
    )
    secondary_goals: List[str] = Field(
        ...,
        description="Supporting objectives that complement the primary goals but receive less direct "
        "programming focus. Should include maintenance goals and complementary adaptations."
    )
    objectives: List[Objective] = Field(
        default_factory=list,
        description="Structured breakdown of each goal into specific, measurable objectives with clear "
        "priority levels. Should operationalize abstract goals into concrete targets."
    )
    timeframe_analysis: TimeframeAnalysis = Field(
        ...,
        description="Comprehensive analysis of goal timeframes that balances client expectations with "
        "physiological reality. Should provide both assessment and constructive recommendations."
    )
    goals_split: Optional[GoalSplit] = Field(
        None,
        description="Periodized breakdown of larger goals into specific weekly, monthly and quarterly "
        "targets. Should establish a clear progression that builds toward the ultimate objectives."
    )"""
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Calculate optimal caloric needs for this client based on their profile, "
            "body composition, and specific goals. Apply principles of energy balance "
            "and nutritional science to create a comprehensive caloric recommendation.\n\n"
            
            f"CLIENT PROFILE:\n"
            f"- Name: {client_name}\n"
            f"- Age: {age}\n"
            f"- Gender: {gender}\n"
            f"- Activity Level: {activity_level}\n\n"
            
            f"BODY COMPOSITION:\n"
            f"- Height: {height}\n"
            f"- Weight: {weight}\n"
            f"- Body Fat Percentage: {body_fat_percentage}\n"
            f"- Fat-Free Mass: {fat_free_mass}\n\n"
            
            f"GOAL ANALYSIS:\n"
            f"- Primary Goal: {primary_goal}\n"
            f"- Goal Timeframe: {goal_timeframe}\n"
            f"- Goal Intensity/Priority: {goal_intensity}\n\n"
            
            f"ADDITIONAL CONTEXT:\n{self._format_dict(goal_analysis)}\n\n"
            
            "Your caloric needs recommendation should include:\n"
            "1. Detailed calorie calculation showing BMR, activity adjustments, and goal-specific modifications\n"
            "2. A progressive calorie phasing strategy that adapts to changes in metabolism and body composition\n"
            "3. Meal structure guidelines that optimize nutrient timing around training\n"
            "4. A monitoring and adjustment protocol based on measurable progress indicators\n"
            "5. Scientific rationale for all recommendations\n\n"
            
            "Consider caloric needs through the lens of both thermodynamics (energy balance) "
            "and metabolic adaptation (hormonal impacts of different nutritional approaches)."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=CaloricNeedsRecommendation)
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