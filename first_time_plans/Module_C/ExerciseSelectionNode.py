from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

class ExerciseCategory(Enum):
    COMPOUND = "compound"
    ISOLATION = "isolation"
    ACCESSORY = "accessory"

@dataclass
class Exercise:
    name: str
    category: ExerciseCategory
    target_muscles: List[str]
    equipment_needed: List[str]
    technical_difficulty: int  # 1-5 scale
    joint_stress: int  # 1-5 scale
    recommended_rep_range: tuple[int, int]

class ExerciseSelectionDecisionNode:
    """
    Determines optimal exercise selection based on split type, available equipment,
    and client factors.
    """
    
    def __init__(self):
        self.exercise_library = self._initialize_exercise_library()
        
    def process(self, 
                client_data: Dict[str, Any],
                training_history: Dict[str,Any], 
                split_recommendation: Dict[str, Any],
                volume_guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process client data to determine exercise selection.
        """
        # Extract relevant data
        available_equipment = client_data.get('fitness', {}).get('available_equipment', [])
        movement_restrictions = training_history.get('training_limitations', {}).get('movement_restrictions', [])
        
        # Get training schedule
        training_schedule = split_recommendation.get('schedule', [])
        
        # Generate exercise selection for each training day
        exercise_selection = []
        for day in training_schedule:
            day_exercises = self._select_exercises_for_day(
                day,
                available_equipment,
                movement_restrictions,
                volume_guidelines,
                training_history
            )
            exercise_selection.append({
                'day': day['day'],
                'focus': day['focus'],
                'exercises': day_exercises,
                'notes': self._generate_exercise_notes(day_exercises, training_history)
            })
        
        return {
            'training_days': exercise_selection,
            'exercise_rotation_strategy': self._generate_rotation_strategy(training_history),
            'technical_guidelines': self._generate_technical_guidelines(training_history)
        }
    
    def _initialize_exercise_library(self) -> Dict[str, Dict[str, Exercise]]:
        """
        Initialize the exercise library with categorized exercises.
        """
        library = {
            'push': {
                'bench_press': Exercise(
                    name="Barbell Bench Press",
                    category=ExerciseCategory.COMPOUND,
                    target_muscles=['chest', 'shoulders', 'triceps'],
                    equipment_needed=['barbell', 'bench'],
                    technical_difficulty=3,
                    joint_stress=3,
                    recommended_rep_range=(6, 12)
                ),
                'overhead_press': Exercise(
                    name="Standing Overhead Press",
                    category=ExerciseCategory.COMPOUND,
                    target_muscles=['shoulders', 'triceps'],
                    equipment_needed=['barbell'],
                    technical_difficulty=3,
                    joint_stress=3,
                    recommended_rep_range=(6, 12)
                ),
                # Add more push exercises...
            },
            'pull': {
                'pullup': Exercise(
                    name="Pull-up",
                    category=ExerciseCategory.COMPOUND,
                    target_muscles=['back', 'biceps'],
                    equipment_needed=['pullup_bar'],
                    technical_difficulty=3,
                    joint_stress=2,
                    recommended_rep_range=(6, 12)
                ),
                'row': Exercise(
                    name="Barbell Row",
                    category=ExerciseCategory.COMPOUND,
                    target_muscles=['back', 'biceps', 'rear_delts'],
                    equipment_needed=['barbell'],
                    technical_difficulty=3,
                    joint_stress=3,
                    recommended_rep_range=(8, 12)
                ),
                # Add more pull exercises...
            },
            'legs': {
                'squat': Exercise(
                    name="Barbell Back Squat",
                    category=ExerciseCategory.COMPOUND,
                    target_muscles=['quads', 'glutes', 'core'],
                    equipment_needed=['barbell', 'rack'],
                    technical_difficulty=4,
                    joint_stress=4,
                    recommended_rep_range=(5, 10)
                ),
                'deadlift': Exercise(
                    name="Conventional Deadlift",
                    category=ExerciseCategory.COMPOUND,
                    target_muscles=['hamstrings', 'back', 'glutes'],
                    equipment_needed=['barbell'],
                    technical_difficulty=4,
                    joint_stress=4,
                    recommended_rep_range=(5, 8)
                ),
                # Add more leg exercises...
            }
        }
        
        return library
    
    def _select_exercises_for_day(self,
                                day: Dict[str, Any],
                                available_equipment: List[str],
                                movement_restrictions: List[str],
                                volume_guidelines: Dict[str, Any],
                                training_history: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select appropriate exercises for a training day.
        """
        focus = day['focus'].lower()
        target_muscles = day.get('target_muscles', [])
        
        # Get relevant exercises from library
        potential_exercises = self._filter_exercises_by_constraints(
            focus,
            available_equipment,
            movement_restrictions,
            training_history
        )
        
        # Determine exercise distribution
        exercise_distribution = self._determine_exercise_distribution(
            focus,
            volume_guidelines,
            training_history
        )
        
        selected_exercises = []
        
        # Select compound movements first
        compound_exercises = self._select_compound_exercises(
            potential_exercises,
            exercise_distribution['compound'],
            target_muscles,
            training_history
        )
        selected_exercises.extend(compound_exercises)
        
        # Select isolation exercises
        isolation_exercises = self._select_isolation_exercises(
            potential_exercises,
            exercise_distribution['isolation'],
            target_muscles,
            training_history,
            [ex['name'] for ex in compound_exercises]
        )
        selected_exercises.extend(isolation_exercises)
        
        return selected_exercises
    
    def _filter_exercises_by_constraints(self,
                                       focus: str,
                                       available_equipment: List[str],
                                       movement_restrictions: List[str],
                                       training_history: Dict[str, Any]) -> List[Exercise]:
        """
        Filter exercises based on equipment and movement restrictions.
        """
        filtered_exercises = []
        relevant_exercises = self.exercise_library.get(focus, {})
        
        for exercise in relevant_exercises.values():
            # Check if required equipment is available
            if not all(eq in available_equipment for eq in exercise.equipment_needed):
                continue
                
            # Check for movement restrictions
            if any(restriction in exercise.name.lower() for restriction in movement_restrictions):
                continue
                
            # Check technical difficulty against training age
            training_age = training_history.get('training_age', {}).get('category', 'intermediate').lower()
            if training_age == 'beginner' and exercise.technical_difficulty > 3:
                continue
                
            filtered_exercises.append(exercise)
            
        return filtered_exercises
    
    def _determine_exercise_distribution(self,
                                       focus: str,
                                       volume_guidelines: Dict[str, Any],
                                       training_history: Dict[str, Any]) -> Dict[str, int]:
        """
        Determine the distribution of compound vs isolation exercises.
        """
        training_age = training_history.get('training_age', {}).get('category', 'intermediate').lower()
        
        # Base distributions by training age
        distributions = {
            'beginner': {'compound': 2, 'isolation': 1},
            'intermediate': {'compound': 2, 'isolation': 2},
            'advanced': {'compound': 3, 'isolation': 2}
        }
        
        base_distribution = distributions.get(training_age, distributions['intermediate'])
        
        # Adjust based on volume guidelines
        muscle_volumes = volume_guidelines.get('volume_guidelines', {})
        if any(volume.maximum_adaptive_volume > 15 for volume in muscle_volumes.values()):
            base_distribution['isolation'] += 1
            
        return base_distribution
    
    def _select_compound_exercises(self,
                                 available_exercises: List[Exercise],
                                 num_compounds: int,
                                 target_muscles: List[str],
                                 training_history: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select appropriate compound exercises.
        """
        compound_exercises = [ex for ex in available_exercises 
                            if ex.category == ExerciseCategory.COMPOUND]
        
        # Sort by technical proficiency
        technique_proficiency = training_history.get('technique_proficiency', {})
        compound_exercises.sort(
            key=lambda x: technique_proficiency.get(x.name, 3),
            reverse=True
        )
        
        selected = []
        for _ in range(min(num_compounds, len(compound_exercises))):
            exercise = compound_exercises.pop(0)
            selected.append({
                'name': exercise.name,
                'category': exercise.category.value,
                'sets': self._determine_sets_for_exercise(exercise, training_history),
                'rep_range': exercise.recommended_rep_range,
                'notes': self._generate_exercise_specific_notes(exercise, training_history)
            })
            
        return selected
    
    def _select_isolation_exercises(self,
                                  available_exercises: List[Exercise],
                                  num_isolations: int,
                                  target_muscles: List[str],
                                  training_history: Dict[str, Any],
                                  selected_exercises: List[str]) -> List[Dict[str, Any]]:
        """
        Select appropriate isolation exercises.
        """
        isolation_exercises = [ex for ex in available_exercises 
                             if ex.category == ExerciseCategory.ISOLATION]
        
        # Prioritize exercises for underdeveloped muscles
        muscle_distribution = training_history.get('movement_pattern_analysis', {})
        isolation_exercises.sort(
            key=lambda x: any(muscle in str(muscle_distribution.get('underdeveloped', []))
                            for muscle in x.target_muscles),
            reverse=True
        )
        
        selected = []
        for _ in range(min(num_isolations, len(isolation_exercises))):
            exercise = isolation_exercises.pop(0)
            selected.append({
                'name': exercise.name,
                'category': exercise.category.value,
                'sets': self._determine_sets_for_exercise(exercise, training_history),
                'rep_range': exercise.recommended_rep_range,
                'notes': self._generate_exercise_specific_notes(exercise, training_history)
            })
            
        return selected
    
    def _determine_sets_for_exercise(self,
                                   exercise: Exercise,
                                   training_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine appropriate sets for an exercise.
        """
        training_age = training_history.get('training_age', {}).get('category', 'intermediate').lower()
        volume_tolerance = training_history.get('volume_tolerance', {}).get('volume_category', 'moderate').lower()
        
        base_sets = {
            'beginner': {'warmup': 2, 'working': 3},
            'intermediate': {'warmup': 2, 'working': 4},
            'advanced': {'warmup': 3, 'working': 5}
        }
        
        sets = base_sets.get(training_age, base_sets['intermediate'])
        
        # Adjust for volume tolerance
        if volume_tolerance == 'high':
            sets['working'] += 1
        elif volume_tolerance == 'low':
            sets['working'] -= 1
            
        return sets
    
    def _generate_exercise_specific_notes(self,
                                        exercise: Exercise,
                                        training_history: Dict[str, Any]) -> str:
        """
        Generate specific notes for an exercise based on client factors.
        """
        notes = []
        
        # Check technical proficiency
        technique_level = training_history.get('technique_proficiency', {}).get('overall_level', 2)
        if technique_level < 3 and exercise.technical_difficulty > 3:
            notes.append("Focus on form and controlled execution")
            
        # Check joint stress considerations
        if exercise.joint_stress >= 4:
            notes.append("Monitor joint stress and adjust load as needed")
            
        # Add exercise-specific cues
        if 'squat' in exercise.name.lower():
            notes.append("Maintain proper depth and knee tracking")
        elif 'deadlift' in exercise.name.lower():
            notes.append("Focus on maintaining neutral spine")
            
        return '. '.join(notes) if notes else "Standard execution"
    
    def _generate_rotation_strategy(self, training_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate strategy for exercise rotation.
        """
        training_age = training_history.get('training_age', {}).get('category', 'intermediate').lower()
        
        strategies = {
            'beginner': {
                'rotation_frequency': 'Every 8-12 weeks',
                'exercise_substitution': 'Minimal - focus on mastering basic movements',
                'variation_strategy': 'Progressive overload on main lifts'
            },
            'intermediate': {
                'rotation_frequency': 'Every 4-6 weeks',
                'exercise_substitution': 'Moderate - introduce variations of main lifts',
                'variation_strategy': 'Alternate between main lifts and variations'
            },
            'advanced': {
                'rotation_frequency': 'Every 2-4 weeks',
                'exercise_substitution': 'Regular - utilize wide exercise selection',
                'variation_strategy': 'Frequent variation while maintaining movement patterns'
            }
        }
        
        return strategies.get(training_age, strategies['intermediate'])
    
    def _generate_technical_guidelines(self, training_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate technical guidelines based on training history.
        """
        technique_level = training_history.get('technique_proficiency', {}).get('overall_level', 2)
        
        if technique_level <= 2:
            return {
                'focus_areas': ['Movement pattern mastery', 'Basic technique development'],
                'cues': ['Control the eccentric', 'Maintain proper positioning'],
                'progression_approach': 'Master form before increasing load'
            }
        elif technique_level <= 3:
            return {
                'focus_areas': ['Advanced technique refinement', 'Movement efficiency'],
                'cues': ['Optimize bar path', 'Speed control'],
                'progression_approach': 'Balance load increases with technique maintenance'
            }
        else:
            return {
                'focus_areas': ['Technical mastery', 'Movement optimization'],
                'cues': ['Position-specific power application', 'Advanced tempo manipulation'],
                'progression_approach': 'Implement advanced variations while maintaining technique'
            }


