from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class BodyAnalysisSection(BaseModel):
    """Detailed body composition analysis section."""
    current_metrics: Dict[str, Any]
    structural_analysis: str
    muscular_potential: str
    body_composition_considerations: List[str]
    recommendations: List[str]

class TrainingAnalysisSection(BaseModel):
    """Detailed training analysis section."""
    current_capability: str
    volume_tolerance: str
    exercise_proficiency: str
    recovery_capacity: str
    limiting_factors: List[str]
    strengths: List[str]

class NutritionAnalysisSection(BaseModel):
    """Detailed nutrition analysis section."""
    caloric_needs_analysis: str
    macronutrient_rationale: str
    meal_timing_strategy: str
    metabolic_considerations: str
    nutrient_partitioning: str
    supplementation_needs: str
    dietary_preferences: List[str]
    special_considerations: List[str]
    nutritional_priorities: List[str]
    implementation_strategy: str

class ProgramDesignRationale(BaseModel):
    """Rationale for program design decisions."""
    split_selection_reasoning: str
    volume_approach: str
    exercise_selection_logic: str
    progression_model: str
    key_focus_points: List[str]

class DetailedReport(BaseModel):
    """Enhanced professional report with detailed analysis."""
    report_date: datetime
    executive_summary: str
    body_analysis: BodyAnalysisSection
    training_analysis: TrainingAnalysisSection
    nutrition_analysis: NutritionAnalysisSection
    program_rationale: ProgramDesignRationale
    implementation_guidelines: List[str]
    progress_metrics: List[str]
    references: List[str]

class ProfessionalReportAnalysisClass:
    """
    Generates comprehensive, professional-grade client reports following
    Dr. Mike Israetel's scientific principles of training and nutrition.
    
    This class creates detailed reports that explain the reasoning behind
    each recommendation and provide clear implementation guidelines.
    """
    
    def __init__(self):
        """Initialize the ProfessionalReportAnalysisClass."""
        logger.info("Initializing ProfessionalReportAnalysisClass")
    
    def process(
        self,
        client_data: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any],
        workout_plan: Dict[str, Any],
        nutrition_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process all analyses to generate a comprehensive professional report.
        """
        try:
            # Generate detailed analysis sections
            body_analysis_section = self._create_body_analysis(body_analysis, goal_analysis)
            training_analysis_section = self._create_training_analysis(history_analysis, recovery_analysis)
            nutrition_analysis_section = self._create_nutrition_analysis(
                nutrition_plan, body_analysis, goal_analysis, workout_plan
            )
            program_rationale = self._create_program_rationale(workout_plan, nutrition_plan, goal_analysis)
            
            # Create comprehensive report
            report = DetailedReport(
                report_date=datetime.now(),
                executive_summary=self._generate_executive_summary(
                    client_data, goal_analysis, body_analysis
                ),
                body_analysis=body_analysis_section,
                training_analysis=training_analysis_section,
                nutrition_analysis=nutrition_analysis_section,
                program_rationale=program_rationale,
                implementation_guidelines=self._generate_implementation_guidelines(
                    workout_plan, nutrition_plan
                ),
                progress_metrics=self._generate_progress_metrics(goal_analysis),
                references=self._generate_references()
            )
            
            # Format the report
            formatted_report = self._format_professional_report(report)
            
            return {
                "report": report.dict(),
                "formatted_report": formatted_report
            }
            
        except Exception as e:
            logger.error(f"Error generating professional report: {str(e)}")
            raise e

    def _create_body_analysis(
        self,
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> BodyAnalysisSection:
        """Create detailed body composition analysis."""
        return BodyAnalysisSection(
            current_metrics=body_analysis.get("metrics", {}),
            structural_analysis=self._generate_structural_analysis(body_analysis),
            muscular_potential=self._analyze_muscular_potential(body_analysis, goal_analysis),
            body_composition_considerations=self._generate_body_considerations(body_analysis),
            recommendations=self._generate_body_recommendations(body_analysis, goal_analysis)
        )
    
    def _generate_structural_analysis(self, body_analysis: Dict[str, Any]) -> str:
        """Generate professional structural analysis text."""
        metrics = body_analysis.get("metrics", {})
        return (
            f"Current body composition metrics indicate {metrics.get('body_fat_percentage', 'N/A')}% body fat with "
            f"notable muscular development in {', '.join(metrics.get('developed_muscle_groups', []))}. "
            f"Structural factors suggest potential for further development, particularly in "
            f"{', '.join(metrics.get('development_potential', []))}."
        )
    
    def _analyze_muscular_potential(
        self,
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> str:
        """Analyze muscular development potential."""
        return (
            "Based on structural analysis and current development status, there is significant potential "
            "for muscular development particularly in key areas aligned with training goals. Frame size "
            "and insertion points suggest favorable potential for overall development."
        )
    
    def _generate_body_considerations(self, body_analysis: Dict[str, Any]) -> List[str]:
        """Generate body composition considerations."""
        return [
            "Current lean mass provides good foundation for further development",
            "Body fat levels allow for productive training phase",
            "Structural proportions suggest emphasis on specific development areas",
            "Recovery capacity indicates room for increased training volume"
        ]
    
    def _generate_body_recommendations(
        self,
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate body composition recommendations."""
        return [
            "Focus on progressive overload while maintaining current body composition",
            "Prioritize hypertrophy in identified development areas",
            "Implement strategic nutrition planning to support training goals",
            "Regular body composition assessments to track progress"
        ]



    def _create_training_analysis(
        self,
        history_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any]
    ) -> TrainingAnalysisSection:
        """Create detailed training analysis."""
        return TrainingAnalysisSection(
            current_capability=self._analyze_current_capability(history_analysis),
            volume_tolerance=self._analyze_volume_tolerance(history_analysis, recovery_analysis),
            exercise_proficiency=self._analyze_exercise_proficiency(history_analysis),
            recovery_capacity=self._analyze_recovery_capacity(recovery_analysis),
            limiting_factors=self._identify_limiting_factors(history_analysis, recovery_analysis),
            strengths=self._identify_training_strengths(history_analysis)
        )
    
    def _analyze_current_capability(self, history_analysis: Dict[str, Any]) -> str:
        """Analyze current training capabilities."""
        return (
            "Current training capability demonstrates solid foundational strength and conditioning. "
            "Movement patterns show good technical proficiency with room for advanced progression. "
            "Work capacity indicates readiness for increased training demands."
        )
    
    def _analyze_volume_tolerance(
        self,
        history_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any]
    ) -> str:
        """Analyze volume tolerance capacity."""
        return (
            "Based on training history and recovery metrics, volume tolerance is currently moderate "
            "with potential for progressive increase. Previous exposure to high-volume training phases "
            "suggests good adaptability to increased workload."
        )
    
    def _analyze_exercise_proficiency(self, history_analysis: Dict[str, Any]) -> str:
        """Analyze exercise technical proficiency."""
        return (
            "Technical proficiency in core movements is well-developed, allowing for focus on "
            "progressive overload rather than technical correction. Advanced movement patterns "
            "may require additional technical development."
        )
    
    def _analyze_recovery_capacity(self, recovery_analysis: Dict[str, Any]) -> str:
        """Analyze recovery capacity."""
        return (
            "Recovery capacity shows good potential for handling increased training stress. "
            "Sleep quality and stress management support optimal recovery between sessions. "
            "Nutrition and lifestyle factors are aligned with recovery needs."
        )
    
    def _identify_limiting_factors(
        self,
        history_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify training limiting factors."""
        return [
            "Current work schedule may impact training consistency",
            "Previous injury history requires attention to specific movement patterns",
            "Recovery metrics indicate need for strategic deload planning",
            "Time availability suggests need for efficient training structure"
        ]
    
    def _identify_training_strengths(self, history_analysis: Dict[str, Any]) -> List[str]:
        """Identify training strengths."""
        return [
            "Consistent training history demonstrates good adherence",
            "Strong technical foundation in primary movements",
            "Good work capacity in moderate volume ranges",
            "Positive adaptation to progressive overload"
        ]
    



    def _create_nutrition_analysis(
        self,
        nutrition_plan: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        training_plan: Dict[str, Any]
    ) -> NutritionAnalysisSection:
        """Create detailed nutrition analysis with scientific rationale."""
        return NutritionAnalysisSection(
            caloric_needs_analysis=self._analyze_caloric_needs(nutrition_plan, body_analysis, goal_analysis),
            macronutrient_rationale=self._analyze_macronutrient_distribution(nutrition_plan, training_plan),
            meal_timing_strategy=self._analyze_meal_timing(nutrition_plan, training_plan),
            metabolic_considerations=self._analyze_metabolic_factors(body_analysis),
            nutrient_partitioning=self._analyze_nutrient_partitioning(body_analysis, training_plan),
            supplementation_needs=self._analyze_supplementation_needs(nutrition_plan, goal_analysis),
            dietary_preferences=self._analyze_dietary_preferences(nutrition_plan),
            special_considerations=self._identify_nutritional_considerations(nutrition_plan, body_analysis),
            nutritional_priorities=self._identify_nutritional_priorities(goal_analysis),
            implementation_strategy=self._create_nutrition_implementation_strategy(nutrition_plan)
        )
    
    def _analyze_caloric_needs(
        self,
        nutrition_plan: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> str:
        """Generate detailed caloric needs analysis."""
        caloric_data = nutrition_plan.get("caloric_needs", {})
        goals = goal_analysis.get("primary_goals", [])
        
        return (
            f"Based on the client's current body composition metrics and activity level, "
            f"their maintenance calories are calculated at {caloric_data.get('maintenance_calories', 'N/A')} kcal/day. "
            f"Given their primary goal of {', '.join(goals)}, we have strategically adjusted their target intake to "
            f"{caloric_data.get('target_calories', 'N/A')} kcal/day. This {caloric_data.get('caloric_adjustment', '')} "
            f"creates an optimal environment for {caloric_data.get('intended_outcome', '')}. This calculation accounts "
            f"for their BMR, TEF, NEAT, and exercise activity, with additional consideration for their metabolic efficiency "
            f"and adaptive capacity."
        )

    def _analyze_macronutrient_distribution(
        self,
        nutrition_plan: Dict[str, Any],
        training_plan: Dict[str, Any]
    ) -> str:
        """Generate detailed macronutrient distribution rationale."""
        macros = nutrition_plan.get("macronutrient_split", {})
        training_freq = training_plan.get("training_frequency", 0)
        
        return (
            f"The macronutrient distribution has been strategically designed to optimize body composition and "
            f"performance outcomes. Protein is set at {macros.get('protein', 'N/A')}g/day ({macros.get('protein_per_kg', 'N/A')}g/kg) "
            f"to ensure optimal muscle protein synthesis and recovery. Carbohydrates are targeted at "
            f"{macros.get('carbs', 'N/A')}g/day, prioritizing peri-workout nutrition for {training_freq} training days "
            f"per week. Fat intake is set at {macros.get('fats', 'N/A')}g/day to support hormonal function while "
            f"maintaining the caloric target. This distribution follows Dr. Israetel's guidelines for optimal "
            f"nutrient partitioning and recovery capacity."
        )

    def _analyze_meal_timing(
        self,
        nutrition_plan: Dict[str, Any],
        training_plan: Dict[str, Any]
    ) -> str:
        """Generate detailed meal timing strategy."""
        timing = nutrition_plan.get("meal_timing", {})
        
        return (
            f"Meal timing is structured to optimize training performance and recovery. The plan includes "
            f"{timing.get('meals_per_day', 'N/A')} meals per day, with specific emphasis on the peri-workout "
            f"window. Pre-workout nutrition is timed {timing.get('pre_workout_timing', 'N/A')} hours before "
            f"training, focusing on easily digestible carbohydrates and moderate protein. Post-workout nutrition "
            f"prioritizes rapid glycogen replenishment and protein synthesis, with {timing.get('post_workout_carbs', 'N/A')}g "
            f"of carbohydrates and {timing.get('post_workout_protein', 'N/A')}g of protein within 2 hours post-training."
        )

    def _analyze_nutrient_partitioning(
        self,
        body_analysis: Dict[str, Any],
        training_plan: Dict[str, Any]
    ) -> str:
        """Generate nutrient partitioning analysis."""
        return (
            "Nutrient partitioning has been optimized through strategic timing of macronutrients relative to "
            "training stimulus and circadian rhythms. Carbohydrate intake is concentrated around training sessions "
            "to maximize muscle glycogen repletion and minimize fat storage. Protein distribution follows an even "
            "pattern throughout the day, with slight increases in the post-workout and pre-bed periods to optimize "
            "muscle protein synthesis."
        )

    def _analyze_supplementation_needs(
        self,
        nutrition_plan: Dict[str, Any],
        goal_analysis: Dict[str, Any]
    ) -> str:
        """Generate supplementation needs analysis."""
        supps = nutrition_plan.get("supplementation", {})
        
        return (
            f"Based on the client's goals and nutritional assessment, the following evidence-based supplements "
            f"are recommended: {', '.join(supps.get('recommended_supplements', []))}. Creatine monohydrate is "
            f"prioritized at {supps.get('creatine_dose', 'N/A')}g daily for enhanced strength and hypertrophy. "
            f"Additional supplements are selected based on specific deficiencies and performance needs."
        )

    def _format_professional_report(self, report: DetailedReport) -> str:
        """Format the comprehensive professional report."""
        # Previous formatting remains the same...
        
        # Add detailed nutrition section
        formatted_output += (
            f"## Nutrition Analysis and Strategy\n"
            f"### Caloric Needs Assessment\n"
            f"{report.nutrition_analysis.caloric_needs_analysis}\n\n"
            
            f"### Macronutrient Distribution Rationale\n"
            f"{report.nutrition_analysis.macronutrient_rationale}\n\n"
            
            f"### Meal Timing Strategy\n"
            f"{report.nutrition_analysis.meal_timing_strategy}\n\n"
            
            f"### Nutrient Partitioning Considerations\n"
            f"{report.nutrition_analysis.nutrient_partitioning}\n\n"
            
            f"### Supplementation Protocol\n"
            f"{report.nutrition_analysis.supplementation_needs}\n\n"
            
            f"### Implementation Strategy\n"
            f"{report.nutrition_analysis.implementation_strategy}\n\n"
            
            f"### Nutritional Priorities\n"
            f"{chr(10).join('- ' + priority for priority in report.nutrition_analysis.nutritional_priorities)}\n\n"
        )
        
        return formatted_output