import json
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM

# Set up basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class StepReasoningForBodyAnalysis(BaseModel):
    explanation: str = Field(
        ...,
        description="Detailed reasoning process explaining how body composition data was analyzed. "
        "Should include scientific principles, measurement interpretation, and comparative analysis."
    )
    output: str = Field(
        ...,
        description="The concrete assessment or conclusion derived from the reasoning process. "
        "Should be concise, specific, and directly address the body composition status."
    )

class MuscleGroup(BaseModel):
    """Represents analysis of a specific muscle group based on measurements."""
    name: str = Field(
        ..., 
        description="The name of the muscle group being assessed (e.g., 'Upper Body', 'Lower Body', 'Core')."
    )
    development_status: str = Field(
        ..., 
        description="Current development level relative to overall physique (e.g., 'Well-developed', 'Underdeveloped', 'Balanced')."
    )
    primary_measurements: List[str] = Field(
        ...,
        description="List of the specific measurements used to assess this muscle group (e.g., 'Chest Girth', 'Arm Circumference')."
    )
    training_priority: str = Field(
        ..., 
        description="Priority level: high, medium, or low. Indicates whether this muscle group needs prioritization based on goals and current development."
    )

class BodyProportionAnalysis(BaseModel):
    upper_lower_balance: str = Field(
        ...,
        description="Assessment of balance between upper and lower body development based on measurement ratios. "
        "Should reference standard proportions and identify any significant imbalances."
    )
    symmetry_assessment: str = Field(
        ...,
        description="Evaluation of left-right symmetry across the body based on comparative measurements. "
        "Should identify any asymmetries that might affect training or indicate potential issues."
    )
    limb_torso_ratios: str = Field(
        ...,
        description="Analysis of limb-to-torso proportions and their implications for exercise selection. "
        "Should consider biomechanical advantages/disadvantages based on body structure."
    )

class BodyCompositionEstimate(BaseModel):
    estimated_body_fat_percentage: str = Field(
        ...,
        description="Evidence-based estimate of body fat percentage using available measurements. "
        "Should provide a range (e.g., '15-18%') rather than a precise number if direct measurements are unavailable."
    )
    lean_mass_estimate: str = Field(
        ...,
        description="Calculated estimate of lean body mass based on weight and estimated body fat percentage. "
        "Should include methodology used and confidence level in the estimate."
    )
    assessment_reliability: str = Field(
        ...,
        description="Evaluation of the reliability of these estimates based on available data quality. "
        "Should honestly assess limitations and include recommendations for more accurate assessment if needed."
    )

class BodyComposition(BaseModel):
    steps: List[StepReasoningForBodyAnalysis] = Field(
        default_factory=list,
        description="Sequence of reasoning steps that trace the logical progression from measurement data "
        "to final body composition assessment. Each step should build upon previous reasoning."
    )
    muscle_groups_analysis: List[MuscleGroup] = Field(
        ...,
        description="Detailed assessment of individual muscle groups based on available measurements. "
        "Should evaluate current development status relative to the whole body and goals."
    )
    body_proportion_analysis: BodyProportionAnalysis = Field(
        ...,
        description="Analysis of overall body proportions, symmetry, and structural considerations that "
        "impact training approach. Should identify structural strengths and limitations."
    )
    composition_estimates: BodyCompositionEstimate = Field(
        ...,
        description="Evidence-based estimates of body fat percentage and lean mass based on available "
        "measurements. Should include reliability assessment of these estimates."
    )
    training_implications: List[str] = Field(
        ...,
        description="Specific training recommendations based on body composition analysis. "
        "Should include exercise selection, volume distribution, and technique considerations."
    )
    morphology_classification: str = Field(
        ...,
        description="Assessment of the client's body type according to somatotype theory (ectomorph, mesomorph, "
        "endomorph) and its implications for training and nutrition approaches."
    )

class BodyCompositionModule:
    """
    Analyzes client body measurements and composition.
    
    Uses an LLM-driven approach to analyze body proportions, estimate composition,
    and provide training implications based on structural considerations.
    """
    def __init__(self, llm_client: Optional[Any] = None):
        # Use provided LLM client or fallback to the BaseLLM
        self.llm_client = llm_client or BaseLLM()

    def process(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method that returns a structured body composition analysis.
        
        :param standardized_profile: The standardized client profile.
        :return: A dictionary containing the body composition analysis.
        """
        try:
           ##  body_analysis = self._analyze_body_composition(standardized_profile)
            body_analysis_schema = self._analyze_body_composition_schema(standardized_profile)
            return {"body_analysis_schema": body_analysis_schema}
        except Exception as e:
            logger.error("Error during body composition analysis: %s", e)
            raise e

    def get_body_analysis_system_message(self) -> str:
        """
        Returns an enhanced system message for body composition analysis.
        
        This structured prompt guides the LLM through a comprehensive analysis
        of body measurements following evidence-based principles.
        
        :return: Formatted system message string
        """
        return (
            "You are a body composition specialist trained in anthropometric analysis and exercise science. "
            "Your task is to analyze client body measurements and provide insights that can guide training program design. "
            "Use a structured approach that evaluates measurements to determine muscle development, body proportions, and composition estimates.\n\n"
            
            "Consider the following when analyzing body composition:\n"
            "1. **Muscle Development**: Assess key muscle groups based on circumference measurements and identify potential imbalances.\n"
            "2. **Body Proportions**: Evaluate upper-to-lower body balance, limb-to-torso ratios, and symmetry.\n"
            "3. **Composition Estimates**: Provide evidence-based estimates of body fat percentage using available measurements.\n"
            "4. **Structural Implications**: Determine how body structure might affect exercise selection and technique.\n"
            "5. **Somatotype Assessment**: Classify the general body type and its implications for training response.\n\n"
            
            "Use the following measurement interpretation guidelines:\n"
            "- Circumference measurements (bust, waist, hip, thigh, etc.) indicate muscle mass and fat distribution\n"
            "- Width measurements (shoulder, waist, hip width) indicate frame size and potential leverages\n"
            "- Height measurements and ratios indicate proportions and biomechanical considerations\n"
            "- Girth ratios (waist-to-hip, chest-to-waist) indicate body composition and fat distribution patterns\n\n"
            
            "Deliver a comprehensive analysis that identifies specific training considerations based on the client's unique body structure."
        )

    def _analyze_body_composition(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses an LLM function call to analyze body measurements and composition.
        
        :param standardized_profile: The standardized client profile.
        :return: Structured body composition analysis as a dictionary.
        """
        # Extract relevant data from the standardized profile
        personal_info = standardized_profile.get("personal_info", {})
        measurements_data = standardized_profile.get("body_composition", {})
        
        system_message = self.get_body_analysis_system_message()
        
        prompt = (
            "Conduct a comprehensive analysis of this client's body composition using the available measurements. "
            "Follow a scientific approach and document your reasoning for each conclusion.\n\n"
            f"CLIENT PROFILE:\n{json.dumps(personal_info)}\n\n"
            f"CLIENT MEASUREMENTS:\n{json.dumps(measurements_data)}\n\n"
            "Analyze these measurements to determine muscle development status, body proportions, and "
            "composition estimates. Focus on how these factors influence training program design.\n\n"
            "Return your analysis as a JSON with the following keys: "
            "'muscle_groups_analysis' (array of muscle group assessments), "
            "'body_proportion_analysis' (object with balance and symmetry assessments), "
            "'composition_estimates' (object with body fat and lean mass estimates), "
            "'training_implications' (array of specific training recommendations), and "
            "'morphology_classification' (string describing overall body type)."
        )

        # Define the function schema that the LLM should adhere to:
        function_schema = {
            "name": "analyze_body_composition",
            "description": "Analyze body measurements and composition to provide training insights.",
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
                    "muscle_groups_analysis": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "development_status": {"type": "string"},
                                "primary_measurements": {"type": "array", "items": {"type": "string"}},
                                "training_priority": {"type": "string"}
                            },
                            "required": ["name", "development_status", "primary_measurements", "training_priority"]
                        }
                    },
                    "body_proportion_analysis": {
                        "type": "object",
                        "properties": {
                            "upper_lower_balance": {"type": "string"},
                            "symmetry_assessment": {"type": "string"},
                            "limb_torso_ratios": {"type": "string"}
                        },
                        "required": ["upper_lower_balance", "symmetry_assessment", "limb_torso_ratios"]
                    },
                    "composition_estimates": {
                        "type": "object",
                        "properties": {
                            "estimated_body_fat_percentage": {"type": "string"},
                            "lean_mass_estimate": {"type": "string"},
                            "assessment_reliability": {"type": "string"}
                        },
                        "required": ["estimated_body_fat_percentage", "lean_mass_estimate", "assessment_reliability"]
                    },
                    "training_implications": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "morphology_classification": {"type": "string"}
                },
                "required": [
                    "steps", "muscle_groups_analysis", "body_proportion_analysis", 
                    "composition_estimates", "training_implications", "morphology_classification"
                ]
            }
        }

        # Call the LLM using the defined function schema
        result = self.llm_client.call_llm(prompt, system_message, function_schema=function_schema)
        return result
    
    def _analyze_body_composition_schema(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses an LLM with Pydantic schema to analyze body composition.
        
        :param standardized_profile: The standardized client profile.
        :return: Structured body composition analysis as a Pydantic model.
        """
        personal_info = standardized_profile.get("personal_info", {})
        measurements_data = standardized_profile.get("measurements", {})

        system_message = self.get_body_analysis_system_message()
        
        prompt = (
            "Analyze this client's body composition using anthropometric measurements and exercise science principles. "
            "Document your reasoning process and assessment methodology for each conclusion.\n\n"
            f"CLIENT PROFILE:\n{json.dumps(personal_info)}\n\n"
            f"CLIENT MEASUREMENTS:\n{json.dumps(measurements_data)}\n\n"
            "Provide a detailed analysis that includes muscle group assessments, proportion analysis, "
            "composition estimates, and specific training implications based on structural considerations. "
            "Use established anthropometric formulas and ratios where appropriate, and be honest about "
            "assessment limitations when measurements are incomplete.\n\n"
            "Return your analysis as a properly structured JSON conforming to the BodyComposition model schema."
        )
        
        # Call the LLM using the Pydantic model as schema
        result = self.llm_client.call_llm(prompt, system_message, schema=BodyComposition)
        return result