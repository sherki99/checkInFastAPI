# check_time_plans/data_ingestion/training_logs.py

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

class ExercisePerformance(BaseModel):
    name: str
    planned_sets: Optional[int]
    completed_sets: int
    planned_reps: Optional[int]
    avg_completed_reps: float
    planned_weight: Optional[float]
    actual_weight: float
    weight_progression: float  # Percentage change
    completion_rate: float  # Percentage

class WorkoutAdherence(BaseModel):
    planned_workouts: int
    completed_workouts: int
    adherence_percentage: float
    exercise_performances: List[ExercisePerformance]
    training_intensity_adherence: float  # Percentage
    volume_completed_percentage: float
    main_issues: List[str]

class TrainingLogsExtractor:
    """Module for extracting training log data from standardized check-in data."""
    
    def extract_training_logs(self, exercise_logs: List[Any], workout_plan: Any = None) -> WorkoutAdherence:
        """
        Extracts training adherence metrics by comparing exercise logs with workout plan.
        
        Args:
            exercise_logs: Standardized exercise log data
            workout_plan: Optional workout plan to compare against logs
            
        Returns:
            WorkoutAdherence: Calculated workout adherence metrics
        """
        # Default values
        planned_workouts = 0
        completed_workouts = 0
        adherence_percentage = 0.0
        exercise_performances = []
        training_intensity = 0.0
        volume_completed = 0.0
        issues = []
        
        # Count planned workouts from workout plan if available
        if workout_plan:
            planned_workouts = sum(1 for day in workout_plan.schedule if day.type == "Training Day")
        
        # Count completed workouts from exercise logs
        # This is a simple approximation - in a real system you would match dates
        exercise_dates = set()
        for exercise in exercise_logs:
            for entry in exercise.entries:
                exercise_dates.add(entry.date)
        
        completed_workouts = len(exercise_dates)
        
        # Calculate adherence percentage
        if planned_workouts > 0:
            adherence_percentage = (completed_workouts / planned_workouts) * 100
        else:
            adherence_percentage = 100 if completed_workouts > 0 else 0
        
        # Process individual exercises
        for exercise in exercise_logs:
            # Skip if no entries
            if not exercise.entries:
                continue
                
            # For this example, we'll create simple metrics
            exercise_name = exercise.name
            completed_sets = len(exercise.entries)
            actual_weight = sum(entry.weight for entry in exercise.entries) / completed_sets if completed_sets > 0 else 0
            
            # Try to find planned exercise data if workout plan is available
            planned_sets = None
            planned_reps = None
            planned_weight = None
            
            if workout_plan:
                for day in workout_plan.schedule:
                    if day.exercises:
                        for planned_ex in day.exercises:
                            if planned_ex.name.lower() == exercise_name.lower():
                                planned_sets = planned_ex.sets
                                planned_reps = planned_ex.reps
                                # Planned weight not available in this data structure
                                break
            
            # Calculate metrics
            avg_completed_reps = 10  # Placeholder, not available in data
            weight_progression = 0  # Placeholder, would need historical data
            
            # Calculate completion rate
            completion_rate = 100.0
            if planned_sets:
                completion_rate = min(100, (completed_sets / planned_sets) * 100)
            
            exercise_performances.append(
                ExercisePerformance(
                    name=exercise_name,
                    planned_sets=planned_sets,
                    completed_sets=completed_sets,
                    planned_reps=planned_reps,
                    avg_completed_reps=avg_completed_reps,
                    planned_weight=planned_weight,
                    actual_weight=actual_weight,
                    weight_progression=weight_progression,
                    completion_rate=completion_rate
                )
            )
        
        # Calculate overall metrics and identify issues
        training_intensity = 90.0  # Placeholder value
        volume_completed = 85.0  # Placeholder value
        
        if adherence_percentage < 80:
            issues.append("Low workout completion rate")
        if volume_completed < 80:
            issues.append("Training volume below target")
        
        return WorkoutAdherence(
            planned_workouts=planned_workouts,
            completed_workouts=completed_workouts,
            adherence_percentage=adherence_percentage,
            exercise_performances=exercise_performances,
            training_intensity_adherence=training_intensity,
            volume_completed_percentage=volume_completed,
            main_issues=issues
        )
