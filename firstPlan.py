from typing import Dict, Any
from datetime import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
OPENAI_MODEL = "gpt-4o-mini"

class RPAnalysisSystem:
    def __init__(self, system_message: str = None):
        self.SYSTEM_MESSAGE = system_message or """You are Dr. Mike Israetel, a renowned expert in exercise science and bodybuilding. 
        Your role is to analyze client data and create evidence-based training and nutrition plans following 
        Renaissance Periodization (RP) principles. Focus on:
        1. Scientific analysis of measurements and client data
        2. Volume landmarks and progressive overload
        3. Practical, implementable recommendations
        4. Clear explanations of rationale"""

        self.body_analysis = BodyAnalysis(self.SYSTEM_MESSAGE)
        self.workout_plan = WorkoutPlanGenerator(self.SYSTEM_MESSAGE)
        self.nutrition_plan = NutritionPlanGenerator(self.SYSTEM_MESSAGE)

    async def _call_llm(self, prompt: str) -> str:
        """Modified LLM call to return string responses"""
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.SYSTEM_MESSAGE},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content.strip()

    async def analyze_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Modified client analysis with string responses"""
        try:
            body_analysis = await self.body_analysis.analyze(client_data.get('measurements', {}))
            if "ERROR:" in body_analysis:
                return {
                    'status': 'error',
                    'message': body_analysis
                }

            analysis_report = await self._generate_analysis_report(client_data, body_analysis)
            if "ERROR:" in analysis_report:
                return {
                    'status': 'error',
                    'message': analysis_report
                }

            workout_plan = await self.workout_plan.generate(analysis_report)
            nutrition_plan = await self.nutrition_plan.generate(analysis_report)

            return {
                'status': 'success',
                'body_analysis': body_analysis,
                'analysis_report': analysis_report,
                'workout_plan': workout_plan,
                'nutrition_plan': nutrition_plan
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Analysis failed: {str(e)}'
            }

class BodyAnalysis:
    def __init__(self, system_message: str):
        self.SYSTEM_MESSAGE = system_message

    async def analyze(self, measurements: Dict[str, float]) -> str:
        """Analyzes body measurements returning string format"""
        measurements_str = "\n".join([f"{k}: {v}" for k, v in measurements.items()])
        
        prompt = f"""Based on these measurements:
        {measurements_str}
        
        Provide a detailed analysis with:
        1. Structure and proportions
        2. Muscle mass distribution
        3. Potential imbalances
        4. Training implications
        
        Format as clear sections with headings."""
        
        return await RPAnalysisSystem._call_llm(self, prompt)

class WorkoutPlanGenerator:
    def __init__(self, system_message: str):
        self.SYSTEM_MESSAGE = system_message
        self.volume_calculator = VolumeCalculator()

    async def generate(self, analysis_report: str) -> str:
        """Generates a detailed workout plan in string format"""
        volume_info = self.volume_calculator.calculate_optimal_volumes(
            self._extract_fitness_level(analysis_report),
            self._extract_recovery_capacity(analysis_report)
        )
        
        prompt = f"""Based on this analysis and volume information:
        Analysis: {analysis_report}
        Volume Info: {volume_info}
        
        Create a detailed workout plan including:
        1. Exercise selection
        2. Volume distribution
        3. Progressive overload design
        4. Weekly structure
        
        Format as a clear, structured training program."""
        
        return await RPAnalysisSystem._call_llm(self, prompt)

    def _extract_fitness_level(self, analysis: str) -> float:
        """Extract fitness level from analysis text"""
        # Simple extraction - could be made more sophisticated
        if "beginner" in analysis.lower():
            return 1.0
        elif "intermediate" in analysis.lower():
            return 2.0
        elif "advanced" in analysis.lower():
            return 3.0
        return 1.5  # default moderate level

    def _extract_recovery_capacity(self, analysis: str) -> float:
        """Extract recovery capacity from analysis text"""
        # Simple extraction - could be made more sophisticated
        if "poor recovery" in analysis.lower():
            return 0.8
        elif "good recovery" in analysis.lower():
            return 1.2
        return 1.0  # default normal recovery

class NutritionPlanGenerator:
    def __init__(self, system_message: str):
        self.SYSTEM_MESSAGE = system_message
        self.nutrition_calculator = NutritionCalculator()

    async def generate(self, analysis_report: str) -> str:
        """Generates a nutrition plan in string format"""
        stats = self._extract_body_stats(analysis_report)
        activity = self._extract_activity_level(analysis_report)
        goals = self._extract_goals(analysis_report)
        
        nutrition_info = self.nutrition_calculator.calculate_needs(stats, activity, goals)
        nutrition_str = "\n".join([f"{k}: {v}" for k, v in nutrition_info.items()])

        prompt = f"""Based on this analysis and nutrition information:
        Analysis: {analysis_report}
        Calculated Needs: {nutrition_str}
        
        Create a detailed nutrition plan including:
        1. Daily macronutrient targets
        2. Meal timing recommendations
        3. Food choices and preferences
        4. Nutrition periodization strategy
        
        Format as a clear, structured nutrition program."""
        
        return await RPAnalysisSystem._call_llm(self, prompt)

    def _extract_body_stats(self, analysis: str) -> Dict:
        """Extract body stats from analysis text"""
        # Simple extraction - could be made more sophisticated
        weight = 70  # default
        for line in analysis.split('\n'):
            if 'weight' in line.lower():
                try:
                    weight = float(line.split(':')[1].strip().split()[0])
                except:
                    pass
        return {"weight": weight}

    def _extract_activity_level(self, analysis: str) -> str:
        """Extract activity level from analysis text"""
        if "sedentary" in analysis.lower():
            return "sedentary"
        elif "very active" in analysis.lower():
            return "very_active"
        return "moderate"

    def _extract_goals(self, analysis: str) -> Dict:
        """Extract goals from analysis text"""
        if "muscle gain" in analysis.lower() or "bulk" in analysis.lower():
            return {"goal": "bulk"}
        elif "fat loss" in analysis.lower() or "cut" in analysis.lower():
            return {"goal": "cut"}
        return {"goal": "maintain"}

class VolumeCalculator:
    def calculate_optimal_volumes(self, fitness_level: float, recovery_capacity: float) -> str:
        """Calculate training volume returning string format"""
        weekly_sets = fitness_level * recovery_capacity * 10
        return f"Recommended weekly sets per muscle group: {weekly_sets:.1f}"

class NutritionCalculator:
    def calculate_needs(self, body_stats: Dict, activity_level: str, goals: Dict) -> Dict:
        """Calculates nutritional needs returning dictionary"""
        weight = body_stats.get("weight", 70)
        goal = goals.get("goal", "maintain")
        
        # Calculate macros
        if goal == "bulk":
            protein = weight * 2.2
            carbs = weight * 4
            fats = weight * 1
        elif goal == "cut":
            protein = weight * 2.5
            carbs = weight * 2
            fats = weight * 0.8
        else:
            protein = weight * 2
            carbs = weight * 3
            fats = weight * 0.9

        return {
            "Daily Protein": f"{round(protein, 1)}g",
            "Daily Carbs": f"{round(carbs, 1)}g",
            "Daily Fats": f"{round(fats, 1)}g"
        }