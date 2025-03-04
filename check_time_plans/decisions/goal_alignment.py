from typing import Dict, Any, List
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

class GoalProgressAssessment(BaseModel):
    """Comprehensive assessment of goal progress and alignment."""
    overall_goal_progress: float = Field(..., description="Percentage of goal achievement (0-100)")
    goal_alignment_status: str = Field(..., description="Current status of goal alignment (e.g., 'On Track', 'Needs Adjustment')")
    specific_goal_insights: List[str] = Field(..., description="Detailed insights about individual goal progress")
    primary_limiting_factors: List[str] = Field(..., description="Key factors preventing goal achievement")
    recommended_focus_areas: List[str] = Field(..., description="Areas requiring concentrated effort")

class GoalAlignmentNode:
    """
    Decision node for evaluating goal progress and alignment across body metrics and training performance.
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or BaseLLM()
        self.logger = logging.getLogger(__name__)
    
    def evaluate_goal_progress(self, metrics_analysis: Dict[str, Any], training_analysis: Dict[str, Any]) -> GoalProgressAssessment:
        """
        Comprehensively evaluate goal progress based on body metrics and training performance.
        
        Args:
            metrics_analysis: Detailed body metrics analysis
            training_analysis: Comprehensive training performance analysis
        
        Returns:
            Structured goal progress assessment
        """
        try:
            # Prepare detailed prompt with performance and metrics data
            prompt = self._construct_goal_alignment_prompt(metrics_analysis, training_analysis)
            system_message = self._get_goal_alignment_system_message()
            
            # Use LLM to generate goal progress assessment
            goal_assessment = self.llm_client.call_llm(
                prompt, 
                system_message, 
                schema=GoalProgressAssessment
            )
            
            return goal_assessment
        
        except Exception as e:
            self.logger.error(f"Error evaluating goal progress: {e}")
            raise
    
    def _construct_goal_alignment_prompt(self, metrics_analysis: Dict[str, Any], training_analysis: Dict[str, Any]) -> str:
        """
        Construct a comprehensive prompt for goal alignment assessment.
        
        Args:
            metrics_analysis: Body metrics analysis data
            training_analysis: Training performance analysis data
        
        Returns:
            Formatted prompt for LLM goal alignment analysis
        """
        composition_metrics = metrics_analysis.get('body_metrics_analysis', {}).get('composition_metrics', {})
        specific_changes = metrics_analysis.get('body_metrics_analysis', {}).get('specific_measurement_changes', [])
        training_performance = training_analysis.get('training_performance_analysis', {})
        
        return (
            "Evaluate goal progress based on the following performance and body composition data:\n\n"
            
            "BODY COMPOSITION METRICS:\n"
            f"Weight Change: {composition_metrics.get('weight_change', 'N/A')} kg\n"
            f"Waist Measurement Change: {composition_metrics.get('waist_measurement_change', 'N/A')} cm\n\n"
            
            "SPECIFIC BODY MEASUREMENTS:\n" +
            "\n".join([
                f"- {change[0]}: {change[1]} {change[3]} ({change[2]})"
                for change in specific_changes
            ]) + "\n\n"
            
            "TRAINING PERFORMANCE:\n"
            f"Training Effectiveness Score: {training_performance.get('training_effectiveness_score', 'N/A')}\n"
            f"Program Adherence Score: {training_performance.get('program_adherence_score', 'N/A')}\n"
            f"Progression Assessment: {training_performance.get('progression_assessment', 'N/A')}\n\n"
            
            "GOAL CONTEXT:\n"
            "- Weekly Goal: Increase bench press by 5kg while maintaining current body weight\n"
            "- Monthly Goal: Add 2cm to arm circumference while improving overall conditioning\n"
            "- Quarterly Goal: Reach 45kg body weight with 15% body fat and improve all major lifts by 10%\n\n"
            
            "Provide a comprehensive assessment of goal progress considering:\n"
            "1. Alignment between current performance and stated goals\n"
            "2. Progress across body composition, strength, and fitness metrics\n"
            "3. Potential barriers to goal achievement\n"
            "4. Recommended adjustments to stay on track\n"
        )
    
    def _get_goal_alignment_system_message(self) -> str:
        """Define system instructions for goal alignment assessment."""
        return (
            "You are an expert performance coach specializing in personalized fitness goal tracking. "
            "Your task is to provide a nuanced, data-driven assessment of an individual's progress "
            "towards their fitness goals, identifying strengths, limitations, and strategic recommendations.\n\n"
            
            "Assessment Principles:\n"
            "1. Holistic evaluation across multiple performance dimensions\n"
            "2. Precise quantification of goal progress\n"
            "3. Contextual understanding of individual goals\n"
            "4. Actionable, supportive recommendations\n"
            "5. Balance between objective metrics and qualitative insights"
        )
