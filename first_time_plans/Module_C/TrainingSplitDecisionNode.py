from typing import Dict, Any, List, Tuple
import math

class TrainingSplitDecisionNode:
    def __init__(self):
        """Initialize the TrainingSplitDecisionNode."""
        self.split_options = {
            'push_pull_legs': {
                'min_sessions': 3,
                'optimal_sessions': 6,
                'recovery_demand': 'moderate',
                'time_per_session': 1.0,  # hours
                'complexity': 'moderate',
                'suitable_experience_levels': ['intermediate', 'advanced']
            },
            'upper_lower': {
                'min_sessions': 2,
                'optimal_sessions': 4,
                'recovery_demand': 'moderate',
                'time_per_session': 1.25,
                'complexity': 'low',
                'suitable_experience_levels': ['beginner', 'intermediate', 'advanced']
            },
            'full_body': {
                'min_sessions': 2,
                'optimal_sessions': 3,
                'recovery_demand': 'high',
                'time_per_session': 1.5,
                'complexity': 'high',
                'suitable_experience_levels': ['beginner', 'intermediate']
            },
            'body_part_split': {
                'min_sessions': 4,
                'optimal_sessions': 5,
                'recovery_demand': 'low',
                'time_per_session': 1.0,
                'complexity': 'low',
                'suitable_experience_levels': ['intermediate', 'advanced']
            }
        }

    def process(self, profile_analysis: Dict[str, Any], goal_analysis: Dict[str, Any], 
                body_analysis: Dict[str, Any], history_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process all inputs to determine the optimal training split.
        
        Args:
            profile_analysis: Output from ClientProfileModule
            goal_analysis: Output from GoalClarificationModule
            body_analysis: Output from BodyCompositionModule
            history_analysis: Output from TrainingHistoryModule
            
        Returns:
            Dictionary containing selected split and rationale
        """
        # Extract key parameters
        sessions_per_week = profile_analysis.get('weekly_training_frequency', 0)
        hours_per_session = profile_analysis.get('session_duration_hours', 0)
        training_age = history_analysis.get('training_age', {}).get('category', '').lower()
        primary_goal = goal_analysis.get('primary_goal', '').lower()
        
        # Get movement limitations and equipment access
        movement_restrictions = history_analysis.get('training_limitations', {}).get('movement_restrictions', [])
        equipment_limitations = history_analysis.get('training_limitations', {}).get('equipment_limitations', [])
        
        # Analyze muscle distribution imbalances
        muscle_distribution = body_analysis.get('muscle_distribution', {})
        
        # Score each split based on various factors
        split_scores = self._score_splits(
            sessions_per_week=sessions_per_week,
            hours_per_session=hours_per_session,
            training_age=training_age,
            primary_goal=primary_goal,
            movement_restrictions=movement_restrictions,
            equipment_limitations=equipment_limitations,
            muscle_distribution=muscle_distribution
        )
        
        # Select the best split and generate rationale
        selected_split, rationale = self._select_best_split(split_scores)
        
        # Generate the training days distribution
        training_days = self._generate_training_days(selected_split, sessions_per_week)
        
        return {
            'selected_split': selected_split,
            'rationale': rationale,
            'training_days': training_days,
            'sessions_per_week': sessions_per_week,
            'split_scores': split_scores  # Include for transparency
        }

    def _score_splits(self, sessions_per_week: int, hours_per_session: float,
                     training_age: str, primary_goal: str, movement_restrictions: List[str],
                     equipment_limitations: List[str], muscle_distribution: Dict[str, str]) -> Dict[str, float]:
        """Score each split based on various factors."""
        scores = {}
        
        for split_name, split_params in self.split_options.items():
            score = 0.0
            
            # Base score from session frequency match
            frequency_match = min(sessions_per_week / split_params['optimal_sessions'], 1.0)
            score += frequency_match * 30  # Max 30 points
            
            # Time per session compatibility
            if hours_per_session >= split_params['time_per_session']:
                score += 20
            else:
                score += (hours_per_session / split_params['time_per_session']) * 20
            
            # Experience level compatibility
            if training_age in split_params['suitable_experience_levels']:
                score += 20
            
            # Goal compatibility
            goal_compatibility = self._assess_goal_compatibility(split_name, primary_goal)
            score += goal_compatibility * 15
            
            # Movement restrictions impact
            movement_impact = self._assess_movement_restrictions(split_name, movement_restrictions)
            score -= movement_impact * 10
            
            # Equipment limitations impact
            equipment_impact = self._assess_equipment_limitations(split_name, equipment_limitations)
            score -= equipment_impact * 10
            
            # Muscle distribution considerations
            distribution_bonus = self._assess_muscle_distribution(split_name, muscle_distribution)
            score += distribution_bonus * 5
            
            scores[split_name] = max(0, min(100, score))  # Clamp between 0 and 100
            
        return scores

    def _assess_goal_compatibility(self, split_name: str, primary_goal: str) -> float:
        """Assess how well a split matches the primary goal."""
        compatibility_matrix = {
            'push_pull_legs': {
                'hypertrophy': 1.0,
                'strength': 0.8,
                'general_fitness': 0.6,
                'specific_skill': 0.7
            },
            'upper_lower': {
                'hypertrophy': 0.8,
                'strength': 1.0,
                'general_fitness': 0.8,
                'specific_skill': 0.7
            },
            'full_body': {
                'hypertrophy': 0.6,
                'strength': 0.7,
                'general_fitness': 1.0,
                'specific_skill': 0.8
            },
            'body_part_split': {
                'hypertrophy': 1.0,
                'strength': 0.7,
                'general_fitness': 0.5,
                'specific_skill': 0.6
            }
        }
        
        return compatibility_matrix.get(split_name, {}).get(primary_goal, 0.5)

    def _assess_movement_restrictions(self, split_name: str, restrictions: List[str]) -> float:
        """Assess the impact of movement restrictions on split viability."""
        if not restrictions:
            return 0.0
            
        # Define which splits are most affected by common restrictions
        restriction_impact = {
            'push_pull_legs': ['shoulder_pain', 'elbow_pain', 'back_pain'],
            'upper_lower': ['knee_pain', 'hip_pain', 'ankle_pain'],
            'full_body': ['general_fatigue', 'joint_pain'],
            'body_part_split': ['shoulder_pain', 'knee_pain']
        }
        
        impact_count = sum(1 for r in restrictions if r in restriction_impact.get(split_name, []))
        return impact_count / len(restrictions)

    def _assess_equipment_limitations(self, split_name: str, limitations: List[str]) -> float:
        """Assess the impact of equipment limitations on split viability."""
        if not limitations:
            return 0.0
            
        # Define minimum equipment needs for each split
        equipment_needs = {
            'push_pull_legs': ['barbell', 'rack', 'bench', 'dumbbells'],
            'upper_lower': ['barbell', 'rack', 'bench'],
            'full_body': ['barbell', 'rack', 'bench', 'dumbbells'],
            'body_part_split': ['cables', 'machines', 'dumbbells']
        }
        
        missing_equipment = sum(1 for eq in equipment_needs.get(split_name, [])
                              if any(lim in eq for lim in limitations))
        return missing_equipment / len(equipment_needs.get(split_name, [1]))

    def _assess_muscle_distribution(self, split_name: str, distribution: Dict[str, str]) -> float:
        """Award bonus points for splits that can address muscle distribution imbalances."""
        if not distribution:
            return 0.0
            
        bonus = 0.0
        
        # Check for specific imbalances and match with appropriate splits
        if 'upper_body' in distribution and 'underdeveloped' in distribution['upper_body'].lower():
            if split_name in ['push_pull_legs', 'upper_lower']:
                bonus += 0.5
                
        if 'lower_body' in distribution and 'underdeveloped' in distribution['lower_body'].lower():
            if split_name in ['push_pull_legs', 'upper_lower']:
                bonus += 0.5
                
        return bonus

    def _select_best_split(self, split_scores: Dict[str, float]) -> Tuple[str, str]:
        """Select the best split and generate rationale."""
        best_split = max(split_scores.items(), key=lambda x: x[1])[0]
        
        # Generate rationale based on the winning split
        rationale_templates = {
            'push_pull_legs': "Selected Push/Pull/Legs split due to its optimal balance between volume, frequency, and recovery. This split allows dedicated focus on each movement pattern while maintaining adequate recovery.",
            'upper_lower': "Selected Upper/Lower split for its practical frequency and clear targeting of major muscle groups. This split provides good recovery while maintaining training efficiency.",
            'full_body': "Selected Full Body split to maximize frequency and efficiency. This approach allows for high practice frequency of movement patterns while managing fatigue.",
            'body_part_split': "Selected Body Part split to allow maximum volume per muscle group with dedicated recovery periods. This split enables intense focus on specific muscle groups."
        }
        
        return best_split, rationale_templates.get(best_split, "Split selected based on optimal scoring across all factors.")

    def _generate_training_days(self, split_type: str, sessions_per_week: int) -> List[str]:
        """Generate training day distribution based on split type and frequency."""
        if split_type == 'push_pull_legs':
            if sessions_per_week >= 6:
                return ['Push', 'Pull', 'Legs', 'Push', 'Pull', 'Legs'][:sessions_per_week]
            else:
                return (['Push', 'Pull', 'Legs'] * 2)[:sessions_per_week]
                
        elif split_type == 'upper_lower':
            return (['Upper', 'Lower'] * 3)[:sessions_per_week]
            
        elif split_type == 'full_body':
            return ['Full Body'] * sessions_per_week
            
        elif split_type == 'body_part_split':
            return ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms'][:sessions_per_week]
            
        return ['Unspecified'] * sessions_per_week