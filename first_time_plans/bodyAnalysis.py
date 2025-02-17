from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
from openai import OpenAI
from dotenv import load_dotenv
import os 

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
    
class BodyAnalysis:
    def __init__(self):
        self.system_message = """
        You are Dr. Mike Israetel analyzing body measurements with extreme precision.
        Your task is to extract specific numerical parameters and classifications that will be used
        for program design. Format your response in a structured way that can be parsed into
        the following parameters:

        REQUIRED OUTPUT FORMAT:
        ======================
        BODY_FAT_PERCENTAGE: [number]
        LEAN_MASS_INDEX: [number]
        BODY_TYPE: [ectomorph|mesomorph|endomorph|ecto-mesomorph|endo-mesomorph]
        
        MUSCLE_MASS_DISTRIBUTION:
        - UPPER_BODY: [0-1 ratio]
        - LOWER_BODY: [0-1 ratio]
        - CORE: [0-1 ratio]
        
        BODY_STRUCTURE:
        - SHOULDER_HIP_RATIO: [number]
        - WAIST_HIP_RATIO: [number]
        - LIMB_TORSO_RATIO: [number]
        
        GENETIC_POTENTIAL_SCORE: [1-10]
        RECOVERY_CAPACITY_SCORE: [1-10]
        
        INJURY_RISK_AREAS:
        - [area1]
        - [area2]
        ...
        
        VOLUME_TOLERANCE:
        - UPPER_BODY: [sets per week]
        - LOWER_BODY: [sets per week]
        - CORE: [sets per week]
        
        ANALYSIS_NOTES:
        [Additional analysis notes here]
        """

    def _parse_analysis_output(self, output: str) -> BodyAnalysisResults:
        """Parse the LLM output into structured data."""
        lines = output.split('\n')
        data = {}
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.endswith(':'):
                current_section = line[:-1]
                data[current_section] = []
                continue
                
            if current_section:
                if line.startswith('- '):
                    data[current_section].append(line[2:])
                else:
                    data[current_section] = line

        # Extract body fat percentage
        bf_pct = float(data.get('BODY_FAT_PERCENTAGE', 0))
        
        # Extract muscle mass distribution
        mmd_data = {item.split(':')[0].lower(): float(item.split(':')[1]) 
                   for item in data.get('MUSCLE_MASS_DISTRIBUTION', [])}
        muscle_dist = MuscleMassDistribution(
            upper_body=mmd_data.get('upper_body', 0),
            lower_body=mmd_data.get('lower_body', 0),
            core=mmd_data.get('core', 0)
        )
        
        # Extract body structure
        struct_data = {item.split(':')[0].lower(): float(item.split(':')[1]) 
                      for item in data.get('BODY_STRUCTURE', [])}
        structure = BodyStructure(
            shoulder_hip_ratio=struct_data.get('shoulder_hip_ratio', 0),
            waist_hip_ratio=struct_data.get('waist_hip_ratio', 0),
            limb_torso_ratio=struct_data.get('limb_torso_ratio', 0)
        )
        
        # Extract volume tolerance
        volume_tolerance = {
            item.split(':')[0].lower(): int(item.split(':')[1])
            for item in data.get('VOLUME_TOLERANCE', [])
        }
        
        return BodyAnalysisResults(
            body_fat_percentage=bf_pct,
            lean_mass_index=float(data.get('LEAN_MASS_INDEX', 0)),
            body_type=BodyType(data.get('BODY_TYPE', 'mesomorph').lower()),
            muscle_mass_distribution=muscle_dist,
            structure=structure,
            genetic_potential_score=float(data.get('GENETIC_POTENTIAL_SCORE', 5)),
            recovery_capacity_score=float(data.get('RECOVERY_CAPACITY_SCORE', 5)),
            injury_risk_areas=data.get('INJURY_RISK_AREAS', []),
            recommended_volume_tolerance=volume_tolerance
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

        Using Dr. Mike Israetel's methodology, analyze these measurements and provide:

        1. Body Composition Analysis:
        - Calculate body fat percentage using appropriate formula
        - Determine lean mass index
        - Classify body type based on structural indicators
        
        2. Structural Analysis:
        - Calculate key body ratios
        - Analyze muscle mass distribution
        - Evaluate limb-to-torso proportions
        
        3. Training Potential:
        - Assess genetic potential for muscle gain
        - Evaluate recovery capacity
        - Determine volume tolerance by body part
        
        4. Risk Assessment:
        - Identify potential injury risk areas
        - Flag structural imbalances
        - Note biomechanical considerations

        Provide ALL parameters in the exact format specified in the system message.
        Each number should be justified by measurement analysis and calculations.
        """
        
        analysis_output = await call_llm(self.system_message, prompt)
        return self._parse_analysis_output(analysis_output)