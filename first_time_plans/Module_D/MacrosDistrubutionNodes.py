from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MacroNutrientTargets(BaseModel):
    """Detailed macronutrient targets."""
    protein_grams: int = Field(..., description="Daily protein target in grams")
    protein_per_kg: float = Field(..., description="Protein per kg of bodyweight")
    protein_percentage: int = Field(..., description="Percentage of calories from protein")
    carb_grams: int = Field(..., description="Daily carbohydrate target in grams")
    carb_per_kg: float = Field(..., description="Carbs per kg of bodyweight")
    carb_percentage: int = Field(..., description="Percentage of calories from carbs")
    fat_grams: int = Field(..., description="Daily fat target in grams")
    fat_per_kg: float = Field(..., description="Fat per kg of bodyweight")
    fat_percentage: int = Field(..., description="Percentage of calories from fat")

class TrainingDayMacros(BaseModel):
    """Macronutrient targets for training days."""
    total_calories: int = Field(..., description="Total calories on training days")
    macros: MacroNutrientTargets = Field(..., description="Macro breakdown for training days")
    scientific_rationale: str = Field(..., description="Scientific basis for training day distribution")

class RestDayMacros(BaseModel):
    """Macronutrient targets for rest days."""
    total_calories: int = Field(..., description="Total calories on rest days")
    macros: MacroNutrientTargets = Field(..., description="Macro breakdown for rest days")
    scientific_rationale: str = Field(..., description="Scientific basis for rest day distribution")

class MacroDistributionPlan(BaseModel):
    """Complete macronutrient distribution plan."""
    client_name: str = Field(..., description="Client's name")
    primary_goal: str = Field(..., description="Client's primary goal influencing macro distribution")
    maintenance_calories: int = Field(..., description="Estimated maintenance calories")
    adjusted_daily_calories: int = Field(..., description="Goal-adjusted daily calorie target")
    training_day_plan: TrainingDayMacros = Field(..., description="Training day macro targets")
    rest_day_plan: RestDayMacros = Field(..., description="Rest day macro targets")
    protein_justification: str = Field(..., description="Scientific justification for protein targets")
    carb_justification: str = Field(..., description="Scientific justification for carb targets")
    fat_justification: str = Field(..., description="Scientific justification for fat targets")
    individual_considerations: List[str] = Field(..., description="Client-specific factors influencing recommendations")
    nutrient_timing_guidelines: List[str] = Field(..., description="Guidelines for nutrient timing throughout the day")
    adaptive_strategies: List[str] = Field(..., description="Strategies for adjusting macros based on progress")

class MacroDistributionDecisionNode:
    """
    Determines optimal macronutrient distribution based on caloric needs, goals, and body composition.
    
    This class uses evidence-based approaches to calculate appropriate macronutrient
    ratios for muscle gain, fat loss, or performance optimization.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the MacroDistributionDecisionNode with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self,
        caloric_targets: Dict[str, Any],
        client_data: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal macronutrient distribution.
        
        This method integrates data from multiple sources to calculate
        appropriate macronutrient targets based on:
        - Caloric targets for training and rest days
        - Body composition and lean mass estimates
        - Primary and secondary goals
        - Training history and experience level
        - Individual factors and dietary preferences
        
        Args:
            caloric_targets: Caloric needs assessment
            client_data: Raw client profile data
            body_analysis: Body composition and measurement analysis
            goal_analysis: Client goals and objectives analysis
            history_analysis: Training history and experience analysis
            
        Returns:
            A dictionary containing structured macronutrient recommendations
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_macro_distribution_schema(
                caloric_targets, client_data, body_analysis, goal_analysis, history_analysis
            )
            
            return {
                "macro_plan": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining macronutrient distribution: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in macronutrient distribution determination.
        
        The system message establishes the context and criteria for determining
        optimal macronutrient ratios according to scientific principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a sports nutrition specialist with expertise in macronutrient optimization "
            "for athletes and fitness enthusiasts. Your task is to determine optimal macronutrient "
            "distribution based on the client's caloric needs, goals, body composition, "
            "training history, and individual factors.\n\n"
            
            "Apply these scientific principles when calculating macronutrient distribution:\n"
            "1. **Protein Requirements**: Base protein needs on activity level, goals, and bodyweight:\n"
            "   - Strength/hypertrophy: 1.6-2.2g/kg bodyweight\n"
            "   - Fat loss: 2.0-2.4g/kg bodyweight\n"
            "   - Endurance: 1.4-1.6g/kg bodyweight\n"
            "2. **Carbohydrate Distribution**: Adjust based on activity level and goals:\n"
            "   - High-intensity training: 4-7g/kg bodyweight\n"
            "   - Moderate training: 3-5g/kg bodyweight\n"
            "   - Fat loss focus: 2-3g/kg bodyweight\n"
            "3. **Fat Requirements**: Ensure minimum fat intake for hormonal health:\n"
            "   - Minimum 0.5g/kg bodyweight or 20-30% of total calories\n"
            "4. **Training vs. Rest Days**: Adjust carbohydrate intake based on training status:\n"
            "   - Higher carbs on training days, especially for hypertrophy\n"
            "   - Potentially lower carbs on rest days, maintaining protein intake\n"
            "5. **Individual Response**: Consider training history and individual metabolic factors\n"
            "6. **Dietary Preferences**: Account for client's dietary preferences when possible\n\n"
            
            "Your recommendation should include precise macronutrient targets for both training "
            "and rest days, with scientific justification for your calculations."
        )
    
    def _determine_macro_distribution_schema(
        self,
        caloric_targets: Dict[str, Any],
        client_data: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine macronutrient distribution using Pydantic schema validation.
        
        Args:
            caloric_targets: Caloric needs assessment
            client_data: Raw client profile data
            body_analysis: Body composition and measurement analysis
            goal_analysis: Client goals and objectives analysis
            history_analysis: Training history and experience analysis
            
        Returns:
            Structured macronutrient recommendation as a Pydantic model
        """
        # Extract relevant data for prompt construction
        personal_info = client_data.get("personal_info", {}).get("data", {})
        nutrition_info = client_data.get("nutrition", {}).get("data", {})
        
        caloric_data = caloric_targets.get("caloric_targets", {})
        goals = goal_analysis.get("goal_analysis_schema", {})
        primary_goals = goals.get("primary_goals", [])
        body_composition = body_analysis.get("body_analysis_schema", {})
        training_experience = history_analysis.get("experience_level", "Intermediate")
        
        # Extract weight for calculations
        weight_str = personal_info.get("weight", "0 kg").split()[0]
        try:
            weight_kg = float(weight_str)
        except ValueError:
            weight_kg = 70  # Default fallback
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Calculate optimal macronutrient distribution for this client based on scientific principles "
            "of sports nutrition. Create a complete macro plan that aligns with their caloric targets, "
            "goals, body composition, and training history.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Name: {personal_info.get('name', 'Client')}\n"
            f"- Weight: {personal_info.get('weight', 'Unknown')}\n"
            f"- Training Experience: {training_experience}\n"
            f"- Primary Goals: {', '.join(primary_goals)}\n"
            f"- Dietary Preferences: {nutrition_info.get('dietPreference', 'Balanced diet')}\n\n"
            
            f"CALORIC TARGETS:\n{self._format_dict(caloric_data)}\n\n"
            f"BODY COMPOSITION:\n{self._format_dict(body_composition)}\n\n"
            f"GOAL ANALYSIS:\n{self._format_dict(goals)}\n\n"
            f"TRAINING HISTORY:\n{self._format_dict(history_analysis)}\n\n"
            
            "Your macronutrient distribution plan should include:\n"
            "1. Precise protein, carb, and fat targets for training days\n"
            "2. Precise protein, carb, and fat targets for rest days\n"
            "3. Targets expressed in grams, percentage of calories, and g/kg bodyweight\n"
            "4. Scientific justification for each macronutrient target\n"
            "5. Considerations for nutrient timing throughout the day\n"
            "6. Strategies for adjusting macros based on progress\n\n"
            
            "Create a complete macronutrient distribution plan with scientific justification "
            "for your recommendations."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=MacroDistributionPlan)
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