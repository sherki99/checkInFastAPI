
from typing import Dict, Any, List
from datetime import datetime, timedelta


"""1. **PlanIntegrationNode**
    - **Input:**
        - Workout decision outputs (training split, volume, exercises)
        - Nutrition decision outputs (caloric targets, macros, meal timing)
    - **Process:**
        - Integrates all parameters into a coherent, synchronized plan
        - Ensures that the workout and nutrition plans support each other (e.g., meal timing aligns with training sessions)
    - **Output:** A unified training and nutrition strategy

"""


class PlanIntegrationNode:
    def __init__(self):
        """Initialize the PlanIntegrationNode."""
        self.integrated_plan = {}
    
    def process(self, workout_plan: Dict[str, Any], nutrition_plan: Dict[str, Any],
                client_profile: Dict[str, Any], training_history: Dict[str, Any],
                goal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate workout and nutrition plans into a synchronized strategy.
        
        Args:
            workout_plan: Complete workout plan with training split, volume, exercises
            nutrition_plan: Complete nutrition plan with macros and meal timing
            client_profile: Client profile analysis
            training_history: Training history analysis
            goal_analysis: Goal clarification analysis
            
        Returns:
            Dictionary containing the integrated plan
        """
        # Extract key parameters
        training_days = workout_plan.get('training_split', {}).get('days_per_week', 5)
        session_duration = client_profile.get('session_duration_hours', 1.5)
        primary_goal = goal_analysis.get('primary_goal', '').lower()
        barriers = goal_analysis.get('barriers', {})
        
        # Generate integrated weekly schedule
        weekly_schedule = self._create_weekly_schedule(
            workout_plan, nutrition_plan, training_days, session_duration, barriers
        )
        
        # Generate daily protocols
        daily_protocols = self._create_daily_protocols(
            workout_plan, nutrition_plan, primary_goal
        )
        
        # Create recovery guidelines
        recovery_guidelines = self._create_recovery_guidelines(
            workout_plan, training_history, barriers
        )
        
        # Generate progress tracking metrics
        tracking_metrics = self._create_tracking_metrics(
            workout_plan, nutrition_plan, goal_analysis
        )
        
        # Build the integrated plan
        self.integrated_plan = {
            'weekly_schedule': weekly_schedule,
            'daily_protocols': daily_protocols,
            'recovery_guidelines': recovery_guidelines,
            'tracking_metrics': tracking_metrics,
            'plan_synchronization': self._create_plan_synchronization(
                workout_plan, nutrition_plan, primary_goal
            ),
            'adherence_strategies': self._create_adherence_strategies(barriers, primary_goal),
            'adaptation_guidelines': self._create_adaptation_guidelines(
                workout_plan, nutrition_plan, goal_analysis
            )
        }
        
        return self.integrated_plan
    
    def _create_weekly_schedule(self, workout_plan: Dict[str, Any], 
                              nutrition_plan: Dict[str, Any],
                              training_days: int, session_duration: float,
                              barriers: Dict[str, bool]) -> Dict[str, Any]:
        """
        Create an integrated weekly schedule aligning training and nutrition.
        
        Args:
            workout_plan: Workout plan details
            nutrition_plan: Nutrition plan details
            training_days: Number of training days per week
            session_duration: Training session duration
            barriers: Client barriers
            
        Returns:
            Dictionary containing weekly schedule
        """
        # Default schedule template
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        schedule = {}
        
        # Get training split details
        split_type = workout_plan.get('training_split', {}).get('type', 'full_body')
        workouts = workout_plan.get('training_split', {}).get('workouts', [])
        
        # Get nutrition timing
        meal_timing = nutrition_plan.get('nutrient_timing', {})
        
        # Create optimal training distribution
        training_distribution = self._optimize_training_distribution(
            training_days, barriers.get('time_constraints', False)
        )
        
        # Build daily schedules
        workout_index = 0
        for day in days:
            is_training_day = day in training_distribution
            
            if is_training_day and workout_index < len(workouts):
                current_workout = workouts[workout_index]
                workout_index += 1
            else:
                current_workout = None
            
            schedule[day] = self._create_daily_schedule(
                is_training_day,
                current_workout,
                meal_timing,
                session_duration,
                barriers
            )
        
        return schedule
    
    def _optimize_training_distribution(self, training_days: int, 
                                     time_constrained: bool) -> List[str]:
        """
        Optimize the distribution of training days across the week.
        
        Args:
            training_days: Number of training days
            time_constrained: Whether client has time constraints
            
        Returns:
            List of optimal training days
        """
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        if time_constrained:
            # Prioritize weekday evenings and weekend mornings
            if training_days == 3:
                return ['Monday', 'Wednesday', 'Friday']
            elif training_days == 4:
                return ['Monday', 'Tuesday', 'Thursday', 'Saturday']
            elif training_days == 5:
                return ['Monday', 'Tuesday', 'Thursday', 'Friday', 'Saturday']
            elif training_days == 6:
                return ['Monday', 'Tuesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        else:
            # More balanced distribution
            if training_days == 3:
                return ['Monday', 'Wednesday', 'Friday']
            elif training_days == 4:
                return ['Monday', 'Tuesday', 'Thursday', 'Friday']
            elif training_days == 5:
                return ['Monday', 'Tuesday', 'Wednesday', 'Friday', 'Saturday']
            elif training_days == 6:
                return ['Monday', 'Tuesday', 'Wednesday', 'Friday', 'Saturday', 'Sunday']
        
        return days[:training_days]
    
    def _create_daily_schedule(self, is_training_day: bool, workout: Dict[str, Any],
                             meal_timing: Dict[str, Any], session_duration: float,
                             barriers: Dict[str, bool]) -> Dict[str, Any]:
        """
        Create detailed schedule for a single day.
        
        Args:
            is_training_day: Whether this is a training day
            workout: Workout details for training days
            meal_timing: Nutrition timing guidelines
            session_duration: Training session duration
            barriers: Client barriers
            
        Returns:
            Dictionary containing daily schedule
        """
        schedule = {
            'type': 'training' if is_training_day else 'rest',
            'meals': [],
            'activities': []
        }
        
        if is_training_day:
            # Add workout details
            schedule['workout'] = {
                'type': workout.get('type', 'Not specified'),
                'target_muscles': workout.get('target_muscles', []),
                'duration': f"{session_duration} hours",
                'exercises': workout.get('exercises', [])
            }
            
            # Add pre-workout meal
            schedule['meals'].append({
                'timing': 'Pre-workout (1-2 hours before)',
                'focus': meal_timing.get('pre_workout', {})
            })
            
            # Add post-workout meal
            schedule['meals'].append({
                'timing': 'Post-workout (within 1 hour)',
                'focus': meal_timing.get('post_workout', {})
            })
        else:
            # Rest day nutrition focus
            schedule['recovery_focus'] = {
                'nutrition': 'Maintain protein intake, moderate carbs',
                'activities': ['Light mobility work', 'Walking', 'Stretching']
            }
        
        # Add general meal timing
        schedule['meals'].extend(self._get_general_meal_timing(
            is_training_day, barriers.get('time_constraints', False)
        ))
        
        return schedule
    
    def _get_general_meal_timing(self, is_training_day: bool, 
                               time_constrained: bool) -> List[Dict[str, Any]]:
        """
        Generate general meal timing guidelines.
        
        Args:
            is_training_day: Whether this is a training day
            time_constrained: Whether client has time constraints
            
        Returns:
            List of meal timing guidelines
        """
        meals = []
        
        if time_constrained:
            # Simplified meal structure
            meals.extend([
                {
                    'timing': 'Morning',
                    'focus': {'protein': 'High', 'carbs': 'Moderate', 'fats': 'Moderate'}
                },
                {
                    'timing': 'Evening',
                    'focus': {'protein': 'High', 'carbs': 'Low to moderate', 'fats': 'Moderate'}
                }
            ])
        else:
            # More structured approach
            meals.extend([
                {
                    'timing': 'Breakfast (within 1 hour of waking)',
                    'focus': {'protein': 'High', 'carbs': 'Moderate to high', 'fats': 'Moderate'}
                },
                {
                    'timing': 'Mid-morning snack',
                    'focus': {'protein': 'Moderate', 'carbs': 'Low to moderate', 'fats': 'Low'}
                },
                {
                    'timing': 'Lunch',
                    'focus': {'protein': 'High', 'carbs': 'Moderate', 'fats': 'Moderate'}
                },
                {
                    'timing': 'Evening meal',
                    'focus': {'protein': 'High', 'carbs': 'Low to moderate', 'fats': 'Moderate'}
                }
            ])
        
        return meals
    
    def _create_daily_protocols(self, workout_plan: Dict[str, Any],
                              nutrition_plan: Dict[str, Any],
                              primary_goal: str) -> Dict[str, Any]:
        """
        Create detailed daily protocols for training and rest days.
        
        Args:
            workout_plan: Workout plan details
            nutrition_plan: Nutrition plan details
            primary_goal: Client's primary goal
            
        Returns:
            Dictionary containing daily protocols
        """
        return {
            'training_days': {
                'pre_training': {
                    'nutrition': nutrition_plan.get('nutrient_timing', {}).get('pre_workout', {}),
                    'preparation': [
                        'Dynamic warm-up sequence',
                        'Mobility work for target muscles',
                        'Light cardio activation (5-10 minutes)'
                    ]
                },
                'during_training': {
                    'execution_guidelines': workout_plan.get('execution_guidelines', {}),
                    'intra_workout_nutrition': nutrition_plan.get('nutrient_timing', {}).get('intra_workout', {})
                },
                'post_training': {
                    'immediate_nutrition': nutrition_plan.get('nutrient_timing', {}).get('post_workout', {}),
                    'recovery_protocols': [
                        'Static stretching for worked muscles',
                        'Progressive cool-down',
                        'Post-workout mobility work'
                    ]
                }
            },
            'rest_days': {
                'nutrition': {
                    'focus': 'Maintenance of protein intake, moderate carbs and fats',
                    'meal_timing': 'Regular 3-4 hour intervals',
                    'hydration': 'Maintain high water intake'
                },
                'activity': {
                    'recommended': [
                        'Light mobility work',
                        'Walking (30-45 minutes)',
                        'Stretching or yoga',
                        'Foam rolling'
                    ],
                    'intensity': 'Low to moderate'
                }
            }
        }
    
    def _create_recovery_guidelines(self, workout_plan: Dict[str, Any],
                                 training_history: Dict[str, Any],
                                 barriers: Dict[str, bool]) -> Dict[str, Any]:
        """
        Create comprehensive recovery guidelines.
        
        Args:
            workout_plan: Workout plan details
            training_history: Training history analysis
            barriers: Client barriers
            
        Returns:
            Dictionary containing recovery guidelines
        """
        volume_tolerance = training_history.get('volume_tolerance', {}).get('volume_category', 'moderate')
        
        return {
            'sleep_optimization': {
                'target_duration': '7-9 hours',
                'quality_guidelines': [
                    'Maintain consistent sleep/wake schedule',
                    'Dark, cool sleeping environment',
                    'Limit screen time before bed',
                    'Consider sleep tracking'
                ]
            },
            'stress_management': {
                'strategies': [
                    'Daily meditation or deep breathing',
                    'Regular walking in nature',
                    'Time management techniques',
                    'Regular relaxation practices'
                ]
            },
            'active_recovery': {
                'frequency': 'Daily (including rest days)',
                'methods': [
                    'Light cardio (walking, swimming)',
                    'Mobility work',
                    'Yoga or stretching',
                    'Foam rolling'
                ],
                'intensity': 'Low to moderate (4-5/10 RPE)'
            },
            'nutrition_support': {
                'hydration': {
                    'daily_target': '3-4 liters',
                    'guidelines': [
                        'Start day with 500ml water',
                        'Drink throughout the day',
                        'Increase intake on training days'
                    ]
                },
                'supplementation': self._get_recovery_supplements(volume_tolerance, barriers)
            }
        }
    
    def _get_recovery_supplements(self, volume_tolerance: str,
                               barriers: Dict[str, bool]) -> Dict[str, Any]:
        """
        Generate recovery supplementation guidelines.
        
        Args:
            volume_tolerance: Training volume tolerance
            barriers: Client barriers
            
        Returns:
            Dictionary containing supplement recommendations
        """
        supplements = {
            'essential': [
                {
                    'supplement': 'Whey Protein',
                    'timing': 'Post-workout and as needed',
                    'purpose': 'Support protein requirements and recovery'
                },
                {
                    'supplement': 'Creatine Monohydrate',
                    'timing': '5g daily',
                    'purpose': 'Support strength and muscle recovery'
                }
            ],
            'conditional': []
        }
        
        if volume_tolerance == 'high':
            supplements['conditional'].extend([
                {
                    'supplement': 'EAAs/BCAAs',
                    'timing': 'During training',
                    'purpose': 'Support training volume and recovery'
                },
                {
                    'supplement': 'Beta-Alanine',
                    'timing': '3-5g daily',
                    'purpose': 'Buffer fatigue during high-volume training'
                }
            ])
        
        if barriers.get('recovery_concerns', False):
            supplements['conditional'].extend([
                {
                    'supplement': 'Magnesium',
                    'timing': 'Evening',
                    'purpose': 'Support sleep and recovery'
                },
                {
                    'supplement': 'Fish Oil',
                    'timing': 'With meals',
                    'purpose': 'Support recovery and reduce inflammation'
                }
            ])
        
        return supplements
    
def _create_tracking_metrics(self, workout_plan: Dict[str, Any],
                              nutrition_plan: Dict[str, Any],
                              goal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive tracking metrics for both training and nutrition.
        
        Args:
            workout_plan: Workout plan details
            nutrition_plan: Nutrition plan details
            goal_analysis: Goal analysis details
            
        Returns:
            Dictionary containing tracking metrics
        """
        primary_goal = goal_analysis.get('primary_goal', '').lower()
        target_metrics = goal_analysis.get('target_metrics', {})
        
        tracking_metrics = {
            'weekly_metrics': {
                'body_composition': [
                    {
                        'metric': 'Body weight',
                        'frequency': 'Daily, same time',
                        'method': 'Morning, after bathroom, before food',
                        'target': f"{target_metrics.get('weight_kg', 'N/A')} kg"
                    },
                    {
                        'metric': 'Body measurements',
                        'frequency': 'Weekly',
                        'sites': [
                            'Chest', 'Waist', 'Hips', 'Arms (relaxed/flexed)',
                            'Thighs', 'Calves'
                        ]
                    },
                    {
                        'metric': 'Progress photos',
                        'frequency': 'Weekly',
                        'positions': ['Front', 'Side', 'Back']
                    }
                ],
                'training_performance': [
                    {
                        'metric': 'Exercise progression',
                        'tracking': 'Weight, reps, RPE per exercise',
                        'frequency': 'Every session'
                    },
                    {
                        'metric': 'Volume accumulation',
                        'tracking': 'Sets per muscle group',
                        'frequency': 'Weekly total'
                    },
                    {
                        'metric': 'Recovery quality',
                        'tracking': 'Sleep duration, soreness, energy',
                        'frequency': 'Daily'
                    }
                ],
                'nutrition_adherence': [
                    {
                        'metric': 'Caloric intake',
                        'tracking': 'Daily total calories',
                        'target': f"{nutrition_plan.get('daily_calories', 'N/A')} kcal"
                    },
                    {
                        'metric': 'Macronutrient ratios',
                        'tracking': 'Protein, carbs, fats',
                        'targets': nutrition_plan.get('macronutrients', {})
                    },
                    {
                        'metric': 'Hydration',
                        'tracking': 'Daily water intake',
                        'target': '3-4 liters'
                    }
                ]
            },
            'monthly_metrics': self._get_monthly_metrics(primary_goal, target_metrics),
            'progress_markers': self._get_progress_markers(primary_goal),
            'adjustment_triggers': self._get_adjustment_triggers(primary_goal)
        }
        
        return tracking_metrics

def _get_monthly_metrics(self, primary_goal: str, 
                        target_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate monthly tracking metrics based on goals.
    
    Args:
        primary_goal: Client's primary goal
        target_metrics: Target metrics from goal analysis
        
    Returns:
        Dictionary containing monthly metrics
    """
    monthly_metrics = {
        'body_composition': {
            'metrics': ['Body composition assessment', 'Progress photos'],
            'comparison': 'Against initial baseline and previous month'
        },
        'performance': {
            'metrics': ['Strength in key lifts', 'Volume tolerance', 'Work capacity'],
            'comparison': 'Against previous month'
        }
    }
    
    if 'hypertrophy' in primary_goal:
        monthly_metrics['muscle_growth'] = {
            'metrics': [
                'Muscle girth measurements',
                'Visual muscle development',
                'Strength progression'
            ],
            'targets': {
                'arm_circumference': f"{target_metrics.get('arm_circumference_cm', 'N/A')} cm",
                'chest_circumference': f"{target_metrics.get('chest_circumference_cm', 'N/A')} cm",
                'thigh_circumference': f"{target_metrics.get('thigh_circumference_cm', 'N/A')} cm"
            }
        }
    
    return monthly_metrics

def _get_progress_markers(self, primary_goal: str) -> Dict[str, Any]:
    """
    Define progress markers based on primary goal.
    
    Args:
        primary_goal: Client's primary goal
        
    Returns:
        Dictionary containing progress markers
    """
    base_markers = {
        'training_quality': [
            'Form improvement',
            'Movement confidence',
            'Exercise technique mastery'
        ],
        'recovery_quality': [
            'Reduced soreness duration',
            'Improved sleep quality',
            'Better energy levels'
        ],
        'lifestyle_factors': [
            'Stress management',
            'Sleep consistency',
            'Nutrition adherence'
        ]
    }
    
    if 'hypertrophy' in primary_goal:
        base_markers['hypertrophy_indicators'] = [
            'Muscle fullness and pumps',
            'Visual changes in target muscles',
            'Strength progression in hypertrophy ranges',
            'Improved mind-muscle connection'
        ]
    elif 'strength' in primary_goal:
        base_markers['strength_indicators'] = [
            'Load progression on key lifts',
            'Technical proficiency under load',
            'Rate of force development',
            'Neural efficiency improvements'
        ]
    
    return base_markers

def _get_adjustment_triggers(self, primary_goal: str) -> Dict[str, Any]:
    """
    Define triggers for plan adjustments.
    
    Args:
        primary_goal: Client's primary goal
        
    Returns:
        Dictionary containing adjustment triggers
    """
    return {
        'volume_adjustments': {
            'increase_triggers': [
                'Consistent RPE below target',
                'Recovery metrics indicate capacity',
                'Strength plateaus with good recovery'
            ],
            'decrease_triggers': [
                'Poor recovery between sessions',
                'Consistent RPE above target',
                'Declining performance'
            ]
        },
        'nutrition_adjustments': {
            'calorie_increase_triggers': [
                'Weight loss exceeding 1% per week',
                'Declining performance with good recovery',
                'Consistent hunger affecting adherence'
            ],
            'calorie_decrease_triggers': [
                'Weight gain exceeding targets',
                'Body fat increasing too rapidly',
                'Poor nutrient partitioning signs'
            ]
        },
        'deload_triggers': [
            'Three weeks of plateaued progression',
            'Accumulated fatigue indicators',
            'Joint or connective tissue stress',
            'Psychological fatigue signs'
        ]
    }

def _create_plan_synchronization(self, workout_plan: Dict[str, Any],
                                nutrition_plan: Dict[str, Any],
                                primary_goal: str) -> Dict[str, Any]:
    """
    Create guidelines for workout and nutrition plan synchronization.
    
    Args:
        workout_plan: Workout plan details
        nutrition_plan: Nutrition plan details
        primary_goal: Client's primary goal
        
    Returns:
        Dictionary containing synchronization guidelines
    """
    return {
        'training_nutrition_alignment': {
            'pre_workout': {
                'timing': '1-2 hours before training',
                'focus': nutrition_plan.get('nutrient_timing', {}).get('pre_workout', {})
            },
            'intra_workout': {
                'timing': 'During training',
                'focus': nutrition_plan.get('nutrient_timing', {}).get('intra_workout', {})
            },
            'post_workout': {
                'timing': 'Within 1 hour post-training',
                'focus': nutrition_plan.get('nutrient_timing', {}).get('post_workout', {})
            }
        },
        'rest_day_nutrition': {
            'focus': 'Recovery and preparation',
            'caloric_adjustment': self._get_rest_day_caloric_adjustment(primary_goal),
            'macro_adjustment': self._get_rest_day_macro_adjustment(primary_goal)
        },
        'weekly_structure': {
            'training_day_nutrition': workout_plan.get('training_split', {}).get('nutrition_guidelines', {}),
            'rest_day_structure': 'Maintenance of protein, reduced carbs, moderate fats'
        }
    }

def _get_rest_day_caloric_adjustment(self, primary_goal: str) -> Dict[str, Any]:
    """
    Define rest day caloric adjustments based on goal.
    
    Args:
        primary_goal: Client's primary goal
        
    Returns:
        Dictionary containing rest day caloric adjustments
    """
    if 'hypertrophy' in primary_goal:
        return {
            'adjustment': 'Slight reduction',
            'reduction': '10-15% below training day calories',
            'focus': 'Maintain anabolic environment while managing fat gain'
        }
    elif 'fat loss' in primary_goal:
        return {
            'adjustment': 'Maintained deficit',
            'reduction': 'Same as training day calories',
            'focus': 'Consistent deficit for fat loss'
        }
    else:
        return {
            'adjustment': 'Moderate reduction',
            'reduction': '5-10% below training day calories',
            'focus': 'Match lower energy requirements'
        }

def _get_rest_day_macro_adjustment(self, primary_goal: str) -> Dict[str, Any]:
    """
    Define rest day macronutrient adjustments based on goal.
    
    Args:
        primary_goal: Client's primary goal
        
    Returns:
        Dictionary containing rest day macro adjustments
    """
    if 'hypertrophy' in primary_goal:
        return {
            'protein': 'Maintained high',
            'carbs': 'Reduced by 20-30%',
            'fats': 'Increased by 5-10%'
        }
    elif 'fat loss' in primary_goal:
        return {
            'protein': 'Increased by 5-10%',
            'carbs': 'Reduced by 30-40%',
            'fats': 'Increased by 10-15%'
        }
    else:
        return {
            'protein': 'Maintained',
            'carbs': 'Reduced by 15-25%',
            'fats': 'Maintained'
        }

def _create_adherence_strategies(self, barriers: Dict[str, bool],
                                primary_goal: str) -> Dict[str, Any]:
    """
    Create strategies for maintaining program adherence.
    
    Args:
        barriers: Client barriers
        primary_goal: Client's primary goal
        
    Returns:
        Dictionary containing adherence strategies
    """
    strategies = {
        'training_adherence': {
            'scheduling': [
                'Pre-book weekly sessions',
                'Set consistent training times',
                'Plan backup sessions for conflicts'
            ],
            'preparation': [
                'Pre-pack gym bag',
                'Plan workouts in advance',
                'Set reminders and alarms'
            ]
        },
        'nutrition_adherence': {
            'meal_prep': [
                'Weekly meal preparation',
                'Batch cooking strategies',
                'Emergency meal options'
            ],
            'tracking': [
                'Use nutrition tracking app',
                'Weekly meal planning',
                'Regular progress check-ins'
            ]
        }
    }
    
    if barriers.get('time_constraints', True):
        strategies['time_management'] = {
            'strategies': [
                'Shorter, higher-intensity sessions',
                'Supersets and circuit training',
                'Meal prep in bulk'
            ]
        }
    
    if barriers.get('motivation', False):
        strategies['motivation_support'] = {
            'strategies': [
                'Set progressive micro-goals',
                'Regular progress tracking',
                'Reward system for adherence'
            ]
        }
    
    return strategies

def _create_adaptation_guidelines(self, workout_plan: Dict[str, Any],
                                nutrition_plan: Dict[str, Any],
                                goal_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create guidelines for program adaptation based on progress.
    
    Args:
        workout_plan: Workout plan details
        nutrition_plan: Nutrition plan details
        goal_analysis: Goal analysis details
        
    Returns:
        Dictionary containing adaptation guidelines
    """
    return {
        'progress_assessment': {
            'frequency': 'Weekly review, monthly detailed assessment',
            'metrics': self._get_progress_metrics(goal_analysis.get('primary_goal', ''))
        },
        'adjustment_protocols': {
            'training': {
                'volume': 'Adjust based on recovery and progression',
                'intensity': 'Modify based on performance metrics',
                'exercise_selection': 'Rotate exercises based on progress and response'
            },
            'nutrition': {
                'calories': 'Adjust based on weight and composition changes',
                'macros': 'Fine-tune based on performance and recovery',
                'meal_timing': 'Optimize based on schedule and energy levels'
            }
        },
        'deload_protocol': {
            'frequency': 'Every 4-6 weeks or as needed',
            'implementation': [
                'Reduce volume by 40-50%',
                'Maintain intensity at 60-70%',
                'Focus on technique and recovery'
            ]
        }
    }

