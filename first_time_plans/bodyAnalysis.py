from typing import Dict, Any, List, Optional
from enum import Enum
import re
from dataclasses import dataclass
import os
from openai import OpenAI
from dotenv import load_dotenv


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

class FiberType(Enum):
    FAST_TWITCH = "fast-twitch-dominant"
    SLOW_TWITCH = "slow-twitch-dominant"
    BALANCED = "balanced"

@dataclass
class MuscleMassDistribution:
    upper_body: float
    lower_body: float
    core: float

@dataclass
class BodyStructure:
    shoulder_hip_ratio: float
    waist_hip_ratio: float
    limb_torso_ratio: float
    joint_sizes: Dict[str, float]

@dataclass
class PosturalAnalysis:
    anterior_pelvic_tilt: float
    shoulder_protraction: float
    spinal_alignment: float
    asymmetries: List[str]

@dataclass
class MobilityAssessment:
    hip_mobility: float
    shoulder_mobility: float
    ankle_mobility: float
    spine_mobility: float
    limiting_factors: List[str]

@dataclass
class BiomechanicalProfile:
    leverage_points: Dict[str, float]
    mechanical_advantages: List[str]
    limitations: List[str]

@dataclass
class BodyAnalysisResults:
    # Primary Analysis
    body_fat_percentage: float
    lean_mass_index: float
    body_type: BodyType
    fiber_type: FiberType
    muscle_mass_distribution: MuscleMassDistribution
    structure: BodyStructure
    
    # Secondary Analysis
    postural_analysis: PosturalAnalysis
    mobility_assessment: MobilityAssessment
    biomechanical_profile: BiomechanicalProfile
    
    # Performance Metrics
    genetic_potential_score: float
    recovery_capacity_score: float
    injury_risk_areas: List[str]
    recommended_volume_tolerance: Dict[str, int]

class BodyAnalysis:
    def __init__(self):
        self.system_message = """
        You are Dr. Mike Israetel performing an advanced body analysis with extreme precision.
        Provide a comprehensive analysis covering both primary and secondary factors.
        
        FORMAT YOUR RESPONSE EXACTLY AS SHOWN:

        PRIMARY ANALYSIS:
        ================
        BODY_FAT_PERCENTAGE: [number between 3-40]
        LEAN_MASS_INDEX: [number between 15-35]
        BODY_TYPE: [one of: ECTOMORPH, MESOMORPH, ENDOMORPH, ECTO-MESOMORPH, ENDO-MESOMORPH]
        FIBER_TYPE: [one of: FAST-TWITCH-DOMINANT, SLOW-TWITCH-DOMINANT, BALANCED]
        
        MUSCLE_MASS_DISTRIBUTION:
        UPPER_BODY: [number between 0-1]
        LOWER_BODY: [number between 0-1]
        CORE: [number between 0-1]
        
        BODY_STRUCTURE:
        SHOULDER_HIP_RATIO: [number between 0.8-2.0]
        WAIST_HIP_RATIO: [number between 0.6-1.2]
        LIMB_TORSO_RATIO: [number between 0.8-1.5]
        JOINT_SIZES:
        WRIST: [number]
        ANKLE: [number]
        KNEE: [number]
        ELBOW: [number]
        
        SECONDARY ANALYSIS:
        ==================
        POSTURAL_ANALYSIS:
        ANTERIOR_PELVIC_TILT: [number between 0-10]
        SHOULDER_PROTRACTION: [number between 0-10]
        SPINAL_ALIGNMENT: [number between 0-10]
        ASYMMETRIES:
        [asymmetry1]
        [asymmetry2]
        
        MOBILITY_ASSESSMENT:
        HIP_MOBILITY: [number between 0-10]
        SHOULDER_MOBILITY: [number between 0-10]
        ANKLE_MOBILITY: [number between 0-10]
        SPINE_MOBILITY: [number between 0-10]
        LIMITING_FACTORS:
        [factor1]
        [factor2]
        
        BIOMECHANICAL_PROFILE:
        LEVERAGE_POINTS:
        BENCH: [number between 0.5-1.5]
        SQUAT: [number between 0.5-1.5]
        DEADLIFT: [number between 0.5-1.5]
        
        MECHANICAL_ADVANTAGES:
        [advantage1]
        [advantage2]
        
        LIMITATIONS:
        [limitation1]
        [limitation2]
        
        PERFORMANCE_METRICS:
        GENETIC_POTENTIAL_SCORE: [number between 1-10]
        RECOVERY_CAPACITY_SCORE: [number between 1-10]
        
        INJURY_RISK_AREAS:
        [area1]
        [area2]
        
        VOLUME_TOLERANCE:
        UPPER_BODY: [number between 10-30]
        LOWER_BODY: [number between 10-30]
        CORE: [number between 10-20]
        
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

    def _extract_single_value(self, text: str, key: str, default: str = "") -> str:
        pattern = f"{key}:[\s]*([^\n]+)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else default

    def _parse_joint_sizes(self, text: str) -> Dict[str, float]:
        joint_lines = self._extract_section(text, "JOINT_SIZES")
        joint_sizes = {}
        for line in joint_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                joint_sizes[key.strip().lower()] = self._safe_float(value)
        return joint_sizes or {"wrist": 0.0, "ankle": 0.0, "knee": 0.0, "elbow": 0.0}

    def _parse_analysis_output(self, output: str) -> BodyAnalysisResults:
        try:
            # Parse primary analysis
            body_fat = self._safe_float(self._extract_single_value(output, "BODY_FAT_PERCENTAGE"), 15.0)
            lean_mass = self._safe_float(self._extract_single_value(output, "LEAN_MASS_INDEX"), 20.0)
            body_type_str = self._extract_single_value(output, "BODY_TYPE", "MESOMORPH").lower()
            fiber_type_str = self._extract_single_value(output, "FIBER_TYPE", "BALANCED").lower()
            
            try:
                body_type = BodyType(body_type_str)
                fiber_type = FiberType(fiber_type_str)
            except ValueError:
                body_type = BodyType.MESOMORPH
                fiber_type = FiberType.BALANCED

            # Parse muscle mass distribution
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

            # Parse body structure
            struct_lines = self._extract_section(output, "BODY_STRUCTURE")
            struct = {}
            for line in struct_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    struct[key.strip().lower()] = self._safe_float(value, 1.0)
            
            joint_sizes = self._parse_joint_sizes(output)
            
            structure = BodyStructure(
                shoulder_hip_ratio=struct.get('shoulder_hip_ratio', 1.0),
                waist_hip_ratio=struct.get('waist_hip_ratio', 0.8),
                limb_torso_ratio=struct.get('limb_torso_ratio', 1.0),
                joint_sizes=joint_sizes
            )

            # Parse postural analysis
            postural = PosturalAnalysis(
                anterior_pelvic_tilt=self._safe_float(self._extract_single_value(output, "ANTERIOR_PELVIC_TILT"), 5.0),
                shoulder_protraction=self._safe_float(self._extract_single_value(output, "SHOULDER_PROTRACTION"), 5.0),
                spinal_alignment=self._safe_float(self._extract_single_value(output, "SPINAL_ALIGNMENT"), 5.0),
                asymmetries=self._extract_section(output, "ASYMMETRIES") or ["None identified"]
            )

            # Parse mobility assessment
            mobility = MobilityAssessment(
                hip_mobility=self._safe_float(self._extract_single_value(output, "HIP_MOBILITY"), 5.0),
                shoulder_mobility=self._safe_float(self._extract_single_value(output, "SHOULDER_MOBILITY"), 5.0),
                ankle_mobility=self._safe_float(self._extract_single_value(output, "ANKLE_MOBILITY"), 5.0),
                spine_mobility=self._safe_float(self._extract_single_value(output, "SPINE_MOBILITY"), 5.0),
                limiting_factors=self._extract_section(output, "LIMITING_FACTORS") or ["None identified"]
            )

            # Parse biomechanical profile
            leverage_points = {}
            leverage_lines = self._extract_section(output, "LEVERAGE_POINTS")
            for line in leverage_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    leverage_points[key.strip().lower()] = self._safe_float(value, 1.0)

            biomechanical = BiomechanicalProfile(
                leverage_points=leverage_points or {"bench": 1.0, "squat": 1.0, "deadlift": 1.0},
                mechanical_advantages=self._extract_section(output, "MECHANICAL_ADVANTAGES") or ["None identified"],
                limitations=self._extract_section(output, "LIMITATIONS") or ["None identified"]
            )

            # Parse performance metrics
            genetic_score = self._safe_float(self._extract_single_value(output, "GENETIC_POTENTIAL_SCORE"), 5.0)
            recovery_score = self._safe_float(self._extract_single_value(output, "RECOVERY_CAPACITY_SCORE"), 5.0)
            injury_areas = self._extract_section(output, "INJURY_RISK_AREAS") or ["None identified"]

            # Parse volume tolerance
            volume_lines = self._extract_section(output, "VOLUME_TOLERANCE")
            volume_tolerance = {}
            for line in volume_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    volume_tolerance[key.strip().lower()] = int(self._safe_float(value, 15))

            if not volume_tolerance:
                volume_tolerance = {"upper_body": 15, "lower_body": 15, "core": 10}

            return BodyAnalysisResults(
                body_fat_percentage=body_fat,
                lean_mass_index=lean_mass,
                body_type=body_type,
                fiber_type=fiber_type,
                muscle_mass_distribution=muscle_dist,
                structure=structure,
                postural_analysis=postural,
                mobility_assessment=mobility,
                biomechanical_profile=biomechanical,
                genetic_potential_score=genetic_score,
                recovery_capacity_score=recovery_score,
                injury_risk_areas=injury_areas,
                recommended_volume_tolerance=volume_tolerance
            )
            
        except Exception as e:
            print(f"Error parsing analysis output: {str(e)}")
            return self._create_default_results()

    def _create_default_results(self) -> BodyAnalysisResults:
        """Create default results when parsing fails"""
        return BodyAnalysisResults(
            body_fat_percentage=15.0,
            lean_mass_index=20.0,
            body_type=BodyType.MESOMORPH,
            fiber_type=FiberType.BALANCED,
            muscle_mass_distribution=MuscleMassDistribution(0.33, 0.33, 0.34),
            structure=BodyStructure(1.0, 0.8, 1.0, {"wrist": 0.0, "ankle": 0.0, "knee": 0.0, "elbow": 0.0}),
            postural_analysis=PosturalAnalysis(5.0, 5.0, 5.0, ["None identified"]),
            mobility_assessment=MobilityAssessment(5.0, 5.0, 5.0, 5.0, ["None identified"]),
            biomechanical_profile=BiomechanicalProfile(
                {"bench": 1.0, "squat": 1.0, "deadlift": 1.0},
                ["None identified"],
                ["None identified"]
            ),
            genetic_potential_score=5.0,
            recovery_capacity_score=5.0,
            injury_risk_areas=["None identified"],
            recommended_volume_tolerance={"upper_body": 15, "lower_body": 15, "core": 10}
        )

    async def analyze(self, measurements: Dict[str, float]) -> BodyAnalysisResults:
        measurements_str = "\n".join(f"{k.capitalize()}: {v}" for k, v in measurements.items())
        
        prompt = f"""
        Analyze these client measurements and provide specific parameters:

        CLIENT MEASUREMENTS:
        ==================
        {measurements_str}

        Using Dr. Mike Israetel's methodology, provide a complete analysis following EXACTLY 
        the format specified. Include all required parameters with appropriate numerical values.
        """
        
        analysis_output = await call_llm(self.system_message, prompt)
        return self._parse_analysis_output(analysis_output)
    