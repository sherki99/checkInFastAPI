from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from first_time_plans.call_llm_class import BaseLLM
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class TrainingDecision(BaseModel):
    """Structured format for training-related decisions."""
    principle: str = Field(..., description="Core scientific principle behind the decision")
    application: str = Field(..., description="How the principle was applied")
    reasoning: List[str] = Field(..., description="Bullet points explaining the reasoning")
    individual_modifications: List[str] = Field(..., description="How it was modified for the client")
    expected_outcomes: List[str] = Field(..., description="Expected results from this decision")
    monitoring_metrics: List[str] = Field(..., description="What to track for this decision")
    adjustment_criteria: List[str] = Field(..., description="When to modify this decision")

    @validator('reasoning', 'individual_modifications', 'expected_outcomes', 'monitoring_metrics', 'adjustment_criteria')
    def ensure_minimum_points(cls, v):
        if len(v) < 3:
            raise ValueError("Must provide at least 3 points")
        return v

class WorkoutSplitDecision(TrainingDecision):
    frequency_justification: str
    recovery_considerations: List[str]
    volume_distribution: str

class ExerciseSelectionDecision(TrainingDecision):
    biomechanical_analysis: str
    progression_model: str
    exercise_hierarchy: List[str]

class VolumeDecision(TrainingDecision):
    volume_landmarks: Dict[str, str]
    progression_strategy: str
    deload_criteria: List[str]

class NutritionDecision(TrainingDecision):
    metabolic_factors: str
    timing_strategy: str
    supplement_recommendations: List[str]

class ComprehensiveReport(BaseModel):
    """Strictly structured program decision documentation."""
    client_profile: Dict[str, str]
    executive_summary: str
    
    # Training Decisions
    split_decision: WorkoutSplitDecision
    volume_decision: VolumeDecision
    exercise_decision: ExerciseSelectionDecision
    
    # Nutrition Decisions
    caloric_decision: NutritionDecision
    macro_decision: NutritionDecision
    meal_timing_decision: NutritionDecision
    
    implementation_guidelines: List[str]
    progress_metrics: List[str]
    adjustment_protocols: List[str]

class EnhancedDecisionReportGenerator:
    """Generates strictly formatted decision explanations with scientific backing."""
    
    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client or BaseLLM()
    
    def _get_section_template(self, section_type: str) -> str:
        """Returns specific template for different decision sections."""
        templates = {
            "split": """
Training Split Decision Analysis:
1. Core Scientific Principle:
   - [Explain the fundamental training science principle]

2. Practical Application:
   - [Describe how the principle was applied]

3. Scientific Reasoning:
   - [At least 3 evidence-based points]

4. Individual Modifications:
   - [At least 3 client-specific adjustments]

5. Expected Outcomes:
   - [Minimum 3 specific expected results]

6. Monitoring Approach:
   - [At least 3 specific metrics to track]

7. Adjustment Criteria:
   - [Minimum 3 specific triggers for changes]
            """,
            "volume": """
Volume Landmarks Analysis:
1. Scientific Foundation:
   - [Explain volume principle]

2. Volume Landmarks:
   MEV: [Maintenance Volume]
   MAV: [Maximum Adaptive Volume]
   MRV: [Maximum Recoverable Volume]

3. Individual Considerations:
   - [At least 3 client-specific factors]

4. Progressive Overload Plan:
   - [Detailed progression strategy]

5. Deload Criteria:
   - [At least 3 specific triggers]
            """
            # Add other templates for exercise, nutrition, etc.
        }
        return templates.get(section_type, "")

    def _format_decision_prompt(self, decision_type: str, data: Dict[str, Any]) -> str:
        """Creates strictly formatted prompt for specific decision type."""
        base_prompt = f"""
Analyze the following {decision_type} decision using Dr. Mike Israetel's scientific approach:

Input Data:
{self._format_dict(data)}

Required Format:
{self._get_section_template(decision_type)}

Requirements:
1. Must connect to scientific principles
2. Must reference specific research-backed concepts
3. Must include specific numbers and metrics
4. Must provide clear monitoring criteria
5. Must explain individual modifications
6. Must follow exact template structure
"""
        return base_prompt

    def generate_report(
        self,
        client_data: Dict[str, Any],
        program_data: Dict[str, Any]
    ) -> ComprehensiveReport:
        """Generates comprehensive report with strict formatting."""
        try:
            # Validate and extract data
            self._validate_input_data(client_data, program_data)
            training_data = self._extract_training_data(program_data)
            nutrition_data = self._extract_nutrition_data(program_data)
            
            # Generate each section with strict formatting
            report = ComprehensiveReport(
                client_profile=self._generate_client_profile(client_data),
                executive_summary=self._generate_executive_summary(client_data, program_data),
                split_decision=self._generate_split_decision(training_data, client_data),
                volume_decision=self._generate_volume_decision(training_data, client_data),
                exercise_decision=self._generate_exercise_decision(training_data, client_data),
                caloric_decision=self._generate_nutrition_decision(nutrition_data, "calories"),
                macro_decision=self._generate_nutrition_decision(nutrition_data, "macros"),
                meal_timing_decision=self._generate_nutrition_decision(nutrition_data, "timing"),
                implementation_guidelines=self._generate_implementation_guidelines(),
                progress_metrics=self._generate_progress_metrics(),
                adjustment_protocols=self._generate_adjustment_protocols()
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    def _generate_split_decision(self, training_data: Dict[str, Any], client_data: Dict[str, Any]) -> WorkoutSplitDecision:
        """Generates strictly formatted split decision analysis."""
        prompt = self._format_decision_prompt("split", {
            "training_data": training_data,
            "client_factors": client_data
        })
        
        return self.llm_client.call_llm(
            prompt=prompt,
            system_message=self.get_system_message(),
            schema=WorkoutSplitDecision
        )

    @staticmethod
    def get_system_message() -> str:
        """Returns system message enforcing scientific writing style."""
        return """You are Dr. Mike Israetel explaining training and nutrition program decisions. 
        Use specific, scientific language and maintain exact formatting requirements.
        
        Writing Style:
        - Use precise scientific terminology
        - Reference specific principles and mechanisms
        - Include exact numbers and metrics
        - Maintain professional, academic tone
        - Follow templates exactly
        - Focus on explaining existing decisions
        
        Required Elements:
        - Scientific principles
        - Evidence-based reasoning
        - Specific metrics
        - Clear monitoring criteria
        - Individual modifications
        - Exact formatting
        """