from typing import Dict, Any

class CheckInDataIngestionModule:
    """
    ClientCheckInModule processes raw client check-in data into a standardized profile.
    
    Expected raw_data structure:
    {
        "checkIn_info": {
            "mealPlanLastWeek": "...",
            "analysisReportStart": "...",
            "bodyMeasurementsLastWeek": { ... },
            "dailyReportsLastWeek": { ... },
            "exercisesLogLastWeek": { ... },
            "userWorkoutDetailsLastWeek": { ... }
        }
    }
    """

    def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw client check-in data and return a standardized profile.
        
        :param raw_data: Raw data dictionary from the client.
        :return: Standardized check-in profile with necessary sections.
        """
        standardized = {}
        
        check_in_info = raw_data.get("checkIn_info", {})
        
        standardized["meal_plan_last_week"] = check_in_info.get("mealPlanLastWeek", "")
        standardized["analysis_report_start"] = check_in_info.get("analysisReportStart", "")
        standardized["body_measurements_last_week"] = self._extract_body_measurements(check_in_info)
        standardized["daily_reports_last_week"] = self._extract_daily_reports(check_in_info)
        standardized["exercise_log_last_week"] = self._extract_exercise_log(check_in_info)
        standardized["user_workout_details_last_week"] = self._extract_user_workout_details(check_in_info)
        
        return standardized

    def _extract_body_measurements(self, check_in_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize body measurements.
        
        Assumes that the raw check_in_info contains a 'bodyMeasurementsLastWeek' key.
        """
        return check_in_info.get("bodyMeasurementsLastWeek", {})

    def _extract_daily_reports(self, check_in_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize daily reports.
        """
        return check_in_info.get("dailyReportsLastWeek", {})

    def _extract_exercise_log(self, check_in_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract exercise log data.
        """
        return check_in_info.get("exercisesLogLastWeek", {})

    def _extract_user_workout_details(self, check_in_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract user workout details.
        """
        return check_in_info.get("userWorkoutDetailsLastWeek", {})
