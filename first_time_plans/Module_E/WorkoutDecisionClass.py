from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ExerciseDetail(BaseModel):
    """Details for a specific exercise in the workout plan."""
    name: str = Field(..., description="Name of the exercise")
    sets: int = Field(..., description="Number of sets")
    reps: str = Field(..., description="Rep range (e.g., '8-10', '12')")
    rest: str = Field(..., description="Rest period between sets in seconds")
    intensity: str = Field(..., description="Intensity level (High/Medium/Low)")
    notes: Optional[str] = Field(None, description="Special instructions or form cues")

class WorkoutDay(BaseModel):
    """Complete workout plan for a specific training day."""
    day_name: str = Field(..., description="Name of the workout day (e.g., 'Push Day', 'Upper Body')")
    target_muscle_groups: List[str] = Field(..., description="Primary muscle groups targeted")
    exercises: List[ExerciseDetail] = Field(..., description="List of exercises for this workout day")
    notes: Optional[str] = Field(None, description="Special notes for this workout day")

class CompletePlan(BaseModel):
    """Complete structured workout plan."""
    plan_name: str = Field(..., description="Name/title of the workout plan")
    description: str = Field(..., description="Brief description of the workout program and its goals")
    days: List[WorkoutDay] = Field(..., description="Detailed breakdown of each workout day")
    rest_days: List[str] = Field(..., description="Specified rest days in the program")
    progression_notes: Optional[str] = Field(None, description="Guidelines for progression and overload")

class WorkoutDecisionClass:
    """
    Integrates training split, volume/intensity, and exercise selection decisions
    to generate a complete, formatted workout plan that follows Dr. Mike Israetel's principles.
    
    This class serves as the final workout plan generator, taking the outputs from 
    previous decision nodes and formatting them into a comprehensive, client-ready
    workout program that includes specific exercises, sets, reps, and training schedule.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the WorkoutDecisionClass with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self,
        client_data: Dict[str, Any],
        split_recommendation: Dict[str, Any],
        volume_guidelines: Dict[str, Any],
        exercise_selection: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process decision node outputs to generate a complete workout plan.
        
        Args:
            client_data: Standardized client profile data
            split_recommendation: Output from TrainingSplitDecisionNode
            volume_guidelines: Output from VolumeAndIntensityDecisionNode
            exercise_selection: Output from ExerciseSelectionDecisionNode
            goal_analysis: Client goals analysis output
            history_analysis: Training history analysis output
            body_analysis: Body composition analysis output
            
        Returns:
            Dict containing the formatted workout plan and relevant metadata
        """
        try:
            # Generate the complete workout plan
            workout_plan = self._generate_workout_plan(
                client_data,
                split_recommendation,
                volume_guidelines,
                exercise_selection,
                goal_analysis,
                history_analysis,
                body_analysis
            )
            
            # Format the workout plan according to the required format
            formatted_plan = self._format_workout_plan(workout_plan)
            
            return {
                "workout_plan": workout_plan,
                "formatted_workout_plan": formatted_plan
            }
            
        except Exception as e:
            logger.error(f"Error generating workout plan: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in workout plan generation.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are an expert exercise scientist and strength coach specializing in program design, "
            "following Dr. Mike Israetel's principles of scientific hypertrophy training. Your task is "
            "to create a detailed, executable workout plan based on previous analyses of the client's "
            "training split, volume/intensity needs, and exercise selection requirements.\n\n"
            
            "Follow these guidelines when generating the workout plan:\n"
            "1. **Evidence-Based Programming**: Apply scientific principles regarding volume landmarks (MEV, MAV, MRV), "
            "frequency, exercise selection, and training splits.\n"
            "2. **Progressive Overload Framework**: Include clear progression strategies that respect recovery capacity "
            "and training experience.\n"
            "3. **Specificity Principle**: Ensure exercises, volume, and intensity match the client's specific goals.\n"
            "4. **Individual Considerations**: Account for the client's recovery capacity, training age, and any "
            "limitations.\n"
            "5. **Exercise Execution**: Include precise technical notes for proper exercise execution.\n"
            "6. **Format Compliance**: Strictly follow the required output format for the workout plan.\n\n"
            
            "Your output should be a comprehensive workout plan that a client can immediately begin following, "
            "with clear instructions for exercises, sets, reps, rest periods, and progression strategies."
        )
    
    def _generate_workout_plan(
        self,
        client_data: Dict[str, Any],
        split_recommendation: Dict[str, Any],
        volume_guidelines: Dict[str, Any],
        exercise_selection: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any]
    ) -> CompletePlan:
        """
        Generate a complete workout plan using the LLM based on decision node outputs.
        
        Args:
            client_data: Standardized client profile data
            split_recommendation: Output from TrainingSplitDecisionNode
            volume_guidelines: Output from VolumeAndIntensityDecisionNode
            exercise_selection: Output from ExerciseSelectionDecisionNode
            goal_analysis: Client goals analysis output
            history_analysis: Training history analysis output
            body_analysis: Body composition analysis output
            
        Returns:
            CompletePlan object containing the complete workout plan
        """
        # Extract relevant client info
        client_name = client_data.get("personal_info", {}).get("name", "Client")
        primary_goals = goal_analysis.get("goal_analysis_schema", {}).get("primary_goals", [])
        
        # Get training split details
        split_type = split_recommendation.get("split_type", "Full Body")
        training_frequency = split_recommendation.get("training_frequency", 3)
        split_days = split_recommendation.get("split_days", [])
        
        # Get volume/intensity guidelines
        intensity_guidelines = volume_guidelines.get("volume_intensity_recommendation", {}).get("intensity_guidelines", {})
        muscle_group_recommendations = volume_guidelines.get("volume_intensity_recommendation", {}).get("muscle_group_guidelines", [])
        
        # Construct the prompt
        prompt = (
            f"Create a detailed workout plan for {client_name} based on the following analyses:\n\n"
            
            f"PRIMARY GOALS:\n{', '.join(primary_goals)}\n\n"
            
            f"TRAINING SPLIT RECOMMENDATION:\n"
            f"Split Type: {split_type}\n"
            f"Training Frequency: {training_frequency} days per week\n\n"
                
            f"SPLIT DAYS:\n"
            f"{json.dumps(split_days, indent=2)}\n\n"

            f"VOLUME AND INTENSITY GUIDELINES:\n"
            f"{json.dumps(volume_guidelines.get('volume_intensity_recommendation', {}), indent=2)}\n\n"
            
            f"EXERCISE SELECTION:\n"
            f"{json.dumps(exercise_selection, indent=2)}\n\n"

            
            "Generate a complete workout plan that includes:\n"
            "1. A descriptive name for the program\n"
            "2. A brief overview of the program's principles and goals\n"
            "3. Detailed workout for each training day including:\n"
            "   - Specific exercises with sets, reps, rest periods, and intensity\n"
            "   - Technical notes for proper execution\n"
            "4. Rest day recommendations\n"
            "5. Progression guidelines\n\n"
            
            "Follow Dr. Mike Israetel's principles for exercise selection, volume landmarks, and progression strategies. "
            "Create a plan that is immediately executable by the client."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=CompletePlan)
        return result
    
    def _format_workout_plan(self, workout_plan: CompletePlan) -> str:
        """
        Format the workout plan according to the required output format.
        
        Args:
            workout_plan: CompletePlan object containing the complete workout plan
            
        Returns:
            Formatted workout plan as a string
        """
        formatted_output = f"### Workout Plan: {workout_plan.plan_name}  \n"
        formatted_output += f"**Description**: {workout_plan.description}  \n\n"
        
        # Format each workout day
        for day in workout_plan.days:
            formatted_output += f"#### **{day.day_name}**  \n"
            
            for exercise in day.exercises:
                formatted_output += f"- **{exercise.name}**  \n"
                formatted_output += f"  - Sets: {exercise.sets}  \n"
                formatted_output += f"  - Reps: {exercise.reps}  \n"
                formatted_output += f"  - Rest: {exercise.rest}  \n"
                formatted_output += f"  - Intensity: {exercise.intensity}  \n"
                
                if exercise.notes:
                    formatted_output += f"  - Notes: {exercise.notes}  \n"
                
                formatted_output += "\n"
            
            if day.notes:
                formatted_output += f"*{day.notes}*  \n\n"
        
        # Format rest days
        for rest_day in workout_plan.rest_days:
            formatted_output += f"#### **{rest_day}**  \n"
            formatted_output += "*(No exercises. Full recovery day.)*  \n\n"
        
        # Add progression notes if available
        if workout_plan.progression_notes:
            formatted_output += f"### Progression Guidelines:  \n{workout_plan.progression_notes}"
        
        return formatted_output