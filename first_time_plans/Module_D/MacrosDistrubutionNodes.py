from typing import Dict, Any, Tuple

class MacroDistributionDecisionNode:
    def __init__(self):
        """Initialize the MacroDistributionDecisionNode."""
        self.macro_distribution = {}
    
    def process(self, caloric_targets: Dict[str, Any], client_profile: Dict[str, Any],
                body_composition: Dict[str, Any], goal_analysis: Dict[str, Any],
                training_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decide on the optimal macronutrient split based on caloric needs and client goals.
        
        Args:
            caloric_targets: Output from CaloricNeedsDecisionNode
            client_profile: Client profile analysis
            body_composition: Body composition analysis
            goal_analysis: Goal clarification analysis
            training_history: Training history analysis
            
        Returns:
            Dictionary containing macronutrient distribution
        """
        # Extract required data
        adjusted_calories = caloric_targets.get('adjusted_daily_calories', 0)
        primary_goal = goal_analysis.get('primary_goal', '').lower()
        age = client_profile.get('age', 25)
        gender = client_profile.get('gender', '').lower()
        weight_kg = body_composition.get('weight_kg', 0)
        height_cm = body_composition.get('height_cm', 0)
        body_fat_percentage = body_composition.get('estimated_body_fat_percentage', 15)
        training_age_category = training_history.get('training_age', {}).get('category', 'beginner').lower()
        training_volume = training_history.get('volume_tolerance', {}).get('volume_category', 'moderate').lower()
        barriers = goal_analysis.get('barriers', {})
        
        # Calculate macronutrient distribution
        protein_g, carbs_g, fats_g = self._calculate_macros(
            adjusted_calories, primary_goal, weight_kg, body_fat_percentage,
            training_age_category, training_volume, barriers, age, gender
        )
        
        # Calculate calories from macros
        protein_cals = protein_g * 4
        carbs_cals = carbs_g * 4
        fats_cals = fats_g * 9
        total_cals = protein_cals + carbs_cals + fats_cals
        
        # Calculate percentages
        protein_percent = round((protein_cals / total_cals) * 100, 1)
        carbs_percent = round((carbs_cals / total_cals) * 100, 1)
        fats_percent = round((fats_cals / total_cals) * 100, 1)
        
        # Build and return the macro distribution plan
        self.macro_distribution = {
            'daily_calories': round(total_cals),
            'macronutrients': {
                'protein': {
                    'grams': round(protein_g),
                    'calories': round(protein_cals),
                    'percentage': protein_percent
                },
                'carbohydrates': {
                    'grams': round(carbs_g),
                    'calories': round(carbs_cals),
                    'percentage': carbs_percent
                },
                'fats': {
                    'grams': round(fats_g),
                    'calories': round(fats_cals),
                    'percentage': fats_percent
                }
            },
            'meal_guidelines': self._generate_meal_guidelines(
                protein_g, carbs_g, fats_g, primary_goal, barriers
            ),
            'nutrient_timing': self._generate_nutrient_timing(
                primary_goal, training_volume, barriers
            )
        }
        
        return self.macro_distribution
    
    def _calculate_macros(self, calories: float, primary_goal: str, weight_kg: float,
                         body_fat_percentage: float, training_age: str, 
                         training_volume: str, barriers: Dict[str, bool],
                         age: int, gender: str) -> Tuple[float, float, float]:
        """
        Calculate detailed macronutrient distribution based on all factors.
        
        Args:
            calories: Adjusted daily caloric target
            primary_goal: Client's primary goal
            weight_kg: Client's weight in kg
            body_fat_percentage: Estimated body fat percentage
            training_age: Training experience category
            training_volume: Training volume category
            barriers: Dictionary of potential barriers
            age: Client's age
            gender: Client's gender
            
        Returns:
            Tuple of (protein_g, carbs_g, fats_g)
        """
        # Calculate lean body mass (LBM) in kg
        lbm_kg = weight_kg * (1 - (body_fat_percentage / 100))
        
        # STEP 1: Calculate protein based on LBM, training age, and goal
        protein_g = self._calculate_protein_needs(lbm_kg, primary_goal, training_age, body_fat_percentage, age)
        
        # STEP 2: Calculate essential fats based on weight and gender
        min_essential_fats_g = self._calculate_essential_fats(weight_kg, gender)
        
        # STEP 3: Calculate optimal fat intake based on goal and hormonal considerations
        fats_g = self._calculate_fat_needs(weight_kg, min_essential_fats_g, primary_goal, 
                                         body_fat_percentage, age, gender)
        
        # STEP 4: Allocate remaining calories to carbohydrates
        protein_calories = protein_g * 4
        fat_calories = fats_g * 9
        remaining_calories = calories - protein_calories - fat_calories
        carbs_g = max(remaining_calories / 4, 50)  # Ensure minimum 50g carbs
        
        # STEP 5: Adjust based on specific conditions
        protein_g, carbs_g, fats_g = self._apply_macro_adjustments(
            protein_g, carbs_g, fats_g, primary_goal, training_volume, barriers
        )
        
        return protein_g, carbs_g, fats_g
    
    def _calculate_protein_needs(self, lbm_kg: float, primary_goal: str, 
                              training_age: str, body_fat_percentage: float, age: int) -> float:
        """
        Calculate protein needs based on multiple factors.
        
        Args:
            lbm_kg: Lean body mass in kg
            primary_goal: Client's primary goal
            training_age: Training experience level
            body_fat_percentage: Body fat percentage
            age: Client's age
            
        Returns:
            Protein intake in grams
        """
        # Base protein requirements (g/kg of LBM) by training age
        if training_age in ['beginner', 'novice']:
            protein_factor = 1.6  # g per kg of LBM
        elif training_age in ['intermediate']:
            protein_factor = 1.8  # g per kg of LBM
        else:  # advanced, elite
            protein_factor = 2.0  # g per kg of LBM
        
        # Adjust for goal
        if 'hypertrophy' in primary_goal or 'muscle' in primary_goal:
            protein_factor += 0.2  # Increased for muscle building
        elif 'fat loss' in primary_goal or 'cut' in primary_goal:
            protein_factor += 0.3  # Higher to preserve muscle during deficit
        
        # Adjust for body fat percentage
        if body_fat_percentage > 25:
            protein_factor += 0.1  # Higher for greater fat loss
        
        # Adjust for age (increased protein needs for older individuals)
        if age > 40:
            protein_factor += 0.1  # Age-related protein needs
        elif age > 55:
            protein_factor += 0.2  # Further increased for older individuals
        
        return lbm_kg * protein_factor
    
    def _calculate_essential_fats(self, weight_kg: float, gender: str) -> float:
        """
        Calculate minimum essential fat intake based on weight and gender.
        
        Args:
            weight_kg: Weight in kg
            gender: Client gender
            
        Returns:
            Minimum essential fat intake in grams
        """
        # Base minimum essential fats (roughly 0.5g/kg of bodyweight)
        min_fats = weight_kg * 0.5
        
        # Gender adjustments (women typically need slightly higher essential fats)
        if gender == 'female':
            min_fats *= 1.1
        
        return min_fats
    
    def _calculate_fat_needs(self, weight_kg: float, min_essential_fats: float,
                          primary_goal: str, body_fat_percentage: float,
                          age: int, gender: str) -> float:
        """
        Calculate optimal fat intake considering hormonal health and goal.
        
        Args:
            weight_kg: Weight in kg
            min_essential_fats: Minimum essential fat intake
            primary_goal: Client's primary goal
            body_fat_percentage: Body fat percentage
            age: Client's age
            gender: Client's gender
            
        Returns:
            Optimal fat intake in grams
        """
        # Start with minimum essential fats
        target_fats = min_essential_fats
        
        # Adjust based on goal
        if 'fat loss' in primary_goal or 'cut' in primary_goal:
            # Lower fat intake during cutting, but never below essential
            fat_factor = 0.8  # g per kg of bodyweight
        elif 'hypertrophy' in primary_goal or 'muscle' in primary_goal:
            # Moderate fat intake for muscle building
            fat_factor = 1.0  # g per kg of bodyweight
        else:  # maintenance or general fitness
            fat_factor = 0.9  # g per kg of bodyweight
        
        target_fats = max(target_fats, weight_kg * fat_factor)
        
        # Adjust for hormonal considerations
        if age > 40:
            target_fats *= 1.1  # Increased for hormonal support
        
        # Gender-specific adjustments
        if gender == 'female':
            target_fats *= 1.05  # Slightly higher for females
        
        # Body composition adjustments
        if body_fat_percentage < 10 and gender == 'male':
            target_fats *= 1.15  # Higher fats for very lean males (hormonal support)
        elif body_fat_percentage < 18 and gender == 'female':
            target_fats *= 1.15  # Higher fats for very lean females (hormonal support)
        
        return target_fats
    
    def _apply_macro_adjustments(self, protein_g: float, carbs_g: float, fats_g: float,
                              primary_goal: str, training_volume: str,
                              barriers: Dict[str, bool]) -> Tuple[float, float, float]:
        """
        Apply final adjustments to macronutrients based on training volume and barriers.
        
        Args:
            protein_g: Calculated protein intake
            carbs_g: Calculated carbohydrate intake
            fats_g: Calculated fat intake
            primary_goal: Client's primary goal
            training_volume: Training volume category
            barriers: Dictionary of potential barriers
            
        Returns:
            Adjusted macronutrient values as (protein_g, carbs_g, fats_g)
        """
        # Adjust protein for recovery barriers
        if barriers.get('recovery_concerns', False) or barriers.get('sleep', False):
            protein_g *= 1.05  # Slight increase for recovery support
        
        # Adjust carbs based on training volume
        if training_volume == 'high':
            carbs_g *= 1.1  # Increase carbs for high volume training
        elif training_volume == 'low':
            carbs_g *= 0.9  # Decrease carbs for low volume training
            fats_g *= 1.1  # Compensate with slightly higher fats
        
        # Adjust carbs and fats for nutrition compliance barriers
        if barriers.get('nutrition_compliance', False):
            # For clients with compliance issues, make the plan more flexible
            if 'fat loss' in primary_goal:
                # For fat loss, keep protein high but allow more fats vs carbs for satiety
                carbs_g *= 0.95
                fats_g *= 1.05
        
        # Adjust for motivation barriers by making the plan more sustainable
        if barriers.get('motivation', False):
            if 'fat loss' in primary_goal:
                # Less aggressive deficit for motivation issues
                total_calories = (protein_g * 4) + (carbs_g * 4) + (fats_g * 9)
                new_total_calories = total_calories * 1.05
                extra_calories = new_total_calories - total_calories
                # Distribute extra calories to carbs and fats
                carbs_g += (extra_calories * 0.6) / 4
                fats_g += (extra_calories * 0.4) / 9
        
        return protein_g, carbs_g, fats_g
    
    def _generate_meal_guidelines(self, protein_g: float, carbs_g: float, fats_g: float,
                               primary_goal: str, barriers: Dict[str, bool]) -> Dict[str, Any]:
        """
        Generate practical meal guidelines based on macronutrient targets.
        
        Args:
            protein_g: Daily protein target in grams
            carbs_g: Daily carbohydrate target in grams
            fats_g: Daily fat target in grams
            primary_goal: Client's primary goal
            barriers: Dictionary of potential barriers
            
        Returns:
            Dictionary with meal frequency and distribution guidelines
        """
        # Determine ideal meal frequency
        if barriers.get('time_constraints', False):
            meal_count = 3  # Fewer meals for those with time constraints
        else:
            meal_count = 4  # Default to 4 meals for most clients
        
        # Adjust meal count based on goal
        if 'hypertrophy' in primary_goal and not barriers.get('time_constraints', False):
            meal_count = 5  # More frequent meals for muscle building
        
        # Calculate protein per meal
        protein_per_meal = protein_g / meal_count
        
        # Generate meal distribution guidelines
        guidelines = {
            'meal_frequency': meal_count,
            'protein_distribution': {
                'grams_per_meal': round(protein_per_meal, 1),
                'strategy': 'Evenly distribute protein across all meals'
            },
            'carbohydrate_distribution': self._get_carb_distribution_strategy(primary_goal, meal_count, carbs_g),
            'fat_distribution': self._get_fat_distribution_strategy(primary_goal, meal_count, fats_g),
            'compliance_strategies': self._get_compliance_strategies(barriers, primary_goal)
        }
        
        return guidelines
    
    def _get_carb_distribution_strategy(self, primary_goal: str, meal_count: int, 
                                      carbs_g: float) -> Dict[str, Any]:
        """
        Generate carbohydrate distribution strategy based on goals.
        
        Args:
            primary_goal: Client's primary goal
            meal_count: Number of meals per day
            carbs_g: Daily carbohydrate target
            
        Returns:
            Dictionary with carbohydrate distribution guidelines
        """
        if 'hypertrophy' in primary_goal or 'muscle' in primary_goal:
            return {
                'strategy': 'Higher carbs around training',
                'distribution': {
                    'pre_workout_meal': f"{round(carbs_g * 0.25, 1)}g ({round(carbs_g * 0.25 / carbs_g * 100)}%)",
                    'post_workout_meal': f"{round(carbs_g * 0.35, 1)}g ({round(carbs_g * 0.35 / carbs_g * 100)}%)",
                    'other_meals': f"{round(carbs_g * 0.4 / (meal_count - 2), 1)}g per meal ({round(carbs_g * 0.4 / carbs_g * 100 / (meal_count - 2))}% each)"
                }
            }
        elif 'fat loss' in primary_goal or 'cut' in primary_goal:
            return {
                'strategy': 'Concentrate carbs around training, reduce in evening',
                'distribution': {
                    'pre_workout_meal': f"{round(carbs_g * 0.3, 1)}g ({round(carbs_g * 0.3 / carbs_g * 100)}%)",
                    'post_workout_meal': f"{round(carbs_g * 0.3, 1)}g ({round(carbs_g * 0.3 / carbs_g * 100)}%)",
                    'other_meals': f"{round(carbs_g * 0.4 / (meal_count - 2), 1)}g per meal ({round(carbs_g * 0.4 / carbs_g * 100 / (meal_count - 2))}% each)",
                    'evening_guideline': "Minimize carbs in evening meals"
                }
            }
        else:  # maintenance or general fitness
            return {
                'strategy': 'Balanced distribution with emphasis on training window',
                'distribution': {
                    'pre_workout_meal': f"{round(carbs_g * 0.25, 1)}g ({round(carbs_g * 0.25 / carbs_g * 100)}%)",
                    'post_workout_meal': f"{round(carbs_g * 0.25, 1)}g ({round(carbs_g * 0.25 / carbs_g * 100)}%)",
                    'other_meals': f"{round(carbs_g * 0.5 / (meal_count - 2), 1)}g per meal ({round(carbs_g * 0.5 / carbs_g * 100 / (meal_count - 2))}% each)"
                }
            }
    
    def _get_fat_distribution_strategy(self, primary_goal: str, meal_count: int, 
                                     fats_g: float) -> Dict[str, Any]:
        """
        Generate fat distribution strategy based on goals.
        
        Args:
            primary_goal: Client's primary goal
            meal_count: Number of meals per day
            fats_g: Daily fat target
            
        Returns:
            Dictionary with fat distribution guidelines
        """
        if 'hypertrophy' in primary_goal or 'muscle' in primary_goal:
            return {
                'strategy': 'Moderate fats throughout the day, lower around workouts',
                'distribution': {
                    'pre_workout_meal': f"{round(fats_g * 0.15, 1)}g ({round(fats_g * 0.15 / fats_g * 100)}%)",
                    'post_workout_meal': f"{round(fats_g * 0.15, 1)}g ({round(fats_g * 0.15 / fats_g * 100)}%)",
                    'other_meals': f"{round(fats_g * 0.7 / (meal_count - 2), 1)}g per meal ({round(fats_g * 0.7 / fats_g * 100 / (meal_count - 2))}% each)"
                }
            }
        elif 'fat loss' in primary_goal or 'cut' in primary_goal:
            return {
                'strategy': 'Distribute fats evenly with slight emphasis in morning/evening for satiety',
                'distribution': {
                    'morning_meal': f"{round(fats_g * 0.25, 1)}g ({round(fats_g * 0.25 / fats_g * 100)}%)",
                    'pre_workout_meal': f"{round(fats_g * 0.15, 1)}g ({round(fats_g * 0.15 / fats_g * 100)}%)",
                    'post_workout_meal': f"{round(fats_g * 0.15, 1)}g ({round(fats_g * 0.15 / fats_g * 100)}%)",
                    'evening_meal': f"{round(fats_g * 0.25, 1)}g ({round(fats_g * 0.25 / fats_g * 100)}%)",
                    'other_meals': f"{round(fats_g * 0.2 / (meal_count - 4), 1)}g per meal ({round(fats_g * 0.2 / fats_g * 100 / (meal_count - 4))}% each)"
                }
            }
        else:  # maintenance or general fitness
            return {
                'strategy': 'Balanced distribution throughout the day',
                'distribution': {
                    'per_meal': f"{round(fats_g / meal_count, 1)}g ({round(100 / meal_count)}% each)"
                }
            }
    
    def _get_compliance_strategies(self, barriers: Dict[str, bool], primary_goal: str) -> Dict[str, str]:
        """
        Generate compliance strategies based on identified barriers.
        
        Args:
            barriers: Dictionary of potential barriers
            primary_goal: Client's primary goal
            
        Returns:
            Dictionary with compliance strategies
        """
        strategies = {}
        
        if barriers.get('nutrition_compliance', False):
            strategies['meal_prep'] = "Prepare meals 2-3 days in advance to increase adherence"
            strategies['flexible_approach'] = "Implement an 80/20 approach: 80% adherence to plan, 20% flexibility"
        
        if barriers.get('time_constraints', False):
            strategies['meal_frequency'] = "Focus on hitting daily targets versus exact meal timing"
            strategies['quick_options'] = "Keep easy high-protein options available (protein shakes, Greek yogurt, pre-cooked meat)"
        
        if 'hypertrophy' in primary_goal:
            strategies['caloric_surplus'] = "If you miss your target, prioritize hitting protein goals first"
        elif 'fat loss' in primary_goal:
            strategies['hunger_management'] = "Emphasize high-volume, low-calorie foods to manage hunger (vegetables, lean proteins)"
            strategies['deficit_adherence'] = "If struggling with the deficit, maintain it for 5 days and allow more flexibility on weekends"
        
        return strategies
    
    def _generate_nutrient_timing(self, primary_goal: str, training_volume: str,
                               barriers: Dict[str, bool]) -> Dict[str, Any]:
        """
        Generate nutrient timing recommendations based on goals and training.
        
        Args:
            primary_goal: Client's primary goal
            training_volume: Training volume category
            barriers: Dictionary of potential barriers
            
        Returns:
            Dictionary with nutrient timing recommendations
        """
        timing_recommendations = {
            'pre_workout': {},
            'intra_workout': {},
            'post_workout': {},
            'general_timing': {}
        }
        
        # Pre-workout recommendations
        if 'hypertrophy' in primary_goal:
            timing_recommendations['pre_workout'] = {
                'timing': '1-2 hours before training',
                'carbohydrates': 'Moderate to high (0.5-0.75g per kg bodyweight)',
                'protein': 'Moderate (0.25g per kg bodyweight)',
                'fats': 'Low to moderate (limit fats close to training)'
            }
        elif 'fat loss' in primary_goal:
            timing_recommendations['pre_workout'] = {
                'timing': '1-2 hours before training',
                'carbohydrates': 'Moderate (0.25-0.5g per kg bodyweight)',
                'protein': 'Moderate (0.25g per kg bodyweight)',
                'fats': 'Low (minimize fats pre-workout)'
            }
        else:
            timing_recommendations['pre_workout'] = {
                'timing': '1-2 hours before training',
                'carbohydrates': 'Moderate (0.3-0.5g per kg bodyweight)',
                'protein': 'Moderate (0.2g per kg bodyweight)',
                'fats': 'Low to moderate'
            }
        
        # Intra-workout recommendations based on training volume
        if training_volume == 'high':
            timing_recommendations['intra_workout'] = {
                'recommendation': 'Consider intra-workout carbohydrates',
                'carbohydrates': '15-30g per hour for sessions over 60 minutes',
                'hydration': 'Drink 500-750ml water per hour of training'
            }
        else:
            timing_recommendations['intra_workout'] = {
                'recommendation': 'Hydration only for most sessions',
                'carbohydrates': 'Not necessary for sessions under 60 minutes',
                'hydration': 'Drink 500ml water per hour of training'
            }
        
        # Post-workout recommendations
        if 'hypertrophy' in primary_goal:
            timing_recommendations['post_workout'] = {
                'timing': 'Within 1 hour post-training',
                'carbohydrates': 'High (0.5-1.0g per kg bodyweight)',
                'protein': 'High (0.4g per kg bodyweight)',
                'fats': 'Low (minimize fats immediately post-workout)'
            }
        elif 'fat loss' in primary_goal:
            timing_recommendations['post_workout'] = {
                'timing': 'Within 1 hour post-training',
                'carbohydrates': 'Moderate (0.3-0.5g per kg bodyweight)',
                'protein': 'High (0.4g per kg bodyweight)',
                'fats': 'Low (minimize fats immediately post-workout)'
            }
        else:
            timing_recommendations['post_workout'] = {
                'timing': 'Within 1 hour post-training',
                'carbohydrates': 'Moderate to high (0.4-0.7g per kg bodyweight)',
                'protein': 'Moderate to high (0.3-0.4g per kg bodyweight)',
                'fats': 'Low to moderate'
            }
        
        # General timing recommendations
        if barriers.get('time_constraints', False):
            timing_recommendations['general_timing'] = {
                'meal_spacing': 'Aim for meals every 3-5 hours, but total daily intake takes priority',
                'protein_distribution': 'Try to include protein in each meal',
                'flexible_approach': 'Focus on hitting daily targets rather than perfect timing'
            }
        else:
            timing_recommendations['general_timing'] = {
                'meal_spacing': 'Aim for meals every 3-4 hours',
                'protein_distribution': 'Distribute protein evenly across all meals',
                'nighttime_nutrition': 'Consider a slow-digesting protein source before bed (casein or cottage cheese)',
                'carb_timing': 'Place majority of carbohydrates in morning and around workouts'
            }
        
        return timing_recommendations