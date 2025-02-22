from typing import Dict, Any
from pydantic import BaseModel

class CheckInDataIngestionModule:
    def process_check_in_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Organizes check-in data into a clean structure without complex processing.
        """
        try:
            standardized_data = {
                "user_info": self._get_user_info(raw_data),
                "meal_data": self._get_meal_data(raw_data),
                "training_data": self._get_training_data(raw_data),
                "body_metrics": self._get_body_metrics(raw_data),
                "recovery_data": self._get_recovery_data(raw_data),
            }
            
            return standardized_data
            
        except Exception as e:
            return {
                "error": f"Error processing check-in data: {str(e)}",
                "raw_data": raw_data
            }

    def _get_user_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gets basic user information."""
        return {
            "user_id": raw_data.get("userId", ""),
            "analysis_report": raw_data.get("analysisReportStart", "")
        }

    def _get_meal_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gets meal plan data in a structured format."""
        meal_plan = raw_data.get("mealPlanLastWeek", {})
        
        return {
            "meal_plan_details": meal_plan,
            "training_day_meals": self._extract_meals(meal_plan, "Training Day"),
            "non_training_day_meals": self._extract_meals(meal_plan, "Non-Training Day")
        }

    def _extract_meals(self, meal_plan: str, meal_type: str) -> list:
        """Extract meals of specific type from meal plan."""
        # Basic extraction of meals based on type
        if not meal_plan:
            return []
            
        meals = []
        if "Training Day Meals:" in meal_plan and meal_type == "Training Day":
            meals = meal_plan.split("Training Day Meals:")[1].split("Not Training Day Meals:")[0]
        elif "Not Training Day Meals:" in meal_plan and meal_type == "Non-Training Day":
            meals = meal_plan.split("Not Training Day Meals:")[1]
            
        return meals.strip() if isinstance(meals, str) else meals

    def _get_training_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gets training data in a structured format."""
        return {
            "workout_details": raw_data.get("userWorkoutDetailsLastWeek", ""),
            "exercise_logs": raw_data.get("exercisesLogLastWeek", ""),
            "exercises": self._extract_exercises(raw_data.get("exercisesLogLastWeek", ""))
        }

    def _extract_exercises(self, exercise_log: str) -> list:
        """Extract exercises from exercise log."""
        if not exercise_log:
            return []
            
        exercises = []
        for line in exercise_log.split('\n'):
            if "Exercise ID:" in line:
                exercise = {}
                exercise["id"] = line.split("Exercise ID:")[1].strip()
                # Get weight if it exists in next line
                weight_line = next((l for l in exercise_log.split('\n') if "Weights:" in l), None)
                if weight_line:
                    exercise["weight"] = weight_line.split("Weights:")[1].strip()
                exercises.append(exercise)
                
        return exercises

    def _get_body_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gets body measurement data in a structured format."""
        measurements = raw_data.get("bodyMeasurementsLastWeek", {})
        
        return {
            "dates": measurements.get("dates", {}),
            "measurements": measurements.get("measurements", {})
        }

    def _get_recovery_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gets recovery and daily report data in a structured format."""
        daily_reports = raw_data.get("dailyReportsLastWeek", "")
        
        reports = []
        current_report = {}
        
        if daily_reports:
            lines = daily_reports.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("Day"):
                    if current_report:
                        reports.append(current_report)
                    current_report = {"day": line}
                elif ":" in line:
                    key, value = line.split(":", 1)
                    current_report[key.strip()] = value.strip()
            
            if current_report:
                reports.append(current_report)
        
        return {
            "daily_reports": reports
        }