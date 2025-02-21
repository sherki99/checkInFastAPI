import json
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, model_validator
from first_time_plans.call_llm_class import BaseLLM

# Set up basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class StepReasoningForHistoryAnalysis(BaseModel):
    explanation: str = Field(
        ...,
        description="Detailed reasoning process explaining how training history data was analyzed. "
        "Should include assessment of experience level, training consistency, exercise selection patterns, and adaptation responses."
    )
    output: str = Field(
        ...,
        description="The concrete assessment or conclusion derived from the reasoning process. "
        "Should be concise, specific, and directly address training history implications."
    )

class ExercisePreference(BaseModel):
    """Represents analysis of client's exercise preferences based on history."""
    exercise_type: str = Field(
        ..., 
        description="The category or specific exercise (e.g., 'Compound lifts', 'Isolation movements', 'Bench Press')."
    )
    preference_level: str = Field(
        ..., 
        description="Client's preference level (e.g., 'Strongly preferred', 'Neutral', 'Disliked')."
    )
    effectiveness_assessment: str = Field(
        ...,
        description="Assessment of how effective this exercise type has been for the client historically."
    )
    inclusion_recommendation: str = Field(
        ..., 
        description="Recommendation for including this exercise: 'Primary', 'Secondary', 'Avoid', 'Modify'."
    )
    modification_notes: Optional[str] = Field(
        None,
        description="If modifications are needed, specific notes on how to adapt the exercise."
    )

class TrainingAdaptationHistory(BaseModel):
    strength_adaptation: str = Field(
        ...,
        description="Assessment of client's historical response to strength training stimuli. "
        "Should evaluate rate of strength gains, plateaus, and effective protocols."
    )
    hypertrophy_adaptation: str = Field(
        ...,
        description="Assessment of client's historical response to hypertrophy training. "
        "Should evaluate muscle growth response, volume tolerance, and effective protocols."
    )
    recovery_capacity: str = Field(
        ...,
        description="Evaluation of the client's demonstrated recovery abilities based on training frequency and volume history. "
        "Should identify optimal training frequencies and volume thresholds."
    )

class VolumeToleranceAssessment(BaseModel):
    weekly_volume_tolerance: str = Field(
        ...,
        description="Assessment of total weekly training volume the client has demonstrated ability to recover from. "
        "Should specify approximate set counts per muscle group and overall training volume."
    )
    frequency_tolerance: str = Field(
        ...,
        description="Evaluation of training frequency tolerance for different muscle groups. "
        "Should specify optimal training frequency per muscle group based on historical response."
    )
    intensity_response: str = Field(
        ...,
        description="Analysis of client's response to different training intensities (percentage of 1RM). "
        "Should identify intensity ranges that have produced optimal results."
    )

class TrainingHistory(BaseModel):
    steps: List[StepReasoningForHistoryAnalysis] = Field(
        default_factory=list,
        description="Sequence of reasoning steps that trace the logical progression from training history data "
        "to final assessment. Each step should build upon previous reasoning."
    )
    experience_level: str = Field(
        ...,
        description="Comprehensive assessment of client's training experience level beyond simple years training. "
        "Should include qualitative evaluation of knowledge, consistency, and progression understanding."
    )
    exercise_preferences: List[ExercisePreference] = Field(
        ...,
        description="Detailed analysis of client's exercise preferences and their effectiveness. "
        "Should evaluate both preferred and disliked exercises with recommendations."
    )
    adaptation_history: TrainingAdaptationHistory = Field(
        ...,
        description="Analysis of client's historical responses to different training stimuli. "
        "Should identify patterns in adaptation to strength, hypertrophy, and endurance training."
    )
    volume_tolerance: VolumeToleranceAssessment = Field(
        ...,
        description="Assessment of client's demonstrated ability to recover from and adapt to training volume. "
        "Should provide specific volume landmarks for program design."
    )
    progressive_overload_strategy: List[str] = Field(
        ...,
        description="Recommended progression strategies based on historical adaptation patterns. "
        "Should include specific progression methods that have proven effective for this client."
    )
    technical_proficiency: Dict[str, str] = Field(
        ...,
        description="Assessment of technical proficiency in key movement patterns. Should rate proficiency "
        "in patterns like squat, hinge, push, pull, and carry based on training history."
    )
    
    # Add a model validator to ensure schema compatibility
    @model_validator(mode='before')
    @classmethod
    def validate_schema(cls, data):
        return data

class TrainingHistoryModule:
    """
    Analyzes client training history and experience.
    
    Uses an LLM-driven approach to evaluate training experience, preferences,
    adaptation patterns, and volume tolerance to inform program design decisions.
    """
    def __init__(self, llm_client: Optional[Any] = None):
        # Use provided LLM client or fallback to the BaseLLM
        self.llm_client = llm_client or BaseLLM()

    def process(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method that returns a structured training history analysis.
        
        :param standardized_profile: The standardized client profile.
        :return: A dictionary containing the training history analysis.
        """
        try:
            history_analysis_schema = self._analyze_training_history_schema(standardized_profile)
            return {"history_analysis_schema": history_analysis_schema}
        except Exception as e:
            logger.error("Error during training history analysis: %s", e)
            raise e

    def get_history_analysis_system_message(self) -> str:
        """
        Returns an enhanced system message for training history analysis.
        
        This structured prompt guides the LLM through a comprehensive analysis
        of training history following evidence-based principles.
        
        :return: Formatted system message string
        """
        return (
            "You are a strength training specialist with expertise in program design and adaptation analysis. "
            "Your task is to analyze a client's training history to determine optimal programming variables "
            "including volume, intensity, frequency, and exercise selection. Use a structured approach that "
            "evaluates past training experience to predict future adaptation potential.\n\n"
            
            "Consider the following when analyzing training history:\n"
            "1. **Experience Evaluation**: Assess true training age beyond calendar years, considering consistency and progression.\n"
            "2. **Exercise Effectiveness**: Identify which movements have historically produced results for this client.\n"
            "3. **Volume Landmarks**: Determine Minimum Effective Volume (MEV), Maximum Adaptive Volume (MAV), and Maximum Recoverable Volume (MRV).\n"
            "4. **Adaptation Patterns**: Evaluate how quickly the client adapts to and plateaus with different training stimuli.\n"
            "5. **Technical Proficiency**: Assess movement pattern skill based on training history and preferences.\n\n"
            
            "Use these analysis guidelines:\n"
            "- True beginner status is determined by consistent, progressive training history, not merely time spent exercising\n"
            "- Exercise effectiveness is evaluated based on documented progression, not just preference\n"
            "- Volume tolerance should consider both per-session and weekly recovery demonstrated historically\n"
            "- Progressive overload strategies should be tailored to demonstrated adaptation patterns\n"
            "- Technical proficiency in key movement patterns informs exercise selection and progression rates\n\n"
            
            "Deliver a comprehensive analysis that provides specific programming guidelines based on the client's unique adaptation history."
        )

    def _analyze_training_history_schema(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses an LLM with Pydantic schema to analyze training history.
        
        :param standardized_profile: The standardized client profile.
        :return: Structured training history analysis as a Pydantic model.
        """
        personal_info = standardized_profile.get("personal_info", {})
        fitness_data = standardized_profile.get("fitness", {}).get("data", {})

        system_message = self.get_history_analysis_system_message()
        
        prompt = (
            "Analyze this client's training history using principles of exercise science and adaptation theory. "
            "Document your reasoning process and assessment methodology for each conclusion.\n\n"
            f"CLIENT PROFILE:\n{json.dumps(personal_info)}\n\n"
            f"CLIENT FITNESS HISTORY:\n{json.dumps(fitness_data)}\n\n"
            "Provide a detailed analysis that evaluates true training experience, exercise effectiveness, "
            "volume tolerance, and adaptation patterns. Use concepts from scientific training literature "
            "including MEV, MAV, MRV, and SRA (Stimulus-Recovery-Adaptation) principles.\n\n"
            "Be specific about volume recommendations (sets per muscle group), intensity ranges (% of 1RM), "
            "and frequency guidelines (sessions per muscle group per week) based on the training history.\n\n"
            "Return your analysis as a properly structured JSON conforming to the TrainingHistory model schema."
        )
        
        # Modified approach: Convert Pydantic model to JSON schema manually
        schema = self._pydantic_to_compatible_schema(TrainingHistory)
        
        # Call the LLM using the modified schema
        result = self.llm_client.call_llm(prompt, system_message, schema=schema)
        
        # Parse the result back into a Pydantic model for validation
        if isinstance(result, dict):
            return TrainingHistory.model_validate(result).model_dump()
        return result

    def _pydantic_to_compatible_schema(self, model_class) -> Dict[str, Any]:
        """
        Converts a Pydantic model to a schema that's compatible with LLM APIs.
        
        This function ensures the required fields are properly specified in the format
        expected by the LLM API.
        
        :param model_class: The Pydantic model class
        :return: A modified schema compatible with LLM APIs
        """
        # Get the JSON schema from the Pydantic model
        schema = model_class.model_json_schema()
        
        # Extract required fields
        required_fields = []
        properties = schema.get("properties", {})
        
        for field_name, field_info in properties.items():
            field_def = model_class.model_fields.get(field_name)
            if field_def and field_def.default is ...:
                required_fields.append(field_name)
        
        # Update the schema with the required fields
        schema["required"] = required_fields
        
        # Additional adjustments for nested models
        self._fix_nested_schemas(schema)
        
        return schema
    
    def _fix_nested_schemas(self, schema: Dict[str, Any]) -> None:
        """
        Recursively fixes nested schemas to ensure compatibility.
        
        :param schema: The schema dictionary to fix
        """
        if "properties" not in schema:
            return
            
        # Process each property
        for prop_name, prop_schema in schema["properties"].items():
            # Handle arrays with items
            if prop_schema.get("type") == "array" and "items" in prop_schema:
                self._fix_nested_schemas(prop_schema["items"])
                
            # Handle nested objects
            elif prop_schema.get("type") == "object" or "$ref" in prop_schema:
                self._fix_nested_schemas(prop_schema)




                
    
    def _analyze_training_history(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses an LLM function call to analyze training history and experience.
        
        :param standardized_profile: The standardized client profile.
        :return: Structured training history analysis as a dictionary.
        """
        # Extract relevant data from the standardized profile
        personal_info = standardized_profile.get("personal_info", {})
        fitness_data = standardized_profile.get("fitness", {}).get("data", {})
        
        system_message = self.get_history_analysis_system_message()
        
        prompt = (
            "Conduct a comprehensive analysis of this client's training history using evidence-based principles. "
            "Follow a scientific approach to strength and hypertrophy training and document your reasoning for each conclusion.\n\n"
            f"CLIENT PROFILE:\n{json.dumps(personal_info)}\n\n"
            f"CLIENT FITNESS HISTORY:\n{json.dumps(fitness_data)}\n\n"
            "Analyze this training history to determine experience level, exercise preferences, adaptation patterns, "
            "volume tolerance, and technical proficiency. Focus on how these factors should influence program design.\n\n"
            "Return your analysis as a JSON with the following keys: "
            "'experience_level' (string describing true training age), "
            "'exercise_preferences' (array of exercise assessments), "
            "'adaptation_history' (object with strength, hypertrophy, and recovery assessments), "
            "'volume_tolerance' (object with volume, frequency, and intensity assessments), "
            "'progressive_overload_strategy' (array of effective progression methods), and "
            "'technical_proficiency' (object mapping movement patterns to proficiency levels)."
        )

        # Define the function schema that the LLM should adhere to:
        function_schema = {
            "name": "analyze_training_history",
            "description": "Analyze training history to provide program design guidelines.",
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
                    "experience_level": {"type": "string"},
                    "exercise_preferences": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "exercise_type": {"type": "string"},
                                "preference_level": {"type": "string"},
                                "effectiveness_assessment": {"type": "string"},
                                "inclusion_recommendation": {"type": "string"},
                                "modification_notes": {"type": "string", "nullable": True}
                            },
                            "required": ["exercise_type", "preference_level", "effectiveness_assessment", "inclusion_recommendation"]
                        }
                    },
                    "adaptation_history": {
                        "type": "object",
                        "properties": {
                            "strength_adaptation": {"type": "string"},
                            "hypertrophy_adaptation": {"type": "string"},
                            "recovery_capacity": {"type": "string"}
                        },
                        "required": ["strength_adaptation", "hypertrophy_adaptation", "recovery_capacity"]
                    },
                    "volume_tolerance": {
                        "type": "object",
                        "properties": {
                            "weekly_volume_tolerance": {"type": "string"},
                            "frequency_tolerance": {"type": "string"},
                            "intensity_response": {"type": "string"}
                        },
                        "required": ["weekly_volume_tolerance", "frequency_tolerance", "intensity_response"]
                    },
                    "progressive_overload_strategy": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "technical_proficiency": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    }
                },
                "required": [
                    "steps", "experience_level", "exercise_preferences", "adaptation_history", 
                    "volume_tolerance", "progressive_overload_strategy", "technical_proficiency"
                ]
            }
        }

        # Call the LLM using the defined function schema
        result = self.llm_client.call_llm(prompt, system_message, function_schema=function_schema)
        return result
    