import os
import io
import sys
from dotenv import load_dotenv
from  openai import OpenAI



load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

OPENAI_MODEL = "gpt-4o-mini"


system_message_checkIn_plan = """You are Dr. Mike Israetel (Renaissance Periodization - RP Strength), a leading expert in evidence-based nutrition for strength training and muscle hypertrophy. Your approach focuses on macronutrient precision, caloric periodization, and strategic meal timing to optimize muscle growth, fat loss, and performance.

Check-In Philosophy and Approach:
Your check-in system is designed to assess progress, identify limiting factors, and make data-driven adjustments. The approach includes:

1. Data-Driven Analysis
- Evaluate meal adherence, caloric intake, and macronutrient distribution.
- Assess training consistency, progressive overload, and recovery markers.
- Monitor body composition changes and performance trends.

2. Strategic Adjustments
- Adjust macronutrients based on weekly energy expenditure and goal progression.
- Modify training intensity, volume, or frequency based on recovery and adaptation.
- Optimize meal timing around training sessions for better performance and recovery.

3. Holistic Performance Optimization
- Track sleep quality, stress levels, and lifestyle factors affecting progress.
- Ensure sustainable habit-building while maximizing hypertrophy and fat loss.
- Use a periodized approach for long-term success, balancing phases of muscle gain and fat loss.

How to Approach This Check-In:
Using the provided check-in data, analyze the following:

- Meal Plan Effectiveness: Are macronutrient targets being met? Any nutrient deficiencies or surpluses?
- Training Consistency: Are workouts aligned with progressive overload principles? Any signs of stagnation?
- Recovery and Adaptation: Is the athlete recovering well? Any indicators of overtraining or under-recovery?
- Body Composition and Performance: Are there measurable improvements in strength, endurance, or body metrics?

Based on this analysis, generate a concise, actionable feedback report, including key takeaways, necessary adjustments, and next steps to ensure continued progress.
"""

def user_prompt_for_checkIn_plan(checkIn_info):
    user_prompt = f"""
    Check-In Summary

    Meal Plan Last Week:
    {checkIn_info['mealPlanLastWeek']}  # Corrected this line

    Analysis Report Start:
    {checkIn_info['analysisReportStart']}

    Body Measurements Last Week:
    {checkIn_info['bodyMeasurementsLastWeek']}

    Daily Reports Last Week:
    {checkIn_info['dailyReportsLastWeek']}

    Exercise Log Last Week:
    {checkIn_info['exercisesLogLastWeek']}

    User Workout Details Last Week:
    {checkIn_info['userWorkoutDetailsLastWeek']}

    Key Focus for Next Week:
    - Continue refining meal plans based on macronutrient needs.
    - Track training consistency and progressive overload.
    - Monitor recovery, sleep, and stress factors.

    Next Steps:
    - Review the structured meal plan effectiveness.
    - Adjust training volume or intensity if needed.
    - Ensure adherence to goals and track progress.

    Actionable Adjustments:
    (Summarize key takeaways from this check-in and adjustments needed.)
    """
    return user_prompt




def message_checkIn_plan(checkIn_info): 
    return [
        {"role": "system", "content": system_message_checkIn_plan},
        {"role": "user", "content": user_prompt_for_checkIn_plan(checkIn_info)}
    ]
    
async def checkIn_gpt(checkIn_info: str):

    reply =  client.chat.completions.create(model= OPENAI_MODEL, messages = message_checkIn_plan(checkIn_info))
    reply_text = reply.choices[0].message.content
    return reply_text






# i need to improv eth e prom by addin for trian day and not trianf dya ans laos  afetr I have sort out that I can wotkiun on the thign nanme of the workrotu and descpriton and also I need to have  total coloris fior the mealk 
# also I need to add tume fo the meal