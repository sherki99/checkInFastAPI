from typing import Dict, Any, List, Set

class TrainingHistoryModule:
    """
    Module responsible for assessing past training experience, exercise preferences,
    and limitations to determine volume tolerance and exercise selection guidance.
    """
    
    def __init__(self):
        """Initialize the TrainingHistoryModule."""
        self.training_parameters = {}
        
        # Define common movement patterns for categorization
        self.movement_patterns = {
            'push': {'bench press', 'overhead press', 'pushup', 'dips'},
            'pull': {'pullup', 'row', 'lat pulldown', 'chin up'},
            'squat': {'squat', 'leg press', 'front squat', 'hack squat'},
            'hinge': {'deadlift', 'romanian deadlift', 'good morning'},
            'lunge': {'lunge', 'split squat', 'bulgarian split squat'},
            'carry': {'farmers walk', 'suitcase carry', 'overhead carry'},
            'core': {'plank', 'crunch', 'leg raise', 'ab wheel'}
        }
        
    def process(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the standardized profile to analyze training history.
        
        Args:
            standardized_profile: Standardized client profile
            
        Returns:
            Training history analysis and parameters
        """
        fitness_info = standardized_profile.get('fitness', {})
        personal_info = standardized_profile.get('personal_info', {})
        
        # Extract training history data
        training_age = fitness_info.get('training_experience_years', 0)
        weekly_frequency = fitness_info.get('training_frequency_per_week', 0)
        session_duration = fitness_info.get('session_duration_hours', 0)
        preferred_exercises = fitness_info.get('preferred_exercises', [])
        avoided_exercises = fitness_info.get('avoided_exercises', [])
        available_equipment = fitness_info.get('available_equipment', [])
        
        # Analyze exercise preferences and limitations
        movement_analysis = self._analyze_movement_patterns(preferred_exercises, avoided_exercises)
        
        # Calculate volume tolerance based on training history
        volume_tolerance = self._calculate_volume_tolerance(
            training_age,
            weekly_frequency,
            session_duration,
            movement_analysis
        )
        
        # Assess exercise technique proficiency
        technique_proficiency = self._assess_technique_proficiency(
            training_age,
            preferred_exercises,
            movement_analysis
        )
        
        # Identify potential red flags or limitations
        limitations = self._identify_limitations(
            avoided_exercises,
            movement_analysis,
            standardized_profile
        )
        
        # Generate equipment-based exercise recommendations
        equipment_based_exercises = self._generate_equipment_based_exercises(
            available_equipment,
            movement_analysis,
            limitations
        )
        
        # Compile training history parameters
        self.training_parameters = {
            'training_age': {
                'years': training_age,
                'category': self._categorize_training_age(training_age)
            },
            'volume_tolerance': volume_tolerance,
            'movement_pattern_analysis': movement_analysis,
            'technique_proficiency': technique_proficiency,
            'training_limitations': limitations,
            'recommended_exercises': equipment_based_exercises,
            'weekly_training_capacity': {
                'sessions_per_week': weekly_frequency,
                'hours_per_session': session_duration,
                'total_weekly_hours': weekly_frequency * session_duration
            }
        }
        
        return self.training_parameters
    
    def _analyze_movement_patterns(self, 
                                 preferred_exercises: List[str],
                                 avoided_exercises: List[str]) -> Dict[str, Any]:
        """
        Analyze movement pattern preferences and limitations.
        
        Args:
            preferred_exercises: List of preferred exercises
            avoided_exercises: List of avoided exercises
            
        Returns:
            Movement pattern analysis
        """
        # Convert to lowercase for matching
        preferred_lower = [ex.lower() for ex in preferred_exercises]
        avoided_lower = [ex.lower() for ex in avoided_exercises]
        
        pattern_analysis = {}
        for pattern, exercises in self.movement_patterns.items():
            preferred_count = sum(1 for ex in preferred_lower if any(p in ex for p in exercises))
            avoided_count = sum(1 for ex in avoided_lower if any(p in ex for p in exercises))
            
            pattern_analysis[pattern] = {
                'preference_score': preferred_count - avoided_count,
                'preferred_movements': [ex for ex in preferred_lower if any(p in ex for p in exercises)],
                'avoided_movements': [ex for ex in avoided_lower if any(p in ex for p in exercises)],
                'status': 'preferred' if preferred_count > avoided_count else 'avoided' if avoided_count > preferred_count else 'neutral'
            }
        
        return pattern_analysis
    
    def _calculate_volume_tolerance(self,
                                  training_age: float,
                                  weekly_frequency: int,
                                  session_duration: float,
                                  movement_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate volume tolerance based on training history.
        
        Args:
            training_age: Years of training experience
            weekly_frequency: Training sessions per week
            session_duration: Hours per session
            movement_analysis: Movement pattern analysis
            
        Returns:
            Volume tolerance parameters
        """
        # Base volume tolerance factors
        base_tolerance = {
            'beginner': {'sets_per_movement': 8, 'frequency_multiplier': 1.0},
            'intermediate': {'sets_per_movement': 12, 'frequency_multiplier': 1.2},
            'advanced': {'sets_per_movement': 15, 'frequency_multiplier': 1.4}
        }
        
        training_category = self._categorize_training_age(training_age)
        base_metrics = base_tolerance[training_category]
        
        # Calculate adjusted volume metrics
        weekly_volume_capacity = weekly_frequency * session_duration * 60  # Convert to minutes
        
        # Adjust for movement pattern preferences
        pattern_adjustments = {}
        for pattern, analysis in movement_analysis.items():
            if analysis['status'] == 'preferred':
                adjustment = 1.2  # 20% more volume for preferred patterns
            elif analysis['status'] == 'avoided':
                adjustment = 0.8  # 20% less volume for avoided patterns
            else:
                adjustment = 1.0
                
            pattern_adjustments[pattern] = {
                'sets_per_session': round(base_metrics['sets_per_movement'] * adjustment),
                'weekly_frequency': round(weekly_frequency * base_metrics['frequency_multiplier'] * adjustment),
                'recovery_requirement': 'high' if adjustment < 1 else 'normal'
            }
        
        return {
            'base_weekly_volume_capacity': weekly_volume_capacity,
            'pattern_specific_tolerance': pattern_adjustments,
            'volume_category': training_category
        }
    
    def _assess_technique_proficiency(self,
                                    training_age: float,
                                    preferred_exercises: List[str],
                                    movement_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess exercise technique proficiency based on experience.
        
        Args:
            training_age: Years of training experience
            preferred_exercises: List of preferred exercises
            movement_analysis: Movement pattern analysis
            
        Returns:
            Technique proficiency assessment
        """
        # Base proficiency levels
        base_proficiency = {
            'beginner': 1,      # Needs constant form correction
            'intermediate': 2,   # Can maintain form with occasional checks
            'advanced': 3        # Mastered basic movement patterns
        }
        
        training_category = self._categorize_training_age(training_age)
        base_level = base_proficiency[training_category]
        
        # Assess pattern-specific proficiency
        pattern_proficiency = {}
        for pattern, analysis in movement_analysis.items():
            # Adjust base level based on pattern preference
            if analysis['status'] == 'preferred':
                adjusted_level = min(base_level + 1, 3)
            elif analysis['status'] == 'avoided':
                adjusted_level = max(base_level - 1, 1)
            else:
                adjusted_level = base_level
                
            pattern_proficiency[pattern] = {
                'level': adjusted_level,
                'description': self._get_proficiency_description(adjusted_level),
                'recommended_supervision': adjusted_level == 1
            }
        
        return {
            'overall_level': base_level,
            'pattern_proficiency': pattern_proficiency,
            'training_focus_needed': [pattern for pattern, prof in pattern_proficiency.items() 
                                    if prof['level'] == 1]
        }
    
    def _identify_limitations(self,
                            avoided_exercises: List[str],
                            movement_analysis: Dict[str, Any],
                            standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify training limitations and potential red flags.
        
        Args:
            avoided_exercises: List of avoided exercises
            movement_analysis: Movement pattern analysis
            standardized_profile: Complete standardized profile
            
        Returns:
            Identified limitations and recommendations
        """
        limitations = {
            'movement_restrictions': [],
            'equipment_limitations': [],
            'recovery_concerns': [],
            'technique_limitations': []
        }
        
        # Check for movement pattern limitations
        for pattern, analysis in movement_analysis.items():
            if analysis['status'] == 'avoided':
                limitations['movement_restrictions'].append({
                    'pattern': pattern,
                    'avoided_exercises': analysis['avoided_movements'],
                    'alternative_patterns': self._suggest_alternative_patterns(pattern)
                })
        
        # Check equipment availability
        available_equipment = standardized_profile.get('fitness', {}).get('available_equipment', [])
        if not available_equipment:
            limitations['equipment_limitations'].append('Limited equipment access')
        
        # Check recovery factors
        lifestyle = standardized_profile.get('lifestyle', {})
        if lifestyle.get('stress_level') == 'High' or lifestyle.get('daily_work_hours', 0) > 10:
            limitations['recovery_concerns'].append('High stress / long work hours may impact recovery')
        
        return limitations
    
    def _generate_equipment_based_exercises(self,
                                          available_equipment: List[str],
                                          movement_analysis: Dict[str, Any],
                                          limitations: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate exercise recommendations based on available equipment.
        
        Args:
            available_equipment: List of available equipment
            movement_analysis: Movement pattern analysis
            limitations: Identified limitations
            
        Returns:
            Equipment-based exercise recommendations
        """
        recommendations = {}
        
        for pattern, analysis in movement_analysis.items():
            pattern_exercises = []
            
            # Check if pattern is restricted
            is_restricted = any(
                restriction['pattern'] == pattern 
                for restriction in limitations.get('movement_restrictions', [])
            )
            
            if not is_restricted:
                # Generate exercises based on available equipment
                if 'barbell' in available_equipment:
                    pattern_exercises.extend(self._get_barbell_exercises(pattern))
                if 'dumbbell' in available_equipment:
                    pattern_exercises.extend(self._get_dumbbell_exercises(pattern))
                if 'bodyweight' in available_equipment:
                    pattern_exercises.extend(self._get_bodyweight_exercises(pattern))
                if 'machines' in available_equipment:
                    pattern_exercises.extend(self._get_machine_exercises(pattern))
            
            recommendations[pattern] = pattern_exercises
        
        return recommendations
    
    @staticmethod
    def _categorize_training_age(years: float) -> str:
        """Categorize training age into experience levels."""
        if years < 1:
            return 'beginner'
        elif years < 3:
            return 'intermediate'
        else:
            return 'advanced'
    
    @staticmethod
    def _get_proficiency_description(level: int) -> str:
        """Get description for proficiency level."""
        descriptions = {
            1: "Needs regular form correction and supervision",
            2: "Can maintain proper form with occasional checks",
            3: "Mastered basic movement patterns and can self-correct"
        }
        return descriptions.get(level, "Unknown proficiency level")
    
    @staticmethod
    def _suggest_alternative_patterns(pattern: str) -> List[str]:
        """Suggest alternative movement patterns."""
        alternatives = {
            'push': ['pull', 'core'],
            'pull': ['push', 'core'],
            'squat': ['hinge', 'lunge'],
            'hinge': ['squat', 'lunge'],
            'lunge': ['squat', 'hinge'],
            'carry': ['core', 'pull'],
            'core': ['carry', 'push', 'pull']
        }
        return alternatives.get(pattern, [])
    
    @staticmethod
    def _get_barbell_exercises(pattern: str) -> List[str]:
        """Get barbell exercises for movement pattern."""
        exercises = {
            'push': ['Bench Press', 'Overhead Press', 'Close Grip Bench Press'],
            'pull': ['Barbell Row', 'Pendlay Row', 'Power Clean'],
            'squat': ['Back Squat', 'Front Squat', 'Box Squat'],
            'hinge': ['Deadlift', 'Romanian Deadlift', 'Good Morning'],
            'lunge': ['Walking Lunge', 'Split Squat', 'Reverse Lunge'],
            'carry': ['Farmers Walk'],
            'core': ['Landmine Rotation', 'Ab Rollout']
        }
        return exercises.get(pattern, [])
    
    @staticmethod
    def _get_dumbbell_exercises(pattern: str) -> List[str]:
        """Get dumbbell exercises for movement pattern."""
        exercises = {
            'push': ['Dumbbell Press', 'Shoulder Press', 'Incline Press'],
            'pull': ['Single Arm Row', 'Renegade Row', 'Meadows Row'],
            'squat': ['Goblet Squat', 'Dumbbell Squat'],
            'hinge': ['Single Leg RDL', 'Dumbbell RDL'],
            'lunge': ['Dumbbell Lunge', 'Bulgarian Split Squat'],
            'carry': ['Farmers Walk', 'Suitcase Carry'],
            'core': ['Russian Twist', 'Side Bend']
        }
        return exercises.get(pattern, [])
    
    @staticmethod
    def _get_bodyweight_exercises(pattern: str) -> List[str]:
        """Get bodyweight exercises for movement pattern."""
        exercises = {
            'push': ['Pushup', 'Dips', 'Pike Pushup'],
            'pull': ['Pullup', 'Chinup', 'Inverted Row'],
            'squat': ['Air Squat', 'Jump Squat', 'Pistol Squat'],
            'hinge': ['Back Extension', 'Nordic Curl'],
            'lunge': ['Walking Lunge', 'Reverse Lunge', 'Jump Lunge'],
            'carry': [],  # No strict body
        }

        return exercises.get(pattern, [])
    

    # need to be imlen correctly 
    @staticmethod
    def _get_machine_exercises(self) -> List[str]:
        """
        Retrieve a list of machine-based exercises.
        Returns:
            A list of machine-based exercises.
        """
        return ["leg press", "lat pulldown", "chest press", "seated row"]
