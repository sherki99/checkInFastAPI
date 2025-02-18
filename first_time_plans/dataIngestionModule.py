from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class DataIngestionModule:
    """
    Module responsible for parsing and structuring raw JSON data into a standardized client profile.
    This is the first step in the processing pipeline.
    """
    
    def __init__(self):
        """Initialize the DataIngestionModule with default parameters."""
        self.standardized_profile = {}
    
    def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw JSON data into a standardized format for use by subsequent modules.
        
        Args:
            raw_data: Raw JSON data containing user profile and measurements
            
        Returns:
            A clean, structured client profile
        """
        # Extract main sections
        user_id = raw_data.get('userId', '')
        profile = raw_data.get('profile', {})
        measurements = raw_data.get('measurements', {})
        
        # Process personal information
        personal_info = self._process_personal_info(profile.get('personal', {}).get('data', {}))
        
        # Process goals
        goals_info = self._process_goals(profile.get('goals', {}).get('data', {}))
        
        # Process fitness/training information
        fitness_info = self._process_fitness(profile.get('fitness', {}).get('data', {}))
        
        # Process nutrition information
        nutrition_info = self._process_nutrition(profile.get('nutrition', {}).get('data', {}))
        
        # Process lifestyle information
        lifestyle_info = self._process_lifestyle(profile.get('lifestyle', {}).get('data', {}))
        
        # Process body measurements
        body_composition = self._process_measurements(measurements.get('measurements', {}))
        
        # Compile standardized profile
        self.standardized_profile = {
            'user_id': user_id,
            'personal_info': personal_info,
            'goals': goals_info,
            'fitness': fitness_info,
            'nutrition': nutrition_info,
            'lifestyle': lifestyle_info,
            'body_composition': body_composition,
            'measurement_date': measurements.get('date', '')
        }
        
        return self.standardized_profile
    
    def _process_personal_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process personal information from raw data."""
        # Extract height in cm (numeric value only)
        height_str = data.get('height', '0 cm')
        height = float(height_str.split()[0]) if ' ' in height_str else float(height_str)
        
        # Extract weight in kg (numeric value only)
        weight_str = data.get('weight', '0 kg')
        weight = float(weight_str.split()[0]) if ' ' in weight_str else float(weight_str)
        
        return {
            'name': data.get('name', ''),
            'age': int(data.get('age', 0)),
            'gender': data.get('gender', ''),
            'height_cm': height,
            'weight_kg': weight,
            'bmi': round(weight / ((height / 100) ** 2), 2) if height > 0 else 0
        }
    
    def _process_goals(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process goals and motivation from raw data."""
        main_goals_str = data.get('main_goals', '')
        main_goals_list = [goal.strip() for goal in main_goals_str.split('\n') if goal.strip()]
        
        return {
            'main_goals': main_goals_list,
            'motivation_level': int(data.get('motivationLevel', 0)),
            'expected_barriers': data.get('expectedBarriers', ''),
            'desired_timeframe_weeks': self._extract_weeks(data.get('timeToSeeChanges', ''))
        }
    
    def _process_fitness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process fitness and training information from raw data."""
        weekly_exercise_time = self._extract_hours(data.get('weeklyExerciseTime', '0 hours'))
        session_duration = self._extract_hours(data.get('trainingSessionDuration', '0 hours'))
        
        return {
            'activity_level': data.get('activityLevel', ''),
            'exercise_routine': data.get('exerciseRoutine', ''),
            'fitness_knowledge': data.get('fitnessKnowledge', ''),
            'preferred_exercises': self._extract_exercise_list(data.get('exercise_mostLiked', '')),
            'avoided_exercises': self._extract_exercise_list(data.get('exercise_leastLiked', '')),
            'weekly_exercise_hours': weekly_exercise_time,
            'training_frequency_per_week': self._extract_frequency(data.get('trainingFrequency', '0x Week')),
            'training_experience_years': self._extract_experience(data.get('trainingDuration', '')),
            'session_duration_hours': session_duration,
            'available_equipment': self._extract_equipment_list(data.get('fitnessEquipment', ''))
        }
    
    def _process_nutrition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process nutrition and recovery information from raw data."""
        water_intake_liters = self._extract_volume(data.get('waterIntake', '0 liters'))
        
        return {
            'diet_preference': data.get('dietPreference', '').strip(),
            'meals_per_day': int(data.get('mealsPerDay', 0)),
            'meal_schedule': self._extract_meal_schedule(data.get('mealTime', '')),
            'supplements': self._extract_supplement_list(data.get('supplements', '')),
            'water_intake_liters': water_intake_liters,
            'alcohol_units_per_week': self._extract_alcohol_units(data.get('alcoholUnits', '0 units'))
        }
    
    def _process_lifestyle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process lifestyle factors from raw data."""
        work_hours = self._extract_hours(data.get('workHours', '0 hours'))
        
        return {
            'work_environment': data.get('workEnvironment', ''),
            'daily_work_hours': work_hours,
            'stress_level': data.get('stressLevel', ''),
            'sports_background': data.get('sports', '')
        }
    
    def _process_measurements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process body measurements from raw data."""
        # Convert measurements to standardized format
        standardized_measurements = {}
        
        # Map of measurement keys to human-readable names
        measurement_map = {
            'upperArmGirthR': 'arm_circumference',
            'forearmGirthR': 'forearm_circumference',
            'neckGirth': 'neck_circumference',
            'bustGirth': 'chest_circumference',
            'waistGirth': 'waist_circumference',
            'hipGirth': 'hip_circumference',
            'thighGirthR': 'thigh_circumference',
            'midThighGirthR': 'mid_thigh_circumference',
            'calfGirthR': 'calf_circumference',
            'wristGirthR': 'wrist_circumference'
        }
        
        for key, readable_name in measurement_map.items():
            if key in data:
                # Convert from millimeters to centimeters
                current_value = data[key].get('current', 0) / 10.0 if data[key].get('current') else 0
                standardized_measurements[readable_name] = round(current_value, 1)
        
        # Calculate derived measurements
        if 'waist_circumference' in standardized_measurements and 'hip_circumference' in standardized_measurements:
            waist = standardized_measurements['waist_circumference']
            hip = standardized_measurements['hip_circumference']
            if hip > 0:
                standardized_measurements['waist_to_hip_ratio'] = round(waist / hip, 2)
        
        return standardized_measurements
    
    # Helper methods for extracting specific data types
    
    def _extract_weeks(self, time_str: str) -> int:
        """Extract number of weeks from a time string."""
        try:
            if 'week' in time_str.lower():
                return int(time_str.split()[0])
            elif 'month' in time_str.lower():
                return int(time_str.split()[0]) * 4
            else:
                return 0
        except:
            return 0
    
    def _extract_hours(self, time_str: str) -> float:
        """Extract number of hours from a time string."""
        try:
            if '-' in time_str:
                # Range like "7-8 Hours"
                parts = time_str.split('-')
                lower = float(parts[0].strip())
                upper = float(parts[1].split()[0].strip())
                return (lower + upper) / 2
            else:
                # Single value like "1.5 hours"
                return float(time_str.split()[0])
        except:
            return 0.0
    
    def _extract_frequency(self, freq_str: str) -> int:
        """Extract training frequency per week."""
        try:
            if 'x' in freq_str.lower():
                return int(freq_str.split('x')[0])
            else:
                return 0
        except:
            return 0
    
    def _extract_experience(self, exp_str: str) -> float:
        """Extract years of training experience."""
        try:
            if 'year' in exp_str.lower():
                # Simple case: "Two Years" or "2 Years"
                if exp_str.split()[0].isdigit():
                    return float(exp_str.split()[0])
                elif exp_str.lower().startswith(('one', 'two', 'three', 'four', 'five')):
                    word_to_num = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
                    first_word = exp_str.lower().split()[0]
                    return float(word_to_num.get(first_word, 0))
            elif 'month' in exp_str.lower():
                # Convert months to years
                if exp_str.split()[0].isdigit():
                    return float(exp_str.split()[0]) / 12
            return 0
        except:
            return 0
    
    def _extract_volume(self, volume_str: str) -> float:
        """Extract volume in liters."""
        try:
            if 'liter' in volume_str.lower() or 'l' in volume_str.lower():
                return float(volume_str.split()[0])
            elif 'ml' in volume_str.lower():
                return float(volume_str.split()[0]) / 1000
            else:
                return 0
        except:
            return 0
    
    def _extract_alcohol_units(self, alcohol_str: str) -> float:
        """Extract alcohol units per week."""
        try:
            if '-' in alcohol_str:
                # Range like "1-2 units"
                parts = alcohol_str.split('-')
                lower = float(parts[0].strip())
                upper = float(parts[1].split()[0].strip())
                return (lower + upper) / 2
            else:
                # Single value
                return float(alcohol_str.split()[0])
        except:
            return 0
    
    def _extract_exercise_list(self, exercise_str: str) -> List[str]:
        """Extract a list of exercises from a string."""
        return [ex.strip() for ex in exercise_str.split('and') if ex.strip()]
    
    def _extract_equipment_list(self, equipment_str: str) -> List[str]:
        """Extract a list of available equipment from a string."""
        equipment_list = []
        for item in equipment_str.split(','):
            clean_item = item.strip().rstrip('.').lower()
            if clean_item:
                equipment_list.append(clean_item)
        return equipment_list
    
    def _extract_meal_schedule(self, schedule_str: str) -> Dict[str, str]:
        """Extract meal schedule from a string."""
        schedule = {}
        for line in schedule_str.split('\n'):
            if ':' in line:
                meal, time = line.split(':', 1)
                schedule[meal.strip()] = time.strip()
        return schedule
    
    def _extract_supplement_list(self, supplement_str: str) -> List[str]:
        """Extract a list of supplements from a string."""
        supplements = []
        for part in supplement_str.split(','):
            clean_part = part.strip().lower()
            if clean_part:
                supplements.append(clean_part)
        return supplements


"""{"standardized_profile": {"body_composition": {"arm_circumference": 24.7, "calf_circumference": 34, "chest_circumference": 81, "forearm_circumference": 23.2, "hip_circumference": 85.2, "mid_thigh_circumference": 43.8, "neck_circumference": 30.3, "thigh_circumference": 50.3, "waist_circumference": 68.7, "waist_to_hip_ratio": 0.81, "wrist_circumference": 15.1}, "fitness": {"activity_level": "Active", "available_equipment": [Array], "avoided_exercises": [Array], "exercise_routine": "Effective", "fitness_knowledge": "I am quite experienced", "preferred_exercises": [Array], "session_duration_hours": 1.5, "training_experience_years": 2, "training_frequency_per_week": 5, "weekly_exercise_hours": 7.5}, "goals": {"desired_timeframe_weeks": 4, "expected_barriers": "Occasional shoulder pain limits some movements, and balancing training with other responsibilities can be a challenge. Maintaining a strict diet is also sometimes difficult due to time constraints.", "main_goals": [Array], "motivation_level": 5}, "lifestyle": {"daily_work_hours": 5, "sports_background": "Football untill the age of 18 then played time tim", "stress_level": "Stressful", "work_environment": "Sitting"}, "measurement_date": "2024-09-17T11:37:30.217+00:00", "nutrition": {"alcohol_units_per_week": 1.5, "diet_preference": "I prefer a balanced diet with a mix of Mediterranean, Italian, and Moroccan influences. I enjoy whole foods like vegetables, lean meats, grains (like couscous and quinoa), and a moderate amount of dairy. I like to avoid processed foods and prefer home-cooked meals.", "meal_schedule": [Object], "meals_per_day": 5, "supplements": [Array], "water_intake_liters": 2.5}, "personal_info": {"age": 25, "bmi": 24.86, "gender": "Male", "height_cm": 186, "name": "Sherki", "weight_kg": 86}, "user_id": "66e037ef43e9199baf5d"}, "status": "success"}"""

"""
The process_data method is the main entry point that:

Extracts the user ID, profile, and measurements
Processes each section of data through specialized helper methods
Compiles everything into a standardized profile dictionary


Helper methods like _process_personal_info, _process_goals, etc., handle specific sections of the input data, applying appropriate transformations:

Converting string measurements to numeric values
Parsing lists from text
Standardizing units (e.g., converting to cm, kg, etc.)
Adding derived metrics (like BMI and waist-to-hip ratio)


Additional utility methods extract specific formats of data, such as:

Time periods (weeks, hours)
Frequencies
Volume measurements
Lists of items from comma or newline-separated strings
"""

