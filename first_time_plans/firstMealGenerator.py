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


class NutritionCalculator:
    def calculate_needs(self, body_stats: Dict, activity_level: str, goals: Dict) -> Dict:
        """
        Calculates nutritional needs based on the client's body stats, activity level, and goals.
        """
        weight = body_stats.get("weight", 70)
        goal = goals.get("goal", "maintain")

        if goal == "bulk":
            protein = weight * 2.2
            carbs = weight * 4
            fats = weight * 1
        elif goal == "cut":
            protein = weight * 2.5
            carbs = weight * 2
            fats = weight * 0.8
        else:  # maintain
            protein = weight * 2
            carbs = weight * 3
            fats = weight * 0.9

        return {
            "Daily Protein": f"{round(protein, 1)}g",
            "Daily Carbs": f"{round(carbs, 1)}g",
            "Daily Fats": f"{round(fats, 1)}g"
        }


class MealPlanGenerator:
    def __init__(self, system_message: str = None):
        self.system_message = system_message or (
            "You are Dr. Mike Israetel, a nutrition expert specializing in evidence-based meal planning for "
            "bodybuilding and athletic performance. Generate detailed meal plans with clear chain-of-thought reasoning."
        )
        self.nutrition_calculator = NutritionCalculator()

    async def extract_nutrition_parameters(self, report: str) -> Dict[str, Any]:
        """
        Extracts nutritional parameters such as body weight, activity level, and goals from the analysis report.
        """
        # Extract body weight (or other key body stats)
        prompt_stats = (
            "Analyze the following report to extract the client's body weight in kilograms. "
            "End your answer with 'Weight: X' where X is the numeric weight.\n\n"
            f"{report}"
        )
        stats_response = await call_llm(self.system_message, prompt_stats)
        try:
            weight_str = stats_response.split("Weight:")[1].strip().split()[0]
            weight = float(weight_str)
        except Exception:
            weight = 70.0  # Default if extraction fails

        # Extract activity level
        prompt_activity = (
            "From the report below, determine the client's activity level. "
            "Provide one of the following labels: sedentary, moderate, or very_active. "
            "End your answer with 'Activity Level: <level>'.\n\n"
            f"{report}"
        )
        activity_response = await call_llm(self.system_message, prompt_activity)
        try:
            activity_level = activity_response.split("Activity Level:")[1].strip().split()[0]
        except Exception:
            activity_level = "moderate"

        # Extract goals
        prompt_goals = (
            "Based on the following report, determine the client's primary nutritional goal. "
            "Provide one of the following options: bulk, cut, or maintain. "
            "End your answer with 'Goal: <goal>'.\n\n"
            f"{report}"
        )
        goals_response = await call_llm(self.system_message, prompt_goals)
        try:
            goal = goals_response.split("Goal:")[1].strip().split()[0]
        except Exception:
            goal = "maintain"

        return {"weight": weight, "activity_level": activity_level, "goal": goal}

    async def generate_meal_plan(self, client_data: Dict[str, Any], report: str) -> str:
        """
        Generates a detailed meal plan. The multi-step approach:
          1. Extract key nutritional parameters from the analysis report.
          2. Calculate macronutrient targets using these parameters.
          3. Generate a final meal plan that includes daily targets, meal timing, food suggestions, and explanations.
        """
        # Step 1: Extract nutritional parameters from the report.
        nutrition_params = await self.extract_nutrition_parameters(report)
        weight = nutrition_params.get("weight", 70)
        activity_level = nutrition_params.get("activity_level", "moderate")
        goal = nutrition_params.get("goal", "maintain")

        # Step 2: Calculate nutritional needs.
        calculated_needs = self.nutrition_calculator.calculate_needs(
            {"weight": weight},
            activity_level,
            {"goal": goal}
        )
        needs_str = "\n".join(f"{k}: {v}" for k, v in calculated_needs.items())

        # Step 3: Compose a final meal plan prompt.
        prompt_meal = (
            "Using the client data, analysis report, and calculated nutritional needs provided below, "
            "generate a detailed meal plan. Your meal plan should include:\n"
            "1. Daily macronutrient targets.\n"
            "2. Recommended meal timing and frequency.\n"
            "3. Example food choices and portion sizes.\n"
            "4. A brief explanation of how the plan supports the client's nutritional goals.\n\n"
            f"Calculated Nutritional Needs:\n{needs_str}\n\n"
            f"Client Data:\n{client_data}\n\n"
            f"Analysis Report:\n{report}\n\n"
            "Explain your reasoning step-by-step (chain-of-thought) and then provide the final meal plan."
        )

        final_meal_plan = await call_llm(self.system_message, prompt_meal)
        return final_meal_plan
