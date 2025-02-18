from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

@dataclass
class VolumeGuidelines:
    minimum_effective_volume: int  # Sets per week
    maximum_adaptive_volume: int   # Sets per week
    maximum_recoverable_volume: int # Sets per week

class IntensityZone(Enum):
    STRENGTH = "strength"
    HYPERTROPHY = "hypertrophy"
    ENDURANCE = "endurance"

@dataclass
class IntensityGuidelines:
    rpe_range: tuple[int, int]
    rep_range: tuple[int, int]
    rest_period_minutes: tuple[float, float]

class VolumeAndIntensityDecisionNode:
    """
    Determines optimal volume and intensity guidelines for each muscle group
    based on client data and recovery capacity.
    """
    
    def __init__(self):
        self.volume_guidelines = {}
        self.base_volumes = {
            'chest': {'mev': 10, 'mav': 16, 'mrv': 20},
            'back': {'mev': 12, 'mav': 18, 'mrv': 22},
            'shoulders': {'mev': 8, 'mav': 14, 'mrv': 18},
            'quads': {'mev': 10, 'mav': 16, 'mrv': 20},
            'hamstrings': {'mev': 8, 'mav': 14, 'mrv': 18},
            'calves': {'mev': 6, 'mav': 12, 'mrv': 16},
            'biceps': {'mev': 6, 'mav': 12, 'mrv': 16},
            'triceps': {'mev': 6, 'mav': 12, 'mrv': 16}
        }
        
    def process(self, client_data: Dict[str, Any], training_history:  Dict[str, Any], body_comp:  Dict[str, Any],goals:  Dict[str, Any]) -> Dict[str, Any]:
        """
        Process client data to determine volume and intensity guidelines.
        """
        # Extract relevant data
        
        # Calculate recovery capacity
        recovery_multiplier = self._calculate_recovery_multiplier(client_data)
        
        # Get volume adjustments based on muscle distribution
        muscle_distribution = body_comp.get('muscle_distribution', {})
        
        # Calculate adjusted volumes for each muscle group
        muscle_volumes = self._calculate_muscle_volumes(
            recovery_multiplier,
            muscle_distribution,
            training_history
        )
        
        # Determine intensity guidelines based on goals and experience
        intensity_guidelines = self._determine_intensity_guidelines(
            goals.get('primary_goal'),
            training_history.get('training_age', {}).get('category')
        )
        
        # Create progression strategy
        progression = self._create_progression_strategy(
            training_history,
            goals
        )
        
        return {
            'volume_guidelines': muscle_volumes,
            'intensity_guidelines': intensity_guidelines,
            'progression_strategy': progression,
            'recovery_recommendations': self._generate_recovery_guidelines(recovery_multiplier)
        }
    
    def _calculate_recovery_multiplier(self, client_data: Dict[str, Any]) -> float:
        """
        Calculate recovery capacity multiplier based on various factors.
        """
        base_multiplier = 1.0
        
        # Extract relevant factors
        sleep_quality = client_data.get('standardized_profile', {}).get('lifestyle', {}).get('sleep_quality', 'good')
        stress_level = client_data.get('standardized_profile', {}).get('lifestyle', {}).get('stress_level', 'moderate')
        training_age = client_data.get('histroy', {}).get('training_age', {}).get('category', 'intermediate')
        
        # Adjust for sleep quality
        sleep_adjustments = {'poor': 0.8, 'moderate': 0.9, 'good': 1.0, 'excellent': 1.1}
        base_multiplier *= sleep_adjustments.get(sleep_quality.lower(), 1.0)
        
        # Adjust for stress
        stress_adjustments = {'high': 0.8, 'moderate': 0.9, 'low': 1.0}
        base_multiplier *= stress_adjustments.get(stress_level.lower(), 0.9)
        
        # Adjust for training age
        age_adjustments = {'beginner': 0.9, 'intermediate': 1.0, 'advanced': 1.1}
        base_multiplier *= age_adjustments.get(training_age.lower(), 1.0)
        
        return round(base_multiplier, 2)
    
    def _calculate_muscle_volumes(self, 
                                recovery_multiplier: float,
                                muscle_distribution: Dict[str, str],
                                training_history: Dict[str, Any]) -> Dict[str, VolumeGuidelines]:
        """
        Calculate specific volume guidelines for each muscle group.
        """
        adjusted_volumes = {}
        volume_tolerance = training_history.get('volume_tolerance', {}).get('volume_category', 'moderate')
        
        for muscle, base_volume in self.base_volumes.items():
            # Start with base volumes
            mev = base_volume['mev']
            mav = base_volume['mav']
            mrv = base_volume['mrv']
            
            # Adjust for recovery capacity
            mev = int(mev * recovery_multiplier)
            mav = int(mav * recovery_multiplier)
            mrv = int(mrv * recovery_multiplier)
            
            # Adjust for muscle development status
            if any(f"{muscle} underdeveloped" in str(value) for value in muscle_distribution.values()):
                mev += 2
                mav += 2
                mrv += 2
            elif any(f"{muscle} overdeveloped" in str(value) for value in muscle_distribution.values()):
                mev -= 1
                mav -= 1
                mrv -= 1
            
            # Adjust for volume tolerance
            tolerance_multipliers = {
                'low': 0.9,
                'moderate': 1.0,
                'high': 1.1
            }
            volume_multiplier = tolerance_multipliers.get(volume_tolerance.lower(), 1.0)
            
            mev = int(mev * volume_multiplier)
            mav = int(mav * volume_multiplier)
            mrv = int(mrv * volume_multiplier)
            
            adjusted_volumes[muscle] = VolumeGuidelines(mev, mav, mrv)
            
        return adjusted_volumes
    
    def _determine_intensity_guidelines(self, 
                                     primary_goal: str,
                                     training_age: str) -> Dict[str, IntensityGuidelines]:
        """
        Determine intensity guidelines based on goals and training age.
        """
        # Base intensity guidelines by goal
        goal_guidelines = {
            'hypertrophy': IntensityGuidelines(
                rpe_range=(7, 9),
                rep_range=(8, 12),
                rest_period_minutes=(1.5, 2.5)
            ),
            'strength': IntensityGuidelines(
                rpe_range=(8, 10),
                rep_range=(3, 6),
                rest_period_minutes=(2.5, 4)
            ),
            'endurance': IntensityGuidelines(
                rpe_range=(6, 8),
                rep_range=(12, 20),
                rest_period_minutes=(1, 1.5)
            )
        }
        
        # Get base guidelines for goal
        base_guidelines = goal_guidelines.get(
            primary_goal.lower() if primary_goal else 'hypertrophy'
        )
        
        # Adjust based on training age
        if training_age.lower() == 'beginner':
            return IntensityGuidelines(
                rpe_range=(6, 8),
                rep_range=base_guidelines.rep_range,
                rest_period_minutes=base_guidelines.rest_period_minutes
            )
        
        return base_guidelines
    
    def _create_progression_strategy(self,
                                   training_history: Dict[str, Any],
                                   goals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a progression strategy based on training history and goals.
        """
        training_age = training_history.get('training_age', {}).get('category', 'intermediate').lower()
        primary_goal = goals.get('primary_goal', 'hypertrophy').lower()
        
        strategies = {
            'beginner': {
                'type': 'linear',
                'load_increment': '2.5-5kg per week',
                'deload_frequency': 'Every 8-10 weeks',
                'volume_progression': 'Add 1 set per muscle group every 2-3 weeks'
            },
            'intermediate': {
                'type': 'double-progression',
                'load_increment': 'When upper rep range is exceeded for 2 sessions',
                'deload_frequency': 'Every 6-8 weeks',
                'volume_progression': 'Add 1-2 sets per muscle group every 3-4 weeks'
            },
            'advanced': {
                'type': 'undulating',
                'load_increment': 'Based on performance and readiness',
                'deload_frequency': 'Every 4-6 weeks or as needed',
                'volume_progression': 'Wave loading approach with periodic overreaching'
            }
        }
        
        return strategies.get(training_age, strategies['intermediate'])
    
    def _generate_recovery_guidelines(self, recovery_multiplier: float) -> Dict[str, Any]:
        """
        Generate recovery recommendations based on recovery capacity.
        """
        if recovery_multiplier <= 0.8:
            return {
                'intra_workout_rest': 'Extended rest periods (+30 seconds)',
                'between_sessions': 'Minimum 48 hours between training same muscle groups',
                'recovery_methods': ['Extra sleep', 'Stress management', 'Light cardio on rest days']
            }
        elif recovery_multiplier <= 0.9:
            return {
                'intra_workout_rest': 'Standard rest periods',
                'between_sessions': '36-48 hours between training same muscle groups',
                'recovery_methods': ['Adequate sleep', 'Light stretching', 'Active recovery']
            }
        else:
            return {
                'intra_workout_rest': 'Standard to shortened rest periods',
                'between_sessions': '24-36 hours between training same muscle groups',
                'recovery_methods': ['Maintenance of current recovery practices']
            }
