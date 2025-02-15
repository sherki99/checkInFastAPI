from typing import Dict, Any
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
        2. Analyze the rest of the client information.
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

class BodyAnalysis:

    """
    Enhanced BodyAnalysis class implementing structured chain-of-thought prompting.
    
    The class uses a systematic approach to analyze body measurements by breaking down
    the thinking process into explicit steps and encouraging detailed reasoning at each stage.
    """
        
    def __init__(self):
        self.system_message = """
        You are Dr. Mike Israetel (RP Strength), a leading expert in evidence-based hypertrophy training and body composition analysis.
        As the first step in a comprehensive client analysis system, your role is to:

        1. COMPREHENSIVE MEASUREMENT ANALYSIS
        Primary Analysis:
        - Decode body composition implications from measurements
        - Estimate body fat percentage ranges based on measurement patterns
        - Identify muscle mass distribution and potential muscle fiber types
        - Analyze joint structures and mechanical advantage indicators
        
        Secondary Analysis:
        - Evaluate postural indicators from measurement relationships
        - Assess mobility/flexibility potential from joint measurements
        - Identify potential muscle imbalances or asymmetries
        - Determine genetic structural advantages/limitations
        
        2. PREDICTIVE ANALYSIS
        Training Response Indicators:
        - Likely response to different training stimuli
        - Potential for muscle gain in specific areas
        - Recovery capacity indicators
        - Exercise selection implications
        
        Risk Assessment:
        - Joint stress considerations
        - Potential injury prevention needs
        - Movement pattern modifications needed
        
        3. PROGRAM DESIGN IMPLICATIONS
        Volume Considerations:
        - Optimal training frequency indicators
        - Volume tolerance predictions
        - Exercise selection priorities
        
        Progressive Planning:
        - Short-term training priorities
        - Long-term development pathway
        - Periodization considerations
        
        4. NEXT PHASE PREPARATION
        Data Collection Needs:
        - Additional measurements needed
        - Movement assessments to prioritize
        - Strength baseline tests to conduct
        
        Integration Points:
        - Key findings for program design phase
        - Critical constraints for exercise selection
        - Important considerations for loading parameters
        
        For each analysis component:
        1. State your reasoning process explicitly
        2. Support conclusions with scientific rationale
        3. Indicate confidence level in each conclusion
        4. Note what additional information would be valuable
        5. Explain how findings connect to next analysis phases
        """
        

        # this symstme message e is linked with "prompt" test_one with one runnign now is just testing I will see in the future,  
        system_message = """
        You are Dr. Mike Israetel (RP Strength), a leading expert in evidence-based hypertrophy training.
        Approach each analysis using the following chain-of-thought process:
        
        1. DATA UNDERSTANDING
        - Examine each measurement carefully
        - Compare measurements to established norms
        - Note any unusual patterns or relationships
        
        2. STRUCTURAL ANALYSIS
        - Analyze proportions between body parts
        - Identify structural balance indicators
        - Consider biomechanical implications
        
        3. PRACTICAL IMPLICATIONS
        - Determine training priorities
        - Identify potential limitations
        - Suggest specific interventions
        
        For each step, explicitly state your reasoning before moving to conclusions.
        Support each observation with scientific reasoning or empirical evidence when possible.
        """


    async def analyze(self, measurements: Dict[str, str]) -> str:
    
        """
        Analyzes client measurements using structured chain-of-thought reasoning.
        
        Args:
            measurements: Dictionary of body measurements (e.g., {'chest': 42.0, 'waist': 32.0})
        
        Returns:
            Detailed analysis with explicit reasoning steps
        """


        measurements_str = "\n".join(f"{k.capitalize()}: {v}" for k, v in measurements.items())
        
        prompt = f"""
        Analyze these body measurements using explicit step-by-step reasoning:
        
        CLIENT MEASUREMENTS:
        ==================
        {measurements_str}

        Follow this specific thought process:
        
        1. First, examine the raw data:
        - What stands out about these measurements?
        - How do they compare to population averages?
        - What initial patterns do you notice?
        - How do the different units (cm/in) affect your analysis?
        
        2. Then, analyze structural relationships:
        - Calculate and assess key ratios (considering unit conversions)
        - Identify any potential imbalances
        - Consider the implications for movement patterns
        
        3. Finally, provide practical recommendations:
        - What are the priority areas for development?
        - What specific training approaches would be most effective?
        - What potential limitations should be considered?
        
        4. Unit Analysis:
        - Explain how the presence of units adds context
        - Discuss any implications of mixed unit usage
        - Suggest optimal unit standardization if needed
        
        For each step, explain your reasoning before stating conclusions.
        Begin each major section with 'Reasoning:' followed by your analysis process.
        """

        test_one_prompt = f"""
        Analyze these client measurements using advanced chain-of-thought reasoning:

        CLIENT MEASUREMENTS:
        ==================
        {measurements_str}

        Follow this detailed analysis protocol:
        
        1. Initial Measurement Assessment:
        - What are the key insights from each measurement?
        - How do measurements relate to each other?
        - What body composition indicators are present?
        - What structural patterns emerge?
        
        2. Body Composition Analysis:
        - What do these measurements suggest about body fat levels?
        - What muscle mass distribution patterns are indicated?
        - How do proportions suggest fiber type dominance?
        - What genetic structural advantages are apparent?
        
        3. Training Implications:
        - How will these measurements affect exercise selection?
        - What loading parameters are suggested?
        - What volume tolerances are indicated?
        - Which movement patterns need special consideration?
        
        4. Program Design Considerations:
        - What should be prioritized in program design?
        - Which body parts need additional attention?
        - What structural balance issues need addressing?
        - How should progression be structured?
        
        5. Risk and Limitation Analysis:
        - What potential injury risks are indicated?
        - Which movements might need modification?
        - What recovery considerations are suggested?
        - What structural limitations need consideration?
        
        6. Next Phase Integration:
        - What key findings should inform program design?
        - Which measurements need additional context?
        - What movement assessments should follow?
        - How should these findings guide exercise selection?
        
        For each section:
        1. Start with "Reasoning Process:" and explain your thought process
        2. Follow with "Evidence:" and list supporting indicators
        3. Include "Confidence Level:" (High/Medium/Low) for conclusions
        4. Note "Additional Information Needed:" for uncertain areas
        5. End with "Next Phase Implications:" for system integration
        
        Conclude with a summary of the most critical findings for program design.
        """
        
        print(test_one_prompt)

        return await self._call_llm(test_one_prompt)

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
        formatted_data = self._prepare_data(client_data)
        
        prompt = f"""
        Conduct a thorough scientific analysis of this client's data:

        CLIENT PROFILE:
        ===============
        {formatted_data}

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
        
        return await self._call_llm(prompt)

    def _prepare_data(self, data: dict) -> str:
        """
        Prepares client data for analysis, organizing critical factors.
        """
        sections = []
        
        for section, content in data.items():
            section_title = content.get('title', section.upper())
            sections.append(f"\n{section_title}")
            
            fields = content.get('fields', {})
            for field, value in fields.items():
                formatted_value = f"{value['key']} {value['unit']}" if isinstance(value, dict) else value
                sections.append(f"- {field}: {formatted_value}")
        
        return "\n".join(sections)

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
        formatted_data = self._format_client_data(client_data)
        
        prompt = f"""
        Analyze this client data using advanced chain-of-thought reasoning:

        CLIENT INFORMATION:
        ==================
        {formatted_data}

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
        
        return await self._call_llm(prompt)

    def _format_client_data(self, data: dict) -> str:
        """
        Formats client data for analysis, organizing by section with clear headers.
        """
        formatted_sections = []
        
        for section, content in data.items():
            section_title = content.get('title', section.capitalize())
            formatted_sections.append(f"\n{section_title}:")
            
            for field, value in content.get('fields', {}).items():
                if isinstance(value, dict):
                    formatted_value = f"{value['key']} ({value['unit']})"
                else:
                    formatted_value = value
                formatted_sections.append(f"- {formatted_value}")
        
        return "\n".join(formatted_sections)
















