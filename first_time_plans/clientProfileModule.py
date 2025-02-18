from typing import Dict, Any, List, Optional

class ClientProfileModule:
    """
    Module responsible for extracting basic parameters from the standardized client profile
    and providing a base structure for later modules.
    """
    
    def __init__(self):
        """Initialize the ClientProfileModule."""
        self.base_profile = {}
    
    def process(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the standardized profile to extract base parameters.
        
        Args:
            standardized_profile: Standardized client profile from DataIngestionModule
            
        Returns:
            A base profile with essential parameters
        """
        user_id = standardized_profile.get('user_id', '')
        personal_info = standardized_profile.get('personal_info', {})
        fitness_info = standardized_profile.get('fitness', {})
        
        # Calculate training age category
        training_experience_years = fitness_info.get('training_experience_years', 0)
        training_age_category = self._determine_training_age_category(training_experience_years)
        
        # Extract essential parameters
        self.base_profile = {
            'user_id': user_id,
            'age': personal_info.get('age', 0),
            'gender': personal_info.get('gender', ''),
            'height_cm': personal_info.get('height_cm', 0),
            'weight_kg': personal_info.get('weight_kg', 0),
            'bmi': personal_info.get('bmi', 0),
            'training_age': {
                'years': training_experience_years,
                'category': training_age_category
            },
            'weekly_training_frequency': fitness_info.get('training_frequency_per_week', 0),
            'weekly_exercise_hours': fitness_info.get('weekly_exercise_hours', 0),
            'session_duration_hours': fitness_info.get('session_duration_hours', 0),
            'available_equipment': fitness_info.get('available_equipment', []),
        }
        
        return self.base_profile
    
    def _determine_training_age_category(self, years: float) -> str:
        """
        Determine training age category based on years of experience.
        
        Args:
            years: Years of training experience
            
        Returns:
            Training age category (Beginner, Intermediate, Advanced, Elite)
        """
        if years < 1:
            return "Beginner"
        elif years < 3:
            return "Intermediate"
        elif years < 5:
            return "Advanced"
        else:
            return "Elite"