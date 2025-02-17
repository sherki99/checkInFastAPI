from typing import Dict, Any, List, Optional
from enum import Enum
import re
from dataclasses import dataclass
import os
from openai import OpenAI
from dotenv import load_dotenv
from first_time_plans.bodyAnalysis import BodyAnalysis

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


        # step 2: insted of analyze client I want to get body analsis paramters which are they main foucsu for n

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








