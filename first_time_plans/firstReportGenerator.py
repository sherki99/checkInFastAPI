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
        self.body_analyzer = BodyAnalysis(self.system_message)
        self.info_analyzer = ClientInfoAnalysis(self.system_message)
        self.report_generator = ReportGenerator(self.system_message)

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
        info_analysis = await self.info_analyzer.analyze(client_info)

        # Step 3: Generate overall report
        report = await self.report_generator.generate(body_analysis, info_analysis)

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

        print(prompt)

        return await self._call_llm(prompt)


class ClientInfoAnalysis:

    def __init__(self, system_message: str):
        self.system_message = system_message

    async def analyze(self, info: Dict[str, Any]) -> str:
        """
        Analyzes general client information.
        """
        info_str = "\n".join(f"{k}: {v}" for k, v in info.items())
    
        prompt = (
            f"Analyze the following client information:\n{info_str}\n\n"
            "Provide an overview of the client's fitness level, training history, goals, and recovery capacity. "
            "Structure your analysis clearly."
        )
        return await call_llm(self.system_message, prompt)


class ReportGenerator:
    def __init__(self, system_message: str):
        self.system_message = system_message

    async def generate(self, body_analysis: str, info_analysis: str) -> str:
        """
        Generates a comprehensive report that combines the body analysis and client info analysis.
        """
        prompt = (
            "Using the two analyses provided below, create a detailed report with the following sections:\n"
            "1. Detailed Body Analysis\n"
            "2. Client Information Analysis\n"
            "3. Overall Recommendations (e.g., training, nutrition, and progression strategies)\n\n"
            f"Body Analysis:\n{body_analysis}\n\n"
            f"Client Info Analysis:\n{info_analysis}"
        )
        return await call_llm(self.system_message, prompt)