from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MuscleGroupVolumeGuideline(BaseModel):
    """Volume recommendations for a specific muscle group."""
    muscle_group: str = Field(..., description="Name of the muscle group (e.g., 'Chest', 'Back', 'Legs')")
    weekly_sets_range: str = Field(..., description="Recommended weekly set range (e.g., '12-20')")
    session_sets_range: str = Field(..., description="Recommended sets per session (e.g., '4-8')")
    frequency: str = Field(..., description="Optimal weekly training frequency (e.g., '2-3 times')")
    mev: int = Field(..., description="Minimum Effective Volume (sets per week)")
    mav: int = Field(..., description="Maximum Adaptive Volume (sets per week)")
    mrv: int = Field(..., description="Maximum Recoverable Volume (sets per week)")

class IntensityGuideline(BaseModel):
    """Intensity recommendations for different training goals."""
    strength_focus: str = Field(..., description="Rep ranges and intensity for strength development")
    hypertrophy_focus: str = Field(..., description="Rep ranges and intensity for hypertrophy")
    endurance_focus: str = Field(..., description="Rep ranges and intensity for muscular endurance")
    primary_intensity_recommendation: str = Field(..., description="The main intensity approach based on client goals")
    rpe_guideline: str = Field(..., description="Rating of Perceived Exertion guidelines")
    rest_period_recommendation: str = Field(..., description="Rest period recommendations between sets")

class ProgressionGuideline(BaseModel):
    """Guidelines for progressive overload implementation."""
    initial_adaptation_phase: str = Field(..., description="Guidelines for the first 2-4 weeks")
    volume_progression: str = Field(..., description="How to progress training volume over time")
    intensity_progression: str = Field(..., description="How to progress training intensity over time")
    deload_frequency: str = Field(..., description="Recommended frequency and structure of deload weeks")
    progression_indicators: List[str] = Field(..., description="Key metrics to track for progression")

class VolumeIntensityRecommendation(BaseModel):
    """Complete volume and intensity recommendations for the training plan."""
    primary_goal_focus: str = Field(..., description="The primary training goal that shapes these recommendations")
    experience_level_adjustment: str = Field(..., description="How these recommendations are adjusted for client's experience")
    recovery_capacity_assessment: str = Field(..., description="Assessment of client's recovery capabilities")
    muscle_group_guidelines: List[MuscleGroupVolumeGuideline] = Field(..., description="Volume guidelines for each major muscle group")
    intensity_guidelines: IntensityGuideline = Field(..., description="Intensity recommendations across different goals")
    progression_model: ProgressionGuideline = Field(..., description="Progressive overload implementation guidelines")
    special_considerations: List[str] = Field(..., description="Additional factors that influenced these recommendations")
    scientific_justification: str = Field(..., description="Scientific principles supporting these recommendations")

class VolumeAndIntensityDecisionNode:
    """
    Determines optimal training volume and intensity based on client data and analysis.
    
    This class uses an LLM-driven decision process to generate scientifically-grounded
    volume and intensity guidelines that align with the client's goals, recovery capacity,
    training experience, and individual constraints.
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
        Process client data to determine optimal training volume and intensity.
        
        This method integrates data from multiple analysis modules to determine
        the most appropriate volume landmarks and intensity parameters, considering:
        - Primary and secondary goals
        - Recovery capacity and training experience
        - Individual muscle group development needs
        - Current training volume tolerance
        
        Args:
            client_data: Raw client profile data
            history_analysis: Training history and experience analysis
            body_analysis: Body composition and measurement analysis
            goal_analysis: Client goals and objectives analysis
            
        Returns:
            A dictionary containing structured volume and intensity guidelines
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
            logger.error(f"Error determining volume and intensity guidelines: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in volume and intensity decision-making.
        
        The system message establishes the context and criteria for determining
        optimal training volume and intensity according to scientific principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are an exercise science specialist with expertise in program design, "
            "following evidence-based methodologies from researchers like Dr. Mike Israetel, Dr. Brad Schoenfeld, "
            "and Dr. Eric Helms. Your task is to determine optimal training volume and intensity "
            "parameters based on the client's goals, training history, body composition, and recovery capacity.\n\n"
            
            "Apply these scientific principles when designing volume and intensity guidelines:\n"
            "1. **Volume Landmarks**: Use MEV (Minimum Effective Volume), MAV (Maximum Adaptive Volume), "
            "and MRV (Maximum Recoverable Volume) concepts for different muscle groups.\n"
            "2. **Training Age Consideration**: Adjust volume based on training experience - beginners need "
            "less volume to progress while advanced trainees require more.\n"
            "3. **Recovery Capacity**: Individual recovery abilities affect optimal volume - better recovery "
            "allows higher training volumes.\n"
            "4. **Intensity Zones**: Apply appropriate intensity zones based on goals:\n"
            "   - Strength: 1-6 reps, 80-95% 1RM, RPE 8-10\n"
            "   - Hypertrophy: 6-12 reps, 65-80% 1RM, RPE 7-9\n"
            "   - Endurance: 12-20+ reps, <65% 1RM, RPE 6-8\n"
            "5. **Volume Distribution**: Distribute volume based on frequency, splitting weekly volume "
            "across sessions for optimal stimulus:recovery ratio.\n"
            "6. **Progressive Overload**: Plan for progressive increases in volume before increasing intensity.\n"
            "7. **Deload Strategy**: Incorporate planned deloads based on training age and systemic fatigue.\n\n"
            
            "Your recommendation should include specific volume landmarks for major muscle groups, "
            "intensity parameters aligned with client goals, and progression guidelines that respect "
            "individual recovery capacity and training experience."
        )

    def _determine_volume_intensity_schema(
        self,
        client_data: Dict[str, Any],
        history_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine volume and intensity guidelines using Pydantic schema validation.
        
        Args:
            client_data: Raw client profile data
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
        recovery_capacity = history_analysis.get("recovery_capacity", "Average")
        
        # Get body measurements for muscle development priorities
        measurements = client_data.get("measurements", {}).get("measurements", {})
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Design optimal volume and intensity guidelines for this client based on scientific principles "
            "of exercise physiology. Apply Dr. Mike Israetel's volume landmarks (MEV, MAV, MRV) and appropriate "
            "intensity parameters based on the client's goals and individual factors.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Training experience: {training_experience}\n"
            f"- Recovery capacity: {recovery_capacity}\n"
            f"- Primary goals: {', '.join(primary_goals)}\n\n"
            
            f"FULL GOAL ANALYSIS:\n{self._format_dict(goals)}\n\n"
            f"BODY COMPOSITION ANALYSIS:\n{self._format_dict(body_analysis)}\n\n"
            f"TRAINING HISTORY ANALYSIS:\n{self._format_dict(history_analysis)}\n\n"
            
            "Your volume and intensity recommendation should include:\n"
            "1. Specific volume landmarks (MEV, MAV, MRV) for each major muscle group\n"
            "2. Appropriate intensity parameters (rep ranges, RPE, rest periods) aligned with goals\n"
            "3. Clear progression guidelines for both volume and intensity\n"
            "4. Deload recommendations based on training age and recovery capacity\n"
            "5. Special considerations based on individual factors\n\n"
            
            "Create a complete volume and intensity prescription with scientific justification for your recommendations. "
            "Explain how these guidelines optimize muscular adaptation while respecting individual recovery capacity."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=VolumeIntensityRecommendation)
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