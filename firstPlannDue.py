from typing import Dict, Any
from datetime import datetime
import json
import os 
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
OPENAI_MODEL = "gpt-4o-mini"


class RPAnalysisSystem:

    """
    Graph TD for Analysis Report Flow:
    graph TD
        A[Client Data] --> B1[Body Analysis]
        A --> B2[Training History]
        A --> B3[Goals & Preferences]
        
        B1 --> C[Current Status]
        B2 --> C
        B3 --> C
        
        C --> D1[Short-term Goals]
        C --> D2[Long-term Goals]
        C --> D3[Limitations]
        
        D1 --> E[Final Analysis Report]
        D2 --> E
        D3 --> E
        
        E --> F1[Training Recommendations]
        E --> F2[Risk Factors]
        E --> F3[Timeline Expectations]
    """
       



    def __init__(self):
        self.SYSTEM_MESSAGE = """You are Dr. Mike Israetel, a renowned expert in exercise science and bodybuilding. 
        Your role is to analyze client data and create evidence-based training and nutrition plans following 
        Renaissance Periodization (RP) principles. Focus on:
        1. Scientific analysis of measurements and client data
        2. Volume landmarks and progressive overload
        3. Practical, implementable recommendations
        4. Clear explanations of rationale"""
        
        # External tools for calculations
        self.measurement_analyzer = MeasurementAnalyzer()
        self.nutrition_calculator = NutritionCalculator()
        self.volume_calculator = VolumeCalculator()

    async def analyze_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis pipeline that processes client data through multiple stages"""
        
        # Stage 1: Body Analysis
        body_analysis = await self._analyze_body(client_data['measurements'])
        
        # Stage 2: Complete Analysis Report
        analysis_report = await self._generate_analysis_report(client_data, body_analysis)
        
        # Stage 3: Workout Plan
        workout_plan = await self._generate_workout_plan(analysis_report)
        
        # Stage 4: Nutrition Plan
        nutrition_plan = await self._generate_nutrition_plan(analysis_report)
        
        return {
            'analysis_report': analysis_report,
            'workout_plan': workout_plan,
            'nutrition_plan': nutrition_plan
        }









    async def _analyze_body(self, measurements: Dict[str, float]) -> Dict[str, Any]:
        """Analyzes body measurements using external tools and LLM analysis"""
        
        # First use external tool for precise calculations
        technical_analysis = self.measurement_analyzer.analyze_measurements(measurements)
        
        # Then use LLM for interpretation
        prompt = f"""Based on these measurements and technical analysis:
        Measurements: {json.dumps(measurements, indent=2)}
        Technical Analysis: {json.dumps(technical_analysis, indent=2)}
        
        Provide a detailed analysis following this chain of thought:
        1. Structure and proportions analysis
        2. Muscle mass distribution evaluation
        3. Potential imbalances or areas needing attention
        4. Training implications based on body structure
        
        Format your response as a structured JSON with clear sections."""

        return await self._call_llm(prompt)

    async def _generate_analysis_report(self, client_data: Dict, body_analysis: Dict) -> Dict:
        """Generates comprehensive analysis report including goals"""
        
        prompt = f"""Given this client data and body analysis:
        Client Data: {json.dumps(client_data, indent=2)}
        Body Analysis: {json.dumps(body_analysis, indent=2)}
        
        Follow this chain of thought:
        1. Evaluate current fitness level and training history
        2. Analyze recovery capacity and limitations
        3. Set specific, measurable goals based on client objectives
        4. Define realistic timelines and progression paths
        
        Create a comprehensive analysis report as JSON including specific goals."""

        return await self._call_llm(prompt)












    async def _generate_workout_plan(self, analysis_report: Dict) -> Dict:
        """Generates workout plan using volume calculations and LLM
    
        Graph TD for Workout Plan Flow:
        graph TD
            A[Analysis Report] --> B1[Volume Calculator]
            A --> B2[Exercise Selection]
            A --> B3[Schedule Constraints]
            
            B1 --> C1[Weekly Volume]
            B2 --> C2[Exercise Database]
            B3 --> C3[Session Distribution]
            
            C1 --> D[Program Structure]
            C2 --> D
            C3 --> D
            
            D --> E1[Mesocycle Plan]
            D --> E2[Progressive Overload]
            D --> E3[Deload Strategy]
            
            E1 --> F[Final Workout Plan]
            E2 --> F
            E3 --> F
        """
  
        
        # Calculate optimal volume ranges using external tool
        volume_ranges = self.volume_calculator.calculate_optimal_volumes(
            analysis_report['fitness_level'],
            analysis_report['recovery_capacity']
        )
        
        prompt = f"""Based on this analysis and calculated volume ranges:
        Analysis: {json.dumps(analysis_report, indent=2)}
        Volume Ranges: {json.dumps(volume_ranges, indent=2)}
        
        Follow this chain of thought:
        1. Exercise selection based on goals and limitations
        2. Volume distribution across muscle groups
        3. Progressive overload scheme design
        4. Weekly schedule structure
        
        Create a detailed workout plan as JSON."""

        return await self._call_llm(prompt)
    





    async def _generate_nutrition_plan(self, analysis_report: Dict) -> Dict:
        """Generates nutrition plan using external calculations and LLM"""
        
        # Calculate baseline nutrition needs
        nutrition_baseline = self.nutrition_calculator.calculate_needs(
            analysis_report['body_stats'],
            analysis_report['activity_level'],
            analysis_report['goals']
        )
        
        prompt = f"""Using this analysis and calculated nutrition baseline:
        Analysis: {json.dumps(analysis_report, indent=2)}
        Nutrition Baseline: {json.dumps(nutrition_baseline, indent=2)}
        
        Follow this chain of thought:
        1. Adjust macronutrients based on specific goals
        2. Design meal timing around training
        3. Consider dietary preferences and restrictions
        4. Plan nutrition periodization
        
        Create a detailed nutrition plan as JSON."""

        return await self._call_llm(prompt)

    async def _call_llm(self, prompt: str) -> Dict:
        """Calls OpenAI's GPT model to generate a response."""
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.SYSTEM_MESSAGE},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()





class MeasurementAnalyzer:
    def analyze_measurements(self, measurements):
        """
        Analyze body measurements and return a structured report.
        :param measurements: Dict containing body measurements (e.g., weight, height, body fat %)
        :return: Dict with analysis results
        """
        weight = measurements.get("weight", 0)
        height = measurements.get("height", 0)
        body_fat = measurements.get("body_fat", 0)
        
        # Basic BMI Calculation
        bmi = weight / ((height / 100) ** 2) if height > 0 else 0
        
        return {
            "BMI": round(bmi, 2),
            "Body Fat Percentage": body_fat,
            "Category": "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
        }

class NutritionCalculator:
    def calculate_macros(self, weight, goal):
        """
        Calculate macronutrient needs based on weight and goal.
        :param weight: User's weight in kg
        :param goal: "bulk", "cut", or "maintain"
        :return: Dict with protein, carbs, fats in grams
        """
        if goal == "bulk":
            protein = weight * 2.2
            carbs = weight * 4
            fats = weight * 1
        elif goal == "cut":
            protein = weight * 2.5
            carbs = weight * 2
            fats = weight * 0.8
        else:  # Maintain
            protein = weight * 2
            carbs = weight * 3
            fats = weight * 0.9
        
        return {
            "Protein (g)": round(protein, 1),
            "Carbs (g)": round(carbs, 1),
            "Fats (g)": round(fats, 1)
        }

class VolumeCalculator:
    def calculate_training_volume(self, exercises):
        """
        Calculate total volume load for a workout.
        :param exercises: List of dicts with 'sets', 'reps', 'weight' per exercise
        :return: Total volume in kg
        """
        total_volume = sum(ex["sets"] * ex["reps"] * ex["weight"] for ex in exercises)
        return {"Total Training Volume (kg)": total_volume}
    

















from typing import Dict, Any
from datetime import datetime
import json
import os
from openai import OpenAI
from dotenv import load_dotenv



load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
OPENAI_MODEL = "gpt-4o-mini"

class RPAnalysisSystem:
    """Main system to coordinate different analysis components."""

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

    async def analyze_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processes client data through multiple stages."""

        body_analysis = await self.body_analysis.analyze(client_data['measurements'])
        analysis_report = await self._generate_analysis_report(client_data, body_analysis)
        workout_plan = await self.workout_plan.generate(analysis_report)
        nutrition_plan = await self.nutrition_plan.generate(analysis_report)

        return {
            'message' : "yes complete ", 
            'body_analysis' : body_analysis, 
            'analysis_report': analysis_report,
            'workout_plan': workout_plan,
            'nutrition_plan': nutrition_plan
        }

    async def _generate_analysis_report(self, client_data: Dict, body_analysis: Dict) -> Dict:

        """Generates a comprehensive analysis report."""
        prompt = f"""Given this client data and body analysis:
        Client Data: {json.dumps(client_data, indent=2)}
        Body Analysis: {json.dumps(body_analysis, indent=2)}
        
        Follow this chain of thought:
        1. Evaluate current fitness level and training history
        2. Analyze recovery capacity and limitations
        3. Set specific, measurable goals based on client objectives
        4. Define realistic timelines and progression paths
        
        Create a comprehensive analysis report as JSON including specific goals.
        """

        return await self._call_llm(prompt)

    async def _call_llm(self, prompt: str) -> Dict:
        """Calls OpenAI's GPT model to generate a response."""
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": self.SYSTEM_MESSAGE}, {"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()


class BodyAnalysis:
    """Handles body analysis using external tools and LLM processing."""

    def __init__(self, system_message: str):
        self.SYSTEM_MESSAGE = system_message
      #  self.measurement_analyzer = MeasurementAnalyzer()

    async def analyze(self, measurements: Dict[str, float]) -> Dict[str, Any]:
        """Analyzes body measurements."""
    #    technical_analysis = self.measurement_analyzer.analyze_measurements(measurements)

        prompt = f"""Based on these measurements and technical analysis:
        Measurements: {json.dumps(measurements, indent=2)}
       
        
        Provide a detailed analysis with:
        1. Structure and proportions
        2. Muscle mass distribution
        3. Potential imbalances
        4. Training implications
        
        Format as structured JSON."""
        
        return await RPAnalysisSystem._call_llm(self, prompt)


class WorkoutPlanGenerator:
    """Handles workout plan generation using volume calculations and LLM."""

    def __init__(self, system_message: str):
        self.SYSTEM_MESSAGE = system_message
        self.volume_calculator = VolumeCalculator()

    async def generate(self, analysis_report: Dict) -> Dict:
        """Generates a detailed workout plan."""
        volume_ranges = self.volume_calculator.calculate_optimal_volumes(
            analysis_report['fitness_level'], analysis_report['recovery_capacity']
        )

        prompt = f"""Based on this analysis and volume ranges:
        Analysis: {json.dumps(analysis_report, indent=2)}
        Volume Ranges: {json.dumps(volume_ranges, indent=2)}
        
        Follow this chain of thought:
        1. Exercise selection
        2. Volume distribution
        3. Progressive overload design
        4. Weekly structure
        
        Generate a structured JSON workout plan."""
        
        return await RPAnalysisSystem._call_llm(self, prompt)

class NutritionPlanGenerator:
    """Handles nutrition plan generation using external tools and LLM."""

    def __init__(self, system_message: str):
        self.SYSTEM_MESSAGE = system_message
        self.nutrition_calculator = NutritionCalculator()

    async def generate(self, analysis_report: Dict) -> Dict:
        """Generates a nutrition plan."""
        nutrition_baseline = self.nutrition_calculator.calculate_needs(
            analysis_report['body_stats'], analysis_report['activity_level'], analysis_report['goals']
        )

        prompt = f"""Using this analysis and nutrition baseline:
        Analysis: {json.dumps(analysis_report, indent=2)}
        Nutrition Baseline: {json.dumps(nutrition_baseline, indent=2)}
        
        Follow this chain of thought:
        1. Adjust macronutrients
        2. Meal timing
        3. Dietary preferences
        4. Nutrition periodization
        
        Generate a structured JSON nutrition plan."""
        
        return await RPAnalysisSystem._call_llm(self, prompt)

class MeasurementAnalyzer:

    def analyze_measurements(self, measurements):
        """Analyze body measurements and return a structured report."""
        weight = measurements.get("weight", 0)
        height = measurements.get("height", 0)
        body_fat = measurements.get("body_fat", 0)

        bmi = weight / ((height / 100) ** 2) if height > 0 else 0

        return {
            "BMI": round(bmi, 2),
            "Body Fat Percentage": body_fat,
            "Category": "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
        }

class NutritionCalculator:

    def calculate_needs(self, body_stats, activity_level, goals):
        """Calculates nutritional needs based on body stats and goals."""
        weight = body_stats.get("weight", 0)
        goal = goals.get("goal", "maintain")

        return self.calculate_macros(weight, goal)

    def calculate_macros(self, weight, goal):
        """Calculates macros based on weight and goal."""
        if goal == "bulk":
            protein, carbs, fats = weight * 2.2, weight * 4, weight * 1
        elif goal == "cut":
            protein, carbs, fats = weight * 2.5, weight * 2, weight * 0.8
        else:
            protein, carbs, fats = weight * 2, weight * 3, weight * 0.9

        return {"Protein (g)": round(protein, 1), "Carbs (g)": round(carbs, 1), "Fats (g)": round(fats, 1)}

class VolumeCalculator:

    def calculate_optimal_volumes(self, fitness_level, recovery_capacity):
        """Calculate training volume based on fitness level."""
        return {"weekly_sets_per_muscle_group": fitness_level * recovery_capacity}