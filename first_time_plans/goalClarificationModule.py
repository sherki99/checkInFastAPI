from typing import Dict, Any, List, Set



class GoalClarificationModule:
    """
    Module responsible for analyzing goals and motivation to define clear, measurable objectives.
    """
    
    def __init__(self):
        """Initialize the GoalClarificationModule."""
        self.goal_parameters = {}
        
        # Define common goal keywords for categorization
        self.hypertrophy_keywords = {"hypertrophy", "muscle gain", "bigger", "size", "mass", "build muscle"}
        self.strength_keywords = {"strength", "stronger", "power", "lift heavy", "force"}
        self.endurance_keywords = {"endurance", "stamina", "cardio", "conditioning", "running", "marathon"}
        self.fat_loss_keywords = {"fat loss", "weight loss", "leaner", "cut", "definition", "shredded"}
        self.general_fitness_keywords = {"fitness", "health", "general", "well-being", "functional"}
        self.specific_skill_keywords = {"pull up", "pull-up", "pushup", "push-up", "handstand", "muscle up"}
    
    def process(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the standardized profile to extract and clarify goals.
        
        Args:
            standardized_profile: Standardized client profile from DataIngestionModule
            
        Returns:
            Clear, measurable goal parameters
        """
        goals_info = standardized_profile.get('goals', {})
        personal_info = standardized_profile.get('personal_info', {})
        body_composition = standardized_profile.get('body_composition', {})
        
        # Extract main goals list
        main_goals_list = goals_info.get('main_goals', [])
        
        # Analyze goal text to categorize primary and secondary objectives
        goal_categories = self._categorize_goals(main_goals_list)
        
        # Extract timeframe
        desired_timeframe_weeks = goals_info.get('desired_timeframe_weeks', 12)
        
        # Extract motivation level (1-5 scale)
        motivation_level = goals_info.get('motivation_level', 3)
        
        # Identify barriers to success
        barriers = goals_info.get('expected_barriers', '')
        identified_barriers = self._identify_barriers(barriers)
        
        # Assess current metrics relevant to goals
        current_metrics = self._assess_current_metrics(personal_info, body_composition, goal_categories)
        
        # Set target metrics based on goals and current metrics
        target_metrics = self._set_target_metrics(current_metrics, goal_categories, desired_timeframe_weeks)
        
        # Compile goal parameters
        self.goal_parameters = {
            'primary_goal': goal_categories['primary'],
            'secondary_goals': goal_categories['secondary'],
            'all_goal_categories': goal_categories['all'],
            'timeframe_weeks': desired_timeframe_weeks,
            'motivation_level': motivation_level,
            'barriers': identified_barriers,
            'current_metrics': current_metrics,
            'target_metrics': target_metrics,
            'goal_statements': self._generate_goal_statements(goal_categories, current_metrics, target_metrics)
        }
        
        return self.goal_parameters
    
    def _categorize_goals(self, goal_texts: List[str]) -> Dict[str, Any]:
        """
        Categorize goals based on keyword analysis.
        
        Args:
            goal_texts: List of goal descriptions
            
        Returns:
            Dictionary containing categorized goals
        """
        # Convert goal texts to lowercase for matching
        lower_goals = [goal.lower() for goal in goal_texts]
        
        # Count occurrences of each category
        category_counts = {
            'hypertrophy': sum(1 for goal in lower_goals if any(kw in goal for kw in self.hypertrophy_keywords)),
            'strength': sum(1 for goal in lower_goals if any(kw in goal for kw in self.strength_keywords)),
            'endurance': sum(1 for goal in lower_goals if any(kw in goal for kw in self.endurance_keywords)),
            'fat_loss': sum(1 for goal in lower_goals if any(kw in goal for kw in self.fat_loss_keywords)),
            'general_fitness': sum(1 for goal in lower_goals if any(kw in goal for kw in self.general_fitness_keywords)),
            'specific_skill': sum(1 for goal in lower_goals if any(kw in goal for kw in self.specific_skill_keywords))
        }
        
        # Get specific skills mentioned if applicable
        specific_skills = []
        for goal in lower_goals:
            for skill in self.specific_skill_keywords:
                if skill in goal:
                    specific_skills.append(skill)
        
        # Determine primary goal (highest count)
        primary_goal = max(category_counts, key=category_counts.get)
        if category_counts[primary_goal] == 0:
            primary_goal = 'general_fitness'  # Default if no clear goals
        
        # Determine secondary goals (any non-zero count that's not the primary)
        secondary_goals = [cat for cat, count in category_counts.items() 
                          if count > 0 and cat != primary_goal]
        
        # Get all goal categories with non-zero counts
        all_categories = [cat for cat, count in category_counts.items() if count > 0]
        
        return {
            'primary': primary_goal,
            'secondary': secondary_goals,
            'all': all_categories,
            'specific_skills': specific_skills,
            'category_counts': category_counts
        }
    
    def _identify_barriers(self, barriers_text: str) -> Dict[str, bool]:
        """
        Identify barriers to success from text description.
        
        Args:
            barriers_text: Text description of expected barriers
            
        Returns:
            Dictionary of identified barriers
        """
        barriers = {
            'time_constraints': 'time' in barriers_text.lower() or 'busy' in barriers_text.lower(),
            'injury': 'injury' in barriers_text.lower() or 'pain' in barriers_text.lower(),
            'nutrition_compliance': 'diet' in barriers_text.lower() or 'nutrition' in barriers_text.lower() or 'food' in barriers_text.lower(),
            'motivation': 'motivation' in barriers_text.lower() or 'lazy' in barriers_text.lower(),
            'equipment_access': 'equipment' in barriers_text.lower() or 'gym' in barriers_text.lower(),
            'stress': 'stress' in barriers_text.lower() or 'work' in barriers_text.lower(),
            'sleep': 'sleep' in barriers_text.lower() or 'tired' in barriers_text.lower()
        }
        
        return barriers
    
    def _assess_current_metrics(self, personal_info: Dict[str, Any], 
                               body_composition: Dict[str, Any],
                               goal_categories: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess current metrics relevant to the identified goals.
        
        Args:
            personal_info: Personal information
            body_composition: Body composition measurements
            goal_categories: Categorized goals
            
        Returns:
            Dictionary of current metrics relevant to goals
        """
        current_metrics = {
            'weight_kg': personal_info.get('weight_kg', 0),
            'bmi': personal_info.get('bmi', 0)
        }
        
        # Add body composition metrics
        if 'hypertrophy' in goal_categories['all'] or 'strength' in goal_categories['all']:
            current_metrics.update({
                'arm_circumference_cm': body_composition.get('arm_circumference', 0),
                'chest_circumference_cm': body_composition.get('chest_circumference', 0),
                'thigh_circumference_cm': body_composition.get('thigh_circumference', 0)
            })
        
        if 'fat_loss' in goal_categories['all']:
            current_metrics.update({
                'waist_circumference_cm': body_composition.get('waist_circumference', 0),
                'hip_circumference_cm': body_composition.get('hip_circumference', 0),
                'waist_to_hip_ratio': body_composition.get('waist_to_hip_ratio', 0)
            })
        
        # For specific skill goals
        if 'specific_skill' in goal_categories['all']:
            # We don't have actual performance metrics, but we can flag this
            current_metrics['needs_performance_baseline'] = True
            current_metrics['target_skills'] = goal_categories.get('specific_skills', [])
        
        return current_metrics
    
    def _set_target_metrics(self, current_metrics: Dict[str, Any],
                           goal_categories: Dict[str, Any],
                           timeframe_weeks: int) -> Dict[str, Any]:
        """
        Set target metrics based on goals and current metrics.
        
        Args:
            current_metrics: Current relevant metrics
            goal_categories: Categorized goals
            timeframe_weeks: Desired timeframe in weeks
            
        Returns:
            Dictionary of target metrics
        """
        target_metrics = {}
        
        # Set target metrics based on primary goal
        primary_goal = goal_categories['primary']
        
        if primary_goal == 'hypertrophy':
            # Target 0.5-1% increase in muscle circumference measurements per month
            monthly_increase_factor = 0.01  # 1% per month
            total_increase_factor = monthly_increase_factor * (timeframe_weeks / 4)
            
            for metric in ['arm_circumference_cm', 'chest_circumference_cm', 'thigh_circumference_cm']:
                if metric in current_metrics:
                    target_metrics[metric] = round(current_metrics[metric] * (1 + total_increase_factor), 1)
            
            # Small weight gain (0.25-0.5kg per week for hypertrophy, depending on experience)
            weight_gain_per_week = 0.25  # Conservative estimate
            target_metrics['weight_kg'] = round(current_metrics['weight_kg'] + (weight_gain_per_week * timeframe_weeks), 1)
        
        elif primary_goal == 'strength':
            # Primarily performance-based, which we can't calculate without baseline
            target_metrics['needs_strength_baseline'] = True
            
            # Slight increase in muscle measurements
            monthly_increase_factor = 0.005  # 0.5% per month
            total_increase_factor = monthly_increase_factor * (timeframe_weeks / 4)
            
            for metric in ['arm_circumference_cm', 'chest_circumference_cm', 'thigh_circumference_cm']:
                if metric in current_metrics:
                    target_metrics[metric] = round(current_metrics[metric] * (1 + total_increase_factor), 1)
        
        elif primary_goal == 'fat_loss':
            # Target 0.5-1% decrease in fat-related measurements per month
            monthly_decrease_factor = 0.01  # 1% per month
            total_decrease_factor = monthly_decrease_factor * (timeframe_weeks / 4)
            
            for metric in ['waist_circumference_cm', 'hip_circumference_cm']:
                if metric in current_metrics:
                    target_metrics[metric] = round(current_metrics[metric] * (1 - total_decrease_factor), 1)
            
            # Weight loss (0.5-1kg per week for fat loss, depending on starting point)
            weight_loss_per_week = 0.5  # Conservative estimate
            target_metrics['weight_kg'] = max(round(current_metrics['weight_kg'] - (weight_loss_per_week * timeframe_weeks), 1),
                                          50)  # Ensure we don't go too low
        
        elif primary_goal == 'specific_skill':
            # We need baseline performance metrics
            target_metrics['needs_performance_baseline'] = True
            target_metrics['target_skills'] = current_metrics.get('target_skills', [])
        
        else:  # General fitness or endurance
            # Set modest improvements across all metrics
            monthly_factor = 0.005  # 0.5% per month
            total_factor = monthly_factor * (timeframe_weeks / 4)
            
            for metric, value in current_metrics.items():
                if isinstance(value, (int, float)) and metric not in ['bmi', 'waist_to_hip_ratio']:
                    if 'circumference' in metric:
                        # For body circumference, we want small changes
                        if 'waist' in metric or 'hip' in metric:
                            target_metrics[metric] = round(value * (1 - total_factor), 1)  # Decrease
                        else:
                            target_metrics[metric] = round(value * (1 + total_factor), 1)  # Increase
                    elif metric == 'weight_kg':
                        # Maintain weight for general fitness
                        target_metrics[metric] = value
        
        return target_metrics
    
    def _generate_goal_statements(self, goal_categories: Dict[str, Any],
                                 current_metrics: Dict[str, Any],
                                 target_metrics: Dict[str, Any]) -> List[str]:
        """
        Generate clear goal statements based on categories and metrics.
        
        Args:
            goal_categories: Categorized goals
            current_metrics: Current relevant metrics
            target_metrics: Target metrics
            
        Returns:
            List of goal statements
        """
        goal_statements = []
        primary_goal = goal_categories['primary']
        
        if primary_goal == 'hypertrophy':
            goal_statements.append(f"Increase muscle mass and size over the next {target_metrics.get('timeframe_weeks', 12)} weeks")
            
            if 'arm_circumference_cm' in current_metrics and 'arm_circumference_cm' in target_metrics:
                increase = target_metrics['arm_circumference_cm'] - current_metrics['arm_circumference_cm']
                goal_statements.append(f"Increase arm circumference by {round(increase, 1)} cm (from {current_metrics['arm_circumference_cm']} to {target_metrics['arm_circumference_cm']} cm)")
            
            if 'weight_kg' in current_metrics and 'weight_kg' in target_metrics and target_metrics['weight_kg'] > current_metrics['weight_kg']:
                weight_increase = target_metrics['weight_kg'] - current_metrics['weight_kg']
                goal_statements.append(f"Gain {round(weight_increase, 1)} kg of lean mass (from {current_metrics['weight_kg']} to {target_metrics['weight_kg']} kg)")
        
        elif primary_goal == 'strength':
            goal_statements.append(f"Increase overall strength and power over the next {target_metrics.get('timeframe_weeks', 12)} weeks")
            goal_statements.append("Establish baseline strength measurements for key lifts and improve by 5-10% depending on training age")
            
            # For specific skills that are strength-related
            if 'target_skills' in target_metrics:
                for skill in target_metrics['target_skills']:
                    if "pull up" in skill:
                        goal_statements.append("Improve pull-up performance, focusing on both maximum reps and controlled form")
        
        elif primary_goal == 'fat_loss':
            goal_statements.append(f"Reduce body fat while preserving muscle mass over the next {target_metrics.get('timeframe_weeks', 12)} weeks")
            
            if 'waist_circumference_cm' in current_metrics and 'waist_circumference_cm' in target_metrics:
                decrease = current_metrics['waist_circumference_cm'] - target_metrics['waist_circumference_cm']
                goal_statements.append(f"Decrease waist circumference by {round(decrease, 1)} cm (from {current_metrics['waist_circumference_cm']} to {target_metrics['waist_circumference_cm']} cm)")
            
            if 'weight_kg' in current_metrics and 'weight_kg' in target_metrics and target_metrics['weight_kg'] < current_metrics['weight_kg']:
                weight_decrease = current_metrics['weight_kg'] - target_metrics['weight_kg']
                goal_statements.append(f"Lose {round(weight_decrease, 1)} kg (from {current_metrics['weight_kg']} to {target_metrics['weight_kg']} kg)")
        
        elif primary_goal == 'specific_skill':
            if 'target_skills' in target_metrics:
                for skill in target_metrics['target_skills']:
                    goal_statements.append(f"Improve performance in {skill}")
            else:
                goal_statements.append("Improve performance in specific skills")
            
            goal_statements.append("Establish baseline performance metrics and set progressive targets")
        
        elif primary_goal == 'general_fitness':
            goal_statements.append(f"Improve overall fitness and health over the next {target_metrics.get('timeframe_weeks', 12)} weeks")
            goal_statements.append("Enhance cardiovascular health, muscular endurance, and flexibility")
            goal_statements.append("Establish balanced exercise routine that promotes long-term health and wellbeing")
        
        elif primary_goal == 'endurance':
            goal_statements.append(f"Increase cardiovascular and muscular endurance over the next {target_metrics.get('timeframe_weeks', 12)} weeks")
            goal_statements.append("Improve aerobic capacity and stamina for sustained activity")
        
        return goal_statements