from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import re
import os
from openai import OpenAI
from dotenv import load_dotenv



# Load environment variables and set up the API client
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
OPENAI_MODEL = "gpt-4o-mini"


# here to imoorve to have more value to use is love to imrpove funciution which has more value, to 



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



class BodyType(Enum):
    ECTOMORPH = "ectomorph"
    MESOMORPH = "mesomorph"
    ENDOMORPH = "endomorph"
    ECTO_MESO = "ecto-mesomorph"
    ENDO_MESO = "endo-mesomorph"

@dataclass
class MuscleMassDistribution:
    upper_body: float  # Ratio of upper body muscle mass
    lower_body: float  # Ratio of lower body muscle mass
    core: float       # Ratio of core muscle mass
    
@dataclass
class BodyStructure:
    shoulder_hip_ratio: float
    waist_hip_ratio: float
    limb_torso_ratio: float

@dataclass
class BodyAnalysisResults:
    body_fat_percentage: float
    lean_mass_index: float
    body_type: BodyType
    muscle_mass_distribution: MuscleMassDistribution
    structure: BodyStructure
    genetic_potential_score: float  # 1-10 scale
    recovery_capacity_score: float  # 1-10 scale
    injury_risk_areas: List[str]
    recommended_volume_tolerance: Dict[str, int]  # e.g., {"upper": 20, "lower": 16} sets per week
    



# the only left here is to follwo a cerrtian proced to determine all of this value thta is it I need to thing If I want to edxtrast the infiiuton an duse mroe  or iuse fiuniton to determin these numenriclaa value in imorve finxiton there two way to do that 

class BodyAnalysis:
    def __init__(self):
        self.system_message = """
        You are Dr. Mike Israetel analyzing body measurements with extreme precision.
        Your task is to extract specific numerical parameters and classifications.
        
        YOU MUST FORMAT YOUR RESPONSE EXACTLY AS SHOWN BELOW:

        BODY_FAT_PERCENTAGE: [number between 3-40]
        LEAN_MASS_INDEX: [number between 15-35]
        BODY_TYPE: [one of: ECTOMORPH, MESOMORPH, ENDOMORPH, ECTO-MESOMORPH, ENDO-MESOMORPH]
        
        MUSCLE_MASS_DISTRIBUTION:
        UPPER_BODY: [number between 0-1]
        LOWER_BODY: [number between 0-1]
        CORE: [number between 0-1]
        
        BODY_STRUCTURE:
        SHOULDER_HIP_RATIO: [number between 0.8-2.0]
        WAIST_HIP_RATIO: [number between 0.6-1.2]
        LIMB_TORSO_RATIO: [number between 0.8-1.5]
        
        GENETIC_POTENTIAL_SCORE: [number between 1-10]
        RECOVERY_CAPACITY_SCORE: [number between 1-10]
        
        INJURY_RISK_AREAS:
        [area1]
        [area2]
        [area3]
        
        VOLUME_TOLERANCE:
        UPPER_BODY: [number between 10-30]
        LOWER_BODY: [number between 10-30]
        CORE: [number between 10-20]
        
        ANALYSIS_NOTES:
        [Your detailed analysis notes here]

        IMPORTANT: Use EXACTLY this format. Do not add extra text, explanations, or deviate from this structure.
        Numbers should be plain numbers without units or extra text.
        """

    def _safe_float(self, value: str, default: float = 0.0) -> float:
        """Safely convert string to float, handling various formats."""
        try:
            # Remove any non-numeric characters except decimal points and minus signs
            clean_value = re.sub(r'[^0-9.-]', '', value)
            return float(clean_value)
        except (ValueError, TypeError):
            return default

    def _safe_int(self, value: str, default: int = 0) -> int:
        """Safely convert string to integer, handling various formats."""
        try:
            # Remove any non-numeric characters except minus signs
            clean_value = re.sub(r'[^0-9-]', '', value)
            return int(clean_value)
        except (ValueError, TypeError):
            return default

    def _extract_section(self, text: str, section_name: str) -> List[str]:
        """Extract a section and its contents from the text."""
        pattern = f"{section_name}:(.*?)(?=\n\n|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return [line.strip() for line in match.group(1).strip().split('\n') if line.strip()]
        return []

    def _extract_single_value(self, text: str, key: str, default: str = "") -> str:
        """Extract a single value from a key-value pair in the text."""
        pattern = f"{key}:[\s]*([^\n]+)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else default

    def _parse_analysis_output(self, output: str) -> BodyAnalysisResults:
        """Parse the LLM output into structured data with improved error handling."""
        try:
            # Extract basic measurements
            body_fat = self._safe_float(self._extract_single_value(output, "BODY_FAT_PERCENTAGE"), 15.0)
            lean_mass = self._safe_float(self._extract_single_value(output, "LEAN_MASS_INDEX"), 20.0)
            
            # Extract body type
            body_type_str = self._extract_single_value(output, "BODY_TYPE", "MESOMORPH").lower()
            try:
                body_type = BodyType(body_type_str)
            except ValueError:
                body_type = BodyType.MESOMORPH

            # Extract muscle mass distribution
            mmd_lines = self._extract_section(output, "MUSCLE_MASS_DISTRIBUTION")
            mmd = {}
            for line in mmd_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    mmd[key.strip().lower()] = self._safe_float(value, 0.33)
            
            muscle_dist = MuscleMassDistribution(
                upper_body=mmd.get('upper_body', 0.33),
                lower_body=mmd.get('lower_body', 0.33),
                core=mmd.get('core', 0.34)
            )

            # Extract body structure
            struct_lines = self._extract_section(output, "BODY_STRUCTURE")
            struct = {}
            for line in struct_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    struct[key.strip().lower()] = self._safe_float(value, 1.0)
            
            structure = BodyStructure(
                shoulder_hip_ratio=struct.get('shoulder_hip_ratio', 1.0),
                waist_hip_ratio=struct.get('waist_hip_ratio', 0.8),
                limb_torso_ratio=struct.get('limb_torso_ratio', 1.0)
            )

            # Extract scores
            genetic_score = self._safe_float(self._extract_single_value(output, "GENETIC_POTENTIAL_SCORE"), 5.0)
            recovery_score = self._safe_float(self._extract_single_value(output, "RECOVERY_CAPACITY_SCORE"), 5.0)

            # Extract injury risk areas
            injury_areas = self._extract_section(output, "INJURY_RISK_AREAS")
            if not injury_areas:
                injury_areas = ["None identified"]

            # Extract volume tolerance
            volume_lines = self._extract_section(output, "VOLUME_TOLERANCE")
            volume_tolerance = {}
            for line in volume_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    volume_tolerance[key.strip().lower()] = self._safe_int(value, 15)

            if not volume_tolerance:
                volume_tolerance = {
                    "upper_body": 15,
                    "lower_body": 15,
                    "core": 10
                }

            return BodyAnalysisResults(
                body_fat_percentage=body_fat,
                lean_mass_index=lean_mass,
                body_type=body_type,
                muscle_mass_distribution=muscle_dist,
                structure=structure,
                genetic_potential_score=genetic_score,
                recovery_capacity_score=recovery_score,
                injury_risk_areas=injury_areas,
                recommended_volume_tolerance=volume_tolerance
            )
        except Exception as e:
            print(f"Error parsing analysis output: {str(e)}")
            # Return default values if parsing fails
            return BodyAnalysisResults(
                body_fat_percentage=15.0,
                lean_mass_index=20.0,
                body_type=BodyType.MESOMORPH,
                muscle_mass_distribution=MuscleMassDistribution(0.33, 0.33, 0.34),
                structure=BodyStructure(1.0, 0.8, 1.0),
                genetic_potential_score=5.0,
                recovery_capacity_score=5.0,
                injury_risk_areas=["None identified"],
                recommended_volume_tolerance={"upper_body": 15, "lower_body": 15, "core": 10}
            )

    async def analyze(self, measurements: Dict[str, float]) -> BodyAnalysisResults:
        """
        Analyzes client measurements and returns structured results.
        
        Args:
            measurements: Dictionary of body measurements
        
        Returns:
            BodyAnalysisResults object containing parsed analysis parameters
        """
        measurements_str = "\n".join(f"{k.capitalize()}: {v}" for k, v in measurements.items())
        
        prompt = f"""
        Analyze these client measurements and provide specific parameters:

        CLIENT MEASUREMENTS:
        ==================
        {measurements_str}

        Using Dr. Mike Israetel's methodology, provide a complete analysis following EXACTLY 
        the format specified. Include all required parameters with appropriate numerical values.
        
        Remember:
        - All numerical values must be plain numbers without units
        - Follow the exact format specified
        - Include all required sections
        - Use only the specified categories for body type
        """
        
        analysis_output = await call_llm(self.system_message, prompt)
        return self._parse_analysis_output(analysis_output)
    