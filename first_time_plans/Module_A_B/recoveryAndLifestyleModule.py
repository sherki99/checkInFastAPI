from typing import Dict, Any, List, Optional

class RecoveryAndLifestyleModule:
    """
    Module responsible for evaluating sleep, stress, work schedule, and overall recovery capacity
    to determine recovery scores and lifestyle constraints.
    """
    
    def __init__(self):
        """Initialize the RecoveryAndLifestyleModule."""
        self.recovery_metrics = {}
        
    def process(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the standardized profile to evaluate recovery capacity and lifestyle factors.
        
        Args:
            standardized_profile: Standardized client profile from DataIngestionModule
            
        Returns:
            Dictionary containing recovery scores and lifestyle constraints
        """
        lifestyle = standardized_profile.get('lifestyle', {})
        fitness = standardized_profile.get('fitness', {})
        nutrition = standardized_profile.get('nutrition', {})
        
        # Calculate recovery capacity score
        recovery_capacity = self._calculate_recovery_capacity(lifestyle, fitness, nutrition)
        
        # Analyze sleep quality and patterns
        sleep_analysis = self._analyze_sleep(lifestyle)
        
        # Evaluate stress levels and management
        stress_evaluation = self._evaluate_stress(lifestyle)
        
        # Assess work/life balance
        work_life_balance = self._assess_work_life_balance(lifestyle, fitness)
        
        # Identify lifestyle constraints
        lifestyle_constraints = self._identify_constraints(lifestyle, fitness, nutrition)
        
        # Calculate overall recovery score
        overall_recovery_score = self._calculate_overall_recovery_score(
            recovery_capacity,
            sleep_analysis,
            stress_evaluation,
            work_life_balance
        )
        
        self.recovery_metrics = {
            'overall_recovery_score': overall_recovery_score,
            'recovery_capacity': recovery_capacity,
            'sleep_analysis': sleep_analysis,
            'stress_evaluation': stress_evaluation,
            'work_life_balance': work_life_balance,
            'lifestyle_constraints': lifestyle_constraints
        }
        
        return self.recovery_metrics
    
    def _calculate_recovery_capacity(self, lifestyle: Dict[str, Any], 
                                   fitness: Dict[str, Any],
                                   nutrition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate recovery capacity based on various factors.
        
        Args:
            lifestyle: Lifestyle-related data
            fitness: Fitness-related data
            nutrition: Nutrition-related data
            
        Returns:
            Dictionary containing recovery capacity metrics
        """
        # Base recovery capacity score (scale of 1-10)
        base_score = 7.0
        
        # Adjust for activity level
        activity_level = fitness.get('activity_level', 'Moderate').lower()
        activity_adjustments = {
            'sedentary': -1.0,
            'lightly active': -0.5,
            'moderate': 0.0,
            'active': 0.5,
            'very active': -0.5  # Very active might need more recovery
        }
        base_score += activity_adjustments.get(activity_level, 0)
        
        # Adjust for water intake
        water_intake = nutrition.get('water_intake_liters', 2.0)
        if water_intake >= 3.0:
            base_score += 0.5
        elif water_intake < 2.0:
            base_score -= 0.5
            
        # Adjust for supplements that aid recovery
        supplements = nutrition.get('supplements', [])
        recovery_supplements = ['magnesium', 'zinc', 'protein', 'creatine']
        supplement_score = sum(0.2 for sup in supplements if sup.lower() in recovery_supplements)
        base_score += min(supplement_score, 1.0)  # Cap supplement bonus at 1.0
        
        return {
            'score': round(min(max(base_score, 1), 10), 1),  # Clamp between 1-10
            'factors': {
                'activity_level_impact': activity_adjustments.get(activity_level, 0),
                'hydration_impact': 0.5 if water_intake >= 3.0 else (-0.5 if water_intake < 2.0 else 0),
                'supplement_impact': min(supplement_score, 1.0)
            }
        }
    
    def _analyze_sleep(self, lifestyle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sleep patterns and quality.
        
        Args:
            lifestyle: Lifestyle-related data
            
        Returns:
            Dictionary containing sleep analysis metrics
        """
        # Default sleep score (scale of 1-10)
        sleep_score = 7.0
        sleep_issues = []
        
        # Get sleep duration if available
        sleep_hours = lifestyle.get('sleep_hours', 7)  # Default to 7 if not specified
        
        # Evaluate sleep duration
        if sleep_hours < 6:
            sleep_score -= 2.0
            sleep_issues.append("Insufficient sleep duration")
        elif sleep_hours < 7:
            sleep_score -= 1.0
            sleep_issues.append("Suboptimal sleep duration")
        elif sleep_hours >= 8:
            sleep_score += 1.0
        
        # Consider work environment impact on sleep
        work_environment = lifestyle.get('work_environment', '').lower()
        if work_environment == 'shift work':
            sleep_score -= 1.5
            sleep_issues.append("Shift work may impact sleep quality")
        
        return {
            'score': round(min(max(sleep_score, 1), 10), 1),
            'sleep_hours': sleep_hours,
            'issues': sleep_issues,
            'recommendations': self._generate_sleep_recommendations(sleep_hours, sleep_issues)
        }
    
    def _evaluate_stress(self, lifestyle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate stress levels and management.
        
        Args:
            lifestyle: Lifestyle-related data
            
        Returns:
            Dictionary containing stress evaluation metrics
        """
        stress_level = lifestyle.get('stress_level', 'Moderate').lower()
        
        # Convert stress level to numeric score (1-10, higher = more stress)
        stress_scores = {
            'very low': 2,
            'low': 4,
            'moderate': 6,
            'high': 8,
            'very high': 10,
            'stressful': 8  # Map 'stressful' to high
        }
        
        stress_score = stress_scores.get(stress_level, 6)
        
        # Generate stress management recommendations
        recommendations = []
        if stress_score >= 7:
            recommendations.extend([
                "Incorporate daily meditation or deep breathing exercises",
                "Consider reducing training volume during high-stress periods",
                "Implement regular deload weeks",
                "Focus on recovery-promoting activities"
            ])
        
        return {
            'stress_score': stress_score,
            'stress_level': stress_level,
            'impact_on_training': 'High' if stress_score >= 8 else 'Moderate' if stress_score >= 6 else 'Low',
            'recommendations': recommendations
        }
    
    def _assess_work_life_balance(self, lifestyle: Dict[str, Any], 
                                fitness: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess work/life balance and its impact on training.
        
        Args:
            lifestyle: Lifestyle-related data
            fitness: Fitness-related data
            
        Returns:
            Dictionary containing work/life balance assessment
        """
        daily_work_hours = lifestyle.get('daily_work_hours', 8)
        weekly_exercise_hours = fitness.get('weekly_exercise_hours', 0)
        
        # Calculate time allocation
        total_weekly_work = daily_work_hours * 5  # Assuming 5-day work week
        total_weekly_commitment = total_weekly_work + weekly_exercise_hours
        
        # Assess balance (scale of 1-10, higher = better balance)
        balance_score = 10
        
        if total_weekly_commitment > 60:
            balance_score -= 3
        elif total_weekly_commitment > 50:
            balance_score -= 1
            
        if daily_work_hours > 10:
            balance_score -= 2
        elif daily_work_hours > 8:
            balance_score -= 1
            
        constraints = []
        if balance_score < 7:
            constraints.append("High time commitment may impact recovery")
        if daily_work_hours > 9:
            constraints.append("Long work hours may affect training consistency")
            
        return {
            'balance_score': round(min(max(balance_score, 1), 10), 1),
            'weekly_work_hours': total_weekly_work,
            'weekly_exercise_hours': weekly_exercise_hours,
            'total_weekly_commitment': total_weekly_commitment,
            'constraints': constraints
        }
    
    def _identify_constraints(self, lifestyle: Dict[str, Any],
                            fitness: Dict[str, Any],
                            nutrition: Dict[str, Any]) -> List[str]:
        """
        Identify lifestyle constraints that may impact training and recovery.
        
        Args:
            lifestyle: Lifestyle-related data
            fitness: Fitness-related data
            nutrition: Nutrition-related data
            
        Returns:
            List of identified constraints
        """
        constraints = []
        
        # Work-related constraints
        if lifestyle.get('daily_work_hours', 8) > 9:
            constraints.append("Limited time availability due to work schedule")
        
        # Stress-related constraints
        if lifestyle.get('stress_level', '').lower() in ['high', 'very high', 'stressful']:
            constraints.append("High stress levels may impact recovery")
        
        # Nutrition-related constraints
        if nutrition.get('meals_per_day', 3) < 3:
            constraints.append("Suboptimal meal frequency")
        
        if nutrition.get('alcohol_units_per_week', 0) > 7:
            constraints.append("Alcohol consumption may impact recovery")
            
        # Exercise-related constraints
        if fitness.get('weekly_exercise_hours', 0) > 12:
            constraints.append("High training volume requires careful recovery management")
            
        return constraints
    
    def _calculate_overall_recovery_score(self, recovery_capacity: Dict[str, Any],
                                        sleep_analysis: Dict[str, Any],
                                        stress_evaluation: Dict[str, Any],
                                        work_life_balance: Dict[str, Any]) -> float:
        """
        Calculate overall recovery score based on all factors.
        
        Args:
            recovery_capacity: Recovery capacity metrics
            sleep_analysis: Sleep analysis metrics
            stress_evaluation: Stress evaluation metrics
            work_life_balance: Work/life balance assessment
            
        Returns:
            Overall recovery score (1-10 scale)
        """
        # Weight factors
        weights = {
            'recovery_capacity': 0.3,
            'sleep': 0.3,
            'stress': 0.25,
            'work_life_balance': 0.15
        }
        
        # Calculate weighted score
        weighted_score = (
            recovery_capacity['score'] * weights['recovery_capacity'] +
            sleep_analysis['score'] * weights['sleep'] +
            (10 - stress_evaluation['stress_score']) * weights['stress'] +  # Invert stress score
            work_life_balance['balance_score'] * weights['work_life_balance']
        )
        
        return round(min(max(weighted_score, 1), 10), 1)
    
    def _generate_sleep_recommendations(self, sleep_hours: float, 
                                      sleep_issues: List[str]) -> List[str]:
        """
        Generate sleep recommendations based on analysis.
        
        Args:
            sleep_hours: Hours of sleep per night
            sleep_issues: Identified sleep issues
            
        Returns:
            List of sleep recommendations
        """
        recommendations = []
        
        if sleep_hours < 7:
            recommendations.extend([
                "Aim to increase sleep duration by 30-60 minutes",
                "Establish a consistent sleep schedule",
                "Create a relaxing bedtime routine"
            ])
            
        if "Shift work" in ' '.join(sleep_issues):
            recommendations.extend([
                "Use blackout curtains during day sleep",
                "Consider supplementing with melatonin (consult healthcare provider)",
                "Maintain consistent sleep timing even on days off"
            ])
            
        if not recommendations:
            recommendations.append("Maintain current sleep habits")
            
        return recommendations