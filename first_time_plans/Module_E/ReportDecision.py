from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ClientInsight(BaseModel):
    """Individual insight about a specific aspect of the client's profile or program."""
    aspect: str = Field(..., description="Area this insight relates to (e.g., 'Training History', 'Body Composition')")
    observation: str = Field(..., description="Key observation about this aspect")
    implications: List[str] = Field(..., description="What this means for the program")
    recommendations: List[str] = Field(..., description="Specific recommendations based on this insight")

class SectionAnalysis(BaseModel):
    """Analysis of a specific program section."""
    section_name: str = Field(..., description="Name of the program section")
    key_findings: List[str] = Field(..., description="Main findings from this section")
    scientific_basis: str = Field(..., description="Scientific principles supporting these findings")
    practical_applications: List[str] = Field(..., description="How these findings apply to the program")

class ProgramReport(BaseModel):
    """Comprehensive program report structure."""
    client_name: str = Field(..., description="Name of the client")
    report_date: str = Field(..., description="Date the report was generated")
    program_overview: str = Field(..., description="Brief overview of the entire program")
    key_insights: List[ClientInsight] = Field(..., description="Important client-specific insights")
    section_analyses: List[SectionAnalysis] = Field(..., description="Analysis of each program section")
    implementation_guidelines: List[str] = Field(..., description="Guidelines for implementing the program")
    success_metrics: List[str] = Field(..., description="How to measure program success")
    adjustment_criteria: List[str] = Field(..., description="When and how to adjust the program")

class ReportAnalysis:
    """
    Analyzes program data and generates comprehensive reports.
    Focuses on explaining the rationale behind program decisions and providing
    clear implementation guidelines.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize with optional LLM client."""
        self.llm_client = llm_client

    def analyze_program_data(
        self,
        client_data: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any],
        caloric_targets: Dict[str, Any],
        macro_plan: Dict[str, Any],
        workout_plan: Dict[str, Any],
        nutrition_plan: Dict[str, Any]
    ) -> ProgramReport:
        """
        Generate a comprehensive program report from all available data.
        """
        try:
            # Extract client name
            client_name = client_data.get("personal_info", {}).get("data", {}).get("name", "Client")
            
            # Generate program overview
            overview = self._generate_program_overview(
                goal_analysis,
                workout_plan,
                nutrition_plan
            )
            
            # Generate key insights
            insights = self._generate_key_insights(
                body_analysis,
                history_analysis,
                client_data
            )
            
            # Analyze each section
            section_analyses = self._analyze_program_sections(
                workout_plan,
                nutrition_plan,
                goal_analysis
            )
            
            # Create implementation guidelines
            implementation_guidelines = self._create_implementation_guidelines(
                workout_plan,
                nutrition_plan
            )
            
            # Define success metrics
            success_metrics = self._define_success_metrics(goal_analysis)
            
            # Define adjustment criteria
            adjustment_criteria = self._define_adjustment_criteria(
                goal_analysis,
                body_analysis
            )
            
            return ProgramReport(
                client_name=client_name,
                report_date=datetime.now().strftime("%Y-%m-%d"),
                program_overview=overview,
                key_insights=insights,
                section_analyses=section_analyses,
                implementation_guidelines=implementation_guidelines,
                success_metrics=success_metrics,
                adjustment_criteria=adjustment_criteria
            )
            
        except Exception as e:
            raise Exception(f"Error generating program report: {str(e)}")

    def _generate_program_overview(
        self,
        goal_analysis: Dict[str, Any],
        workout_plan: Dict[str, Any],
        nutrition_plan: Dict[str, Any]
    ) -> str:
        """Generate a concise overview of the program."""
        primary_goals = goal_analysis.get("primary_goals", [])
        training_split = workout_plan.get("training_split", {}).get("split_type", "")
        nutrition_approach = nutrition_plan.get("approach", "balanced")
        
        return (
            f"Program designed to achieve {', '.join(primary_goals)} through a "
            f"{training_split} training split and {nutrition_approach} nutrition approach. "
            "Incorporates scientific principles of progressive overload, "
            "proper exercise selection, and targeted nutrition strategies."
        )

    def _generate_key_insights(
        self,
        body_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any],
        client_data: Dict[str, Any]
    ) -> List[ClientInsight]:
        """Generate key insights about the client and program."""
        insights = []
        
        # Training history insight
        experience_level = history_analysis.get("experience_level", "")
        if experience_level:
            insights.append(ClientInsight(
                aspect="Training Experience",
                observation=experience_level,
                implications=[
                    "Appropriate exercise complexity can be programmed",
                    "Progressive overload can be more aggressive"
                ],
                recommendations=[
                    "Include advanced training techniques",
                    "Focus on compound movements",
                    "Implement periodization strategies"
                ]
            ))
        
        # Body composition insight
        body_comp = body_analysis.get("composition_estimates", {})
        if body_comp:
            insights.append(ClientInsight(
                aspect="Body Composition",
                observation=f"Estimated {body_comp.get('estimated_body_fat_percentage', '')} body fat",
                implications=[
                    "Good foundation for muscle growth",
                    "Metabolic capacity supports training goals"
                ],
                recommendations=[
                    "Focus on progressive overload",
                    "Maintain current nutritional intake",
                    "Regular body composition assessments"
                ]
            ))
            
        return insights

    def _analyze_program_sections(
        self,
        workout_plan: Dict[str, Any],
        nutrition_plan: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> List[SectionAnalysis]:
        """Analyze each major section of the program."""
        sections = []
        
        # Training analysis
        sections.append(SectionAnalysis(
            section_name="Training Program",
            key_findings=[
                f"Split type: {workout_plan.get('training_split', {}).get('split_type', '')}",
                f"Training frequency: {workout_plan.get('training_split', {}).get('training_frequency', '')} days/week"
            ],
            scientific_basis=(
                "Based on principles of progressive overload, "
                "optimal training frequency, and exercise selection hierarchy"
            ),
            practical_applications=[
                "Follow recommended exercise order",
                "Focus on prescribed rep ranges",
                "Progress weights according to guidelines"
            ]
        ))
        
        # Nutrition analysis
        sections.append(SectionAnalysis(
            section_name="Nutrition Plan",
            key_findings=[
                f"Caloric target: {nutrition_plan.get('caloric_target', '')}",
                f"Macro distribution: {nutrition_plan.get('macro_distribution', '')}"
            ],
            scientific_basis=(
                "Based on metabolic requirements, training demands, "
                "and optimal nutrient timing principles"
            ),
            practical_applications=[
                "Follow meal timing recommendations",
                "Meet daily macro targets",
                "Adjust intake based on progress"
            ]
        ))
        
        return sections

    def _create_implementation_guidelines(
        self,
        workout_plan: Dict[str, Any],
        nutrition_plan: Dict[str, Any]
    ) -> List[str]:
        """Create practical implementation guidelines."""
        return [
            "Follow the prescribed training split and rest days",
            "Track weights and reps for progressive overload",
            "Monitor recovery and adjust intensity as needed",
            "Follow meal timing recommendations around workouts",
            "Track body measurements and progress photos weekly",
            "Maintain a training log for all workouts"
        ]

    def _define_success_metrics(
        self,
        goal_analysis: Dict[str, Any]
    ) -> List[str]:
        """Define how to measure program success."""
        metrics = []
        objectives = goal_analysis.get("objectives", [])
        
        for obj in objectives:
            if isinstance(obj, dict):
                metrics.append(f"{obj.get('objective', '')}: {obj.get('metric', '')}")
        
        return metrics

    def _define_adjustment_criteria(
        self,
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any]
    ) -> List[str]:
        """Define when and how to adjust the program."""
        return [
            "Adjust weights when prescribed reps become too easy",
            "Modify volume if recovery is compromised",
            "Increase calories if weight gain stalls",
            "Decrease volume during high stress periods",
            "Change exercises if plateaus occur",
            "Regular reassessment of goals and progress"
        ]