# check_time_plans/data_ingestion/meal_adherence.py

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

class MealComplianceMetrics(BaseModel):
    total_days_reported: int
    protein_adherence_percentage: float
    carb_adherence_percentage: float
    fat_adherence_percentage: float
    calorie_adherence_percentage: float
    meal_timing_adherence_percentage: float
    training_day_adherence: float
    non_training_day_adherence: float
    main_issues: List[str]

class MealAdherenceExtractor:
    """Module for extracting meal adherence data from standardized check-in data."""
    
    def extract_meal_adherence(self, meal_plan_data: Any, daily_reports: List[Any] = None) -> MealComplianceMetrics:
        """
        Extracts meal adherence metrics by comparing daily reports with meal plan.
        
        Args:
            meal_plan_data: Standardized meal plan data
            daily_reports: Optional daily reports to compare against meal plan
            
        Returns:
            MealComplianceMetrics: Calculated meal compliance metrics
        """
        # Default values
        days_reported = 0
        protein_compliance = 0.0
        carb_compliance = 0.0
        fat_compliance = 0.0
        calorie_compliance = 0.0
        timing_compliance = 0.0
        training_day_compliance = 0.0
        non_training_day_compliance = 0.0
        issues = []
        
        if daily_reports and len(daily_reports) > 0:
            days_reported = len(daily_reports)
            
            # Extract target nutrition values from meal plan
            target_protein = meal_plan_data.totalDailyNutrition.protein
            target_carbs = meal_plan_data.totalDailyNutrition.carbohydrates
            target_fat = meal_plan_data.totalDailyNutrition.fat
            target_calories = meal_plan_data.totalDailyNutrition.calories
            
            # Calculate compliance percentages
            protein_total = sum(report.macros.proteins for report in daily_reports)
            carb_total = sum(report.macros.carbs for report in daily_reports)
            fat_total = sum(report.macros.fats for report in daily_reports)
            
            if target_protein > 0:
                protein_compliance = min(100, (protein_total / (target_protein * days_reported)) * 100)
            if target_carbs > 0:
                carb_compliance = min(100, (carb_total / (target_carbs * days_reported)) * 100)
            if target_fat > 0:
                fat_compliance = min(100, (fat_total / (target_fat * days_reported)) * 100)
            
            # Calculate calorie compliance
            # Assuming 4 calories per gram of protein and carbs, 9 calories per gram of fat
            actual_calories = (protein_total * 4) + (carb_total * 4) + (fat_total * 9)
            if target_calories > 0:
                calorie_compliance = min(100, (actual_calories / (target_calories * days_reported)) * 100)
            
            # Identify main issues
            if protein_compliance < 85:
                issues.append("Protein intake below target")
            if carb_compliance < 85:
                issues.append("Carbohydrate intake below target")
            if fat_compliance < 85:
                issues.append("Fat intake below target")
            if carb_compliance > 115:
                issues.append("Carbohydrate intake above target")
            if fat_compliance > 115:
                issues.append("Fat intake above target")
            
            # For timing and training/non-training day compliance, we would need more data
            # These are placeholder values
            timing_compliance = 90.0
            training_day_compliance = 85.0
            non_training_day_compliance = 80.0
        
        return MealComplianceMetrics(
            total_days_reported=days_reported,
            protein_adherence_percentage=protein_compliance,
            carb_adherence_percentage=carb_compliance,
            fat_adherence_percentage=fat_compliance,
            calorie_adherence_percentage=calorie_compliance,
            meal_timing_adherence_percentage=timing_compliance,
            training_day_adherence=training_day_compliance,
            non_training_day_adherence=non_training_day_compliance,
            main_issues=issues
        )
