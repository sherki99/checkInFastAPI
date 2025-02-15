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
    Helper function to call the LLM with a system message and prompt.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content.strip()


class VolumeCalculator:
    def calculate(self, fitness_level: float, recovery_capacity: float) -> float:
        """
        Calculate recommended weekly sets per muscle group.
        """
        return fitness_level * recovery_capacity * 10


class WorkoutPlanGenerator:
    def __init__(self, system_message: str = None):
        self.system_message = system_message or (
            "You are Dr. Mike Israetel, an expert in exercise science and programming. "
            "Generate detailed, evidence-based workout plans."
        )
        self.volume_calculator = VolumeCalculator()

    async def extract_parameters(self, report: str) -> Dict[str, float]:
        """
        Use chain-of-thought prompts to extract the client's fitness level and recovery capacity
        from the provided analysis report.
        """
        # Extract fitness level
        prompt_fitness = (
            "Analyze the following report and determine the client's fitness level on a scale from 1 (beginner) "
            "to 5 (advanced). Provide a short explanation and end your response with 'Fitness Level: X'.\n\n"
            f"{report}"
        )
        fitness_response = await call_llm(self.system_message, prompt_fitness)
        try:
            fitness_level = float(fitness_response.split("Fitness Level:")[1].strip())
        except Exception:
            fitness_level = 1.0  # Fallback default

        # Extract recovery capacity
        prompt_recovery = (
            "Analyze the following report and determine the client's recovery capacity on a scale from 1 (poor) "
            "to 5 (excellent). Provide a chain-of-thought explanation and end with 'Recovery Capacity: X'.\n\n"
            f"{report}"
        )
        recovery_response = await call_llm(self.system_message, prompt_recovery)
        try:
            recovery_capacity = float(recovery_response.split("Recovery Capacity:")[1].strip())
        except Exception:
            recovery_capacity = 1.0  # Fallback default

        return {"fitness_level": fitness_level, "recovery_capacity": recovery_capacity}

    async def generate_workout(self, client_data: Dict[str, Any], report: str) -> str:
        """
        Generates a detailed workout plan. The function follows a multi-step approach:
          1. Extract key parameters from the analysis report.
          2. Calculate recommended training volume.
          3. Generate a final workout plan incorporating both client data and the report insights.
        """
        # Step 1: Extract key parameters (fitness level and recovery capacity) using chain-of-thought.
        parameters = await self.extract_parameters(report)
        fitness_level = parameters.get("fitness_level", 1.0)
        recovery_capacity = parameters.get("recovery_capacity", 1.0)

        # Step 2: Calculate volume recommendations.
        weekly_sets = self.volume_calculator.calculate(fitness_level, recovery_capacity)

        # Step 3: Create a final workout plan.
        prompt_workout = (
            "Using the client data and analysis report provided, along with the calculated volume information below, "
            "generate a detailed, actionable workout plan. Your plan should include:\n"
            "1. A selection of exercises.\n"
            "2. A breakdown of weekly volume (number of sets per muscle group).\n"
            "3. An explanation for progressive overload and progression strategy.\n"
            "4. A structured weekly training schedule.\n\n"
            f"Calculated Volume Info: Recommended weekly sets per muscle group = {weekly_sets:.1f}\n\n"
            f"Client Data:\n{client_data}\n\n"
            f"Analysis Report:\n{report}\n\n"
            "Explain your reasoning step-by-step (chain-of-thought) and conclude with the final workout plan."
        )

        final_workout_plan = await call_llm(self.system_message, prompt_workout)
        return final_workout_plan
