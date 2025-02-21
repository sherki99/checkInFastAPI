from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class BMRComponent(BaseModel):
    """Basal Metabolic Rate calculation results."""
    formula_used: str = Field(..., description="Formula used to calculate BMR (e.g., 'Mifflin-St Jeor')")
    calculated_bmr: int = Field(..., description="Calculated BMR in calories")
    variables_used: List[str] = Field(
        ...,
        description=(
            "A list representing the variables used in the calculation. "
            "Each entry follows the format 'variable: value'. Common variables include weight, height, age, gender, and activity level. "
            "These values influence the accuracy of the BMR estimation.\n"
            "Example:\n"
            "  - 'weight: 70kg'\n"
            "  - 'height: 175cm'\n"
            "  - 'age: 30'\n"
            "  - 'gender: male'\n"
            "  - 'activity level: moderate'"
        )
    )
    confidence_level: str = Field(..., description="Confidence in calculation based on data quality")

class TEEComponent(BaseModel):
    """Total Energy Expenditure calculation results."""
    activity_multiplier: float = Field(..., description="Activity factor applied to BMR")
    activity_classification: str = Field(..., description="Client's activity level classification")
    calculated_tee: int = Field(..., description="Total Energy Expenditure in calories")
    exercise_adjustment: int = Field(..., description="Additional calories from structured exercise")
    neat_estimate: int = Field(..., description="Non-Exercise Activity Thermogenesis estimate")

class GoalAdjustmentComponent(BaseModel):
    """Calorie adjustments based on client goals."""
    primary_goal: str = Field(..., description="Client's primary goal")
    caloric_adjustment: int = Field(..., description="Calorie surplus/deficit recommended")
    adjustment_percentage: float = Field(..., description="Adjustment as percentage of maintenance")
    scientific_rationale: str = Field(..., description="Scientific basis for adjustment")
    rate_of_change_estimate: str = Field(..., description="Expected rate of change with this adjustment")

class CaloricTargets(BaseModel):
    """Complete caloric needs assessment for client."""
    bmr_analysis: BMRComponent = Field(..., description="BMR calculation details")
    tee_analysis: TEEComponent = Field(..., description="TEE calculation details")
    goal_adjustment: GoalAdjustmentComponent = Field(..., description="Goal-based calorie adjustments")
    maintenance_calories: int = Field(..., description="Estimated maintenance calories")
    goal_calories: int = Field(..., description="Recommended total daily calories for goal")
    training_day_calories: int = Field(..., description="Calories for training days")
    rest_day_calories: int = Field(..., description="Calories for rest days")
    confidence_assessment: str = Field(..., description="Overall confidence in calorie estimates")
    individual_factors: List[str] = Field(..., description="Individual factors affecting calculations")
    adaptive_recommendations: List[str] = Field(..., description="Guidelines for adjusting calories based on progress")

class CaloricNeedsDecisionNode:
    """
    Determines optimal caloric intake based on client data, body composition, and goals.
    
    This class uses validated formulas and scientific principles to calculate
    appropriate caloric targets for muscle gain, fat loss, or maintenance.
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
        client_data: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal caloric intake.
        
        This method integrates data from multiple sources to calculate
        appropriate caloric targets based on:
        - BMR calculation using validated formulas
        - Activity level and exercise frequency
        - Body composition analysis
        - Primary and secondary goals
        
        Args:
            client_data: Raw client profile data
            body_analysis: Body composition and measurement analysis
            goal_analysis: Client goals and objectives analysis
            
        Returns:
            A dictionary containing structured caloric recommendations
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_caloric_needs_schema(
                client_data, body_analysis, goal_analysis
            )
            
            return {
                "caloric_targets": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining caloric needs: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in caloric needs determination.
        
        The system message establishes the context and criteria for determining
        optimal caloric intake according to scientific principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a sports nutrition specialist with expertise in energy balance, "
            "metabolism, and nutritional programming for athletes and fitness enthusiasts. "
            "Your task is to determine optimal caloric intake based on the client's goals, "
            "body composition, activity level, and individual factors.\n\n"
            
            "Apply these scientific principles when calculating caloric needs:\n"
            "1. **Basal Metabolic Rate (BMR)**: Use validated formulas like Mifflin-St Jeor "
            "or Harris-Benedict to estimate BMR based on age, weight, height, and gender.\n"
            "2. **Activity Factors**: Apply appropriate multipliers based on daily activity "
            "levels (1.2 for sedentary, 1.375 for lightly active, 1.55 for moderately active, "
            "1.725 for very active, 1.9 for extremely active).\n"
            "3. **Exercise Energy Expenditure**: Account for additional calories burned during "
            "structured exercise sessions based on type, duration, and intensity.\n"
            "4. **Goal-Specific Adjustments**: Apply evidence-based caloric surpluses/deficits "
            "based on primary goals (e.g., ~500 cal deficit for fat loss, ~250-500 cal surplus "
            "for muscle gain).\n"
            "5. **Body Composition Considerations**: Adjust calculations based on lean body mass "
            "and estimated body fat percentage when available.\n"
            "6. **Metabolic Adaptation**: Consider potential metabolic adaptations based on "
            "training history and previous dieting.\n"
            "7. **Nutrient Timing**: Differentiate between training and non-training day needs "
            "when appropriate.\n\n"
            
            "Your recommendation should include precise caloric targets along with scientific "
            "justification for your calculations and guidelines for adapting intake based on progress."
        )
    
    def _determine_caloric_needs_schema(
        self,
        client_data: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine caloric needs using Pydantic schema validation.
        
        Args:
            client_data: Raw client profile data
            body_analysis: Body composition and measurement analysis
            goal_analysis: Client goals and objectives analysis
            
        Returns:
            Structured caloric needs recommendation as a Pydantic model
        """
        # Extract relevant data for prompt construction
        personal_info = client_data.get("personal_info", {}).get("data", {})
        fitness_info = client_data.get("fitness", {}).get("data", {})
        nutrition_info = client_data.get("nutrition", {}).get("data", {})
        goals = goal_analysis.get("goal_analysis_schema", {})
        primary_goals = goals.get("primary_goals", [])
        body_composition = body_analysis.get("body_analysis_schema", {})
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Calculate optimal caloric needs for this client based on scientific principles "
            "of energy balance and metabolism. Apply appropriate formulas for BMR estimation, "
            "activity factors, and goal-specific adjustments.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Name: {personal_info.get('name', 'Unknown')}\n"
            f"- Age: {personal_info.get('age', 'Unknown')}\n"
            f"- Gender: {personal_info.get('gender', 'Unknown')}\n"
            f"- Height: {personal_info.get('height', 'Unknown')}\n"
            f"- Weight: {personal_info.get('weight', 'Unknown')}\n"
            f"- Activity Level: {fitness_info.get('activityLevel', 'Unknown')}\n"
            f"- Training Frequency: {fitness_info.get('trainingFrequency', 'Unknown')}\n"
            f"- Primary Goals: {', '.join(primary_goals)}\n\n"
            
            f"BODY COMPOSITION ANALYSIS:\n{self._format_dict(body_composition)}\n\n"
            f"GOAL ANALYSIS:\n{self._format_dict(goals)}\n\n"
            f"NUTRITION INFO:\n{self._format_dict(nutrition_info)}\n\n"
            
            "Your caloric needs assessment should include:\n"
            "1. BMR calculation with formula justification\n"
            "2. TEE calculation with activity factor explanation\n"
            "3. Goal-specific caloric adjustments\n"
            "4. Different calorie targets for training vs. rest days\n"
            "5. Guidelines for adjusting intake based on progress\n\n"
            
            "Create a complete caloric needs prescription with scientific justification for your calculations."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=CaloricTargets)
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