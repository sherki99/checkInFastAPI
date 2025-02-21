import json
import logging
from typing import Dict, Any, Optional, List
from first_time_plans.call_llm_class import BaseLLM
from pydantic import BaseModel, Field

# Set up basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



class StepReasoningForPrimaryGoals(BaseModel):
    explanation: str = Field(
        ...,
        description="Detailed reasoning process explaining how and why specific goals were determined. "
        "Should include considerations of client assessment data, scientific principles, and practical constraints."
    )
    output: str = Field(
        ...,
        description="The concrete recommendation or conclusion derived from the reasoning process. "
        "Should be concise, actionable, and directly address the goal requirements."
    )

class Objective(BaseModel):
    """Represents a specific fitness objective with measurement criteria."""
    objective: str = Field(
        ..., 
        description="The specific goal statement that defines what the client wants to achieve. "
        "Should be specific and actionable, such as 'Increase chest muscle mass' or 'Improve squat strength'."
    )
    metric: str = Field(
        ..., 
        description="How progress will be measured quantitatively. Must include a specific numeric "
        "target and timeframe, such as '10% increase in 1RM within 8 weeks' or '2cm arm circumference "
        "increase in 12 weeks'."
    )
    priority: str = Field(
        ..., 
        description="Priority level: high, medium, or low. High priority goals should be addressed "
        "first in programming and receive more volume allocation."
    )

class TimeframeAnalysis(BaseModel):
    realistic_assessment: str = Field(
        ...,
        description="Honest evaluation of whether the client's desired timeframe is realistic based on "
        "physiological principles, training history, and available resources. Should reference relevant "
        "scientific literature on typical adaptation rates."
    )
    recommended_timeline: str = Field(
        ...,
        description="Evidence-based timeline recommendation that balances ambition with physiological "
        "reality. Should specify exact weeks/months and include milestones for progressive achievement."
    )

class GoalSplit(BaseModel):
    goal_next_week: str = Field(
        ...,
        description="Immediate action steps for the first week that initiate progress toward the larger "
        "goal. Should be highly specific, including exercise selection, frequency, intensity, and volume."
    )
    goal_next_four_week: str = Field(
        ...,
        description="Medium-term objectives that build upon week one and establish momentum. Should "
        "include progressive overload parameters and measurable checkpoints."
    )
    goal_next_twelve_week: str = Field(
        ...,
        description="Long-term vision that completes a full mesocycle of training. Should describe the "
        "expected cumulative adaptations and quantifiable outcomes by the end of this period."
    )

class Goal(BaseModel):
    steps: List[StepReasoningForPrimaryGoals] = Field(
        default_factory=list,
        description="Sequence of reasoning steps that trace the logical progression from assessment data "
        "to final goal recommendations. Each step should build upon previous reasoning."
    )
    primary_goals: List[str] = Field(
        ...,
        description="The 1-3 most important objectives that should receive the majority of programming "
        "focus. Should address the client's stated priorities while being physiologically optimal."
    )
    secondary_goals: List[str] = Field(
        ...,
        description="Supporting objectives that complement the primary goals but receive less direct "
        "programming focus. Should include maintenance goals and complementary adaptations."
    )
    objectives: List[Objective] = Field(
        default_factory=list,
        description="Structured breakdown of each goal into specific, measurable objectives with clear "
        "priority levels. Should operationalize abstract goals into concrete targets."
    )
    timeframe_analysis: TimeframeAnalysis = Field(
        ...,
        description="Comprehensive analysis of goal timeframes that balances client expectations with "
        "physiological reality. Should provide both assessment and constructive recommendations."
    )
    goals_split: Optional[GoalSplit] = Field(
        None,
        description="Periodized breakdown of larger goals into specific weekly, monthly and quarterly "
        "targets. Should establish a clear progression that builds toward the ultimate objectives."
    )


class GoalClarificationModule:
    """
    Analyzes client goals and defines measurable objectives.
    
    Uses an LLM-driven function calling approach to separate primary from secondary goals,
    and provides measurable objectives along with a realistic timeframe.
    """
    def __init__(self, llm_client: Optional[Any] = None):
        # Use provided LLM client or fallback to the SimpleLLMClient
        self.llm_client = llm_client or BaseLLM()

    def process(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method that returns a structured goal analysis.
        
        :param standardized_profile: The standardized client profile.
        :return: A dictionary containing the goal analysis.
        """
        try:
            goal_analysis = self._analyze_goals(standardized_profile)
            goal_analysis_schema = self._analyze_goals_schema(standardized_profile)
            return {"goal_analysis_function": goal_analysis, "goal_analysis_schema": goal_analysis_schema}
        except Exception as e:
            logger.error("Error during goal clarification: %s", e)
            raise e

    def get_goal_analysis_system_message(self) -> str:
        """
        Returns an enhanced system message for goal analysis using Dr. Israetel's methodology.
        
        This structured prompt guides the LLM through a comprehensive step-by-step analysis
        of fitness goals following evidence-based principles.
        
        :return: Formatted system message string
        """
        return (

            "You are a fitness goal specialist trained in evidence-based principles, including the methodologies of Dr. Mike Israetel. "
            "Your task is to analyze client goals and structure them according to the principles of periodization, hypertrophy, and strength training."
            "Use a structured output that prioritizes primary goals over secondary ones, defines measurable objectives, and evaluates realistic timeframes."
            "Consider the following when structuring goals:\n"
            "1. **Prioritization**: Identify whether a goal is hypertrophy-focused, strength-focused, endurance-based, or general fitness.\n"
            "2. **Measurable Objectives**: Ensure goals follow SMART principles (Specific, Measurable, Achievable, Relevant, Time-bound).\n"
            "3. **Timeframes & Adaptation**: Provide realistic timeframes for achieving results based on progressive overload and recovery science.\n"
            "4. **Barriers & Solutions**: Identify expected obstacles (e.g., injuries, motivation, diet) and suggest evidence-based modifications.\n"
            "5. **Training Adjustments**: Consider training volume, intensity, and frequency based on the client's goal (e.g., 10-20 sets per muscle group per week for hypertrophy, heavier loads for strength).\n"
            "Deliver a JSON response with the following structure:\n"
            " - 'primary_goals': A list of the client’s most important fitness goals.\n"
            " - 'secondary_goals': A list of additional goals that are relevant but lower priority.\n"
            " - 'objectives': A list of structured objectives, each containing:\n"
            "      - 'objective': The specific goal (e.g., 'Increase bench press strength').\n"
            "      - 'metric': The way progress will be tracked (e.g., 'Increase by 10kg in 8 weeks').\n"
            "      - 'priority': Whether it is high, medium, or low priority.\n"
            " - 'timeframe_analysis': A structured assessment including realistic expectations and recommended timelines."


          """  "You are a fitness goal specialist following Dr. Mike Israetel's evidence-based methodologies. "
            "Analyze the client's goals through this specific step-by-step framework:\n\n"
            
            "STEP 1: GOAL CLASSIFICATION AND IDENTIFICATION\n"
            "- Classify each stated goal by type (hypertrophy, strength, endurance, fat loss, general fitness)\n"
            "- Identify the muscle groups or performance aspects involved\n"
            "- Determine if goals are compatible or potentially conflicting\n"
            
            "STEP 2: PRIORITIZATION ANALYSIS\n"
            "- Identify which goals should be primary based on client motivation, timeframes, and physiological factors\n"
            "- Determine which goals work as secondary and support the primary goals\n"
            "- Consider potential tradeoffs (e.g., maximum hypertrophy vs maximum strength)\n"
            
            "STEP 3: VOLUME-LOAD-FREQUENCY PRESCRIPTION\n"
            "- For hypertrophy goals: Determine appropriate volume (10-20 sets per muscle group per week)\n"
            "- For strength goals: Establish appropriate intensity ranges (70-95% 1RM)\n"
            "- For endurance goals: Set appropriate session durations and heart rate zones\n"
            "- Plan frequency based on recovery capacity and goal priority\n"
            
            "STEP 4: PERIODIZATION STRUCTURE\n"
            "- Outline appropriate weekly undulation patterns\n"
            "- Define mesocycle lengths (typically 4-8 weeks) with appropriate progression\n"
            "- Plan deload timing based on volume and intensity\n"
            
            "STEP 5: PROGRESS METRICS ESTABLISHMENT\n"
            "- Define specific, measurable metrics for each goal\n"
            "- Establish realistic rate-of-gain expectations based on training age\n"
            "- Set specific checkpoints for assessment (weekly, monthly, quarterly)\n"
            
            "STEP 6: TIMELINE AND EXPECTATION SETTING\n"
            "- Provide scientific rationales for expected timeframes\n"
            "- Account for diminishing returns based on training experience\n"
            "- Set clear distinctions between short-term (1-4 weeks), medium-term (1-3 months), and long-term (3+ months) goals\n"
            
            "For each step, explicitly state your reasoning process and how it applies to this specific client. "
            "Provide concrete examples and Dr. Israetel's scientific principles that support your analysis.\n\n"
            
            "Deliver a JSON response with the following structure:\n"
            " - 'steps': A list of analysis steps, each containing:\n"
            "      - 'explanation': Your reasoning for this step\n"
            "      - 'output': The conclusion reached in this step\n"
            " - 'primary_goals': A list of the client's most important fitness goals.\n"
            " - 'secondary_goals': A list of additional goals that are relevant but lower priority.\n"
            " - 'objectives': A list of structured objectives, each containing:\n"
            "      - 'objective': The specific goal (e.g., 'Increase bench press strength').\n"
            "      - 'metric': The way progress will be tracked (e.g., 'Increase by 10kg in 8 weeks').\n"
            "      - 'priority': Whether it is high, medium, or low priority.\n"
            " - 'timeframe_analysis': A structured assessment including realistic expectations and recommended timelines.\n"
            " - 'goals_split': Breakdown of goals by timeframe (weekly, monthly, quarterly)."
"""
        )

    def _analyze_goals(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses an LLM function call to analyze and structure client goals.
        
        :param standardized_profile: The standardized client profile.
        :return: Structured goal analysis as a dictionary.
        """
        # Extract relevant data from the standardized profile
        personal_info = standardized_profile.get("personal_info", {})
        goals_data = standardized_profile.get("goals", {}).get("data", {})
        fitness_data = standardized_profile.get("fitness", {}).get("data", {})

        system_message = self.get_goal_analysis_system_message()
        
        prompt = (
            "Conduct a comprehensive analysis of this client's fitness goals using Dr. Mike Israetel's methodologies. "
            "Follow each step precisely and document your reasoning for each decision.\n\n"
            f"CLIENT PROFILE:\n{json.dumps(personal_info)}\n\n"
            f"CLIENT GOALS:\n{json.dumps(goals_data)}\n\n"
            f"CLIENT FITNESS DATA:\n{json.dumps(fitness_data)}\n\n"
            "Work through each step of the analysis framework and explain the rationale behind your decisions. "
            "Return your analysis as a JSON with the following keys: "
            "'primary_goals' (array of strings), "
            "'secondary_goals' (array of strings), "
            "'objectives' (array of objects with keys: 'objective', 'metric', 'priority'), "
            "'timeframe_analysis' (object with keys: 'realistic_assessment' and 'recommended_timeline'), and "
            "'goals_split' (object with keys: 'goal_next_week', 'goal_next_four_week', 'goal_next_twelve_week')."
        )

        # Define the function schema that the LLM should adhere to:
        function_schema = {
            "name": "analyze_fitness_goals",
            "description": "Analyze fitness goals using Dr. Israetel's methodology and return structured recommendations.",
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
                    "primary_goals": {"type": "array", "items": {"type": "string"}},
                    "secondary_goals": {"type": "array", "items": {"type": "string"}},
                    "objectives": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "objective": {"type": "string"},
                                "metric": {"type": "string"},
                                "priority": {"type": "string"}
                            },
                            "required": ["objective", "metric", "priority"]
                        }
                    },
                    "timeframe_analysis": {
                        "type": "object",
                        "properties": {
                            "realistic_assessment": {"type": "string"},
                            "recommended_timeline": {"type": "string"}
                        },
                        "required": ["realistic_assessment", "recommended_timeline"]
                    },
                    "goals_split": {
                        "type": "object", 
                        "properties": {
                            "goal_next_week": {"type": "string"},
                            "goal_next_four_week": {"type": "string"},
                            "goal_next_twelve_week": {"type": "string"},
                        },
                        "required": ["goal_next_week", "goal_next_four_week", "goal_next_twelve_week"]
                    }
                },
                "required": [
                    "steps", "primary_goals", "secondary_goals", "objectives", "timeframe_analysis", "goals_split"
                ]
            }
        }

        # Call the LLM using the defined function schema
        result = self.llm_client.call_llm(prompt, system_message, function_schema=function_schema)
        return result
    
    def _analyze_goals_schema(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses an LLM with Pydantic schema to analyze and structure client goals.
        
        :param standardized_profile: The standardized client profile.
        :return: Structured goal analysis as a Pydantic model.
        """
        personal_info = standardized_profile.get("personal_info", {})
        goals_data = standardized_profile.get("goals", {}).get("data", {})
        fitness_data = standardized_profile.get("fitness", {}).get("data", {})

        system_message = self.get_goal_analysis_system_message()
        
        prompt = (
            "Conduct a detailed Dr. Mike Israetel-style analysis of this client's fitness profile and goals. "
            "For each step in your analysis, document your reasoning process and conclusions.\n\n"
            f"CLIENT PROFILE:\n{json.dumps(personal_info)}\n\n"
            f"CLIENT GOALS:\n{json.dumps(goals_data)}\n\n"
            f"CLIENT FITNESS DATA:\n{json.dumps(fitness_data)}\n\n"
            "Your analysis must include specific volume recommendations, periodization structures, "
            "and realistic timeline expectations based on Dr. Israetel's scientific principles. "
            "Be explicit about how each recommendation connects to the physiological adaptations needed. "
            "Return your analysis as a properly structured JSON conforming to the Goal model schema."
        )
        
        # Call the LLM using the Pydantic model as schema
        result = self.llm_client.call_llm(prompt, system_message, schema=Goal)
        return result
    