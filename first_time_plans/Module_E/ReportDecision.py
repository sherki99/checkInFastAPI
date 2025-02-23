from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging
from datetime import datetime

# Enhanced logging configuration
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class DecisionExplanation(BaseModel):
    """Detailed explanation of a specific program decision with scientific backing."""
    decision_area: str = Field(..., description="Area of program this decision affects")
    decision_made: str = Field(..., description="What was specifically decided")
    scientific_basis: str = Field(..., description="Scientific principles supporting this decision")
    individual_factors: List[str] = Field(..., description="Client-specific factors that influenced this decision")
    expected_outcomes: str = Field(..., description="Expected results from this decision")
    adjustment_triggers: List[str] = Field(default_factory=list, description="Conditions that would trigger adjustments")

class ProgramDecisions(BaseModel):
    """Comprehensive collection of program decisions with their rationale."""
    split_decisions: List[DecisionExplanation]
    volume_decisions: List[DecisionExplanation]
    exercise_decisions: List[DecisionExplanation]
    nutrition_decisions: List[DecisionExplanation]
    progression_decisions: List[DecisionExplanation]

    class Config:
        schema_extra = {
            "example": {
                "split_decisions": [{
                    "decision_area": "Training Split",
                    "decision_made": "4-day upper/lower split",
                    "scientific_basis": "Optimal frequency for natural recovery cycles",
                    "individual_factors": ["Work schedule", "Recovery capacity"],
                    "expected_outcomes": "Balanced progression with adequate recovery",
                    "adjustment_triggers": ["Consistent recovery issues", "Schedule changes"]
                }]
            }
        }

class ReportStructure(BaseModel):
    """Complete structure for the program decision documentation."""
    client_name: str
    creation_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    executive_summary: str
    key_program_decisions: ProgramDecisions
    implementation_notes: List[str]
    adjustment_criteria: List[str]

class DecisionReportGenerator:
    """
    Enhanced documentation generator for program decisions with scientific rationale.
    
    This class focuses on explaining the reasoning behind program choices by connecting
    scientific principles with individual client factors. It provides structured,
    detailed explanations without making new decisions.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client or BaseLLM()
        
    def generate_report(
        self,
        client_data: Dict[str, Any],
        program_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive decision report from client and program data.
        
        Args:
            client_data: Dictionary containing client information and assessments
            program_data: Dictionary containing all program decisions and plans
            
        Returns:
            Dict containing the structured decision report
            
        Raises:
            ValueError: If required data is missing
            Exception: For other processing errors
        """
        try:
            self._validate_input_data(client_data, program_data)
            
            # Extract relevant data sections
            training_data = self._extract_training_data(program_data)
            nutrition_data = self._extract_nutrition_data(program_data)
            context_data = self._extract_context_data(client_data)
            
            # Generate the report
            report = self._generate_decision_report(
                client_data=client_data,
                training_data=training_data,
                nutrition_data=nutrition_data,
                context_data=context_data
            )
            
            return {"report": report}
            
        except ValueError as e:
            logger.error(f"Invalid input data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating decision report: {str(e)}")
            raise

    def _validate_input_data(self, client_data: Dict[str, Any], program_data: Dict[str, Any]) -> None:
        """Validate that all required data fields are present."""
        required_client_fields = ["data", "goals", "body_analysis", "training_history"]
        required_program_fields = ["workout_plan", "nutrition_plan", "caloric_targets", "macro_plan"]
        
        missing_client = [f for f in required_client_fields if f not in client_data]
        missing_program = [f for f in required_program_fields if f not in program_data]
        
        if missing_client or missing_program:
            raise ValueError(
                f"Missing required data fields: "
                f"Client: {missing_client}, Program: {missing_program}"
            )

    def _extract_training_data(self, program_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure training-related decisions."""
        workout_plan = program_data.get("workout_plan", {})
        return {
            "split": workout_plan.get("training_split", {}),
            "volume": workout_plan.get("volume_guidelines", {}),
            "exercises": workout_plan.get("exercise_selection", {}),
            "progression": workout_plan.get("progression_scheme", {})
        }

    def _extract_nutrition_data(self, program_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure nutrition-related decisions."""
        return {
            "calories": program_data.get("caloric_targets", {}),
            "macros": program_data.get("macro_plan", {}),
            "timing": program_data.get("nutrition_plan", {}).get("meal_timing", {})
        }

    def _extract_context_data(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure contextual client data."""
        return {
            "goals": client_data.get("goals", {}),
            "body_analysis": client_data.get("body_analysis", {}),
            "training_history": client_data.get("training_history", {})
        }

    def _format_prompt_section(self, title: str, data: Dict[str, Any]) -> str:
        """Format a section of the prompt with consistent styling."""
        formatted_data = "\n".join(f"- {k}: {v}" for k, v in data.items())
        return f"{title}:\n{formatted_data}\n"

    def _generate_decision_report(
        self,
        client_data: Dict[str, Any],
        training_data: Dict[str, Any],
        nutrition_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate the detailed decision report using the LLM."""
        prompt = (
            "Create a comprehensive explanation of program decisions, connecting scientific "
            "principles with individual client factors.\n\n"
            
            f"{self._format_prompt_section('CLIENT INFORMATION', client_data.get('data', {}))}"
            
            "TRAINING DECISIONS:\n"
            f"{self._format_prompt_section('Split Design', training_data['split'])}"
            f"{self._format_prompt_section('Volume Guidelines', training_data['volume'])}"
            f"{self._format_prompt_section('Exercise Selection', training_data['exercises'])}\n"
            
            "NUTRITION DECISIONS:\n"
            f"{self._format_prompt_section('Caloric Targets', nutrition_data['calories'])}"
            f"{self._format_prompt_section('Macro Distribution', nutrition_data['macros'])}"
            f"{self._format_prompt_section('Meal Timing', nutrition_data['timing'])}\n"
            
            "CONTEXT:\n"
            f"{self._format_prompt_section('Client Goals', context_data['goals'])}"
            f"{self._format_prompt_section('Body Analysis', context_data['body_analysis'])}"
            f"{self._format_prompt_section('Training History', context_data['training_history'])}\n"
            
            "For each decision, explain:\n"
            "1. Scientific principles guiding the choice\n"
            "2. How client factors influenced the decision\n"
            "3. Expected outcomes and benefits\n"
            "4. Conditions that would trigger adjustments"
        )
        
        return self.llm_client.call_llm(
            prompt=prompt,
            system_message=self.get_system_message(),
            schema=ReportStructure
        )

    @staticmethod
    def get_system_message() -> str:
        """Return the system message for LLM guidance."""
        return """You are documenting training and nutrition program decisions. Explain why specific 
        choices were made by connecting scientific principles with individual client factors.

        Key principles:
        1. Connect Science to Application:
           - Link scientific principles to each decision
           - Show how client factors modified general principles
           - Clarify expected outcomes
        
        2. Explain Training Choices:
           - Justify split selection based on recovery needs
           - Connect volume to training history and goals
           - Explain exercise selection using biomechanics
        
        3. Clarify Nutrition Decisions:
           - Explain caloric targets using goals and metabolism
           - Justify macro distributions with activity level
           - Connect meal timing to training schedule
        
        4. Document Adjustment Criteria:
           - Specify adjustment triggers
           - Explain how progress influences changes
           - Link adjustments to outcomes

        Focus on explaining existing decisions rather than creating new ones."""