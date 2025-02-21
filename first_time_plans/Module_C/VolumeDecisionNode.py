import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class VolumePerMuscleGroup(BaseModel):
    """Represents volume recommendations for a specific muscle group."""
    muscle_group: str = Field(..., description="Name of the muscle group (e.g., 'Chest', 'Back', 'Legs')")
    mev: str = Field(..., description="Minimum Effective Volume (sets per week)")
    mav: str = Field(..., description="Maximum Adaptive Volume (sets per week)")
    mrv: str = Field(..., description="Maximum Recoverable Volume (sets per week)")
    recommended_weekly_sets: str = Field(..., description="Recommended weekly set range based on client's specific situation")
    frequency_recommendation: str = Field(..., description="Optimal training frequency for this muscle group (sessions per week)")

class IntensityGuidelines(BaseModel):
    """Guidelines for training intensity based on client goals and experience."""
    primary_rep_range: str = Field(..., description="Main rep range to focus on for primary goals (e.g., '8-12 reps')")
    secondary_rep_range: str = Field(..., description="Secondary rep range to include for complementary adaptations")
    rpe_recommendation: str = Field(..., description="Rate of Perceived Exertion (RPE) recommendation (e.g., 'RPE 7-9')")
    percentage_1rm_range: str = Field(..., description="Recommended intensity range as percentage of 1RM (e.g., '70-85%')")
    rest_period_recommendation: str = Field(..., description="Recommended rest periods between sets (e.g., '2-3 minutes')")

class ProgressionModel(BaseModel):
    """Structured progression model for implementing progressive overload."""
    initial_phase: str = Field(..., description="First phase of progression (usually 1-4 weeks)")
    intermediate_phase: str = Field(..., description="Second phase of progression (usually 5-8 weeks)")
    advanced_phase: str = Field(..., description="Final phase of progression (usually 9-12 weeks)")
    deload_frequency: str = Field(..., description="Recommended frequency of deload weeks")
    deload_strategy: str = Field(..., description="Method of implementing deloads (volume reduction, intensity reduction, etc.)")
    progression_variables: List[str] = Field(..., description="Variables to manipulate for progression (weight, reps, sets, etc.)")

class VolumeAndIntensityRecommendation(BaseModel):
    """Complete volume and intensity recommendation for training program."""
    overall_volume_assessment: str = Field(..., description="Assessment of client's volume needs and tolerance")
    overall_intensity_assessment: str = Field(..., description="Assessment of client's optimal intensity zones")
    muscle_group_recommendations: List[VolumePerMuscleGroup] = Field(..., description="Volume landmarks for each major muscle group")
    intensity_guidelines: IntensityGuidelines = Field(..., description="Intensity parameters for optimal training")
    progression_model: ProgressionModel = Field(..., description="Progressive overload implementation strategy")
    special_considerations: List[str] = Field(..., description="Client-specific factors affecting volume/intensity prescriptions")
    scientific_justification: str = Field(..., description="Scientific principles supporting these recommendations")

class VolumeAndIntensityDecisionNode:
    """
    Determines optimal training volume and intensity parameters based on client data.
    
    This class uses an LLM-driven approach to generate scientifically-grounded 
    volume, intensity, and progression guidelines tailored to the client's recovery capacity,
    training experience, and specific goals.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the VolumeAndIntensityDecisionNode with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self, 
        client_data: Dict[str, Any],
        history_analysis: Dict[str, Any], 
        body_analysis: Dict[str, Any], 
        goal_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal volume and intensity parameters.
        
        This method integrates data from multiple analysis modules to determine
        appropriate training volume, intensity, and progression strategies considering:
        - Training history and volume tolerance
        - Recovery capacity and lifestyle factors
        - Primary and secondary goals
        - Body composition and training adaptations
        
        Args:
            client_data: Raw client data from the standardized profile
            history_analysis: Training history and experience analysis
            body_analysis: Body composition and measurement analysis
            goal_analysis: Client goals and objectives analysis
            
        Returns:
            A dictionary containing structured volume and intensity recommendations
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_volume_intensity_schema(
                client_data, history_analysis, body_analysis, goal_analysis
            )
            
            return {
                "volume_intensity_recommendation": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining volume and intensity parameters: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in volume and intensity decision-making.
        
        The system message establishes the context and criteria for determining
        optimal training parameters according to scientific principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are an expert exercise scientist specialized in training volume and intensity prescription, "
            "following evidence-based methodologies from researchers like Dr. Mike Israetel, Dr. Brad Schoenfeld, "
            "and Dr. Eric Helms. Your task is to determine optimal training volume, intensity, and progression "
            "strategies based on a client's individual characteristics and goals.\n\n"
            
            "Apply these scientific principles when prescribing volume and intensity:\n"
            "1. **Volume Landmarks**: Prescribe volume using MEV (Minimum Effective Volume), MAV (Maximum Adaptive Volume), "
            "and MRV (Maximum Recoverable Volume) for each muscle group.\n"
            "2. **Intensity Specificity**: Match intensity (load/RPE) to primary training goal (strength: 1-6 reps at 80-95% 1RM, "
            "hypertrophy: 6-12 reps at 65-80% 1RM, endurance: 12-20+ reps at 40-65% 1RM).\n"
            "3. **Recovery Consideration**: Account for systemic recovery capacity based on age, training experience, "
            "sleep quality, stress levels, and nutrition.\n"
            "4. **Progressive Overload**: Design progression models that gradually increase demands "
            "while respecting recovery capacity.\n"
            "5. **Individual Response**: Consider previous volume tolerance, training age, injury history, "
            "and demonstrated adaptations to different intensity ranges.\n\n"
            
            "Provide specific volume recommendations for each major muscle group, intensity parameters "
            "tailored to the client's goals, and a progression strategy that includes deload protocols."
        )
    
    def _determine_volume_intensity_schema(
        self, 
        client_data: Dict[str, Any],
        history_analysis: Dict[str, Any], 
        body_analysis: Dict[str, Any], 
        goal_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine volume and intensity parameters using Pydantic schema validation.
        
        Args:
            client_data: Raw client data from the standardized profile
            history_analysis: Training history and experience analysis
            body_analysis: Body composition and measurement analysis
            goal_analysis: Client goals and objectives analysis
            
        Returns:
            Structured volume and intensity recommendation as a Pydantic model
        """
        # Extract relevant data for prompt construction
        goals = goal_analysis.get("goal_analysis_schema", {})
        primary_goals = goals.get("primary_goals", [])
        training_experience = history_analysis.get("experience_level", "Intermediate")
        volume_tolerance = history_analysis.get("volume_tolerance", {}).get("weekly_volume_tolerance", "Unknown")
        recovery_capacity = history_analysis.get("adaptation_history", {}).get("recovery_capacity", "Average")
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Determine the optimal volume, intensity, and progression parameters for this client. "
            "Apply scientific principles like volume landmarks (MEV, MAV, MRV) and intensity specificity "
            "to create an evidence-based prescription.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Training experience: {training_experience}\n"
            f"- Volume tolerance: {volume_tolerance}\n"
            f"- Recovery capacity: {recovery_capacity}\n"
            f"- Primary goals: {', '.join(primary_goals)}\n\n"
            
            f"FULL GOAL ANALYSIS:\n{self._format_dict(goals)}\n\n"
            f"BODY COMPOSITION ANALYSIS:\n{self._format_dict(body_analysis)}\n\n"
            f"TRAINING HISTORY ANALYSIS:\n{self._format_dict(history_analysis)}\n\n"
            
            "Your volume and intensity recommendation should include:\n"
            "1. Specific volume landmarks (MEV, MAV, MRV) for each major muscle group\n"
            "2. Optimal rep ranges and RPE/intensity zones based on goals\n"
            "3. Training frequency recommendations per muscle group\n"
            "4. Progressive overload strategy across a 12-week timeline\n"
            "5. Deload protocols and frequency\n\n"
            
            "Provide detailed scientific justification for your recommendations, specifically addressing "
            "how they align with the client's recovery capacity and training goals."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=VolumeAndIntensityRecommendation)
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