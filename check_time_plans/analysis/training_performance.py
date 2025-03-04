from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ExerciseInsight(BaseModel):
    """Detailed insight about a specific exercise."""
    exercise_name: str = Field(..., description="Name of the exercise")
    progression_rate: str = Field(..., description="Rate of progression (e.g., 'steady', 'stalled', 'declining')")
    performance_quality: str = Field(..., description="Quality of performance based on reported technique")
    limiting_factors: List[str] = Field(..., description="Factors limiting performance on this exercise")
    optimization_suggestions: List[str] = Field(..., description="Suggestions for optimizing performance")
    technical_notes: Optional[str] = Field(None, description="Notes about technique or execution")

class StrengthAssessment(BaseModel):
    """Assessment of strength qualities and development."""
    strength_profile: List[str] = Field(..., description="Profile of different strength qualities (e.g., maximal, explosive, endurance)")
    relative_strengths: List[str] = Field(..., description="Areas of relative strength")
    relative_weaknesses: List[str] = Field(..., description="Areas needing strength development")
    strength_imbalances: List[str] = Field(..., description="Identified strength imbalances")
    strength_development_suggestions: List[str] = Field(..., description="Suggestions for strength development")

class TrainingPerformanceAnalysis(BaseModel):
    """Comprehensive analysis of training performance and adaptation."""
    training_effectiveness_score: float = Field(..., description="Overall training effectiveness score (0-100)")
    program_adherence_score: float = Field(..., description="Program adherence score (0-100)")
    progression_assessment: str = Field(..., description="Overall assessment of training progression")
    exercise_insights: List[ExerciseInsight] = Field(..., description="Detailed insights for key exercises")
    strength_assessment: StrengthAssessment = Field(..., description="Assessment of strength qualities and development")
    technique_issues: List[str] = Field(..., description="Identified technique issues")
    volume_tolerance: str = Field(..., description="Assessment of volume tolerance")
    intensity_response: str = Field(..., description="Response to training intensity")
    recovery_capacity: str = Field(..., description="Assessment of recovery capacity between sessions")
    performance_patterns: List[str] = Field(..., description="Identified patterns in performance")
    training_recommendations: List[str] = Field(..., description="Recommendations for training optimization")

class TrainingPerformanceModule:
    """
    Module for analyzing training performance data to assess exercise progression and program effectiveness.
    
    This class takes the training logs data extracted by TrainingLogsExtractor and performs
    deeper analysis to guide training-related decisions and recommendations.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the TrainingPerformanceModule with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def analyze_workout_execution(self, training_logs_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze training logs to assess performance and program effectiveness.
        
        This method evaluates the training logs data to identify patterns, progression,
        and opportunities for improvement in the client's training approach.
        
        Args:
            training_logs_data: The training logs data extracted by TrainingLogsExtractor
            
        Returns:
            A dictionary containing structured training performance analysis
        """
        try:
            # Process using the schema-based approach
            schema_result = self._analyze_performance_schema(training_logs_data)
            
            return {
                "training_performance_analysis": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error analyzing training performance: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in training performance analysis.
        
        The system message establishes the context and criteria for analyzing
        training performance according to exercise science principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are an exercise performance analyst specializing in strength training and adaptation. "
            "Your task is to analyze training log data to assess performance, progression, and program "
            "effectiveness according to exercise science principles.\n\n"
            
            "Apply these principles when analyzing training performance:\n"
            "1. **Progressive Overload Analysis**: Evaluate the application of progressive overload principles.\n"
            "2. **Exercise Technique Assessment**: Identify potential technique issues from performance patterns.\n"
            "3. **Strength Quality Analysis**: Assess different strength qualities (maximal, explosive, endurance).\n"
            "4. **Adaptation Indicators**: Identify signs of positive adaptation or plateaus.\n"
            "5. **Movement Pattern Balance**: Evaluate balance across different movement patterns.\n"
            "6. **Volume/Intensity Relationship**: Analyze the relationship between training volume and intensity.\n"
            "7. **Weak Link Identification**: Identify potential weak links in the kinetic chain.\n\n"
            
            "Your analysis should provide actionable insights about training effectiveness, "
            "progression patterns, and specific exercise performance that can guide program optimization."
        )
    
    def _analyze_performance_schema(self, training_logs_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze training performance using Pydantic schema validation.
        
        Args:
            training_logs_data: The training logs data from extractor
            
        Returns:
            Structured training performance analysis as a Pydantic model
        """
        # Extract relevant data from training logs data
        training_logs_analysis = training_logs_data.get("training_logs_analysis", {})
        
        # Extract performance metrics
        exercises_progression = training_logs_analysis.get("exercises_progression", [])
        muscle_groups_assessment = training_logs_analysis.get("muscle_groups_assessment", [])
        strongest_lifts = training_logs_analysis.get("strongest_lifts", [])
        most_improved_lifts = training_logs_analysis.get("most_improved_lifts", [])
        least_improved_lifts = training_logs_analysis.get("least_improved_lifts", [])
        training_consistency = training_logs_analysis.get("training_consistency", 0)
        volume_completion = training_logs_analysis.get("volume_completion_rate", 0)
        intensity_adherence = training_logs_analysis.get("intensity_adherence", 0)
        limiting_factors = training_logs_analysis.get("common_limiting_factors", [])
        performance_trends = training_logs_analysis.get("performance_trends", "")
        
        # Construct detailed prompt with comprehensive training data
        prompt = (
            "Analyze this client's training performance data to assess progression, effectiveness, "
            "and opportunities for optimization. Apply exercise science principles to provide "
            "insights that can guide program adjustments.\n\n"
            
            f"EXERCISE PROGRESSION:\n{self._format_list(exercises_progression)}\n\n"
            f"MUSCLE GROUP ASSESSMENT:\n{self._format_list(muscle_groups_assessment)}\n\n"
            f"STRONGEST LIFTS:\n{self._format_list(strongest_lifts)}\n\n"
            f"MOST IMPROVED LIFTS:\n{self._format_list(most_improved_lifts)}\n\n"
            f"LEAST IMPROVED LIFTS:\n{self._format_list(least_improved_lifts)}\n\n"
            f"TRAINING CONSISTENCY: {training_consistency}%\n"
            f"VOLUME COMPLETION: {volume_completion}%\n"
            f"INTENSITY ADHERENCE: {intensity_adherence}%\n\n"
            f"COMMON LIMITING FACTORS:\n{self._format_list(limiting_factors)}\n\n"
            f"PERFORMANCE TRENDS:\n{performance_trends}\n\n"
            
            "Your training performance analysis should include:\n"
            "1. Overall training effectiveness and program adherence scores\n"
            "2. Detailed insights for key exercises with progression assessment\n"
            "3. Comprehensive strength assessment across different qualities\n"
            "4. Identification of technique issues and movement pattern imbalances\n"
            "5. Assessment of volume tolerance and intensity response\n"
            "6. Recovery capacity evaluation\n"
            "7. Specific recommendations for training optimization\n\n"
            
            "Create a comprehensive training performance analysis with actionable insights."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=TrainingPerformanceAnalysis)
        return result
    
    def _format_list(self, data: List[Any]) -> str:
        """Format list into readable string."""
        if not data:
            return "None available"
        
        formatted = ""
        for item in data:
            if isinstance(item, dict):
                formatted += f"- {self._format_dict(item)}\n"
            else:
                formatted += f"- {item}\n"
        return formatted
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary into readable string."""
        if not data:
            return "No data available"
        
        formatted = ""
        for key, value in data.items():
            formatted += f"  {key}: {value}\n"
        return formatted