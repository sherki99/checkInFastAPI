from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SplitDayDetails(BaseModel):
    """Details for a specific training day in the split."""
    day_name: str = Field(..., description="Name of the training day (e.g., 'Push Day', 'Upper Body')")
    primary_muscle_groups: List[str] = Field(..., description="Primary muscle groups targeted in this day")
    secondary_muscle_groups: List[str] = Field(..., description="Secondary/accessory muscle groups")
    volume_allocation: str = Field(..., description="Volume allocation guidance (e.g., '15-20 sets total')")
    exercise_count_recommendation: str = Field(..., description="Recommended number of exercises (e.g., '4-6 exercises')")
    key_exercise_types: List[str] = Field(..., description="Types of exercises to include (e.g., 'Compound push', 'Isolation')")
    sample_exercises: List[str] = Field(..., description="Example exercises for this training day")
    intensity_guideline: str = Field(..., description="Intensity guidelines specific to this day")
    
class SplitSchedulingGuideline(BaseModel):
    """Guidelines for implementing the training split schedule."""
    weekly_structure: str = Field(..., description="Weekly training day arrangement (e.g., 'M-W-F rest pattern')")
    rest_day_recommendations: str = Field(..., description="Guidance on scheduling rest days")
    deload_strategy: str = Field(..., description="Approach to scheduling deloads in the split")
    recovery_considerations: List[str] = Field(..., description="Recovery factors to consider when scheduling")
    flexibility_options: List[str] = Field(..., description="Ways to adapt the split for schedule changes")

class TrainingSplitRecommendation(BaseModel):
    """Complete training split recommendation with scientific rationale."""
    split_type: str = Field(..., description="Type of split recommended (e.g., 'Upper/Lower', 'Push/Pull/Legs')")
    training_frequency: int = Field(..., description="Total training days per week")
    muscle_group_frequency: str = Field(..., description="Frequency each muscle group is trained per week")
    split_days: List[SplitDayDetails] = Field(..., description="Details for each training day in the split")
    scheduling_guidelines: SplitSchedulingGuideline = Field(..., description="Guidelines for implementing the split")
    key_benefits: List[str] = Field(..., description="Primary benefits of this split for the client")
    scientific_rationale: str = Field(..., description="Scientific justification for this split recommendation")
    individual_considerations: List[str] = Field(..., description="Client-specific factors considered in recommendation")
    progression_strategy: str = Field(..., description="How to progress the split over time")

class TrainingSplitDecisionNode:
    """
    Determines the optimal training split based on client data and analysis from previous modules.
    
    This class uses an LLM-driven decision process to generate a scientifically-grounded
    training split recommendation that aligns with the client's goals, recovery capacity,
    training experience, individual constraints, and preferences.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the TrainingSplitDecisionNode with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self,
        client_profile: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process client data to determine the optimal training split.
        
        This method integrates data from multiple analysis modules to determine
        the most appropriate training split, considering:
        - Primary and secondary goals
        - Training experience and history
        - Body composition and proportions
        - Recovery capacity and lifestyle factors
        - Exercise preferences and limitations
        
        Args:
            client_profile: Standardized client profile data
            goal_analysis: Client goals and objectives analysis
            body_analysis: Body composition and measurement analysis
            history_analysis: Training history and experience analysis
            recovery_analysis: Recovery capacity and lifestyle analysis (optional)
            
        Returns:
            A dictionary containing the structured training split recommendation
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_training_split_schema(
                client_profile, goal_analysis, body_analysis, history_analysis, recovery_analysis
            )
            
            return {
                "training_split_recommendation": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining training split: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in training split decision-making.
        
        The system message establishes the context and criteria for determining
        optimal training split according to scientific principles of exercise science.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are an expert exercise scientist and strength coach with deep expertise in program design. "
            "Your task is to determine the optimal training split for a client based on their goals, training history, "
            "body composition, recovery capacity, and individual factors. Follow these evidence-based principles:\n\n"
            
            "1. **Frequency Optimization**: Consider both total training frequency and per-muscle group frequency based on "
            "the client's recovery capacity and training age. Research indicates that training muscle groups 2-3x weekly "
            "typically optimizes hypertrophy while 1-2x weekly may be sufficient for strength.\n\n"
            
            "2. **Volume Distribution**: Ensure the split allows appropriate volume distribution across muscle groups, "
            "prioritizing areas based on client goals and body analysis.\n\n"
            
            "3. **Fatigue Management**: Account for systemic and local fatigue by designing splits that separate "
            "high-fatigue movements and account for overlapping muscle stress.\n\n"
            
            "4. **Exercise Selection Compatibility**: Ensure the split allows for progression in key exercises and "
            "accommodates client preferences and limitations.\n\n"
            
            "5. **Recovery Consideration**: Balance training frequency with recovery capacity, accounting for lifestyle "
            "factors, stress levels, and sleep quality.\n\n"
            
            "6. **Individuality Principle**: Adapt general training split principles to the client's individual "
            "circumstances, goals, and preferences.\n\n"
            
            "Provide a detailed, scientific rationale for your recommendation that demonstrates clear "
            "connections between client data and split design choices."
        )

    def _determine_training_split_schema(
        self,
        client_profile: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Determine the optimal training split using Pydantic schema validation.
        
        Args:
            client_profile: Standardized client profile data
            goal_analysis: Client goals and objectives analysis
            body_analysis: Body composition and measurement analysis
            history_analysis: Training history and experience analysis
            recovery_analysis: Recovery capacity and lifestyle analysis (optional)
            
        Returns:
            Structured training split recommendation as a Pydantic model
        """
        # Extract relevant data for prompt construction
        goals = goal_analysis.get("goal_analysis_schema", {})
        primary_goals = goals.get("primary_goals", [])
        secondary_goals = goals.get("secondary_goals", [])
        
        training_experience = history_analysis.get("history_analysis_schema", {}).get("experience_level", "Intermediate")
        exercise_preferences = history_analysis.get("history_analysis_schema", {}).get("exercise_preferences", [])
        
        # Recovery factors if available
        recovery_capacity = "Unknown"
        stress_level = "Unknown"
        if recovery_analysis:
            recovery_capacity = recovery_analysis.get("recovery_analysis_schema", {}).get("overall_recovery_capacity", "Unknown")
            stress_level = recovery_analysis.get("recovery_analysis_schema", {}).get("stress_management", {}).get("stress_level_assessment", "Unknown")
        
        # Extract personal info and training status
        personal_info = client_profile.get("personal_info", {}).get("data", {})
        fitness_data = client_profile.get("fitness", {}).get("data", {})
        training_frequency = fitness_data.get("trainingFrequency", "")
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Design an optimal training split for this client based on their goals, training history, body composition, "
            "recovery capacity, and individual preferences. Apply scientific principles of exercise frequency, volume "
            "distribution, fatigue management, and recovery optimization.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Age: {personal_info.get('age', 'Unknown')}\n"
            f"- Gender: {personal_info.get('gender', 'Unknown')}\n"
            f"- Training experience: {training_experience}\n"
            f"- Current training frequency: {training_frequency}\n"
            f"- Primary goals: {', '.join(primary_goals)}\n"
            f"- Secondary goals: {', '.join(secondary_goals)}\n"
            f"- Recovery capacity: {recovery_capacity}\n"
            f"- Stress level: {stress_level}\n\n"
            
            f"EXERCISE PREFERENCES:\n"
            f"{self._format_exercise_preferences(exercise_preferences)}\n\n"
            
            f"GOAL ANALYSIS:\n{self._format_dict(goals)}\n\n"
            f"BODY ANALYSIS:\n{self._format_dict(body_analysis.get('body_analysis_schema', {}))}\n\n"
            f"HISTORY ANALYSIS:\n{self._format_dict(history_analysis.get('history_analysis_schema', {}))}\n\n"
            
            "Your training split recommendation should include:\n"
            "1. The specific type of split (e.g., full body, upper/lower, push/pull/legs)\n"
            "2. Training frequency (days per week) and muscle group frequency\n"
            "3. Detailed breakdown of each training day (muscles worked, volume allocation, exercise types)\n"
            "4. Scheduling guidelines (weekly structure, rest days, deload approach)\n"
            "5. Scientific rationale for this split considering the client's specific factors\n"
            "6. Individualized considerations based on client limitations or preferences\n\n"
            
            "Create a comprehensive training split recommendation that optimizes the client's results while "
            "respecting their recovery capacity, preferences, and limitations."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=TrainingSplitRecommendation)
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
    
    def _format_exercise_preferences(self, preferences: List[Dict[str, Any]]) -> str:
        """
        Format exercise preferences into a readable string.
        
        Args:
            preferences: List of exercise preference dictionaries
            
        Returns:
            Formatted string of exercise preferences
        """
        if not preferences:
            return "No specific exercise preferences provided."
        
        formatted = []
        for pref in preferences:
            exercise = pref.get("exercise_type", "Unknown exercise")
            preference = pref.get("preference_level", "neutral")
            effectiveness = pref.get("effectiveness_assessment", "Unknown effectiveness")
            recommendation = pref.get("inclusion_recommendation", "Consider")
            notes = pref.get("modification_notes", "None")
            
            formatted.append(
                f"- {exercise}: {preference}, {effectiveness}, Recommendation: {recommendation}"
                + (f", Notes: {notes}" if notes else "")
            )
        
        return "\n".join(formatted)