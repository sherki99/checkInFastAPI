


from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import re
from datetime import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv




"""   Training History & Background Analysis
   * Training age evaluation
   * Previous volume tolerance
   * Exercise technique proficiency
   * Past injury patterns
   * Response to different training styles Outputs: Experience level, volume tolerance ranges, exercise selection constraints  
        """



# Load environment variables and set up the API client
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
OPENAI_MODEL = "gpt-4o-mini"


async def call_llm(system_message: str, prompt: str) -> str:
    """
    Helper function to call the LLM with a system message and a prompt.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content.strip()




class ExperienceLevel(Enum):
    BEGINNER = "beginner"
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"

class TrainingStyle(Enum):
    BODYBUILDING = "bodybuilding"
    POWERLIFTING = "powerlifting"
    OLYMPIC = "olympic"
    CROSSFIT = "crossfit"
    CALISTHENICS = "calisthenics"
    GENERAL_FITNESS = "general_fitness"

class ExerciseTechniqueLevel(Enum):
    NEEDS_COACHING = "needs_coaching"
    BASIC_COMPETENCY = "basic_competency"
    PROFICIENT = "proficient"
    ADVANCED = "advanced"
    MASTERY = "mastery"

@dataclass
class VolumeToleranceProfile:
    weekly_sets_upper: Tuple[int, int]  # min, max
    weekly_sets_lower: Tuple[int, int]
    intensity_tolerance: float  # 1-10 scale
    frequency_tolerance: int  # sessions per week
    session_length_tolerance: int  # minutes

@dataclass
class ExerciseProficiency:
    compound_movements: Dict[str, ExerciseTechniqueLevel]
    isolation_movements: Dict[str, ExerciseTechniqueLevel]
    preferred_variations: List[str]
    problematic_movements: List[str]
    technical_notes: List[str]

@dataclass
class InjuryHistory:
    past_injuries: List[Dict[str, str]]  # type, location, severity, status
    current_limitations: List[str]
    rehabilitation_status: Dict[str, str]
    preventive_measures: List[str]

@dataclass
class TrainingResponse:
    volume_response: Dict[str, float]  # muscle group to response rate
    intensity_response: Dict[str, float]
    frequency_response: Dict[str, float]
    recovery_pattern: Dict[str, int]  # exercise type to recovery days

@dataclass
class TrainingHistoryResults:
    # Primary Analysis
    experience_level: ExperienceLevel
    training_age: float  # years
    training_consistency: float  # 1-10 scale
    preferred_styles: List[TrainingStyle]
    
    # Volume Analysis
    volume_tolerance: VolumeToleranceProfile
    
    # Technical Proficiency
    exercise_proficiency: ExerciseProficiency
    
    # Health & Safety
    injury_history: InjuryHistory
    
    # Response Patterns
    training_response: TrainingResponse
    
    # Constraints & Recommendations
    exercise_constraints: List[str]
    recommended_training_styles: List[TrainingStyle]
    volume_recommendations: Dict[str, range]




class TrainingHistoryAnalysis:
    def __init__(self):
        self.system_message = """
        You are Dr. Mike Israetel analyzing a client's training history with extreme precision.
        Provide a comprehensive analysis covering all training background factors.
        
        FORMAT YOUR RESPONSE EXACTLY AS SHOWN:

        PRIMARY ANALYSIS:
        ================
        EXPERIENCE_LEVEL: [one of: BEGINNER, NOVICE, INTERMEDIATE, ADVANCED, ELITE]
        TRAINING_AGE: [number - years]
        TRAINING_CONSISTENCY: [number 1-10]
        PREFERRED_STYLES:
        [style1]
        [style2]
        
        VOLUME_TOLERANCE:
        ================
        WEEKLY_SETS_UPPER: [min-max]
        WEEKLY_SETS_LOWER: [min-max]
        INTENSITY_TOLERANCE: [number 1-10]
        FREQUENCY_TOLERANCE: [sessions per week]
        SESSION_LENGTH_TOLERANCE: [minutes]
        
        EXERCISE_PROFICIENCY:
        ===================
        COMPOUND_MOVEMENTS:
        [movement1]: [one of: NEEDS_COACHING, BASIC_COMPETENCY, PROFICIENT, ADVANCED, MASTERY]
        [movement2]: [level]
        
        ISOLATION_MOVEMENTS:
        [movement1]: [level]
        [movement2]: [level]
        
        PREFERRED_VARIATIONS:
        [variation1]
        [variation2]
        
        PROBLEMATIC_MOVEMENTS:
        [movement1]
        [movement2]
        
        TECHNICAL_NOTES:
        [note1]
        [note2]
        
        INJURY_HISTORY:
        ==============
        PAST_INJURIES:
        [injury1]: [details]
        [injury2]: [details]
        
        CURRENT_LIMITATIONS:
        [limitation1]
        [limitation2]
        
        REHABILITATION_STATUS:
        [condition1]: [status]
        [condition2]: [status]
        
        PREVENTIVE_MEASURES:
        [measure1]
        [measure2]
        
        TRAINING_RESPONSE:
        ================
        VOLUME_RESPONSE:
        [muscle_group1]: [rate 1-10]
        [muscle_group2]: [rate 1-10]
        
        INTENSITY_RESPONSE:
        [muscle_group1]: [rate 1-10]
        [muscle_group2]: [rate 1-10]
        
        FREQUENCY_RESPONSE:
        [muscle_group1]: [rate 1-10]
        [muscle_group2]: [rate 1-10]
        
        RECOVERY_PATTERN:
        [exercise_type1]: [days]
        [exercise_type2]: [days]
        
        CONSTRAINTS_AND_RECOMMENDATIONS:
        ==============================
        EXERCISE_CONSTRAINTS:
        [constraint1]
        [constraint2]
        
        RECOMMENDED_STYLES:
        [style1]
        [style2]
        
        VOLUME_RECOMMENDATIONS:
        [muscle_group1]: [min-max sets]
        [muscle_group2]: [min-max sets]
        
        ANALYSIS_NOTES:
        [Your detailed analysis notes here]
        """

    def _safe_float(self, value: str, default: float = 0.0) -> float:
        try:
            clean_value = re.sub(r'[^0-9.-]', '', value)
            return float(clean_value)
        except (ValueError, TypeError):
            return default

    def _extract_section(self, text: str, section_name: str) -> List[str]:
        pattern = f"{section_name}:(.*?)(?=\n\n|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return [line.strip() for line in match.group(1).strip().split('\n') if line.strip()]
        return []

    def _parse_key_value_section(self, text: str, section_name: str) -> Dict[str, str]:
        lines = self._extract_section(text, section_name)
        result = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result

    def _parse_range(self, range_str: str) -> Tuple[int, int]:
        try:
            clean_str = range_str.replace('[', '').replace(']', '')
            min_val, max_val = map(int, clean_str.split('-'))
            return (min_val, max_val)
        except:
            return (0, 0)

    def _parse_training_history_output(self, output: str) -> TrainingHistoryResults:
        try:
            # Parse primary analysis
            experience_level_str = self._extract_section(output, "EXPERIENCE_LEVEL")[0].lower()
            experience_level = ExperienceLevel(experience_level_str)
            training_age = self._safe_float(self._extract_section(output, "TRAINING_AGE")[0])
            training_consistency = self._safe_float(self._extract_section(output, "TRAINING_CONSISTENCY")[0])
            preferred_styles = [TrainingStyle(style.lower()) for style in self._extract_section(output, "PREFERRED_STYLES")]

            # Parse volume tolerance
            volume_tolerance = VolumeToleranceProfile(
                weekly_sets_upper=self._parse_range(self._parse_key_value_section(output, "VOLUME_TOLERANCE").get("WEEKLY_SETS_UPPER", "0-0")),
                weekly_sets_lower=self._parse_range(self._parse_key_value_section(output, "VOLUME_TOLERANCE").get("WEEKLY_SETS_LOWER", "0-0")),
                intensity_tolerance=self._safe_float(self._parse_key_value_section(output, "VOLUME_TOLERANCE").get("INTENSITY_TOLERANCE", "5")),
                frequency_tolerance=int(self._safe_float(self._parse_key_value_section(output, "VOLUME_TOLERANCE").get("FREQUENCY_TOLERANCE", "3"))),
                session_length_tolerance=int(self._safe_float(self._parse_key_value_section(output, "VOLUME_TOLERANCE").get("SESSION_LENGTH_TOLERANCE", "60")))
            )

            # Parse exercise proficiency
            exercise_proficiency = ExerciseProficiency(
                compound_movements={k: ExerciseTechniqueLevel(v.lower()) for k, v in self._parse_key_value_section(output, "COMPOUND_MOVEMENTS").items()},
                isolation_movements={k: ExerciseTechniqueLevel(v.lower()) for k, v in self._parse_key_value_section(output, "ISOLATION_MOVEMENTS").items()},
                preferred_variations=self._extract_section(output, "PREFERRED_VARIATIONS"),
                problematic_movements=self._extract_section(output, "PROBLEMATIC_MOVEMENTS"),
                technical_notes=self._extract_section(output, "TECHNICAL_NOTES")
            )

            # Parse injury history
            injury_history = InjuryHistory(
                past_injuries=[{"type": k, "details": v} for k, v in self._parse_key_value_section(output, "PAST_INJURIES").items()],
                current_limitations=self._extract_section(output, "CURRENT_LIMITATIONS"),
                rehabilitation_status=self._parse_key_value_section(output, "REHABILITATION_STATUS"),
                preventive_measures=self._extract_section(output, "PREVENTIVE_MEASURES")
            )

            # Parse training response
            training_response = TrainingResponse(
                volume_response={k: self._safe_float(v) for k, v in self._parse_key_value_section(output, "VOLUME_RESPONSE").items()},
                intensity_response={k: self._safe_float(v) for k, v in self._parse_key_value_section(output, "INTENSITY_RESPONSE").items()},
                frequency_response={k: self._safe_float(v) for k, v in self._parse_key_value_section(output, "FREQUENCY_RESPONSE").items()},
                recovery_pattern={k: int(self._safe_float(v)) for k, v in self._parse_key_value_section(output, "RECOVERY_PATTERN").items()}
            )

            # Parse constraints and recommendations
            volume_recommendations = {}
            for item in self._parse_key_value_section(output, "VOLUME_RECOMMENDATIONS").items():
                volume_recommendations[item[0]] = range(*self._parse_range(item[1]))

            return TrainingHistoryResults(
                experience_level=experience_level,
                training_age=training_age,
                training_consistency=training_consistency,
                preferred_styles=preferred_styles,
                volume_tolerance=volume_tolerance,
                exercise_proficiency=exercise_proficiency,
                injury_history=injury_history,
                training_response=training_response,
                exercise_constraints=self._extract_section(output, "EXERCISE_CONSTRAINTS"),
                recommended_training_styles=[TrainingStyle(style.lower()) for style in self._extract_section(output, "RECOMMENDED_STYLES")],
                volume_recommendations=volume_recommendations
            )

        except Exception as e:
            print(f"Error parsing training history: {str(e)}")
            return self._create_default_results()

    def _create_default_results(self) -> TrainingHistoryResults:
        """Create default results when parsing fails"""
        return TrainingHistoryResults(
            experience_level=ExperienceLevel.BEGINNER,
            training_age=0.0,
            training_consistency=5.0,
            preferred_styles=[TrainingStyle.GENERAL_FITNESS],
            volume_tolerance=VolumeToleranceProfile((0, 0), (0, 0), 5.0, 3, 60),
            exercise_proficiency=ExerciseProficiency(
                {}, {}, [], [], []
            ),
            injury_history=InjuryHistory([], [], {}, []),
            training_response=TrainingResponse({}, {}, {}, {}),
            exercise_constraints=[],
            recommended_training_styles=[TrainingStyle.GENERAL_FITNESS],
            volume_recommendations={}
        )

    async def analyze(self, training_history: Dict[str, Any]) -> TrainingHistoryResults:
        client_profiel_str = "\n".join(f"{k.capitalize()}: {v}" for k, v in training_history.items())
        
        prompt = f"""
        Analyze this client's training history and provide specific parameters:

        CLIENT PROFILE:
        ================
        {client_profiel_str}

        Using Dr. Mike Israetel's methodology, provide a complete analysis following EXACTLY 
        the format specified. Include all required parameters with appropriate numerical values.
        """
        
        analysis_output = await call_llm(self.system_message, prompt)
        return self._parse_training_history_output(analysis_output)