from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ActivityMultiplier(BaseModel):
    """Activity level multiplier for TDEE calculation."""
    multiplier: float = Field(..., description="Numeric multiplier for BMR")
    justification: str = Field(..., description="Explanation for the multiplier selection")

class BmrCalculation(BaseModel):
    """Basal Metabolic Rate calculation details."""
    formula_used: str = Field(..., description="Formula used (e.g., 'Mifflin-St Jeor', 'Harris-Benedict')")
    calculated_bmr: float = Field(..., description="Calculated BMR in calories")
    factors_considered: List[str] = Field(..., description="Factors considered in BMR calculation")

class TdeeCalculation(BaseModel):
    """Total Daily Energy Expenditure calculation details."""
    activity_multiplier: ActivityMultiplier = Field(..., description="Activity level multiplier")
    calculated_tdee: float = Field(..., description="Calculated TDEE in calories")
    explanation: str = Field(..., description="Explanation of TDEE calculation")

class CalorieAdjustment(BaseModel):
    """Caloric adjustment based on client goals."""
    adjustment_type: str = Field(..., description="Type of adjustment (surplus/deficit/maintenance)")
    adjustment_amount: int = Field(..., description="Amount of caloric adjustment in calories")
    adjusted_calories: int = Field(..., description="Final caloric target after adjustment")
    scientific_rationale: str = Field(..., description="Scientific explanation for adjustment amount")

class WeeklyAdjustmentStrategy(BaseModel):
    """Strategy for weekly caloric adjustments."""
    initial_adjustment: str = Field(..., description="Initial caloric adjustment approach")
    progress_monitoring: List[str] = Field(..., description="Metrics to monitor for progress")
    adjustment_thresholds: List[str] = Field(..., description="Thresholds for making further adjustments")
    plateau_strategy: str = Field(..., description="Strategy for handling plateaus")

class CaloricNeedsRecommendation(BaseModel):
    """Complete caloric needs recommendation."""
    bmr_calculation: BmrCalculation = Field(..., description="BMR calculation details")
    tdee_calculation: TdeeCalculation = Field(..., description="TDEE calculation details")
    goal_based_adjustment: CalorieAdjustment = Field(..., description="Goal-based caloric adjustment")
    daily_caloric_target: int = Field(..., description="Final daily caloric target")
    weekly_adjustment_strategy: WeeklyAdjustmentStrategy = Field(..., description="Weekly adjustment strategy")
    caloric_cycling_approach: str = Field(..., description="Approach to caloric cycling if applicable")
    scientific_explanation: str = Field(..., description="Comprehensive scientific explanation")
    individual_considerations: List[str] = Field(..., description="Individual factors considered")

class CaloricNeedsDecisionNode:
    """
    Determines optimal caloric intake based on client data and analysis.
    
    This class uses scientific formulas and LLM-driven decision process to
    generate personalized caloric recommendations aligned with the client's
    goals, body composition, and individual factors.
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
        
        This method integrates data from multiple analysis modules to calculate
        appropriate caloric targets, considering:
        - Basal Metabolic Rate (BMR)
        - Total Daily Energy Expenditure (TDEE)
        - Goal-specific caloric adjustments
        - Individual considerations
        
        Args:
            client_data: Raw client profile data
            body_analysis: Body composition analysis
            goal_analysis: Client goals analysis
            
        Returns:
            A dictionary containing structured caloric recommendations
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_caloric_needs_schema(
                client_data, body_analysis, goal_analysis
            )
            
            return {
                "caloric_needs_recommendation": schema_result
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
            "You are a nutrition specialist with expertise in determining optimal caloric needs "
            "based on scientific principles. Your task is to calculate appropriate caloric targets "
            "based on the client's body composition, goals, and individual factors.\n\n"
            
            "Apply these scientific principles when determining caloric needs:\n"
            "1. **BMR Calculation**: Use established formulas (Mifflin-St Jeor or Harris-Benedict) to estimate BMR.\n"
            "2. **TDEE Calculation**: Apply appropriate activity multipliers based on lifestyle and training frequency.\n"
            "3. **Goal Adjustment**: Implement evidence-based caloric adjustments:\n"
            "   - Weight loss: 20-25% deficit (maximum 500-750 cal/day) for sustainable fat loss\n"
            "   - Muscle gain: 10-20% surplus (250-500 cal/day) for optimal muscle growth with minimal fat gain\n"
            "   - Maintenance: TDEE ±100 calories with emphasis on nutrient timing\n"
            "4. **Individual Considerations**: Account for metabolic variations, training history, and recovery capacity.\n"
            "5. **Progressive Adjustment**: Include strategies for weekly caloric adjustments based on progress metrics.\n\n"
            
            "Your recommendation should include detailed calculations, scientific rationale, and a clear "
            "implementation strategy that aligns with the client's goals and lifestyle."
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
            body_analysis: Body composition analysis
            goal_analysis: Client goals analysis
            
        Returns:
            Structured caloric needs recommendation as a Pydantic model
        """
        # Extract relevant data for prompt construction
        personal_info = client_data.get("personal_info", {}).get("data", {})
        age = personal_info.get("age", "25")
        gender = personal_info.get("gender", "Male")
        height = personal_info.get("height", "186 cm").split()[0]
        weight = personal_info.get("weight", "86 kg").split()[0]
        
        fitness_info = client_data.get("fitness", {}).get("data", {})
        activity_level = fitness_info.get("activityLevel", "Active")
        training_frequency = fitness_info.get("trainingFrequency", "5x Week")
        
        goals = goal_analysis.get("goal_analysis_schema", {})
        primary_goals = goals.get("primary_goals", [])
        
        body_comp = body_analysis.get("body_analysis_schema", {})
        body_fat = body_comp.get("composition_estimates", {}).get("estimated_body_fat_percentage", "15-18%")
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Calculate the optimal caloric needs for this client based on scientific principles "
            "of nutrition and exercise physiology. Apply appropriate BMR formulas, activity multipliers, "
            "and goal-specific adjustments.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Age: {age}\n"
            f"- Gender: {gender}\n"
            f"- Height: {height} cm\n"
            f"- Weight: {weight} kg\n"
            f"- Activity level: {activity_level}\n"
            f"- Training frequency: {training_frequency}\n"
            f"- Primary goals: {', '.join(primary_goals)}\n"
            f"- Estimated body fat: {body_fat}\n\n"
            
            f"FULL GOAL ANALYSIS:\n{self._format_dict(goals)}\n\n"
            f"BODY COMPOSITION ANALYSIS:\n{self._format_dict(body_comp)}\n\n"
            
            "Your caloric needs recommendation should include:\n"
            "1. Detailed BMR calculation using appropriate formula\n"
            "2. TDEE calculation with justified activity multiplier\n"
            "3. Goal-specific caloric adjustment with scientific rationale\n"
            "4. Clear daily caloric target\n"
            "5. Strategy for weekly adjustments based on progress\n"
            "6. Consideration of individual factors\n\n"
            
            "Provide a comprehensive caloric needs assessment with scientific justification for your recommendations."
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