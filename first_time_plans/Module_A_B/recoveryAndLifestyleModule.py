import json
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM

# Set up basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class StepReasoningForLifestyleAnalysis(BaseModel):
    explanation: str = Field(
        ...,
        description="Detailed reasoning process explaining how lifestyle and recovery data was analyzed. "
        "Should include assessment of sleep quality, stress management, nutrition timing, and overall recovery capacity."
    )
    output: str = Field(
        ...,
        description="The concrete assessment or conclusion derived from the reasoning process. "
        "Should be concise, specific, and directly address recovery implications for training."
    )

class SleepAssessment(BaseModel):
    """Represents analysis of client's sleep patterns and quality."""
    overall_quality: str = Field(
        ..., 
        description="Assessment of overall sleep quality based on available data."
    )
    duration_adequacy: str = Field(
        ..., 
        description="Evaluation of whether sleep duration is adequate for recovery needs."
    )
    impact_on_training: str = Field(
        ...,
        description="Analysis of how current sleep patterns are likely affecting training outcomes."
    )
    optimization_recommendations: List[str] = Field(
        ..., 
        description="Specific, actionable recommendations to improve sleep quality for better recovery."
    )

class StressManagement(BaseModel):
    stress_level_assessment: str = Field(
        ...,
        description="Evaluation of current stress levels and their potential impact on recovery. "
        "Should consider both psychological and physiological stress markers."
    )
    stress_management_practices: List[str] = Field(
        ...,
        description="Identification of current stress management practices and their effectiveness. "
        "Should evaluate both positive and negative coping mechanisms."
    )
    training_stress_tolerance: str = Field(
        ...,
        description="Assessment of how much additional training stress can be tolerated given current life stressors. "
        "Should provide specific guidelines for training volume modulation."
    )

class NutritionTiming(BaseModel):
    meal_frequency_assessment: str = Field(
        ...,
        description="Evaluation of current meal timing and frequency relative to optimal recovery patterns. "
        "Should assess whether meal timing supports training goals."
    )
    pre_post_workout_nutrition: str = Field(
        ...,
        description="Analysis of pre- and post-workout nutrition practices and their adequacy. "
        "Should evaluate timing, composition, and quantity of peri-workout nutrition."
    )
    nutritional_recovery_recommendations: List[str] = Field(
        ...,
        description="Specific recommendations to optimize nutrition timing for recovery. "
        "Should provide actionable meal timing strategies aligned with training schedule."
    )

class RecoveryAndLifestyle(BaseModel):
    steps: List[StepReasoningForLifestyleAnalysis] = Field(
        default_factory=list,
        description="Sequence of reasoning steps that trace the logical progression from lifestyle data "
        "to recovery assessment. Each step should build upon previous reasoning."
    )
    sleep_assessment: SleepAssessment = Field(
        ...,
        description="Comprehensive analysis of sleep quality, duration, and impact on training outcomes. "
        "Should provide specific recommendations for sleep optimization."
    )
    stress_management: StressManagement = Field(
        ...,
        description="Evaluation of stress levels, coping mechanisms, and impact on recovery capacity. "
        "Should include practical stress management strategies."
    )
    nutrition_timing: NutritionTiming = Field(
        ...,
        description="Analysis of meal timing and composition relative to training schedule. "
        "Should provide specific recommendations for optimizing nutritional recovery."
    )
    recovery_modalities: Dict[str, str] = Field(
        ...,
        description="Assessment of current recovery practices and recommendations for optimization. "
        "Should evaluate active and passive recovery methods and their appropriateness."
    )
    training_schedule_recommendations: List[str] = Field(
        ...,
        description="Specific recommendations for optimal training scheduling based on lifestyle factors. "
        "Should address timing, frequency, and scheduling around life stressors."
    )
    overall_recovery_capacity: str = Field(
        ...,
        description="Holistic assessment of overall recovery capacity with specific training implications. "
        "Should provide a concrete recovery rating and appropriate training volume guidelines."
    )

class RecoveryAndLifestyleModule:
    """
    Analyzes client lifestyle factors and recovery capacity.
    
    Uses an LLM-driven approach to evaluate sleep, stress, nutrition timing,
    and overall recovery potential to inform training frequency and volume decisions.
    """
    def __init__(self, llm_client: Optional[Any] = None):
        # Use provided LLM client or fallback to the BaseLLM
        self.llm_client = llm_client or BaseLLM()

    def process(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method that returns a structured recovery and lifestyle analysis.
        
        :param standardized_profile: The standardized client profile.
        :return: A dictionary containing the recovery and lifestyle analysis.
        """
        try:
           # recovery_analysis = self._analyze_recovery_lifestyle(standardized_profile)
            recovery_analysis_schema = self._analyze_recovery_lifestyle_schema(standardized_profile)
            return {"recovery_analysis_schema": recovery_analysis_schema}
        except Exception as e:
            logger.error("Error during recovery and lifestyle analysis: %s", e)
            raise e

    def get_recovery_analysis_system_message(self) -> str:
        """
        Returns an enhanced system message for recovery and lifestyle analysis.
        
        This structured prompt guides the LLM through a comprehensive analysis
        of recovery factors following evidence-based principles.
        
        :return: Formatted system message string
        """
        return (
            "You are a recovery optimization specialist with expertise in exercise science and stress physiology. "
            "Your task is to analyze a client's lifestyle factors to determine recovery capacity and provide "
            "recommendations for optimizing recovery to support training goals. Use a structured approach that "
            "evaluates sleep, stress, nutrition timing, and recovery practices.\n\n"
            
            "Consider the following when analyzing recovery factors:\n"
            "1. **Sleep Quality**: Evaluate both duration and quality of sleep as primary recovery determinants.\n"
            "2. **Stress Management**: Assess both psychological and physiological stressors that affect recovery.\n"
            "3. **Nutrition Timing**: Analyze meal frequency and peri-workout nutrition for recovery optimization.\n"
            "4. **Recovery Modalities**: Evaluate current active and passive recovery practices.\n"
            "5. **Schedule Optimization**: Determine optimal training timing based on lifestyle constraints.\n\n"
            
            "Use these recovery assessment guidelines:\n"
            "- Sleep duration of 7-9 hours is generally optimal for training recovery\n"
            "- High psychological stress requires reduction in training volume (10-20%)\n"
            "- Protein distribution throughout the day affects recovery capacity\n"
            "- Training should be scheduled during periods of highest energy and lowest stress\n"
            "- Active recovery modalities should be appropriately dosed to avoid additional fatigue\n\n"
            
            "Deliver a comprehensive analysis that provides specific recovery optimization strategies based on the client's unique lifestyle factors."
        )

    def _analyze_recovery_lifestyle(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses an LLM function call to analyze recovery and lifestyle factors.
        
        :param standardized_profile: The standardized client profile.
        :return: Structured recovery and lifestyle analysis as a dictionary.
        """
        # Extract relevant data from the standardized profile
        personal_info = standardized_profile.get("personal_info", {})
        lifestyle_data = standardized_profile.get("lifestyle", {}).get("data", {})
        nutrition_data = standardized_profile.get("nutrition", {}).get("data", {})
        
        system_message = self.get_recovery_analysis_system_message()
        
        prompt = (
            "Conduct a comprehensive analysis of this client's recovery capacity and lifestyle factors. "
            "Document your reasoning for each conclusion and provide specific, actionable recommendations.\n\n"
            f"CLIENT PROFILE:\n{json.dumps(personal_info)}\n\n"
            f"CLIENT LIFESTYLE DATA:\n{json.dumps(lifestyle_data)}\n\n"
            f"CLIENT NUTRITION DATA:\n{json.dumps(nutrition_data)}\n\n"
            "Analyze these factors to determine overall recovery capacity, sleep quality, stress levels, "
            "and nutritional recovery support. Focus on how these factors should influence training programming decisions.\n\n"
            "Return your analysis as a JSON with the following keys: "
            "'sleep_assessment' (object with sleep quality evaluation), "
            "'stress_management' (object with stress level assessment), "
            "'nutrition_timing' (object with meal timing evaluation), "
            "'recovery_modalities' (object mapping recovery methods to assessments), "
            "'training_schedule_recommendations' (array of scheduling suggestions), and "
            "'overall_recovery_capacity' (string describing recovery capacity rating)."
        )

        # Define the function schema that the LLM should adhere to:
        function_schema = {
            "name": "analyze_recovery_lifestyle",
            "description": "Analyze recovery capacity and lifestyle factors to inform training decisions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "explanation": {"type": "string"},
                                "output": {"type": "string"}
                            },
                            "required": ["explanation", "output"]
                        }
                    },
                    "sleep_assessment": {
                        "type": "object",
                        "properties": {
                            "overall_quality": {"type": "string"},
                            "duration_adequacy": {"type": "string"},
                            "impact_on_training": {"type": "string"},
                            "optimization_recommendations": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["overall_quality", "duration_adequacy", "impact_on_training", "optimization_recommendations"]
                    },
                    "stress_management": {
                        "type": "object",
                        "properties": {
                            "stress_level_assessment": {"type": "string"},
                            "stress_management_practices": {"type": "array", "items": {"type": "string"}},
                            "training_stress_tolerance": {"type": "string"}
                        },
                        "required": ["stress_level_assessment", "stress_management_practices", "training_stress_tolerance"]
                    },
                    "nutrition_timing": {
                        "type": "object",
                        "properties": {
                            "meal_frequency_assessment": {"type": "string"},
                            "pre_post_workout_nutrition": {"type": "string"},
                            "nutritional_recovery_recommendations": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["meal_frequency_assessment", "pre_post_workout_nutrition", "nutritional_recovery_recommendations"]
                    },
                    "recovery_modalities": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    },
                    "training_schedule_recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "overall_recovery_capacity": {"type": "string"}
                },
                "required": [
                    "steps", "sleep_assessment", "stress_management", "nutrition_timing", 
                    "recovery_modalities", "training_schedule_recommendations", "overall_recovery_capacity"
                ]
            }
        }

        # Call the LLM using the defined function schema
        result = self.llm_client.call_llm(prompt, system_message, function_schema=function_schema)
        return result
    
    def _analyze_recovery_lifestyle_schema(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses an LLM with Pydantic schema to analyze recovery and lifestyle factors.
        
        :param standardized_profile: The standardized client profile.
        :return: Structured recovery and lifestyle analysis as a Pydantic model.
        """
        personal_info = standardized_profile.get("personal_info", {})
        lifestyle_data = standardized_profile.get("lifestyle", {}).get("data", {})
        nutrition_data = standardized_profile.get("nutrition", {}).get("data", {})

        system_message = self.get_recovery_analysis_system_message()
        
        prompt = (
            "Analyze this client's recovery capacity using principles of exercise science and stress physiology. "
            "Document your reasoning process and provide evidence-based recommendations.\n\n"
            f"CLIENT PROFILE:\n{json.dumps(personal_info)}\n\n"
            f"CLIENT LIFESTYLE DATA:\n{json.dumps(lifestyle_data)}\n\n"
            f"CLIENT NUTRITION DATA:\n{json.dumps(nutrition_data)}\n\n"
            "Provide a detailed analysis that evaluates sleep quality, stress levels, nutrition timing, "
            "and recovery practices. Use concepts from scientific literature on recovery optimization "
            "including sleep phases, cortisol management, and protein timing for muscle protein synthesis.\n\n"
            "Be specific about how these recovery factors should modify training variables such as volume, "
            "frequency, and intensity. Provide concrete recommendations that are immediately actionable.\n\n"
            "Return your analysis as a properly structured JSON conforming to the RecoveryAndLifestyle model schema."
        )
        
        # Call the LLM using the Pydantic model as schema
        result = self.llm_client.call_llm(prompt, system_message, schema=RecoveryAndLifestyle)
        return result