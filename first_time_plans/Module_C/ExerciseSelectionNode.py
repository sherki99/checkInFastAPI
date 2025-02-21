from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ExerciseDetails(BaseModel):
    """Detailed information about a selected exercise."""
    name: str = Field(..., description="Full name of the exercise")
    category: str = Field(..., description="Category (Compound/Isolation/Accessory)")
    equipment: str = Field(..., description="Equipment required (Barbell/Dumbbell/Machine/Bodyweight/Cable)")
    primary_muscles: List[str] = Field(..., description="Primary muscles targeted")
    secondary_muscles: List[str] = Field(..., description="Secondary muscles engaged")
    joint_action: str = Field(..., description="Primary joint action (e.g., 'Hip Hinge', 'Knee Extension')")
    rep_range: str = Field(..., description="Recommended rep range based on goals")
    technical_difficulty: str = Field(..., description="Level of technical skill required (Low/Medium/High)")
    risk_profile: str = Field(..., description="Injury risk assessment (Low/Medium/High)")
    progression_options: List[str] = Field(..., description="Ways to progress this exercise over time")
    regression_options: List[str] = Field(..., description="Simpler variations if needed")

class MuscleFocusGroup(BaseModel):
    """Group of exercises targeting a specific muscle group."""
    muscle_group: str = Field(..., description="Target muscle group (e.g., 'Chest', 'Back', 'Legs')")
    training_priority: str = Field(..., description="Priority level for this muscle group (High/Medium/Low)")
    primary_exercises: List[ExerciseDetails] = Field(..., description="Main compound exercises")
    secondary_exercises: List[ExerciseDetails] = Field(..., description="Secondary/isolation exercises")
    scientific_rationale: str = Field(..., description="Exercise selection rationale based on biomechanics and goals")

class TrainingDayPlan(BaseModel):
    """Complete exercise selection for a specific training day."""
    day_focus: str = Field(..., description="Focus of this training day (e.g., 'Push', 'Pull', 'Lower Body')")
    muscle_groups_targeted: List[str] = Field(..., description="All muscle groups trained on this day")
    recommended_exercise_order: List[str] = Field(..., description="Optimal exercise sequence")
    muscle_focus_groups: List[MuscleFocusGroup] = Field(..., description="Detailed exercise selection by muscle group")
    total_volume_guideline: str = Field(..., description="Volume guideline for this training day")
    workout_duration_estimate: str = Field(..., description="Estimated workout duration")

class ExerciseSelectionPlan(BaseModel):
    """Complete exercise selection plan for the entire training program."""
    client_name: str = Field(..., description="Client's name")
    primary_goal: str = Field(..., description="Client's primary training goal")
    training_split: str = Field(..., description="Selected training split (e.g., 'Upper/Lower', 'PPL')")
    weekly_training_days: List[TrainingDayPlan] = Field(..., description="Exercise selection for each training day")
    exercise_selection_principles: List[str] = Field(..., description="Scientific principles guiding exercise selection")
    client_specific_adaptations: List[str] = Field(..., description="Exercise modifications based on client needs")
    progression_strategy: str = Field(..., description="Overall exercise progression strategy")
    variety_recommendations: str = Field(..., description="Guidelines for exercise rotation and variation")

class ExerciseSelectionDecisionNode:
    """
    Determines optimal exercise selection based on client data, training history,
    and recommendations from previous decision nodes.
    
    This class uses an LLM-driven decision process to select exercises that align
    with the client's goals, biomechanical needs, training history, and the
    established training split and volume guidelines.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the ExerciseSelectionDecisionNode with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self,
        standardized_profile: Dict[str, Any],
        history_analysis: Dict[str, Any],
        split_recommendation: Dict[str, Any],
        volume_guidelines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal exercise selection.
        
        This method integrates data from previous analysis modules to select
        the most appropriate exercises for the client, considering:
        - Training split structure
        - Volume guidelines for each muscle group
        - Individual biomechanics and injury history
        - Training experience and exercise proficiency
        - Equipment availability and preferences
        
        Args:
            standardized_profile: Standardized client profile data
            history_analysis: Training history and experience analysis
            split_recommendation: Recommended training split
            volume_guidelines: Volume and intensity guidelines
            
        Returns:
            A dictionary containing the structured exercise selection plan
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_exercise_selection_schema(
                standardized_profile, history_analysis, split_recommendation, volume_guidelines
            )
            
            return {
                "exercise_selection_plan": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining exercise selection: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in exercise selection decision-making.
        
        The system message establishes the context and criteria for selecting
        optimal exercises according to scientific principles of biomechanics and exercise science.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are an exercise selection specialist with expertise in biomechanics, "
            "exercise science, and program design. Your task is to select optimal exercises "
            "for a client based on their goals, training history, biomechanical needs, "
            "equipment availability, and the established training split and volume guidelines.\n\n"
            
            "Apply these scientific principles when selecting exercises:\n"
            "1. **Exercise Classification**: Categorize exercises as compound, isolation, or accessory "
            "based on the number of joints involved and muscle recruitment patterns.\n"
            "2. **Movement Pattern Balance**: Ensure balanced training across all fundamental movement patterns "
            "(push, pull, squat, hinge, carry, rotation).\n"
            "3. **Biomechanical Efficiency**: Select exercises that match the client's anthropometry and "
            "joint mechanics for optimal force production and safety.\n"
            "4. **Exercise Sequencing**: Order exercises to prioritize neural fatigue management, with "
            "compound movements preceding isolation work.\n"
            "5. **Progressive Overload Potential**: Choose exercises that allow for clear progression pathways "
            "through load, volume, or technical complexity.\n"
            "6. **Exercise Specificity**: Align exercise selection with the primary training goal "
            "(hypertrophy, strength, endurance).\n"
            "7. **Individual Adaptation**: Consider injury history, mobility limitations, and exercise preferences.\n\n"
            
            "Your exercise selection should include a mix of compound and isolation exercises, "
            "with appropriate variations based on the client's experience level and biomechanical needs. "
            "For each exercise, provide clear technical guidelines and progression strategies."
        )

    def _determine_exercise_selection_schema(
        self,
        standardized_profile: Dict[str, Any],
        history_analysis: Dict[str, Any],
        split_recommendation: Dict[str, Any],
        volume_guidelines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine exercise selection using Pydantic schema validation.
        
        Args:
            standardized_profile: Standardized client profile data
            history_analysis: Training history and experience analysis
            split_recommendation: Recommended training split
            volume_guidelines: Volume and intensity guidelines
            
        Returns:
            Structured exercise selection plan as a Pydantic model
        """
        # Extract relevant data from standardized profile
        client_name = standardized_profile.get("personal", {}).get("data", {}).get("name", "Client")
        gender = standardized_profile.get("personal", {}).get("data", {}).get("gender", "Unknown")
        age = standardized_profile.get("personal", {}).get("data", {}).get("age", "Unknown")
        
        # Extract equipment availability
        equipment = standardized_profile.get("fitness", {}).get("data", {}).get("fitnessEquipment", "Unknown")
        
        # Extract exercise preferences
        liked_exercises = standardized_profile.get("fitness", {}).get("data", {}).get("exercise_mostLiked", "Unknown")
        disliked_exercises = standardized_profile.get("fitness", {}).get("data", {}).get("exercise_leastLiked", "Unknown")
        
        # Extract training split information
        split_schema = split_recommendation.get("split_recommendation_schema", {})
        split_name = split_schema.get("split_name", "Unknown Split")
        weekly_schedule = split_schema.get("weekly_schedule", {})
        
        # Extract volume guidelines
        volume_intensity_rec = volume_guidelines.get("volume_intensity_recommendation", {})
        muscle_guidelines = volume_intensity_rec.get("muscle_group_guidelines", [])
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Select optimal exercises for this client based on their profile, training history, "
            "and the established training split and volume guidelines. Apply principles of biomechanics "
            "and exercise science to create a comprehensive exercise selection plan.\n\n"
            
            f"CLIENT PROFILE:\n"
            f"- Name: {client_name}\n"
            f"- Gender: {gender}\n"
            f"- Age: {age}\n"
            f"- Available Equipment: {equipment}\n"
            f"- Preferred Exercises: {liked_exercises}\n"
            f"- Disliked/Problematic Exercises: {disliked_exercises}\n\n"
            
            f"TRAINING SPLIT: {split_name}\n"
            f"Weekly Schedule:\n{self._format_dict(weekly_schedule)}\n\n"
            
            f"VOLUME GUIDELINES BY MUSCLE GROUP:\n{self._format_dict(muscle_guidelines)}\n\n"
            
            f"TRAINING HISTORY ANALYSIS:\n{self._format_dict(history_analysis)}\n\n"
            
            "Your exercise selection plan should include:\n"
            "1. Detailed exercise selection for each training day in the split\n"
            "2. Appropriate exercise ordering within each session\n"
            "3. A mix of compound and isolation exercises for each muscle group\n"
            "4. Biomechanically appropriate variations based on client anthropometry\n"
            "5. Clear progression and regression options for each exercise\n"
            "6. Exercise modifications to accommodate any limitations or preferences\n\n"
            
            "Consider exercise selection through the lens of Scientific Principles of Strength Training "
            "(Israetel, Feather, and Hoffman): specificity, overload, fatigue management, SRA curve, "
            "variation, phase potentiation, and individual differences."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=ExerciseSelectionPlan)
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