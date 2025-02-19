from typing import Dict, Any

class MealTimingDecisionNode:
    def __init__(self):
        """Initialize the MealTimingDecisionNode."""
        self.meal_timing_plan = {}
    
    def process(self, macro_distribution: Dict[str, Any], training_split: Dict[str, Any],
                client_profile: Dict[str, Any], goal_analysis: Dict[str, Any],
                recovery_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine optimal meal timing based on training schedule and other factors.
        
        Args:
            macro_distribution: Output from MacroDistributionDecisionNode
            training_split: Training split recommendations
            client_profile: Client profile analysis
            goal_analysis: Goal clarification analysis
            recovery_analysis: Recovery and lifestyle analysis
            
        Returns:
            Dictionary containing meal timing recommendations
        """
        # Extract relevant data
        daily_calories = macro_distribution.get('daily_calories', 0)
        macros = macro_distribution.get('macronutrients', {})
        training_days = training_split.get('training_days', [])
        training_frequency = client_profile.get('weekly_training_frequency', 5)
        session_duration = client_profile.get('session_duration_hours', 1.5)
        primary_goal = goal_analysis.get('primary_goal', '').lower()
        barriers = goal_analysis.get('barriers', {})
        lifestyle = recovery_analysis.get('lifestyle_factors', {})
        
        # Generate timing recommendations
        self.meal_timing_plan = {
            'general_structure': self._generate_daily_structure(
                daily_calories, training_frequency, session_duration, barriers
            ),
            'training_day_timing': self._generate_training_day_plan(
                macros, training_days, primary_goal, session_duration
            ),
            'non_training_day_timing': self._generate_non_training_day_plan(
                macros, primary_goal, barriers
            ),
            'meal_spacing': self._calculate_meal_spacing(
                lifestyle, barriers, training_days
            ),
            'timing_adjustments': self._generate_timing_adjustments(
                primary_goal, barriers, lifestyle
            ),
            'special_considerations': self._handle_special_considerations(
                goal_analysis, recovery_analysis
            )
        }
        
        return self.meal_timing_plan
    
    def _generate_daily_structure(self, daily_calories: int, training_frequency: int,
                                session_duration: float, barriers: Dict[str, bool]) -> Dict[str, Any]:
        """Generate the basic daily meal structure."""
        # Determine optimal meal frequency
        base_meals = 3 if barriers.get('time_constraints', False) else 4
        
        if daily_calories > 2500 and not barriers.get('time_constraints', False):
            base_meals += 1
        
        return {
            'recommended_meals': base_meals,
            'meal_size_distribution': self._calculate_meal_sizes(base_meals, daily_calories),
            'minimum_meal_frequency': max(3, base_meals - 1),
            'maximum_meal_frequency': base_meals + 1,
            'snack_recommendations': self._generate_snack_recommendations(
                daily_calories, training_frequency, barriers
            )
        }
    
    def _generate_training_day_plan(self, macros: Dict[str, Any], training_days: list,
                                  primary_goal: str, session_duration: float) -> Dict[str, Any]:
        """Generate specific timing recommendations for training days."""
        pre_workout_window = 2  # hours before training
        post_workout_window = 1  # hours after training
        
        plan = {
            'pre_workout_meal': {
                'timing': f"{pre_workout_window} hours before training",
                'protein': f"{round(macros.get('protein', {}).get('grams', 0) * 0.25)}g protein",
                'carbohydrates': f"{round(macros.get('carbohydrates', {}).get('grams', 0) * 0.3)}g carbs",
                'fats': f"{round(macros.get('fats', {}).get('grams', 0) * 0.15)}g fats"
            },
            'post_workout_meal': {
                'timing': f"Within {post_workout_window} hour after training",
                'protein': f"{round(macros.get('protein', {}).get('grams', 0) * 0.25)}g protein",
                'carbohydrates': f"{round(macros.get('carbohydrates', {}).get('grams', 0) * 0.35)}g carbs",
                'fats': f"{round(macros.get('fats', {}).get('grams', 0) * 0.15)}g fats"
            }
        }
        
        if session_duration > 1.5:
            plan['intra_workout'] = {
                'recommendation': 'Consider intra-workout nutrition',
                'carbohydrates': '15-30g fast-acting carbs per hour',
                'hydration': '500-750ml water per hour'
            }
        
        return plan
    
    def _generate_non_training_day_plan(self, macros: Dict[str, Any],
                                      primary_goal: str, barriers: Dict[str, bool]) -> Dict[str, Any]:
        """Generate meal timing recommendations for non-training days."""
        return {
            'meal_distribution': {
                'breakfast': {
                    'timing': 'Within 1-2 hours of waking',
                    'protein': f"{round(macros.get('protein', {}).get('grams', 0) * 0.25)}g protein",
                    'carbohydrates': f"{round(macros.get('carbohydrates', {}).get('grams', 0) * 0.25)}g carbs",
                    'fats': f"{round(macros.get('fats', {}).get('grams', 0) * 0.3)}g fats"
                },
                'lunch': {
                    'timing': '3-4 hours after breakfast',
                    'protein': f"{round(macros.get('protein', {}).get('grams', 0) * 0.25)}g protein",
                    'carbohydrates': f"{round(macros.get('carbohydrates', {}).get('grams', 0) * 0.25)}g carbs",
                    'fats': f"{round(macros.get('fats', {}).get('grams', 0) * 0.3)}g fats"
                },
                'dinner': {
                    'timing': '3-4 hours after lunch',
                    'protein': f"{round(macros.get('protein', {}).get('grams', 0) * 0.25)}g protein",
                    'carbohydrates': f"{round(macros.get('carbohydrates', {}).get('grams', 0) * 0.25)}g carbs",
                    'fats': f"{round(macros.get('fats', {}).get('grams', 0) * 0.3)}g fats"
                }
            },
            'flexibility_guidelines': self._get_flexibility_guidelines(primary_goal, barriers)
        }
    
    def _calculate_meal_spacing(self, lifestyle: Dict[str, Any], barriers: Dict[str, bool],
                              training_days: list) -> Dict[str, Any]:
        """Calculate optimal meal spacing based on lifestyle factors."""
        base_spacing = 3  # hours between meals
        
        if barriers.get('time_constraints', False):
            base_spacing = 4
        
        return {
            'minimum_spacing': f"{base_spacing - 0.5} hours between meals",
            'optimal_spacing': f"{base_spacing} hours between meals",
            'maximum_spacing': f"{base_spacing + 2} hours between meals",
            'overnight_fasting': '8-12 hours',
            'spacing_guidelines': self._get_spacing_guidelines(lifestyle, barriers)
        }
    
    def _calculate_meal_sizes(self, meal_count: int, daily_calories: int) -> Dict[str, str]:
        """Calculate the size distribution of meals throughout the day."""
        if meal_count == 3:
            return {
                'breakfast': f"{round(daily_calories * 0.3)}kcal (30%)",
                'lunch': f"{round(daily_calories * 0.35)}kcal (35%)",
                'dinner': f"{round(daily_calories * 0.35)}kcal (35%)"
            }
        elif meal_count == 4:
            return {
                'breakfast': f"{round(daily_calories * 0.25)}kcal (25%)",
                'lunch': f"{round(daily_calories * 0.30)}kcal (30%)",
                'afternoon_meal': f"{round(daily_calories * 0.20)}kcal (20%)",
                'dinner': f"{round(daily_calories * 0.25)}kcal (25%)"
            }
        else:  # 5 meals
            return {
                'breakfast': f"{round(daily_calories * 0.20)}kcal (20%)",
                'morning_snack': f"{round(daily_calories * 0.15)}kcal (15%)",
                'lunch': f"{round(daily_calories * 0.25)}kcal (25%)",
                'afternoon_snack': f"{round(daily_calories * 0.15)}kcal (15%)",
                'dinner': f"{round(daily_calories * 0.25)}kcal (25%)"
            }
    
    def _generate_snack_recommendations(self, daily_calories: int,
                                      training_frequency: int,
                                      barriers: Dict[str, bool]) -> Dict[str, Any]:
        """Generate snack timing and composition recommendations."""
        return {
            'timing': {
                'pre_workout': '1-2 hours before training',
                'post_workout': 'Within 30 minutes after training',
                'between_meals': '2-3 hours after main meals'
            },
            'composition': {
                'pre_workout': 'Easily digestible carbs with moderate protein',
                'post_workout': 'Fast-digesting protein with high-glycemic carbs',
                'between_meals': 'Balanced protein and fats for satiety'
            },
            'examples': self._get_snack_examples(daily_calories, barriers)
        }
    
    def _get_flexibility_guidelines(self, primary_goal: str,
                                  barriers: Dict[str, bool]) -> Dict[str, str]:
        """Generate flexibility guidelines for meal timing."""
        guidelines = {
            'meal_window_flexibility': '±30 minutes for most meals',
            'priority_meals': 'Pre and post-workout meals require stricter timing',
            'weekend_adjustment': 'Allow ±1 hour flexibility on weekends'
        }
        
        if barriers.get('time_constraints', False):
            guidelines['practical_tips'] = 'Focus on hitting daily targets rather than perfect timing'
            guidelines['meal_prep'] = 'Prepare meals in advance for busy days'
        
        return guidelines
    
    def _get_spacing_guidelines(self, lifestyle: Dict[str, Any],
                              barriers: Dict[str, bool]) -> Dict[str, str]:
        """Generate specific guidelines for meal spacing."""
        return {
            'minimum_time_after_waking': '30 minutes',
            'last_meal_timing': '2-3 hours before bed',
            'workout_considerations': 'Adjust meal timing around training sessions',
            'practical_adjustments': self._get_practical_adjustments(lifestyle, barriers)
        }
    
    def _get_snack_examples(self, daily_calories: int,
                           barriers: Dict[str, bool]) -> Dict[str, list]:
        """Provide specific snack examples based on daily caloric needs."""
        return {
            'pre_workout': [
                'Greek yogurt with berries',
                'Apple with protein shake',
                'Rice cakes with jam'
            ],
            'post_workout': [
                'Protein shake with banana',
                'Rice cakes with tuna',
                'Protein bar with fruit'
            ],
            'between_meals': [
                'Nuts and dried fruit',
                'Protein shake with almonds',
                'Cottage cheese with fruit'
            ]
        }
    
    def _get_practical_adjustments(self, lifestyle: Dict[str, Any],
                                 barriers: Dict[str, bool]) -> Dict[str, str]:
        """Generate practical adjustments for different lifestyle scenarios."""
        adjustments = {
            'early_morning_training': 'Light pre-workout meal or training fasted if preferred',
            'late_night_training': 'Reduce post-workout meal size if close to bedtime',
            'busy_work_schedule': 'Prepare meals in advance and use meal prep strategies'
        }
        
        if barriers.get('time_constraints', False):
            adjustments['quick_meals'] = 'Keep ready-to-eat protein sources available'
        
        return adjustments
    
    def _generate_timing_adjustments(self, primary_goal: str, barriers: Dict[str, bool],
                                   lifestyle: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific timing adjustments based on goals and lifestyle."""
        adjustments = {
            'goal_specific': self._get_goal_specific_adjustments(primary_goal),
            'barrier_specific': self._get_barrier_specific_adjustments(barriers),
            'lifestyle_specific': self._get_lifestyle_specific_adjustments(lifestyle)
        }
        
        return adjustments
    
    def _handle_special_considerations(self, goal_analysis: Dict[str, Any],
                                     recovery_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle any special considerations for meal timing."""
        considerations = {
            'sleep_quality': {
                'last_meal_timing': '2-3 hours before bed',
                'protein_before_bed': 'Consider slow-digesting protein source',
                'carb_timing': 'Adjust based on sleep quality and recovery needs'
            },
            'recovery_optimization': {
                'post_workout_window': 'Priority on post-workout nutrition timing',
                'protein_distribution': 'Evenly space protein feedings',
                'carb_timing': 'Concentrate around training for performance'
            }
        }
        
        return considerations
    
    def _get_goal_specific_adjustments(self, primary_goal: str) -> Dict[str, str]:
        """
        Generate timing adjustments specific to the client's primary goal.
        
        Args:
            primary_goal: Client's primary goal
            
        Returns:
            Dictionary of goal-specific timing adjustments
        """
        adjustments = {}
        
        if 'muscle' in primary_goal or 'hypertrophy' in primary_goal:
            adjustments = {
                'meal_frequency': 'Higher meal frequency (4-6 meals) to support muscle growth',
                'protein_timing': 'Every 3-4 hours to maximize muscle protein synthesis',
                'carb_timing': 'Higher carbs pre/post workout for performance and recovery',
                'pre_bed': 'Slow-digesting protein before bed to support overnight recovery'
            }
        elif 'fat loss' in primary_goal or 'cut' in primary_goal:
            adjustments = {
                'meal_frequency': 'Moderate meal frequency (3-4 meals) for better adherence',
                'meal_timing': 'Larger meals earlier in the day',
                'carb_timing': 'Concentrate carbs around training sessions',
                'evening_meals': 'Lower carb evening meals to support fat loss'
            }
        else:  # maintenance or general fitness
            adjustments = {
                'meal_frequency': 'Moderate meal frequency (3-5 meals) based on preference',
                'timing_flexibility': 'More flexible meal timing windows',
                'nutrient_distribution': 'Even distribution of nutrients throughout day',
                'workout_nutrition': 'Moderate focus on workout nutrition timing'
            }
        
        return adjustments

    def _get_barrier_specific_adjustments(self, barriers: Dict[str, bool]) -> Dict[str, str]:
        """
        Generate timing adjustments based on client-specific barriers.
        
        Args:
            barriers: Dictionary of client barriers
            
        Returns:
            Dictionary of barrier-specific timing adjustments
        """
        adjustments = {}
        
        if barriers.get('time_constraints', False):
            adjustments['scheduling'] = 'Simplified meal timing with wider windows'
            adjustments['preparation'] = 'Batch cooking and meal prep strategies'
            adjustments['meal_frequency'] = 'Lower meal frequency with larger portions'
        
        if barriers.get('stress', False):
            adjustments['cortisol_management'] = 'Avoid large meals close to bedtime'
            adjustments['meal_spacing'] = 'Regular meal timing to stabilize blood sugar'
        
        if barriers.get('sleep', False):
            adjustments['evening_timing'] = 'Last meal 3 hours before bed'
            adjustments['carb_timing'] = 'Consider moderate carbs at dinner for sleep'
        
        if barriers.get('digestion', False):
            adjustments['meal_spacing'] = 'Longer intervals between meals for digestion'
            adjustments['meal_size'] = 'Smaller, more frequent meals if needed'
        
        return adjustments
    

    def _get_lifestyle_specific_adjustments(self, lifestyle: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate timing adjustments based on lifestyle factors.
        
        Args:
            lifestyle: Dictionary of lifestyle factors
            
        Returns:
            Dictionary of lifestyle-specific timing adjustments
        """
        adjustments = {}
        
        work_schedule = lifestyle.get('work_schedule', 'standard')
        stress_level = lifestyle.get('stress_level', 'moderate')
        sleep_schedule = lifestyle.get('sleep_schedule', 'regular')
        
        if work_schedule == 'shift_work':
            adjustments['meal_timing'] = 'Adjust meal timing to match shift schedule'
            adjustments['sleep_consideration'] = 'Maintain consistent meal patterns despite varying sleep'
        
        if stress_level == 'high':
            adjustments['cortisol_management'] = 'Regular meal timing to manage stress response'
            adjustments['evening_nutrition'] = 'Emphasis on relaxing evening meal routine'
        
        if sleep_schedule == 'irregular':
            adjustments['consistency'] = 'Focus on meal spacing rather than specific times'
            adjustments['flexibility'] = 'Adaptable meal windows based on sleep/wake cycle'
        
        return adjustments