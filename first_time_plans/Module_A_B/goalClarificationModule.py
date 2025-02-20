import json
import logging
from typing import Dict, Any, Optional, List
from first_time_plans.call_llm_class import BaseLLM
from pydantic import BaseModel

# Set up basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class StepReasoningForPrimaryGoals(BaseModel):
    explanation: str
    output: str

class Goal(BaseModel): 
    steps: List[StepReasoningForPrimaryGoals]
    primary_goals: List[str]
    secondary_goals: List[str]




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
            return {"goal_analysis_function" : goal_analysis, "goal_analysis_schema" : goal_analysis_schema}
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
        #main_goals = goals_data.get("main_goals", "")  # Default to empty string if not found
        #motivation_level = goals_data.get("motivationLevel", "") 
        # expectedBarriers
        # timeToSeeChanges

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
                " - 'primary_goals': A list of the client’s most important fitness goals.\n"
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
                        "type":  "object", 
                        "properties":  {
                            "gaol_next_week" : {"type": "string"},
                            "goal_next_four_week" : {"type": "string"},
                            "goal_next_twelve_week" : {"type": "string"},
                        }
                    }
                },
                "required": [
                    "primary_goals", "secondary_goals", "objectives", "timeframe_analysis", "goal_split"
                ]
            }
        }

        # Call the LLM using the defined function schema
        result = self.llm_client.call_llm(prompt, system_message, function_schema=function_schema)
        return result
    

    def _analyze_goals_schema(self, standardized_profile :  Dict[str, Any]) -> Dict[str, Any]:

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
                " - 'primary_goals': A list of the client’s most important fitness goals.\n"
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



        result = self.llm_client.call_llm(prompt, system_message, schema=Goal)
        return result

