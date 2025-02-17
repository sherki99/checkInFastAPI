from typing import Dict, Any
import os
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

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

class RPAnalysisSystem:
    def __init__(self, system_message: str = None):
        self.system_message = system_message or (
            "You are Dr. Mike Israetel, a renowned expert in exercise science and bodybuilding. "
            "Analyze client data and provide a comprehensive report."
        )
        # For now, we only implement the analysis portion.
        self.body_analyzer = BodyAnalysis()
        self.info_analyzer = ClientAnalysisSystem()
        self.report_generator = ClientReportGenerator()

    async def analyze_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs the analysis in three steps:
        1. Analyze body measurements.
        2. Analyze the rest of the client information. - this is the deeper part need now I need ot extrat information where it decide the main objetcive for example thr trianign it goes throu aprocess for cretin pran nned to hjave all the to reahc the ytpe of workjtu for hwo many day why decide the current workut plan based always on dr mik eistrel fo nnturo calcualtion need to perform to perform all the claution of macorsa and base don th ejot day decid eth emeal timing the tyeo fiform they tyeo fo meal decide ehwt tyeo of meal lieks whei for both for wokrut meal they will be sned as ku partmeent to the repero t
        # it will be send to correpsite cti to meal which ten it will base donthsipoamrent and based ont he gneral report parmeetr which qare th e reusl of deep analysis of th e
        3. Generate a comprehensive report. 
        """
        # Step 1: Analyze body measurements
        measurements = client_data.get('measurements', {})
        body_analysis = await self.body_analyzer.analyze(measurements)

        # Step 2: Analyze client information (excluding measurements)
        client_info = {k: v for k, v in client_data.items() if k != 'measurements'}
        info_analysis = await self.info_analyzer.analyze_client(client_info, body_analysis)

        # Step 3: Generate overall report
        report = await self.report_generator.generate_report(body_analysis, info_analysis)

        return {
            "report": report,
            "body_analysis": body_analysis,
            "client_info_analysis": info_analysis,
        }





from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import re

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
    


    
class ClientAnalysisSystem:
    """
    Advanced client analysis system that performs deep analysis of client data
    using Dr. Mike Israetel's methodology and scientific principles.
    """
    
    def __init__(self):
        self.system_message = """
        You are Dr. Mike Israetel performing an in-depth scientific analysis of client data.
        Your expertise in exercise science, biomechanics, and program design should guide 
        a thorough analysis using the following structured approach:

        1. TRAINING FOUNDATION ANALYSIS
        Volume Tolerance Indicators:
        - Analyze recovery resources vs training history
        - Evaluate work capacity from current activity
        - Consider age/experience/lifestyle factors
        - Project adaptation potential
        
        Exercise Selection Analysis:
        - Evaluate movement patterns and preferences
        - Analyze injury history implications
        - Consider biomechanical factors
        - Assess technical proficiency indicators
        
        2. PHYSIOLOGICAL PROFILING
        Recovery Profile:
        - Sleep quantity and quality analysis
        - Stress load evaluation
        - Hormone health indicators
        - Age-related recovery factors
        
        Adaptation Potential:
        - Training age consideration
        - Genetic response indicators
        - Previous progress patterns
        - Limiting factor identification
        
        3. PSYCHOLOGICAL ASSESSMENT
        Motivation Analysis:
        - Goal alignment evaluation
        - Adherence pattern prediction
        - Psychological barrier identification
        - Support system assessment
        
        Behavioral Patterns:
        - Schedule consistency analysis
        - Habit formation potential
        - Stress management patterns
        - Lifestyle factor integration
        
        4. NUTRITION AND RECOVERY INTEGRATION
        Meal Timing Analysis:
        - Work schedule integration
        - Energy availability patterns
        - Nutrient timing opportunities
        - Supplement timing optimization
        
        Recovery Window Analysis:
        - Sleep schedule evaluation
        - Stress management periods
        - Recovery activity timing
        - Workload distribution patterns
        
        5. PROGRAM DESIGN IMPLICATIONS
        Volume Distribution:
        - Weekly loading patterns
        - Session distribution options
        - Exercise sequencing requirements
        - Recovery period placement
        
        Progressive Overload Strategy:
        - Load progression potential
        - Volume increase tolerance
        - Technical progression needs
        - Deload timing requirements

        For each analysis component:
        1. Start with baseline data evaluation
        2. Apply scientific principles
        3. Consider individual variation
        4. Project likely outcomes
        5. Identify key success factors
        6. Flag potential obstacles
        7. Determine monitoring needs
        """

    async def analyze_client(self, client_data: dict, body_analysis: str = None) -> str:
        """
        Performs deep analysis of client data to inform program design.
        
        Args:
            client_data: Comprehensive client information
            body_analysis: Previous body analysis results
        """
       # formatted_data = self._prepare_data(client_data)
        
        prompt = f"""
        Conduct a thorough scientific analysis of this client's data:

        CLIENT PROFILE:
        ===============
        {client_data}

        {f'BODY ANALYSIS CONTEXT:\n{body_analysis}\n' if body_analysis else ''}

        Follow this analytical framework:

        1. Training History Analysis:
        - What does the training background indicate about work capacity?
        - How has previous training influenced adaptation potential?
        - What technical proficiency level is indicated?
        - What movement pattern history emerges?
        
        2. Recovery Capacity Evaluation:
        - How do lifestyle factors affect recovery?
        - What is the projected recovery window between sessions?
        - How do stress patterns influence training capacity?
        - What recovery optimization opportunities exist?
        
        3. Training Response Projection:
        - What adaptation rate is likely based on history?
        - How will current factors influence progress?
        - What are the primary limiting factors?
        - What volume tolerance is indicated?
        
        4. Adherence Pattern Analysis:
        - What schedule consistency is likely?
        - How will lifestyle factors affect compliance?
        - What behavioral patterns need consideration?
        - What support systems are available?
        
        5. Program Design Framework:
        - What session structure is optimal?
        - How should volume be distributed?
        - What exercise selection principles apply?
        - How should progression be managed?

        For each analysis point:
        1. State "Initial Data:" - relevant information
        2. Provide "Scientific Reasoning:" - principle application
        3. List "Individual Factors:" - personal considerations
        4. Project "Expected Outcomes:" - likely results
        5. Identify "Key Constraints:" - limiting factors
        6. Suggest "Monitoring Strategy:" - progress tracking
        
        Cross-reference factors between sections to build a complete profile.
        Flag any areas needing additional data collection.
        Prioritize findings based on impact on program success.
        """
        
        return await call_llm(self.system_message, prompt)



    """async def _call_llm(self, prompt: str) -> str:

        Calls the language model with the formatted prompt and system message.
        Placeholder for actual implementation.
    
        # Implementation would go here
        pass"""

class ClientReportGenerator:
    """
    Comprehensive client analysis and report generation system following Dr. Mike Israetel's 
    methodology. Integrates with BodyAnalysis results and provides detailed training recommendations.
    """

    def __init__(self):
        self.system_message = """
        You are Dr. Mike Israetel (RP Strength), conducting an expert analysis of client data for program design.
        Your analysis should follow this structured chain-of-thought process to extract maximum value from each data point:

        1. FOUNDATIONAL ANALYSIS
        Client Profile Integration:
        - Analyze age-related training implications
        - Consider gender-specific factors
        - Evaluate height/weight relationships
        - Cross-reference with body measurements
        
        2. TRAINING POTENTIAL ANALYSIS
        Experience Evaluation:
        - Decode training age implications
        - Analyze current program structure
        - Evaluate exercise selection patterns
        - Assess volume tolerance indicators
        
        Recovery Capacity Assessment:
        - Analyze sleep quality and quantity
        - Evaluate nutrition timing and quality
        - Consider stress and lifestyle impact
        - Assess supplementation strategy
        
        3. PROGRAM DESIGN CONSTRAINTS
        Time & Equipment:
        - Optimize for available training frequency
        - Structure around session duration limits
        - Plan for equipment accessibility
        - Account for schedule restrictions
        
        Individual Factors:
        - Consider exercise preferences
        - Account for problematic movements
        - Plan around lifestyle constraints
        - Adapt to stress patterns
        
        4. NUTRITION & RECOVERY FRAMEWORK
        Meal Structure:
        - Analyze meal timing opportunities
        - Evaluate nutritional preferences
        - Consider supplement integration
        - Plan hydration strategy
        
        Recovery Optimization:
        - Account for lifestyle stressors
        - Plan around work demands
        - Consider athletic background
        - Evaluate recovery limitations
        
        5. MOTIVATION & ADHERENCE
        Goal Analysis:
        - Evaluate goal realism
        - Consider timeline expectations
        - Assess motivation factors
        - Plan for potential barriers
        
        For each analysis component:
        1. State explicit reasoning process
        2. Connect data points to form insights
        3. Identify critical limiting factors
        4. Project likely adaptation rates
        5. Flag potential compliance issues
        
        Maintain focus on:
        - Scientific evidence-based reasoning
        - Practical implementation requirements
        - Long-term sustainability factors
        - Individual optimization opportunities
        """

    async def generate_report(self, client_data: dict, body_analysis_results: str = None) -> str:
        """
        Generates comprehensive client report with detailed analysis and recommendations.
        
        Args:
            client_data: Dictionary containing client information sections
            body_analysis_results: Optional string containing previous body analysis results
        """
   
        
        prompt = f"""
        Analyze this client data using advanced chain-of-thought reasoning:

        CLIENT INFORMATION:
        ==================
        {client_data}

        {f'PREVIOUS BODY ANALYSIS:\n{body_analysis_results}\n' if body_analysis_results else ''}

        Conduct analysis in the following sequence:

        1. Initial Client Assessment:
        - How do personal factors affect training approach?
        - What experience level considerations emerge?
        - How do lifestyle factors impact program design?
        - What are the critical limiting factors?

        2. Training Framework Analysis:
        - What volume tolerance is indicated?
        - How should frequency be structured?
        - What exercise selection principles apply?
        - How should progression be managed?

        3. Recovery Capacity Evaluation:
        - What recovery resources are available?
        - How should nutrition be structured?
        - What supplement strategy is appropriate?
        - How should rest periods be managed?

        4. Program Design Parameters:
        - What session structure is optimal?
        - How should volume be distributed?
        - What exercise modifications are needed?
        - How should deloads be programmed?

        5. Implementation Strategy:
        - What adherence challenges are likely?
        - How should progress be tracked?
        - What education is needed?
        - What monitoring systems are required?

        For each section:
        1. Begin with "Analysis Process:" explaining your reasoning
        2. List "Key Findings:" with specific insights
        3. Provide "Implementation Guidelines:" for practical application
        4. Note "Risk Factors:" for potential issues
        5. Include "Monitoring Points:" for progress tracking

        Import note: If some lackign or not following certain refuse to generte the report by saying information sens is not correct
        Conclude with a prioritized list of recommendations and critical success factors.
        """
        
        return await call_llm(self.system_message, prompt)





# the part regaridn analsys is the esdeentil part 
# maybe undertn hwo implent hsoty chat for each client to stay the same
# in client analsis report need to be deifne everthing for the plan choose type type of bnutron claorue intake 
# I want to do the same 








