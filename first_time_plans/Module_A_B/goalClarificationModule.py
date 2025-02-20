import json
import logging
from typing import Dict, Any, Optional, List
from first_time_plans.call_llm_class import BaseLLM
from pydantic import BaseModel, Field

# Set up basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class StepReasoningForPrimaryGoals(BaseModel):
    explanation: str
    output: str

class Objective(BaseModel):
    objective: str
    metric: str
    priority: str = Field(..., description="Priority level: high, medium, or low")

class TimeframeAnalysis(BaseModel):
    realistic_assessment: str
    recommended_timeline: str

class GoalSplit(BaseModel):
    goal_next_week: str
    goal_next_four_week: str
    goal_next_twelve_week: str

class Goal(BaseModel):
    steps: List[StepReasoningForPrimaryGoals] = Field(default_factory=list)
    primary_goals: List[str]
    secondary_goals: List[str]
    objectives: List[Objective] = Field(default_factory=list)
    timeframe_analysis: TimeframeAnalysis
    goals_split: Optional[GoalSplit] = None

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

    def _analyze_goals(self, standardized_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses an LLM function call to analyze and structure client goals.
        
        :param standardized_profile: The standardized client profile.
        :return: Structured goal analysis as a dictionary.
        """
        # Extract relevant data from the standardized profile
        personal_info = standardized_profile.get("personal_info", {})
        goals_data = standardized_profile.get("goals", {}).get("data", {})

        system_message = (
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
            " - 'primary_goals': A list of the client's most important fitness goals.\n"
            " - 'secondary_goals': A list of additional goals that are relevant but lower priority.\n"
            " - 'objectives': A list of structured objectives, each containing:\n"
            "      - 'objective': The specific goal (e.g., 'Increase bench press strength').\n"
            "      - 'metric': The way progress will be tracked (e.g., 'Increase by 10kg in 8 weeks').\n"
            "      - 'priority': Whether it is high, medium, or low priority.\n"
            " - 'timeframe_analysis': A structured assessment including realistic expectations and recommended timelines."
      
        )
        prompt = (
            "Analyze the following client goals and personal information. Separate primary goals from secondary goals, "
            "and provide measurable objectives along with a realistic timeframe.\n"
            f"Client Information: {json.dumps(personal_info)}\n"
            f"Goal Information: {json.dumps(goals_data)}\n"
            "Return your analysis as a JSON with the following keys: "
            "'primary_goals' (array of strings), "
            "'secondary_goals' (array of strings), "
            "'objectives' (array of objects with keys: 'objective', 'metric', 'priority'), "
            "and 'timeframe_analysis' (object with keys: 'realistic_assessment' and 'recommended_timeline')."
    
        )

        # Define the function schema that the LLM should adhere to:
        function_schema = {
            "name": "analyze_fitness_goals",
            "description": "Analyze fitness goals and return structured recommendations based on client data.",
            "parameters": {
                "type": "object",
                "properties": {
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
                        }
                    }
                },
                "required": [
                    "primary_goals", "secondary_goals", "objectives", "timeframe_analysis"
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

        system_message = (
            "You are a fitness goal specialist trained in evidence-based principles, including the methodologies of Dr. Mike Israetel. "
            "Your task is to analyze client goals and structure them according to the principles of periodization, hypertrophy, and strength training. "
            "Follow a step-by-step approach to identify primary goals, secondary goals, measurable objectives, and realistic timeframes.\n\n"
            "For each step in your analysis, provide:\n"
            "1. An explanation of your reasoning\n"
            "2. The output of that step\n\n"
            "Consider the following when structuring goals:\n"
            "1. **Prioritization**: Identify whether a goal is hypertrophy-focused, strength-focused, endurance-based, or general fitness.\n"
            "2. **Measurable Objectives**: Ensure goals follow SMART principles (Specific, Measurable, Achievable, Relevant, Time-bound).\n"
            "3. **Timeframes & Adaptation**: Provide realistic timeframes for achieving results based on progressive overload and recovery science.\n"
            "4. **Barriers & Solutions**: Identify expected obstacles and suggest evidence-based modifications.\n"
            "5. **Training Adjustments**: Consider training volume, intensity, and frequency based on the client's goals.\n"
            "Deliver a JSON response with the following structure:\n"
            " - 'primary_goals': A list of the client's most important fitness goals.\n"
            " - 'secondary_goals': A list of additional goals that are relevant but lower priority.\n"
            " - 'objectives': A list of structured objectives, each containing:\n"
            "      - 'objective': The specific goal (e.g., 'Increase bench press strength').\n"
            "      - 'metric': The way progress will be tracked (e.g., 'Increase by 10kg in 8 weeks').\n"
            "      - 'priority': Whether it is high, medium, or low priority.\n"
            " - 'timeframe_analysis': A structured assessment including realistic expectations and recommended timelines."
  
        )
        
        prompt = (
            "Analyze the following client goals and personal information step by step. "
            "For each step in your analysis, provide your reasoning and the output.\n"
            f"Client Information: {json.dumps(personal_info)}\n"
            f"Goal Information: {json.dumps(goals_data)}\n"
            "First, identify primary and secondary goals. Then, define measurable objectives. "
            "Finally, provide a realistic timeframe analysis and weekly/monthly goals"
             "Return your analysis as a JSON with the following keys: "
            "'primary_goals' (array of strings), "
            "'secondary_goals' (array of strings), "
            "'objectives' (array of objects with keys: 'objective', 'metric', 'priority'), "
            "and 'timeframe_analysis' (object with keys: 'realistic_assessment' and 'recommended_timeline')."
         )
        

        # Call the LLM using the Pydantic model as schema
        result = self.llm_client.call_llm(prompt, system_message, schema=Goal)
        return result
    

    # this is possibile to imporve the prompt 
    def get_goal_analysis_system_message(self):
            return (
                "You are a fitness goal specialist following Dr. Mike Israetel's evidence-based methodologies. "
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
                " - 'primary_goals': A list of the client's most important fitness goals.\n"
                " - 'secondary_goals': A list of additional goals that are relevant but lower priority.\n"
                " - 'objectives': A list of structured objectives, each containing:\n"
                "      - 'objective': The specific goal (e.g., 'Increase bench press strength').\n"
                "      - 'metric': The way progress will be tracked (e.g., 'Increase by 10kg in 8 weeks').\n"
                "      - 'priority': Whether it is high, medium, or low priority.\n"
                " - 'timeframe_analysis': A structured assessment including realistic expectations and recommended timelines."
            )