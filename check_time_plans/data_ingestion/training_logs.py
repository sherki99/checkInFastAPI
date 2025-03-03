from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ExerciseProgressionMetrics(BaseModel):
    """Metrics for measuring progression in a specific exercise."""
    exercise_name: str = Field(..., description="Name of the exercise")
    starting_weight: float = Field(..., description="Initial weight used (in kg/lbs)")
    current_weight: float = Field(..., description="Most recent weight used (in kg/lbs)")
    weight_change: float = Field(..., description="Change in weight from start to current")
    weight_change_percentage: float = Field(..., description="Percentage change in weight")
    progression_rate: float = Field(..., description="Average increase per week/session")
    consistency_score: float = Field(..., description="Score measuring training consistency (0-10)")
    performance_trend: str = Field(..., description="Overall trend description (e.g., 'Steady increase', 'Plateau')")

class MuscleGroupProgress(BaseModel):
    """Assessment of progression for a muscle group based on multiple exercises."""
    muscle_group: str = Field(..., description="Name of the muscle group (e.g., 'Chest', 'Back', 'Legs')")
    primary_exercises: List[str] = Field(..., description="Main exercises used for this muscle group")
    average_progression_rate: float = Field(..., description="Average progression rate across exercises")
    strongest_exercise: str = Field(..., description="Exercise with best progression")
    weakest_exercise: str = Field(..., description="Exercise with least progression")
    volume_adherence: float = Field(..., description="Adherence to prescribed training volume (%)")
    overall_strength_change: str = Field(..., description="Overall strength change assessment")

class TrainingLogsAnalysis(BaseModel):
    """Comprehensive analysis of client's training logs and performance."""
    exercises_progression: List[ExerciseProgressionMetrics] = Field(..., description="Progression metrics for individual exercises")
    muscle_groups_assessment: List[MuscleGroupProgress] = Field(..., description="Assessment by muscle group")
    strongest_lifts: List[str] = Field(..., description="Exercises with greatest absolute strength")
    most_improved_lifts: List[str] = Field(..., description="Exercises with greatest relative improvement")
    least_improved_lifts: List[str] = Field(..., description="Exercises with least improvement")
    training_consistency: float = Field(..., description="Overall training session adherence (%)")
    volume_completion_rate: float = Field(..., description="Overall prescribed volume completion (%)")
    intensity_adherence: float = Field(..., description="Adherence to prescribed intensity targets (%)")
    technique_observations: Optional[str] = Field(None, description="Observations about technique (if reported)")
    common_limiting_factors: List[str] = Field(..., description="Frequently reported limiting factors")
    energy_level_patterns: str = Field(..., description="Patterns in reported energy levels")
    performance_trends: str = Field(..., description="Overall performance trends and patterns")

class TrainingLogsExtractor:
    """
    Extracts and analyzes client training log data.
    
    This class processes training logs to evaluate exercise progression,
    training consistency, and performance patterns over time, providing
    insights for program adjustment and optimization.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the TrainingLogsExtractor with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def extract_training_logs(self, training_logs: List[Dict[str, Any]], workout_plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process training logs to analyze exercise progression and performance.
        
        This method evaluates training log data to track progression on individual
        exercises, assess muscle group development, and identify performance patterns.
        
        Args:
            training_logs: The client's exercise logs over time
            workout_plan: The client's prescribed workout plan (optional for comparison)
            
        Returns:
            A dictionary containing structured training logs analysis
        """
        try:
            # Process using the schema-based approach
            schema_result = self._analyze_training_logs_schema(training_logs, workout_plan)
            
            return {
                "training_logs_analysis": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error analyzing training logs: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in training log analysis.
        
        The system message establishes the context and criteria for analyzing
        training performance according to exercise science principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are an exercise science specialist with expertise in strength and performance analysis. "
            "Your task is to analyze a client's training logs to evaluate progression, consistency, "
            "and performance patterns that can inform program adjustments.\\n\\n"
            
            "Apply these principles when analyzing training logs:\\n"
            "1. **Progressive Overload**: Track increases in weight, reps, or volume over time.\\n"
            "2. **Exercise Selection**: Evaluate performance across different movement patterns.\\n"
            "3. **Training Consistency**: Assess adherence to planned training frequency.\\n"
            "4. **Volume Completion**: Compare completed vs. prescribed training volume.\\n"
            "5. **Intensity Adherence**: Analyze adherence to prescribed intensity targets.\\n"
            "6. **Strength Imbalances**: Identify relative strengths and weaknesses.\\n"
            "7. **Performance Patterns**: Recognize trends in exercise performance.\\n\\n"
            
            "Your analysis should provide actionable insights about the client's training response, "
            "highlighting both strengths and opportunities for improvement, with particular focus "
            "on progression patterns that can guide program modifications."
        )
    
    def _analyze_training_logs_schema(
        self,
        training_logs: List[Dict[str, Any]],
        workout_plan: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze training logs using Pydantic schema validation.
        
        Args:
            training_logs: The client's exercise logs over time
            workout_plan: The client's prescribed workout plan
            
        Returns:
            Structured training logs analysis as a Pydantic model
        """
        # Extract exercise names and organize log data
        exercise_names = []
        for log in training_logs:
            if log.get("name") and log.get("name") not in exercise_names:
                exercise_names.append(log.get("name"))
                
        # Extract workout plan details if available
        plan_name = ""
        plan_schedule = []
        if workout_plan:
            plan_name = workout_plan.get("name", "Unnamed Plan")
            plan_schedule = workout_plan.get("schedule", [])
        
        # Construct detailed prompt with training data
        prompt = (
            "Analyze this client's training logs to evaluate exercise progression, training consistency, "
            "and performance patterns. Identify strengths, weaknesses, and actionable insights for program adjustment.\\n\\n"
            
            f"EXERCISE LOGS SUMMARY:\\n"
            f"- Total exercises tracked: {len(exercise_names)}\\n"
            f"- Exercise names: {', '.join(exercise_names)}\\n\\n"
            
            f"DETAILED TRAINING LOGS:\\n{self._format_training_logs(training_logs)}\\n\\n"
        )
        
        # Add workout plan information if available
        if workout_plan:
            prompt += (
                f"WORKOUT PLAN:\\n"
                f"- Plan name: {plan_name}\\n"
                f"- Schedule: {self._format_workout_schedule(plan_schedule)}\\n\\n"
            )
        
        prompt += (
            "Your training logs analysis should include:\\n"
            "1. Progression metrics for each tracked exercise\\n"
            "2. Assessment by muscle group\\n"
            "3. Identification of strongest and weakest lifts\\n"
            "4. Training consistency and adherence analysis\\n"
            "5. Performance trends and patterns\\n"
            "6. Common limiting factors affecting performance\\n\\n"
            
            "Create a complete training logs analysis with actionable insights for program optimization."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=TrainingLogsAnalysis)
        return result
    
    def _format_training_logs(self, logs: List[Dict[str, Any]]) -> str:
        """
        Format training log data as a readable string for inclusion in prompts.
        
        Args:
            logs: List of training log dictionaries
            
        Returns:
            Formatted string representation
        """
        if not logs:
            return "No training logs available."
        
        # Group logs by exercise
        exercise_logs = {}
        for log in logs:
            name = log.get("name", "Unnamed Exercise")
            if name not in exercise_logs:
                exercise_logs[name] = []
            
            entries = log.get("entries", [])
            exercise_logs[name].extend(entries)
        
        # Format each exercise's log
        formatted = ""
        for exercise, entries in exercise_logs.items():
            # Sort entries by date
            sorted_entries = sorted(entries, key=lambda x: x.get("date", ""), reverse=False)
            
            formatted += f"  {exercise}:\\n"
            for entry in sorted_entries:
                date = entry.get("date", "Unknown date")
                weight = entry.get("weight", "N/A")
                reps = entry.get("reps", "")
                sets = entry.get("sets", "")
                
                entry_details = f"    - {date}: {weight} "
                if reps:
                    entry_details += f"for {reps} reps "
                if sets:
                    entry_details += f"x {sets} sets "
                    
                notes = entry.get("notes", "")
                if notes:
                    entry_details += f"(Notes: {notes})"
                
                formatted += f"{entry_details}\\n"
            
            formatted += "\\n"
        
        return formatted
    
    def _format_workout_schedule(self, schedule: List[Dict[str, Any]]) -> str:
        """
        Format workout schedule as a readable string for inclusion in prompts.
        
        Args:
            schedule: List of workout days
            
        Returns:
            Formatted string representation
        """
        if not schedule:
            return "No workout schedule available."
        
        formatted = ""
        for day_info in schedule:
            day = day_info.get("day", "Unknown")
            day_type = day_info.get("type", "Training")
            
            formatted += f"  Day {day} - {day_type}:\\n"
            
            if day_type != "Rest Day":
                exercises = day_info.get("exercises", [])
                for ex in exercises:
                    ex_name = ex.get("name", "Unnamed exercise")
                    sets = ex.get("sets", "")
                    reps = ex.get("reps", "")
                    
                    formatted += f"    - {ex_name}: "
                    if sets and reps:
                        formatted += f"{sets} sets x {reps} reps"
                    
                    formatted += "\\n"
            
            formatted += "\\n"
        
        return formatted
    
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