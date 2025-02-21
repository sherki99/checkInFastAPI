import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ExerciseFrequency(BaseModel):
    """Represents recommended training frequency for a specific muscle group."""
    muscle_group: str = Field(..., description="Name of the muscle group (e.g., 'Chest', 'Back', 'Legs')")
    sessions_per_week: int = Field(..., description="Recommended number of weekly training sessions for this muscle group")
    recovery_requirement: str = Field(..., description="Assessment of recovery needs based on volume tolerance and training age")
    volume_per_session: str = Field(..., description="Recommended volume guideline per session (e.g., '12-15 working sets')")

class WeeklySchedule(BaseModel):
    """Detailed day-by-day training schedule recommendation."""
    monday: str = Field(..., description="Monday's training focus and key muscle groups")
    tuesday: str = Field(..., description="Tuesday's training focus and key muscle groups")
    wednesday: str = Field(..., description="Wednesday's training focus and key muscle groups")
    thursday: str = Field(..., description="Thursday's training focus and key muscle groups")
    friday: str = Field(..., description="Friday's training focus and key muscle groups")
    saturday: str = Field(..., description="Saturday's training focus and key muscle groups")
    sunday: str = Field(..., description="Sunday's training focus and key muscle groups")

class SplitJustification(BaseModel):
    """Reasoning for the selected training split based on scientific principles."""
    scientific_basis: str = Field(..., description="Scientific principles supporting this split structure")
    volume_distribution: str = Field(..., description="How training volume is distributed to optimize recovery and growth")
    frequency_rationale: str = Field(..., description="Explanation of why specific frequency was selected")
    individual_adaptations: str = Field(..., description="How this split accounts for individual recovery capacity and goals")

class TrainingSplit(BaseModel):
    """Complete training split recommendation with justification and schedule."""
    split_name: str = Field(..., description="Name of the recommended training split (e.g., 'Upper/Lower', 'Push/Pull/Legs')")
    split_type: str = Field(..., description="Category of split (e.g., 'Body Part', 'Movement Pattern', 'Upper/Lower')")
    training_days_per_week: int = Field(..., description="Total number of training days per week")
    muscle_group_frequencies: List[ExerciseFrequency] = Field(..., description="Breakdown of training frequency by muscle group")
    weekly_schedule: WeeklySchedule = Field(..., description="Day-by-day training schedule")
    justification: SplitJustification = Field(..., description="Scientific reasoning behind the recommended split")
    special_considerations: List[str] = Field(..., description="Additional factors that influenced the recommendation")

class TrainingSplitDecisionNode:
    """
    Determines the optimal training split based on client data and analysis from previous modules.
    
    This class uses an LLM-driven decision process to generate a scientifically-grounded 
    training split recommendation that aligns with the client's goals, recovery capacity, 
    and individual constraints.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the TrainingSplitDecisionNode with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self, 
        profile_analysis: Dict[str, Any], 
        goal_analysis: Dict[str, Any], 
        body_analysis: Dict[str, Any], 
        history_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal training split.
        
        This method integrates data from multiple analysis modules to determine
        the most appropriate training split for the client, considering:
        - Primary and secondary goals
        - Recovery capacity and training experience
        - Time availability and schedule constraints
        - Body composition and muscle development priorities
        
        Args:
            profile_analysis: Client demographics and metrics analysis
            goal_analysis: Client goals and objectives analysis
            body_analysis: Body composition and measurement analysis
            history_analysis: Training history and experience analysis
            
        Returns:
            A dictionary containing the structured training split recommendation
        """
        try:
            # Process using the function-calling approach
            function_result = self._determine_training_split_function(
                profile_analysis, goal_analysis, body_analysis, history_analysis
            )
            
            # Process using the schema-based approach
            schema_result = self._determine_training_split_schema(
                profile_analysis, goal_analysis, body_analysis, history_analysis
            )
            
            # Combine results from both approaches
            return {
                "split_recommendation_function": function_result,
                "split_recommendation_schema": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining training split: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in training split decision-making.
        
        The system message establishes the context and criteria for determining
        an optimal training split according to scientific principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a training program design specialist with expertise in exercise science, "
            "following the methodologies of Dr. Mike Israetel, Dr. Eric Helms, and Dr. Brad Schoenfeld. "
            "Your task is to determine the optimal training split for a client based on their goals, "
            "recovery capacity, training history, and body composition analysis.\n\n"
            
            "Apply these scientific principles when designing training splits:\n"
            "1. **Frequency Optimization**: Each muscle group should be trained 2-3 times per week for optimal protein synthesis.\n"
            "2. **Recovery Management**: Volume must be distributed to allow 48-72 hours between sessions for the same muscle group.\n"
            "3. **Volume Landmarks**: Consider MEV (Minimum Effective Volume), MAV (Maximum Adaptive Volume), and MRV (Maximum Recoverable Volume).\n"
            "4. **Individual Variability**: Account for training age, recovery capacity, and muscle fiber type predominance.\n"
            "5. **Goal Specificity**: Split design should reflect primary goals (hypertrophy, strength, endurance).\n"
            "6. **Time Efficiency**: Account for the client's available training time and frequency preferences.\n"
            "7. **Overlap Management**: Consider systemic fatigue from compound movements and overlapping muscle groups.\n\n"
            
            "For hypertrophy goals, prioritize sufficient volume distribution (10-20 sets per muscle group per week).\n"
            "For strength goals, prioritize fresh neural drive and sufficient frequency for skill practice.\n"
            "For general fitness, balance training stimulus across all major movement patterns.\n\n"
            
            "Your recommendation must include scientific justification, frequency guidelines, and a detailed weekly schedule."
        )
    
    def _determine_training_split_function(
        self, 
        profile_analysis: Dict[str, Any], 
        goal_analysis: Dict[str, Any], 
        body_analysis: Dict[str, Any], 
        history_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine training split using LLM function calling.
        
        Args:
            profile_analysis: Client demographics and metrics analysis
            goal_analysis: Client goals and objectives analysis  
            body_analysis: Body composition and measurement analysis
            history_analysis: Training history and experience analysis
            
        Returns:
            Structured training split recommendation as a dictionary
        """
        # Extract relevant data for prompt construction
        goals = goal_analysis.get("goal_analysis_function", {})
        primary_goals = goals.get("primary_goals", [])
        training_experience = history_analysis.get("experience_level", "Intermediate")
        training_frequency = history_analysis.get("current_frequency", "Unknown")
        recovery_capacity = history_analysis.get("recovery_capacity", "Average")
        
        # Construct prompt with comprehensive client data
        prompt = (
            "Determine the optimal training split for this client based on their analysis data. "
            "Your response should include split type, frequency, and detailed schedule.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Training experience: {training_experience}\n"
            f"- Current training frequency: {training_frequency}\n"
            f"- Recovery capacity: {recovery_capacity}\n"
            f"- Primary goals: {', '.join(primary_goals)}\n\n"
            
            f"FULL GOAL ANALYSIS:\n{self._format_dict(goals)}\n\n"
            f"BODY COMPOSITION ANALYSIS:\n{self._format_dict(body_analysis)}\n\n"
            f"TRAINING HISTORY ANALYSIS:\n{self._format_dict(history_analysis)}\n\n"
            
            "Based on this data, determine the optimal training split that will maximize results "
            "while respecting recovery capacity. Consider frequency optimization, volume distribution, "
            "overlap management, and goal specificity.\n\n"
            
            "Provide a complete split recommendation including:\n"
            "1. Split name and type\n"
            "2. Training days per week\n"
            "3. Frequency recommendations for each muscle group\n"
            "4. Day-by-day schedule\n"
            "5. Scientific justification for your recommendation\n"
            "6. Any special considerations for this client"
        )
        
        function_schema = {
            "name": "determine_training_split",
            "description": "Determine the optimal training split based on client data and scientific principles",
            "parameters": {
                "type": "object",
                "properties": {
                    "split_name": {"type": "string"},
                    "split_type": {"type": "string"},
                    "training_days_per_week": {"type": "integer"},
                    "muscle_group_frequencies": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "muscle_group": {"type": "string"},
                                "sessions_per_week": {"type": "integer"},
                                "recovery_requirement": {"type": "string"},
                                "volume_per_session": {"type": "string"}
                            },
                            "required": ["muscle_group", "sessions_per_week", "recovery_requirement", "volume_per_session"]
                        }
                    },
                    "weekly_schedule": {
                        "type": "object",
                        "properties": {
                            "monday": {"type": "string"},
                            "tuesday": {"type": "string"},
                            "wednesday": {"type": "string"},
                            "thursday": {"type": "string"},
                            "friday": {"type": "string"},
                            "saturday": {"type": "string"},
                            "sunday": {"type": "string"}
                        },
                        "required": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                    },
                    "justification": {
                        "type": "object",
                        "properties": {
                            "scientific_basis": {"type": "string"},
                            "volume_distribution": {"type": "string"},
                            "frequency_rationale": {"type": "string"},
                            "individual_adaptations": {"type": "string"}
                        },
                        "required": ["scientific_basis", "volume_distribution", "frequency_rationale", "individual_adaptations"]
                    },
                    "special_considerations": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": [
                    "split_name", "split_type", "training_days_per_week", 
                    "muscle_group_frequencies", "weekly_schedule", 
                    "justification", "special_considerations"
                ]
            }
        }
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, function_schema=function_schema)
        return result
    
    def _determine_training_split_schema(
        self, 
        profile_analysis: Dict[str, Any], 
        goal_analysis: Dict[str, Any], 
        body_analysis: Dict[str, Any], 
        history_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine training split using Pydantic schema validation.
        
        Args:
            profile_analysis: Client demographics and metrics analysis
            goal_analysis: Client goals and objectives analysis
            body_analysis: Body composition and measurement analysis
            history_analysis: Training history and experience analysis
            
        Returns:
            Structured training split recommendation as a Pydantic model
        """
        # Extract relevant data for prompt construction
        goals = goal_analysis.get("goal_analysis_schema", {})
        primary_goals = goals.get("primary_goals", [])
        training_experience = history_analysis.get("experience_level", "Intermediate")
        training_frequency = history_analysis.get("current_frequency", "Unknown")
        recovery_capacity = history_analysis.get("recovery_capacity", "Average")
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Design the optimal science-based training split for this client. Apply Dr. Mike Israetel's "
            "volume landmarks and frequency principles to create a sustainable and effective program.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Training experience: {training_experience}\n"
            f"- Current training frequency: {training_frequency}\n"
            f"- Recovery capacity: {recovery_capacity}\n"
            f"- Primary goals: {', '.join(primary_goals)}\n\n"
            
            f"FULL GOAL ANALYSIS:\n{self._format_dict(goals)}\n\n"
            f"BODY COMPOSITION ANALYSIS:\n{self._format_dict(body_analysis)}\n\n"
            f"TRAINING HISTORY ANALYSIS:\n{self._format_dict(history_analysis)}\n\n"
            
            "Your training split recommendation should prioritize these factors:\n"
            "1. Optimal frequency for the client's primary muscle groups (2-3x/week for hypertrophy)\n"
            "2. Appropriate volume distribution based on recovery capacity\n"
            "3. Strategic exercise selection and ordering within each session\n"
            "4. Rest periods that support the primary training goal\n"
            "5. Periodization structure that allows for progressive overload\n\n"
            
            "Create a complete weekly training schedule with detailed justification for your choices. "
            "Explain how this split optimizes the scientific principles of muscular adaptation while "
            "addressing this client's specific needs and constraints."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=TrainingSplit)
        return result
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """
        Format a dictionary as a readable string for inclusion in prompts.
        
        Args:
            data: Dictionary to format
            
        Returns:
            Formatted string representation
        """
        try:
            return json.dumps(data, indent=2)
        except:
            # Fallback for non-serializable objects
            return str(data)