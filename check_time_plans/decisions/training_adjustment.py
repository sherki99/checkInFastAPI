from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging


class TrainingAdjustmentRecommendation(BaseModel):
    """Structured recommendation for training adjustments."""
    exercise_modifications: List[str, List[str, Any]] = Field(
        default_factory=dict, 
        description="Recommended changes to specific exercises"
    )
    volume_adjustments: Optional[List[str, float]] = Field(
        None, 
        description="Changes in training volume for different muscle groups"
    )
    intensity_changes: Optional[str] = Field(
        None, 
        description="Recommended changes in training intensity"
    )
    recovery_recommendations: Optional[List[str]] = Field(
        None, 
        description="Suggestions for improved recovery strategies"
    )
    exercise_additions: Optional[List[str]] = Field(
        None, 
        description="New exercises to incorporate into the workout plan"
    )
    exercise_deletions: Optional[List[str]] = Field(
        None, 
        description="Exercises to remove from the current plan"
    )
    rationale: str = Field(
        ..., 
        description="Explanation for the recommended training changes"
    )
    new_workout_plan: Optional[List[str, Any]] = Field(
        None, 
        description="Updated workout plan if significant changes are needed"
    )


class TrainingAdjustmentNode:
    """
    Module for determining training changes based on analysis and goal alignment.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the TrainingAdjustmentNode.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in training adjustment decisions.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a high-performance training optimization expert specializing in creating "
            "personalized workout adjustments. Your task is to provide precise, scientifically-backed "
            "training modifications that align with the client's fitness goals and current performance.\n\n"
            
            "Key Considerations:\n"
            "1. Analyze current training performance and progression\n"
            "2. Align recommendations with specific fitness goals\n"
            "3. Provide actionable exercise, volume, and intensity modifications\n"
            "4. Consider individual strength, recovery, and technique metrics\n"
            "5. Ensure recommendations promote continuous improvement and injury prevention"
        )

    def determine_training_changes(
        self, 
        training_analysis: Dict[str, Any], 
        goal_alignment: Dict[str, Any],
        current_workout_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine training changes based on comprehensive analysis.
        
        Args:
            training_analysis: Detailed training performance analysis
            goal_alignment: Current goal progress and alignment status
            current_workout_plan: Existing workout plan details
            
        Returns:
            Training adjustment recommendations
        """
        try:
            # Prepare comprehensive prompt for LLM analysis
            prompt = (
                "Perform a detailed training adjustment analysis based on the following data:\n\n"
                f"TRAINING ANALYSIS:\n{self._format_dict(training_analysis)}\n\n"
                f"GOAL ALIGNMENT:\n{self._format_dict(goal_alignment)}\n\n"
                f"CURRENT WORKOUT PLAN:\n{self._format_dict(current_workout_plan)}\n\n"
                
                "Provide comprehensive training adjustment recommendations covering:\n"
                "1. Exercise modifications and progressions\n"
                "2. Volume and intensity adjustments\n"
                "3. Recovery and technique improvement strategies\n"
                "4. Rationale for proposed changes\n"
                "5. Potential updates to the workout plan"
            )
            
            system_message = self.get_system_message()
            result = self.llm_client.call_llm(
                prompt, 
                system_message, 
                schema=TrainingAdjustmentRecommendation
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error determining training changes: {str(e)}")
            raise e

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary into readable string."""
        if not data:
            return "No data available"
        
        formatted = ""
        for key, value in data.items():
            formatted += f"  {key}: {value}\n"
        return formatted