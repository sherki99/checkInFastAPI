from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging
from first_time_plans.call_llm_class import BaseLLM

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ClientProfile(BaseModel):
    """Summary of client's basic information and background."""
    name: str
    age: int
    training_experience: str
    primary_goals: List[str]
    relevant_limitations: Optional[List[str]]
    starting_metrics: Dict[str, Any]

class ProgramSummary(BaseModel):
    """Overview of the recommended training and nutrition program."""
    training_split: str
    weekly_frequency: int
    total_volume: Dict[str, Any]
    nutrition_approach: str
    caloric_targets: Dict[str, str]
    macro_breakdown: Dict[str, str]

class DetailedRationale(BaseModel):
    """Detailed explanation of program design decisions."""
    training_split_rationale: str
    volume_selection_rationale: str
    exercise_selection_rationale: str
    nutrition_plan_rationale: str
    progression_strategy: str

class ReportAnalysis:
    """
    Generates a comprehensive analysis report synthesizing all program decisions
    and recommendations following Dr. Mike Israetel's scientific approach.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize with optional LLM client."""
        self.llm_client = llm_client or BaseLLM()
    
    def generate_report(
        self,
        client_data: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        workout_plan: Dict[str, Any],
        nutrition_plan: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive program analysis report.
        
        Args:
            client_data: Standardized client profile data
            goal_analysis: Output from GoalClarificationModule
            body_analysis: Output from BodyCompositionModule
            workout_plan: Final workout plan from WorkoutDecisionClass
            nutrition_plan: Final nutrition plan from NutritionDecisionClass
            history_analysis: Output from TrainingHistoryModule
            
        Returns:
            Dictionary containing the formatted report sections
        """
        try:
            # Extract client profile information
            client_profile = self._extract_client_profile(
                client_data, goal_analysis, body_analysis
            )
            
            # Generate program summary
            program_summary = self._generate_program_summary(
                workout_plan, nutrition_plan
            )
            
            # Generate detailed rationale
            detailed_rationale = self._generate_detailed_rationale(
                goal_analysis,
                body_analysis,
                workout_plan,
                nutrition_plan,
                history_analysis
            )
            
            # Format the complete report
            formatted_report = self._format_report(
                client_profile,
                program_summary,
                detailed_rationale
            )
            
            return {
                "report_date": datetime.now().isoformat(),
                "client_profile": client_profile.dict(),
                "program_summary": program_summary.dict(),
                "detailed_rationale": detailed_rationale.dict(),
                "formatted_report": formatted_report
            }
            
        except Exception as e:
            logger.error(f"Error generating analysis report: {str(e)}")
            raise e

    def _extract_client_profile(
        self,
        client_data: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        history_analysis:  Dict[str, Any]
    ) -> ClientProfile:
        """Extract and format client profile information."""
        personal_info = client_data.get("personal_info", {}).get("data", {})
        
        return ClientProfile(
            name=personal_info.get("name", "Client"),
            age=personal_info.get("age", 0),
            training_experience=history_analysis.get("experience_level", "Beginner"),
            primary_goals=goal_analysis.get("primary_goals", []),
            relevant_limitations=body_analysis.get("limitations", []),
            starting_metrics={
                "weight": body_analysis.get("weight", "N/A"),
                "body_fat": body_analysis.get("body_fat", "N/A"),
                "key_measurements": body_analysis.get("measurements", {})
            }
        )

    def _generate_program_summary(
        self,
        workout_plan: Dict[str, Any],
        nutrition_plan: Dict[str, Any]
    ) -> ProgramSummary:
        """Generate summary of the recommended program."""
        return ProgramSummary(
            training_split=workout_plan.get("split_type", "N/A"),
            weekly_frequency=workout_plan.get("training_frequency", 0),
            total_volume=workout_plan.get("volume_summary", {}),
            nutrition_approach=nutrition_plan.get("approach", "N/A"),
            caloric_targets={
                "training_day": nutrition_plan.get("training_day_calories", "N/A"),
                "rest_day": nutrition_plan.get("rest_day_calories", "N/A")
            },
            macro_breakdown=nutrition_plan.get("macro_distribution", {})
        )

    def _generate_detailed_rationale(
        self,
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        workout_plan: Dict[str, Any],
        nutrition_plan: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> DetailedRationale:
        """Generate detailed rationale for program decisions."""
        return DetailedRationale(
            training_split_rationale=self._explain_training_split(
                workout_plan, goal_analysis, history_analysis
            ),
            volume_selection_rationale=self._explain_volume_selection(
                workout_plan, goal_analysis, history_analysis
            ),
            exercise_selection_rationale=self._explain_exercise_selection(
                workout_plan, body_analysis, history_analysis
            ),
            nutrition_plan_rationale=self._explain_nutrition_plan(
                nutrition_plan, goal_analysis, body_analysis
            ),
            progression_strategy=self._explain_progression_strategy(
                workout_plan, goal_analysis, history_analysis
            )
        )

    def _format_report(
        self,
        client_profile: ClientProfile,
        program_summary: ProgramSummary,
        detailed_rationale: DetailedRationale
    ) -> str:
        """Format the complete analysis report."""
        report = f"""
# Program Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d')}

## Client Profile
Name: {client_profile.name}
Age: {client_profile.age}
Training Experience: {client_profile.training_experience}

### Primary Goals
{self._format_list(client_profile.primary_goals)}

### Starting Metrics
- Weight: {client_profile.starting_metrics['weight']}
- Body Fat: {client_profile.starting_metrics['body_fat']}

## Program Overview
Training Split: {program_summary.training_split}
Weekly Frequency: {program_summary.weekly_frequency} sessions per week

### Volume Distribution
{self._format_dict(program_summary.total_volume)}

### Nutrition Targets
Training Day Calories: {program_summary.caloric_targets['training_day']}
Rest Day Calories: {program_summary.caloric_targets['rest_day']}

Macro Distribution:
{self._format_dict(program_summary.macro_breakdown)}

## Program Design Rationale

### Training Split Selection
{detailed_rationale.training_split_rationale}

### Volume Selection
{detailed_rationale.volume_selection_rationale}

### Exercise Selection
{detailed_rationale.exercise_selection_rationale}

### Nutrition Plan
{detailed_rationale.nutrition_plan_rationale}

### Progression Strategy
{detailed_rationale.progression_strategy}
"""
        return report

    def _format_list(self, items: List[str]) -> str:
        """Format a list of items as bullet points."""
        return "\n".join(f"- {item}" for item in items)

    def _format_dict(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Format a dictionary as indented key-value pairs."""
        indent_str = " " * indent
        return "\n".join(f"{indent_str}- {k}: {v}" for k, v in data.items())

    def _explain_training_split(
        self,
        workout_plan: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> str:
        """Generate explanation for training split selection."""
        # Implementation would use LLM to generate detailed explanation
        prompt = (
            f"Explain the rationale behind the selected training split "
            f"({workout_plan.get('split_type', 'N/A')}) considering the client's "
            f"goals, experience level, and training history. Focus on how this "
            f"split optimizes for the primary goals while accounting for recovery "
            f"capacity and practical constraints."
        )
        
        return self.llm_client.call_llm(prompt)

    def _explain_volume_selection(
        self,
        workout_plan: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> str:
        """Generate explanation for volume selection."""
        prompt = (
            f"Explain the rationale behind the selected training volumes for "
            f"each muscle group, considering the client's recovery capacity, "
            f"training age, and specific hypertrophy goals. Reference MEV, MAV, "
            f"and MRV concepts where appropriate."
        )
        
        return self.llm_client.call_llm(prompt)

    def _explain_exercise_selection(
        self,
        workout_plan: Dict[str, Any],
        body_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> str:
        """Generate explanation for exercise selection."""
        prompt = (
            f"Explain the rationale behind the selected exercises, considering "
            f"the client's biomechanical factors, injury history, and equipment "
            f"availability. Focus on how these selections optimize stimulus while "
            f"managing fatigue and injury risk."
        )
        
        return self.llm_client.call_llm(prompt)

    def _explain_nutrition_plan(
        self,
        nutrition_plan: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any]
    ) -> str:
        """Generate explanation for nutrition plan."""
        prompt = (
            f"Explain the rationale behind the nutrition plan, including caloric "
            f"targets and macro distribution. Consider the client's goals, current "
            f"body composition, and training demands. Reference scientific principles "
            f"of nutrient timing and energy balance."
        )
        
        return self.llm_client.call_llm(prompt)

    def _explain_progression_strategy(
        self,
        workout_plan: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> str:
        """Generate explanation for progression strategy."""
        prompt = (
            f"Explain the recommended progression strategy, including how to "
            f"manage progressive overload, deloads, and program adjustments. "
            f"Consider the client's recovery capacity and long-term development "
            f"needs."
        )
        
        return self.llm_client.call_llm(prompt)