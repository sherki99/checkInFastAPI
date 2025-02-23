from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DecisionExplanation(BaseModel):
    """Detailed explanation of a specific program decision."""
    decision_area: str = Field(..., description="Area of program this decision affects")
    decision_made: str = Field(..., description="What was specifically decided")
    scientific_basis: str = Field(..., description="Scientific principles supporting this decision")
    individual_factors: List[str] = Field(..., description="Client-specific factors that influenced this decision")
    expected_outcomes: str = Field(..., description="Expected results from this decision")

class ProgramDecisions(BaseModel):
    """Collection of key program decisions and their rationale."""
    split_decisions: List[DecisionExplanation] = Field(..., description="Training split design decisions")
    volume_decisions: List[DecisionExplanation] = Field(..., description="Volume and frequency decisions")
    exercise_decisions: List[DecisionExplanation] = Field(..., description="Exercise selection decisions")
    nutrition_decisions: List[DecisionExplanation] = Field(..., description="Nutrition and diet decisions")
    progression_decisions: List[DecisionExplanation] = Field(..., description="Progression scheme decisions")

class ReportStructure(BaseModel):
    """Complete structure for the program decision documentation."""
    client_name: str = Field(..., description="Name of the client")
    creation_date: str = Field(..., description="Date the report was generated")
    executive_summary: str = Field(..., description="Brief overview of key decisions")
    key_program_decisions: ProgramDecisions = Field(..., description="All major program decisions")
    implementation_notes: List[str] = Field(..., description="Notes on implementing these decisions")
    adjustment_criteria: List[str] = Field(..., description="When and why decisions might need adjustment")

class ReportDecision:
    """
    Documents and explains the reasoning behind program decisions.
    
    Focuses on explaining why specific choices were made in the program design,
    considering scientific principles and individual client factors.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self,
        client_data: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any],
        caloric_targets: Dict[str, Any],
        macro_plan: Dict[str, Any],
        workout_plan: Dict[str, Any],
        nutrition_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process and explain all program decisions.
        
        Instead of creating new program elements, this method documents and explains
        the reasoning behind decisions that were made in previous steps.
        """
        try:
            report = self._generate_report(
                client_data,
                goal_analysis,
                body_analysis,
                history_analysis,
                caloric_targets,
                macro_plan,
                workout_plan,
                nutrition_plan
            )
            
            return {
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Error generating decision report: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """Returns the system message to guide the LLM in explaining program decisions."""
        return (
            "You are documenting and explaining the reasoning behind training and nutrition "
            "program decisions. Your task is to clearly explain why specific choices were "
            "made, connecting scientific principles with individual client factors.\n\n"
            
            "Follow these principles when explaining decisions:\n"
            "1. **Connect Science to Application**:\n"
            "   - Explain how scientific principles informed each decision\n"
            "   - Show how individual client factors modified general principles\n"
            "   - Clarify the expected outcomes of each decision\n"
            "2. **Explain Training Choices**:\n"
            "   - Justify split selection based on recovery and volume needs\n"
            "   - Connect volume landmarks to training history and goals\n"
            "   - Explain exercise selection based on biomechanics and preferences\n"
            "3. **Clarify Nutrition Decisions**:\n"
            "   - Explain caloric targets based on goals and metabolism\n"
            "   - Justify macro distributions using activity and body composition\n"
            "   - Connect meal timing to training schedule and lifestyle\n"
            "4. **Document Adjustment Criteria**:\n"
            "   - Specify when and why decisions might need modification\n"
            "   - Explain how progress will inform adjustments\n"
            "   - Connect adjustment triggers to expected outcomes\n\n"
            
            "Focus on explaining why decisions were made rather than creating new program elements."
        )
    
    def _generate_report(
        self,
        client_data: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any],
        caloric_targets: Dict[str, Any],
        macro_plan: Dict[str, Any],
        workout_plan: Dict[str, Any],
        nutrition_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a report explaining all program decisions."""
        prompt = (
            "Document and explain the reasoning behind all program decisions that were made. "
            "Focus on connecting scientific principles with individual client factors to explain "
            "why specific choices were selected.\n\n"

            f"CLIENT DATA\n"
            f"client data:\n{self._format_dict(client_data.get("data",  {}))}"


            f"TRAINING DECISIONS TO EXPLAIN:\n"
            f"Split Design:\n{self._format_dict(workout_plan.get('training_split', {}))}\n"
            f"Volume Guidelines:\n{self._format_dict(workout_plan.get('volume_guidelines', {}))}\n"
            f"Exercise Selection:\n{self._format_dict(workout_plan.get('exercise_selection', {}))}\n\n"
            
            f"NUTRITION DECISIONS TO EXPLAIN:\n"
            f"Caloric Targets:\n{self._format_dict(caloric_targets)}\n"
            f"Macro Distribution:\n{self._format_dict(macro_plan)}\n"
            f"Meal Timing:\n{self._format_dict(nutrition_plan.get('meal_timing', {}))}\n\n"
            
            f"RELEVANT CONTEXT:\n"
            f"Client Goals:\n{self._format_dict(goal_analysis)}\n"
            f"Body Analysis:\n{self._format_dict(body_analysis)}\n"
            f"Training History:\n{self._format_dict(history_analysis)}\n\n"
            
            "For each major decision:\n"
            "The main point here is just to put all the information made previously together and give scientific and profession explanation you do need to decide anythign new just to re write all this is nice professionl way "
            "1. Explain the scientific principles that guided the decision\n"
            "2. Show how client-specific factors influenced the choice\n"
            "3. Connect the decision to expected outcomes\n"
            "4. Specify when and why the decision might need adjustment\n\n"
            
            "Focus on explaining why these specific choices were made rather than "
            "creating new program elements."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=ReportStructure)
        return result
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary data for inclusion in prompts."""
        try:
            return "\n".join(f"- {k}: {v}" for k, v in data.items())
        except:
            return str(data)