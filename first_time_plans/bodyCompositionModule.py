
from typing import Dict, Any, List, Optional
import math

class BodyCompositionModule:
    """
    Module responsible for evaluating measurements and anthropometric data
    to provide detailed body composition metrics.
    """
    
    def __init__(self):
        """Initialize the BodyCompositionModule."""
        self.body_composition_metrics = {}
    
    def process(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the standardized profile to evaluate body composition.
        
        Args:
            standardized_profile: Standardized client profile from DataIngestionModule
            
        Returns:
            Detailed body composition metrics
        """
        personal_info = standardized_profile.get('personal_info', {})
        body_measurements = standardized_profile.get('body_composition', {})
        gender = personal_info.get('gender', '').lower()
        
        # Extract basic metrics
        height_cm = personal_info.get('height_cm', 0)
        weight_kg = personal_info.get('weight_kg', 0)
        age = personal_info.get('age', 0)
        bmi = personal_info.get('bmi', 0)
        
        # Analyze body type based on measurements
        body_type = self._determine_body_type(body_measurements, gender)
        
        # Estimate body fat percentage using available measurements
        estimated_body_fat = self._estimate_body_fat(body_measurements, gender, age, height_cm, weight_kg)
        
        # Analyze muscle distribution
        muscle_distribution = self._analyze_muscle_distribution(body_measurements, gender)
        
        # Calculate structural ratios
        structural_ratios = self._calculate_structural_ratios(body_measurements, height_cm)
        
        # Determine weight category
        weight_category = self._determine_weight_category(bmi)
        
        # Compile body composition metrics
        self.body_composition_metrics = {
            'height_cm': height_cm,
            'weight_kg': weight_kg,
            'bmi': bmi,
            'weight_category': weight_category,
            'estimated_body_fat_percentage': estimated_body_fat,
            'body_type': body_type,
            'muscle_distribution': muscle_distribution,
            'structural_ratios': structural_ratios
        }
        
        return self.body_composition_metrics
    
    def _determine_body_type(self, measurements: Dict[str, Any], gender: str) -> str:
        """
        Determine body type (ectomorph, mesomorph, endomorph) based on measurements.
        
        Args:
            measurements: Body measurements
            gender: Client gender
            
        Returns:
            Body type classification
        """
        # Get key measurements
        wrist_circumference = measurements.get('wrist_circumference', 0)
        chest_circumference = measurements.get('chest_circumference', 0)
        waist_circumference = measurements.get('waist_circumference', 0)
        hip_circumference = measurements.get('hip_circumference', 0)
        
        # If we don't have enough measurements, make an educated guess
        if not all([wrist_circumference, chest_circumference, waist_circumference, hip_circumference]):
            return "Unknown (insufficient measurements)"
        
        # Calculate frame size using wrist circumference
        # This is a simplification - proper frame size assessment would consider height as well
        if gender == 'male':
            if wrist_circumference < 17:  # cm
                frame = "small"
            elif wrist_circumference > 19:  # cm
                frame = "large"
            else:
                frame = "medium"
        else:  # female or other
            if wrist_circumference < 15:  # cm
                frame = "small"
            elif wrist_circumference > 17:  # cm
                frame = "large"
            else:
                frame = "medium"
        
        # Calculate chest-to-waist and hip-to-waist ratios
        chest_to_waist = chest_circumference / waist_circumference if waist_circumference else 0
        hip_to_waist = hip_circumference / waist_circumference if waist_circumference else 0
        
        # Determine body type based on frame and proportions
        if frame == "small" and chest_to_waist < 1.1 and hip_to_waist < 1.1:
            return "Ectomorph"
        elif frame == "large" and chest_to_waist < 1.15 and hip_to_waist < 1.15:
            return "Endomorph"
        elif chest_to_waist > 1.2 or hip_to_waist > 1.2:
            return "Mesomorph"
        elif frame == "medium":
            return "Mesomorph-Ectomorph"
        else:
            return "Balanced"
    
    def _estimate_body_fat(self, measurements: Dict[str, Any], gender: str,
                          age: int, height_cm: float, weight_kg: float) -> float:
        """
        Estimate body fat percentage based on available measurements.
        This is a simplified calculation and should be used as an approximation only.
        
        Args:
            measurements: Body measurements
            gender: Client gender
            age: Client age
            height_cm: Height in centimeters
            weight_kg: Weight in kilograms
            
        Returns:
            Estimated body fat percentage
        """
        # Attempt to use Navy method if we have all required measurements
        neck_cm = measurements.get('neck_circumference', 0)
        waist_cm = measurements.get('waist_circumference', 0)
        hip_cm = measurements.get('hip_circumference', 0)
        
        if neck_cm and waist_cm and (hip_cm or gender == 'male') and height_cm:
            return self._navy_body_fat(neck_cm, waist_cm, hip_cm, height_cm, gender)
        
        # Fallback to BMI-based estimation (very rough approximation)
        bmi = weight_kg / ((height_cm / 100) ** 2) if height_cm else 0
        
        if gender == 'male':
            return (1.20 * bmi) + (0.23 * age) - 16.2
        else:  # female or other
            return (1.20 * bmi) + (0.23 * age) - 5.4
    
    def _navy_body_fat(self, neck_cm: float, waist_cm: float, hip_cm: float,
                      height_cm: float, gender: str) -> float:
        """
        Estimate body fat using Navy method.
        
        Args:
            neck_cm: Neck circumference in cm
            waist_cm: Waist circumference in cm
            hip_cm: Hip circumference in cm (used for women only)
            height_cm: Height in cm
            gender: Client gender
            
        Returns:
            Estimated body fat percentage
        """
        if gender == 'male':
            body_fat = 495 / (1.0324 - 0.19077 * math.log10(waist_cm - neck_cm) + 0.15456 * math.log10(height_cm)) - 450
        else:  # female or other
            body_fat = 495 / (1.29579 - 0.35004 * math.log10(waist_cm + hip_cm - neck_cm) + 0.22100 * math.log10(height_cm)) - 450
        
        return max(min(round(body_fat, 1), 40), 5)  # Clamp to reasonable range
    
    def _analyze_muscle_distribution(self, measurements: Dict[str, Any], gender: str) -> Dict[str, str]:
        """
        Analyze relative muscle distribution based on circumference measurements.
        
        Args:
            measurements: Body measurements
            gender: Client gender
            
        Returns:
            Muscle distribution analysis as a dictionary
        """
        # Get key measurements
        arm_circumference = measurements.get('arm_circumference', 0)
        thigh_circumference = measurements.get('thigh_circumference', 0)
        calf_circumference = measurements.get('calf_circumference', 0)
        chest_circumference = measurements.get('chest_circumference', 0)
        
        # Define baseline proportions by gender (approximations)
        if gender == 'male':
            ideal_arm_to_thigh_ratio = 0.65   # Arm should be about 65% of thigh
            ideal_calf_to_thigh_ratio = 0.75   # Calf should be about 75% of thigh
            ideal_arm_to_chest_ratio = 0.38    # Arm should be about 38% of chest
        else:  # female or other
            ideal_arm_to_thigh_ratio = 0.60
            ideal_calf_to_thigh_ratio = 0.70
            ideal_arm_to_chest_ratio = 0.35
        
        # Calculate actual ratios safely
        arm_to_thigh_ratio = arm_circumference / thigh_circumference if thigh_circumference else 0
        calf_to_thigh_ratio = calf_circumference / thigh_circumference if thigh_circumference else 0
        arm_to_chest_ratio = arm_circumference / chest_circumference if chest_circumference else 0
        
        distribution = {}
        
        # Analyze upper body development based on arm-to-chest ratio
        if arm_to_chest_ratio:
            if arm_to_chest_ratio < ideal_arm_to_chest_ratio * 0.85:
                distribution['upper_body'] = "Arms underdeveloped relative to chest"
            elif arm_to_chest_ratio > ideal_arm_to_chest_ratio * 1.15:
                distribution['upper_body'] = "Arms overdeveloped relative to chest"
            else:
                distribution['upper_body'] = "Balanced upper body development"
        else:
            distribution['upper_body'] = "Unknown (insufficient measurements)"
        
        # Analyze lower body development based on arm-to-thigh and calf-to-thigh ratios
        if arm_to_thigh_ratio and calf_to_thigh_ratio:
            if arm_to_thigh_ratio > ideal_arm_to_thigh_ratio * 1.15:
                distribution['lower_body'] = "Lower body underdeveloped relative to upper body"
            elif arm_to_thigh_ratio < ideal_arm_to_thigh_ratio * 0.85:
                distribution['lower_body'] = "Lower body overdeveloped relative to upper body"
            else:
                distribution['lower_body'] = "Balanced lower body development"
            
            # Evaluate calf development relative to thighs
            if calf_to_thigh_ratio < ideal_calf_to_thigh_ratio * 0.85:
                distribution['calves'] = "Calves underdeveloped relative to thighs"
            elif calf_to_thigh_ratio > ideal_calf_to_thigh_ratio * 1.15:
                distribution['calves'] = "Calves overdeveloped relative to thighs"
            else:
                distribution['calves'] = "Balanced calf development"
        else:
            distribution['lower_body'] = "Unknown (insufficient measurements)"
            distribution['calves'] = "Unknown (insufficient measurements)"
        
        return distribution
    

    def _calculate_structural_ratios(self, measurements: Dict[str, Any], height_cm: float) -> Dict[str, float]:
        """
        Calculate structural ratios based on body measurements and height.

        Args:
            measurements: Dictionary of body measurements
            height_cm: Client's height in centimeters

        Returns:
            Dictionary containing key structural ratios
        """
        ratios = {}
        
        # Ensure height is valid
        if height_cm <= 0:
            return {"error": "Invalid height value"}

        # Example ratios
        if 'waist_circumference' in measurements and 'shoulder_circumference' in measurements:
            ratios['shoulder_to_waist_ratio'] = measurements['shoulder_circumference'] / measurements['waist_circumference']
        
        if 'leg_length' in measurements:
            ratios['leg_to_height_ratio'] = measurements['leg_length'] / height_cm
        
        if 'arm_length' in measurements:
            ratios['arm_to_height_ratio'] = measurements['arm_length'] / height_cm
        
        return ratios
    
    def _determine_weight_category(self, bmi: float) -> str:
        """
        Determine the weight category based on BMI.

        Args:
            bmi: Body Mass Index value

        Returns:
            Weight category as a string
        """
        if bmi <= 0:
            return "Unknown (invalid BMI)"

        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal weight"
        elif 25 <= bmi < 29.9:
            return "Overweight"
        elif 30 <= bmi < 34.9:
            return "Obesity (Class 1)"
        elif 35 <= bmi < 39.9:
            return "Obesity (Class 2)"
        else:
            return "Obesity (Class 3)"


