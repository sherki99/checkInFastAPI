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
    def __init__(self, system_message: str):
        self.system_message = system_message

    async def analyze(self, measurements: Dict[str, float]) -> str:
        """
        Analyzes the client's body measurements.
        """
        measurements_str = "\n".join(f"{k}: {v}" for k, v in measurements.items())
        prompt = (
            f"Analyze the following body measurements:\n{measurements_str}\n\n"
            "Provide insights on body structure, muscle mass distribution, potential imbalances, "
            "and training implications. Format the response with clear section headings."
        )
        return await call_llm(self.system_message, prompt)


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