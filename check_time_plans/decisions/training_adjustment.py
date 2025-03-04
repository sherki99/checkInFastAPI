from typing import Dict, Any, List
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

class TrainingAdjustment(BaseModel):
    """Comprehensive training program modification recommendation."""
    adjustment_type: str = Field(..., description="Primary type of training adjustment")
    exercise_modifications: Dict[str, Any] = Field(..., description="Specific changes to exercise selection, sets, reps, or intensity")
    progression_strategy: List[str] = Field(..., description="Strategies for continuous progression")
    recovery_recommendations: List[str] = Field(..., description="Suggestions for optimizing recovery")
    technique_focus_areas: List[str] = Field(..., description="Specific technique improvements to prioritize")
    rationale: str = Field(..., description="Explanation for recommended training adjustments")
    priority_level: int = Field(default=3, ge=1, le=5, description="Priority of training adjustment")

class TrainingAdjustmentNode:
    """
    Decision node for generating targeted training program adjustments.
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or BaseLLM()
        self.logger = logging.getLogger(__name__)
    
    def determine_training_changes(
        self, 
        training_analysis: Dict[str, Any]
    ) -> TrainingAdjustment:
        """
        Generate training adjustments based on comprehensive training performance analysis.
        
        Args:
            training_analysis: Detailed training performance analysis
        
        Returns:
            Structured training adjustment recommendations
        """
        try:
            prompt = self._construct_training_adjustment_prompt(training_analysis)
            system_message = self._get_training_adjustment_system_message()
            
            training_adjustment = self.llm_client.call_llm(
                prompt, 
                system_message, 
                schema=TrainingAdjustment
            )
            
            return training_adjustment
        
        except Exception as e:
            self.logger.error(f"Error determining training changes: {e}")
            raise
    
    def _construct_training_adjustment_prompt(
        self, 
        training_analysis: Dict[str, Any]
    ) -> str:
        """
        Construct a comprehensive prompt for training adjustment recommendations.
        """
        performance_analysis = training_analysis.get('training_performance_analysis', {})
        exercise_insights = performance_analysis.get('exercise_insights', [])
        strength_assessment = performance_analysis.get('strength_assessment', {})
        
        return (
            "Generate precise training adjustments based on the following performance analysis:\n\n"
            
            "TRAINING PERFORMANCE:\n"
            f"Training Effectiveness Score: {performance_analysis.get('training_effectiveness_score', 'N/A')}\n"
            f"Program Adherence Score: {performance_analysis.get('program_adherence_score', 'N/A')}\n"
            f"Progression Assessment: {performance_analysis.get('progression_assessment', 'N/A')}\n\n"
            
            "EXERCISE PERFORMANCE INSIGHTS:\n" +
            "\n".join([
                f"- {insight.get('exercise_name', 'Unknown')}: "
                f"Progression Rate: {insight.get('progression_rate', 'N/A')}, "
                f"Performance Quality: {insight.get('performance_quality', 'N/A')}"
                for insight in exercise_insights
            ]) + "\n\n"
            
            "STRENGTH ASSESSMENT:\n"
            f"Relative Strengths: {', '.join(strength_assessment.get('relative_strengths', ['N/A']))}\n"
            f"Relative Weaknesses: {', '.join(strength_assessment.get('relative_weaknesses', ['N/A']))}\n"
        )
    
    def _get_training_adjustment_system_message(self) -> str:
        """Define system instructions for nutrition adjustment."""
        return (
            "You are a sports dr mike isratetek specializing in performance-driven hyperfort  strategies. "
            "Your recommendations must be scientifically grounded, personalized, and aligned with "
            "specific fitness goals. Focus on creating actionable, practical hypertofy goals and plans."
        )
