from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
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
    FAST_TWITCH_DOMINANT = "fast-twitch-dominant"
    SLOW_TWITCH_DOMINANT = "slow-twitch-dominant"
    BALANCED = "balanced"

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
    joint_sizes: Dict[str, float]  # e.g., {"wrist": 17.2, "ankle": 22.1}

@dataclass
class PosturalAnalysis:
    anterior_pelvic_tilt: float  # Degree of tilt (0-10)
    shoulder_protraction: float  # Degree of protraction (0-10)
    spinal_alignment: float     # Overall alignment score (0-10)
    asymmetries: List[str]     # List of identified asymmetries

@dataclass
class MobilityAssessment:
    hip_mobility: float        # 0-10 scale
    shoulder_mobility: float   # 0-10 scale
    ankle_mobility: float      # 0-10 scale
    spine_mobility: float      # 0-10 scale
    limiting_factors: List[str]

@dataclass
class BiomechanicalProfile:
    leverage_points: Dict[str, float]  # e.g., {"bench": 0.8, "squat": 1.2}
    movement_efficiency: Dict[str, float]  # Efficiency scores for key movements
    mechanical_advantages: List[str]
    limitations: List[str]

@dataclass
class BodyAnalysisResults:
    # Primary Analysis Components
    body_fat_percentage: float
    lean_mass_index: float
    body_type: BodyType
    muscle_mass_distribution: MuscleMassDistribution
    structure: BodyStructure
    fiber_type_assessment: FiberType
    
    # Secondary Analysis Components
    postural_analysis: PosturalAnalysis
    mobility_assessment: MobilityAssessment
    biomechanical_profile: BiomechanicalProfile
    
    # Performance Metrics
    genetic_potential_score: float  # 1-10 scale
    recovery_capacity_score: float  # 1-10 scale
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
        
        self._initialize_parsers()

    def _initialize_parsers(self):
        """Initialize all the specific section parsers"""
        # Add parser initialization methods here
        pass

    def _parse_primary_analysis(self, text: str) -> Tuple[float, float, BodyType, FiberType]:
        """Parse the primary analysis section"""
        body_fat = self._safe_float(self._extract_single_value(text, "BODY_FAT_PERCENTAGE"), 15.0)
        lean_mass = self._safe_float(self._extract_single_value(text, "LEAN_MASS_INDEX"), 20.0)
        
        body_type_str = self._extract_single_value(text, "BODY_TYPE", "MESOMORPH").lower()
        fiber_type_str = self._extract_single_value(text, "FIBER_TYPE", "BALANCED").lower()
        
        try:
            body_type = BodyType(body_type_str)
            fiber_type = FiberType(fiber_type_str.replace("-", "_"))
        except ValueError:
            body_type = BodyType.MESOMORPH
            fiber_type = FiberType.BALANCED
            
        return body_fat, lean_mass, body_type, fiber_type

    def _parse_secondary_analysis(self, text: str) -> Tuple[PosturalAnalysis, MobilityAssessment, BiomechanicalProfile]:
        """Parse the secondary analysis section"""
        # Parse postural analysis
        posture_section = self._extract_section(text, "POSTURAL_ANALYSIS")
        postural = PosturalAnalysis(
            anterior_pelvic_tilt=self._safe_float(self._extract_single_value('\n'.join(posture_section), "ANTERIOR_PELVIC_TILT"), 5.0),
            shoulder_protraction=self._safe_float(self._extract_single_value('\n'.join(posture_section), "SHOULDER_PROTRACTION"), 5.0),
            spinal_alignment=self._safe_float(self._extract_single_value('\n'.join(posture_section), "SPINAL_ALIGNMENT"), 5.0),
            asymmetries=self._extract_list(text, "ASYMMETRIES")
        )
        
        # Parse mobility assessment
        mobility_section = self._extract_section(text, "MOBILITY_ASSESSMENT")
        mobility = MobilityAssessment(
            hip_mobility=self._safe_float(self._extract_single_value('\n'.join(mobility_section), "HIP_MOBILITY"), 5.0),
            shoulder_mobility=self._safe_float(self._extract_single_value('\n'.join(mobility_section), "SHOULDER_MOBILITY"), 5.0),
            ankle_mobility=self._safe_float(self._extract_single_value('\n'.join(mobility_section), "ANKLE_MOBILITY"), 5.0),
            spine_mobility=self._safe_float(self._extract_single_value('\n'.join(mobility_section), "SPINE_MOBILITY"), 5.0),
            limiting_factors=self._extract_list(text, "LIMITING_FACTORS")
        )
        
        # Parse biomechanical profile
        biomech_section = self._extract_section(text, "BIOMECHANICAL_PROFILE")
        leverage_points = {}
        for movement in ["BENCH", "SQUAT", "DEADLIFT"]:
            leverage_points[movement.lower()] = self._safe_float(
                self._extract_single_value('\n'.join(biomech_section), movement), 1.0
            )
        
        biomech = BiomechanicalProfile(
            leverage_points=leverage_points,
            movement_efficiency={k: v * 0.8 for k, v in leverage_points.items()},  # Simplified efficiency calculation
            mechanical_advantages=self._extract_list(text, "MECHANICAL_ADVANTAGES"),
            limitations=self._extract_list(text, "LIMITATIONS")
        )
        
        return posture, mobility, biomech

    def _safe_float(self, value: str, default: float = 0.0) -> float:
        """Safely convert string to float, handling various formats."""
        try:
            clean_value = re.sub(r'[^0-9.-]', '', value)
            return float(clean_value)
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

    def _extract_list(self, text: str, section_name: str) -> List[str]:
        """Extract a list of items from a section."""
        section = self._extract_section(text, section_name)
        return [item for item in section if not ':' in item] or ["None identified"]

    async def analyze(self, measurements: Dict[str, float]) -> BodyAnalysisResults:
        """
        Performs comprehensive body analysis including primary and secondary factors.
        
        Args:
            measurements: Dictionary of body measurements
            
        Returns:
            BodyAnalysisResults object containing complete analysis
        """
        measurements_str = "\n".join(f"{k.capitalize()}: {v}" for k, v in measurements.items())
        
        prompt = f"""
        Analyze these client measurements for both primary and secondary factors:

        CLIENT MEASUREMENTS:
        ==================
        {measurements_str}

        Provide a complete analysis following the specified format.
        Consider:
        - Body composition and structural implications
        - Muscle fiber type indicators
        - Postural and mobility factors
        - Biomechanical advantages and limitations
        """
        
        analysis_output = await call_llm(self.system_message, prompt)
        
        try:
            # Parse primary analysis
            body_fat, lean_mass, body_type, fiber_type = self._parse_primary_analysis(analysis_output)
            
            # Parse muscle mass distribution
            mmd_section = self._extract_section(analysis_output, "MUSCLE_MASS_DISTRIBUTION")
            muscle_dist = MuscleMassDistribution(
                upper_body=self._safe_float(self._extract_single_value('\n'.join(mmd_section), "UPPER_BODY"), 0.33),
                lower_body=self._safe_float(self._extract_single_value('\n'.join(mmd_section), "LOWER_BODY"), 0.33),
                core=self._safe_float(self._extract_single_value('\n'.join(mmd_section), "CORE"), 0.34)
            )
            
            # Parse body structure
            struct_section = self._extract_section(analysis_output, "BODY_STRUCTURE")
            structure = BodyStructure(
                shoulder_hip_ratio=self._safe_float(self._extract_single_value('\n'.join(struct_section), "SHOULDER_HIP_RATIO"), 1.0),
                waist_hip_ratio=self._safe_float(self._extract_single_value('\n'.join(struct_section), "WAIST_HIP_RATIO"), 0.8),
                limb_torso_ratio=self._safe_float(self._extract_single_value('\n'.join(struct_section), "LIMB_TORSO_RATIO"), 1.0),
                joint_sizes={
                    "wrist": self._safe_float(self._extract_single_value('\n'.join(struct_section), "WRIST"), 17.0),
                    "ankle": self._safe_float(self._extract_single_value('\n'.join(struct_section), "ANKLE"), 22.0),
                    "knee": self._safe_float(self._extract_single_value('\n'.join(struct_section), "KNEE"), 35.0),
                    "elbow": self._safe_float(self._extract_single_value('\n'.join(struct_section), "ELBOW"), 25.0)
                }
            )
            
            # Parse secondary analysis
            posture, mobility, biomech = self._parse_secondary_analysis(analysis_output)
            
            # Parse performance metrics
            genetic_score = self._safe_float(self._extract_single_value(analysis_output, "GENETIC_POTENTIAL_SCORE"), 5.0)
            recovery_score = self._safe_float(self._extract_single_value(analysis_output, "RECOVERY_CAPACITY_SCORE"), 5.0)
            injury_areas = self._extract_list(analysis_output, "INJURY_RISK_AREAS")
        
        except(TypeError): 








from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import re
import os
from openai import OpenAI
from dotenv import load_dotenv
import math

# Load environment variables and set up the API client
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
OPENAI_MODEL = "gpt-4o-mini"

class BodyAnalysisCalculator:
    def calculate_body_fat_percentage(self, measurements: Dict[str, float]) -> float:
        """
        Calculate body fat percentage using Jackson-Pollock method
        """
        if 'waist' in measurements and 'neck' in measurements and 'height' in measurements:
            # Male calculation (simplified)
            waist = measurements['waist']
            neck = measurements['neck']
            height = measurements['height']
            bf = 495 / (1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)) - 450
            return max(3, min(40, bf))
        return 15.0  # Default fallback

    def calculate_lean_mass_index(self, measurements: Dict[str, float]) -> float:
        """
        Calculate lean mass index using height and weight
        """
        if 'weight' in measurements and 'height' in measurements and 'body_fat_percentage' in measurements:
            weight = measurements['weight']
            height = measurements['height']
            bf = measurements['body_fat_percentage']
            lean_mass = weight * (1 - bf/100)
            lmi = lean_mass / (height * height) * 100
            return max(15, min(35, lmi))
        return 20.0  # Default fallback

    def determine_body_type(self, measurements: Dict[str, float]) -> str:
        """
        Determine body type based on measurements
        """
        if 'wrist' in measurements and 'ankle' in measurements and 'shoulder' in measurements:
            frame_score = (measurements['wrist'] + measurements['ankle']) / measurements['shoulder']
            if frame_score < 0.35:
                return "ECTOMORPH"
            elif frame_score > 0.45:
                return "ENDOMORPH"
            else:
                return "MESOMORPH"
        return "MESOMORPH"  # Default fallback

    def calculate_muscle_distribution(self, measurements: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate muscle mass distribution ratios
        """
        # Calculate upper body ratio
        upper_body = 0.33
        if all(k in measurements for k in ['chest', 'shoulders', 'arms']):
            upper_sum = measurements['chest'] + measurements['shoulders'] + measurements['arms']
            upper_body = min(0.45, max(0.25, upper_sum / (sum(measurements.values()))))

        # Calculate lower body ratio
        lower_body = 0.33
        if all(k in measurements for k in ['thighs', 'calves', 'hips']):
            lower_sum = measurements['thighs'] + measurements['calves'] + measurements['hips']
            lower_body = min(0.45, max(0.25, lower_sum / (sum(measurements.values()))))

        # Calculate core ratio (remaining percentage)
        core = 1 - upper_body - lower_body

        return {
            'upper_body': upper_body,
            'lower_body': lower_body,
            'core': core
        }

    def calculate_body_structure(self, measurements: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate body structure ratios
        """
        structure = {
            'shoulder_hip_ratio': 1.0,
            'waist_hip_ratio': 0.8,
            'limb_torso_ratio': 1.0
        }

        if all(k in measurements for k in ['shoulders', 'hips']):
            structure['shoulder_hip_ratio'] = min(2.0, max(0.8, measurements['shoulders'] / measurements['hips']))

        if all(k in measurements for k in ['waist', 'hips']):
            structure['waist_hip_ratio'] = min(1.2, max(0.6, measurements['waist'] / measurements['hips']))

        if all(k in measurements for k in ['arm_length', 'leg_length', 'torso_length']):
            limb_length = measurements['arm_length'] + measurements['leg_length']
            structure['limb_torso_ratio'] = min(1.5, max(0.8, limb_length / (2 * measurements['torso_length'])))

        return structure

    def calculate_genetic_potential(self, measurements: Dict[str, float]) -> float:
        """
        Calculate genetic potential score
        """
        score = 5.0  # Default middle score
        
        if all(k in measurements for k in ['wrist', 'ankle', 'height']):
            # Frame size relative to height
            frame_score = (measurements['wrist'] + measurements['ankle']) / measurements['height']
            frame_points = min(3, max(1, frame_score * 100))
            
            # Symmetry score
            symmetry_points = 2.0
            if 'shoulders' in measurements and 'hips' in measurements:
                ratio = measurements['shoulders'] / measurements['hips']
                symmetry_points = min(3, max(1, ratio * 2))
                
            # Muscle building potential
            muscle_points = 2.0
            if 'testosterone' in measurements:
                muscle_points = min(4, max(1, measurements['testosterone'] / 250))
                
            score = frame_points + symmetry_points + muscle_points
            
        return min(10, max(1, score))

    def calculate_recovery_capacity(self, measurements: Dict[str, float]) -> float:
        """
        Calculate recovery capacity score
        """
        score = 5.0  # Default middle score
        
        factors = {
            'sleep_quality': 2.0,
            'stress_level': 2.0,
            'nutrition_score': 2.0,
            'age_factor': 2.0,
            'hormonal_health': 2.0
        }
        
        if 'age' in measurements:
            age = measurements['age']
            factors['age_factor'] = min(3, max(1, (40 - age) / 10))
            
        if 'sleep_hours' in measurements:
            factors['sleep_quality'] = min(3, max(1, measurements['sleep_hours'] / 3))
            
        if 'cortisol' in measurements:
            factors['stress_level'] = min(3, max(1, 600 / measurements['cortisol']))
            
        score = sum(factors.values()) / 2
        return min(10, max(1, score))

    def identify_injury_risk_areas(self, measurements: Dict[str, float]) -> List[str]:
        """
        Identify potential injury risk areas
        """
        risk_areas = []
        
        # Check shoulder risk
        if 'shoulder_mobility' in measurements and measurements['shoulder_mobility'] < 0.7:
            risk_areas.append("Shoulders")
            
        # Check knee risk
        if 'knee_alignment' in measurements and abs(measurements['knee_alignment'] - 180) > 10:
            risk_areas.append("Knees")
            
        # Check lower back risk
        if 'anterior_pelvic_tilt' in measurements and measurements['anterior_pelvic_tilt'] > 15:
            risk_areas.append("Lower Back")
            
        return risk_areas if risk_areas else ["None identified"]

    def calculate_volume_tolerance(self, measurements: Dict[str, float]) -> Dict[str, int]:
        """
        Calculate recommended training volume tolerance
        """
        tolerance = {
            'upper_body': 15,
            'lower_body': 15,
            'core': 10
        }
        
        # Adjust based on recovery capacity
        recovery_score = self.calculate_recovery_capacity(measurements)
        base_multiplier = recovery_score / 5.0
        
        # Adjust based on muscle fiber type indicators
        if 'fast_twitch_ratio' in measurements:
            ft_ratio = measurements['fast_twitch_ratio']
            volume_modifier = 1.0 - (ft_ratio - 0.5)  # Higher fast-twitch = lower volume
            base_multiplier *= volume_modifier
        
        tolerance['upper_body'] = min(30, max(10, int(15 * base_multiplier)))
        tolerance['lower_body'] = min(30, max(10, int(15 * base_multiplier)))
        tolerance['core'] = min(20, max(10, int(10 * base_multiplier)))
        
        return tolerance

class BodyAnalysis:
    def __init__(self):
        self.calculator = BodyAnalysisCalculator()
        self.system_message = """
        You are Dr. Mike Israetel analyzing body measurements with extreme precision.
        Your task is to extract specific numerical parameters and classifications.
        
        YOU MUST FORMAT YOUR RESPONSE EXACTLY AS SHOWN BELOW:
        [... rest of the system message remains the same ...]
        """

    async def analyze(self, measurements: Dict[str, float]) -> BodyAnalysisResults:
        """
        Analyzes client measurements using calculated values instead of LLM
        """
        try:
            # Calculate all metrics using the calculator
            bf_percentage = self.calculator.calculate_body_fat_percentage(measurements)
            lean_mass = self.calculator.calculate_lean_mass_index(measurements)
            body_type = self.calculator.determine_body_type(measurements)
            muscle_dist = self.calculator.calculate_muscle_distribution(measurements)
            structure = self.calculator.calculate_body_structure(measurements)
            genetic_score = self.calculator.calculate_genetic_potential(measurements)
            recovery_score = self.calculator.calculate_recovery_capacity(measurements)
            injury_areas = self.calculator.identify_injury_risk_areas(measurements)
            volume_tolerance = self.calculator.calculate_volume_tolerance(measurements)

            # Create results object with calculated values
            return BodyAnalysisResults(
                body_fat_percentage=bf_percentage,
                lean_mass_index=lean_mass,
                body_type=BodyType(body_type.lower()),
                muscle_mass_distribution=MuscleMassDistribution(**muscle_dist),
                structure=BodyStructure(**structure),
                genetic_potential_score=genetic_score,
                recovery_capacity_score=recovery_score,
                injury_risk_areas=injury_areas,
                recommended_volume_tolerance=volume_tolerance
            )
            
        except Exception as e:
            print(f"Error in analysis calculations: {str(e)}")
            # Return default values if calculations fail
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