import math
from typing import Dict, Any

class CaloricNeedsDecisionNode:
    def __init__(self):
        """Initialize the CaloricNeedsDecisionNode."""
        self.caloric_targets = {}
    
    def process(self, client_profile: Dict[str, Any], body_composition: Dict[str, Any], 
                goal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Total Daily Energy Expenditure (TDEE) and adjust based on client goals.
        
        Args:
            client_profile: Client profile analysis
            body_composition: Body composition analysis
            goal_analysis: Goal clarification analysis
            
        Returns:
            Dictionary containing caloric targets
        """
        # Extract required data
        gender = client_profile.get('gender', '').lower()
        age = client_profile.get('age', 25)
        weight_kg = body_composition.get('weight_kg', 0)
        height_cm = body_composition.get('height_cm', 0)
        activity_level = client_profile.get('activity_level', 'Moderate')
        primary_goal = goal_analysis.get('primary_goal', '')
        timeframe_weeks = goal_analysis.get('timeframe_weeks', 12)
        target_weight_kg = goal_analysis.get('target_metrics', {}).get('weight_kg', weight_kg)
        body_fat_percentage = body_composition.get('estimated_body_fat_percentage', 15)
        
        # Calculate BMR using Mifflin-St Jeor equation
        bmr = self._calculate_bmr(gender, age, weight_kg, height_cm)
        
        # Calculate TDEE by applying activity multiplier
        tdee = self._calculate_tdee(bmr, activity_level)
        
        # Adjust TDEE based on goals
        adjusted_tdee = self._adjust_for_goals(tdee, primary_goal, timeframe_weeks, 
                                              weight_kg, target_weight_kg, body_fat_percentage)
        
        # Calculate macronutrient distribution (will be refined in MacroDistributionDecisionNode)
        protein_calories, carb_calories, fat_calories = self._estimate_macro_distribution(
            adjusted_tdee, primary_goal, body_fat_percentage
        )
        
        # Compile results
        self.caloric_targets = {
            'bmr': round(bmr),
            'tdee': round(tdee),
            'adjusted_daily_calories': round(adjusted_tdee),
            'estimated_macro_calories': {
                'protein': round(protein_calories),
                'carbohydrates': round(carb_calories),
                'fats': round(fat_calories)
            }
        }
        
        return self.caloric_targets
    
    def _calculate_bmr(self, gender: str, age: int, weight_kg: float, height_cm: float) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.
        
        Args:
            gender: Client gender
            age: Client age
            weight_kg: Weight in kilograms
            height_cm: Height in centimeters
            
        Returns:
            BMR in calories
        """
        if gender == 'male':
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:  # female or other
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    def _calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure by applying activity multiplier to BMR.
        
        Args:
            bmr: Basal Metabolic Rate
            activity_level: Client's activity level
            
        Returns:
            TDEE in calories
        """
        activity_multipliers = {
            'sedentary': 1.2,          # Little or no exercise
            'lightly active': 1.375,   # Light exercise/sports 1-3 days/week
            'moderately active': 1.55, # Moderate exercise/sports 3-5 days/week
            'very active': 1.725,      # Hard exercise/sports 6-7 days/week
            'extra active': 1.9        # Very hard exercise & physical job or 2x training
        }
        
        # Normalize activity level for lookup
        activity_level = activity_level.lower()
        
        # Find the closest matching activity level
        if 'sedentary' in activity_level or 'inactive' in activity_level:
            multiplier = activity_multipliers['sedentary']
        elif any(level in activity_level for level in ['light', 'mild']):
            multiplier = activity_multipliers['lightly active']
        elif any(level in activity_level for level in ['moderate', 'active']):
            multiplier = activity_multipliers['moderately active']
        elif any(level in activity_level for level in ['very active', 'high']):
            multiplier = activity_multipliers['very active']
        elif any(level in activity_level for level in ['extra', 'extreme', 'athlete']):
            multiplier = activity_multipliers['extra active']
        else:
            # Default to moderately active if no match
            multiplier = activity_multipliers['moderately active']
        
        return bmr * multiplier
    
    def _adjust_for_goals(self, tdee: float, primary_goal: str, timeframe_weeks: int,
                          current_weight_kg: float, target_weight_kg: float,
                          body_fat_percentage: float) -> float:
        """
        Adjust TDEE based on client's primary goal.
        
        Args:
            tdee: Total Daily Energy Expenditure
            primary_goal: Client's primary goal (e.g., 'hypertrophy', 'fat_loss')
            timeframe_weeks: Goal timeframe in weeks
            current_weight_kg: Current weight in kg
            target_weight_kg: Target weight in kg
            body_fat_percentage: Estimated body fat percentage
            
        Returns:
            Adjusted daily caloric target
        """
        # Normalize goal for comparison
        goal = primary_goal.lower()
        
        # 1. Bulking/Hypertrophy: caloric surplus
        if any(g in goal for g in ['hypertrophy', 'muscle', 'bulk', 'gain', 'mass']):
            # Calculate weight change goal
            weight_change_goal = target_weight_kg - current_weight_kg
            
            if weight_change_goal > 0:
                # For gains, aim for 0.25-0.5% of bodyweight per week for intermediate lifters
                # The higher the bf%, the smaller the surplus to minimize fat gain
                max_weekly_gain_rate = 0.005 if body_fat_percentage < 15 else 0.0025
                ideal_weekly_gain = min(current_weight_kg * max_weekly_gain_rate, weight_change_goal / timeframe_weeks)
                
                # Each kg of weight gain requires roughly 7700 calories
                daily_surplus = (ideal_weekly_gain * 7700) / 7
                
                # Smaller surplus for higher body fat
                if body_fat_percentage > 20:
                    daily_surplus *= 0.7  # Reduce surplus by 30%
                
                return tdee + daily_surplus
            else:
                # If current weight is already at/above target, use a modest surplus
                return tdee * 1.05  # 5% surplus
        
        # 2. Fat Loss: caloric deficit
        elif any(g in goal for g in ['fat loss', 'cut', 'lean', 'lose', 'decrease']):
            # Calculate weight change goal
            weight_change_goal = current_weight_kg - target_weight_kg
            
            if weight_change_goal > 0:
                # For fat loss, aim for 0.5-1% of bodyweight per week
                # The higher the bf%, the larger the deficit can be
                max_weekly_loss_rate = 0.01 if body_fat_percentage > 20 else 0.005
                ideal_weekly_loss = min(current_weight_kg * max_weekly_loss_rate, weight_change_goal / timeframe_weeks)
                
                # Each kg of weight loss requires roughly 7700 calorie deficit
                daily_deficit = (ideal_weekly_loss * 7700) / 7
                
                # Limit deficit to prevent muscle loss
                max_deficit = tdee * 0.25  # Maximum 25% deficit
                daily_deficit = min(daily_deficit, max_deficit)
                
                return tdee - daily_deficit
            else:
                # If current weight is already at/below target, use a modest deficit
                return tdee * 0.9  # 10% deficit
        
        # 3. Maintenance/Recomp
        elif any(g in goal for g in ['maintain', 'recomp', 'recomposition', 'tone', 'performance']):
            # For recomp, maintain caloric balance or very slight surplus
            return tdee * 1.02  # 2% surplus
        
        # 4. General Fitness
        elif 'fitness' in goal or 'general' in goal or 'health' in goal:
            # Default to a slight deficit for overall fitness if above ideal weight
            if body_fat_percentage > 20:
                return tdee * 0.95  # 5% deficit
            else:
                return tdee  # Maintenance
        
        # Default: return TDEE if no specific goal match
        return tdee
    
    def _estimate_macro_distribution(self, calories: float, primary_goal: str, 
                                    body_fat_percentage: float) -> tuple:
        """
        Provide initial macro distribution estimates based on goals and body composition.
        This will be refined further in the MacroDistributionDecisionNode.
        
        Args:
            calories: Adjusted daily caloric target
            primary_goal: Client's primary goal
            body_fat_percentage: Estimated body fat percentage
            
        Returns:
            Tuple of (protein_calories, carb_calories, fat_calories)
        """
        goal = primary_goal.lower()
        
        # Base protein intake on goal and body composition
        if 'hypertrophy' in goal or 'muscle' in goal or 'bulk' in goal:
            # Higher protein for muscle gain
            protein_percentage = 0.30  # 30% of total calories
        elif 'fat loss' in goal or 'cut' in goal:
            # Higher protein for preserving muscle during fat loss
            protein_percentage = 0.35  # 35% of total calories
        else:
            # Moderate protein for maintenance or general fitness
            protein_percentage = 0.25  # 25% of total calories
        
        # Adjust protein based on body fat percentage
        if body_fat_percentage > 25:
            # Even higher protein for higher body fat (to preserve muscle mass)
            protein_percentage += 0.05
        
        # Calculate initial macro distribution
        protein_calories = calories * protein_percentage
        
        # Remaining calories distributed between carbs and fats
        remaining_calories = calories - protein_calories
        
        # For hypertrophy/bulking goals: prioritize carbs
        if 'hypertrophy' in goal or 'muscle' in goal or 'bulk' in goal:
            carb_percentage_of_remaining = 0.65  # 65% of remaining to carbs
        # For fat loss: lower carbs
        elif 'fat loss' in goal or 'cut' in goal:
            carb_percentage_of_remaining = 0.55  # 55% of remaining to carbs
        else:
            carb_percentage_of_remaining = 0.60  # 60% of remaining to carbs
        
        carb_calories = remaining_calories * carb_percentage_of_remaining
        fat_calories = remaining_calories * (1 - carb_percentage_of_remaining)
        
        return protein_calories, carb_calories, fat_calories