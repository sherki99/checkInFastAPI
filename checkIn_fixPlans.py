import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

OPENAI_MODEL = "gpt-4o-mini"

# System Message for Check-In Report
system_message_checkIn_plan_report = """You are Dr. Mike Israetel (Renaissance Periodization - RP Strength), 
a leading expert in evidence-based nutrition for strength training and muscle hypertrophy. 

Your role is to analyze the provided check-in data and generate a **detailed feedback report** with **clear, actionable recommendations**. 

### Focus Areas:
1. **Meal Plan Adherence** – Assess consistency and effectiveness.
2. **Training Performance** – Evaluate progressive overload, training effort, and recovery.
3. **Body Composition Trends** – Analyze progress in weight, muscle gain, or fat loss.
4. **Daily Reports & Habits** – Identify patterns affecting performance.
5. **Goal Adjustments** – Review **previous goals** and adjust for **short-term (1 week), mid-term (4 weeks), and long-term (12 weeks)**.

### Instructions:
- **Identify key trends and insights** from the check-in data.
- **Suggest modifications** to the nutrition or training plan.
- **Adjust goals based on progress** while maintaining long-term objectives.
- **Summarize key takeaways at the end**, using the given format.

### Output Format:
1. **Detailed analysis** with structured feedback.
2. **Revised goals** for the next check-in period, formatted as:
"""

def user_prompt_for_checkIn_plan_report(checkIn_info):
    return f"""
    ## Weekly Check-In Summary:

    **1️⃣ Meal Plan Adherence:**
    {checkIn_info['mealPlanLastWeek']}

    **2️⃣ Workout Plan & Performance:**
    {checkIn_info['userWorkoutDetailsLastWeek']}

    **3️⃣ Body Measurements & Composition:**
    {checkIn_info['bodyMeasurementsLastWeek']}

    **4️⃣ Daily Reports & Recovery Insights:**
    {checkIn_info['dailyReportsLastWeek']}

    **5️⃣ Exercise Log & Training Effort:**
    {checkIn_info['exercisesLogLastWeek']}

    **6️⃣ Previous Goals & Progress Assessment:**
    {checkIn_info['analysisReportStart']}

    ---
    🔍 **Analysis Requirement:**  
    - Identify **key takeaways** from the check-in data.  
    - Highlight areas of **success** and **needed improvements**.  
    - If progress is **on track**, keep the goal steady.  
    - If adjustments are needed, **modify short-term goals** and **slightly tweak mid/long-term goals**.  

    📌 **Final Report Structure:**  
    - Detailed insights with **specific** recommendations for meal plan & training.  
    - Adjusted **short-term (1-week), mid-term (4-week), and long-term (12-week) goals**.  
    - Important notes added at the end, separated by `--`.  


    📌 **Create always even if missing  Goal Format (MANDATORY—must be included at the END of the report EXACTLY in this structure):** 
    ```
    --------
    GoalOne: [Short-term adjustment based on the report]
    GoalFour: [Mid-term adjustment]
    GoalTwelve: [Long-term adjustment]
    --------
    ```
    """




    return f"""
    Check-In Summary:

    - Meal Plan Last Week:
    {checkIn_info['mealPlanLastWeek']}

    - Workout Plan Last Week:
    {checkIn_info['userWorkoutDetailsLastWeek']}

    - Body Measurements Last Week:
    {checkIn_info['bodyMeasurementsLastWeek']}

    - Daily Reports Last Week:
    {checkIn_info['dailyReportsLastWeek']}

    - Exercise Log Last Week:
    {checkIn_info['exercisesLogLastWeek']}

    - Report made Last Week with the Gaol set for the 12 weeks: 
    {checkIn_info['analysisReportStart']}

    any import point is also add the end of the report separet by line "--" I want to re the goal and from th ebalayis the can cganeg mus tbe chaneg th egoal oen for th enew weke bt the forut and twke week slight chnage it 
    based on hwo the information and reprot write to set new goal 

    Format respoonse must be like this: 
    --------
    GoalOne:  
    GoalFour:  
    GoulTwelve
    --------

    Generate a structured report with insights, suggested changes, and key takeaways.
    """

async def checkIn_gpt(checkIn_info: dict):
    reply = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_message_checkIn_plan_report},
            {"role": "user", "content": user_prompt_for_checkIn_plan_report(checkIn_info)}
        ]
    )
    return reply.choices[0].message.content










# System Message for Plan Adjustment
system_message_plan_adjustment = """You are Dr. Mike Israetel (Renaissance Periodization - RP Strength), 
an expert in evidence-based training and nutrition. Your task is to analyze the user's latest check-in data 
and determine if any adjustments are needed in their workout or nutrition plan. 

**Your response must:**
1. Clearly state whether the workout plan, nutrition plan, or both require changes.
2. Explain why adjustments are necessary, referencing progress, performance, and adherence.
3. Provide a **fully revised workout plan**, if necessary, adjusting volume, intensity, or exercise selection.
4. Provide a **fully revised nutrition plan**, if necessary, modifying macronutrient targets, caloric intake, or meal timing.
5. Provide the new four week goal if there is any change to it
5. Ensure the new plan follows the **exact format** of the user's existing plan for compatibility.
6. **Important:** Your response must be in plain text only. **Do not use markdown, bullet points, or special formatting.** 

"""

def user_prompt_for_plan_adjustment(checkIn_info, checkIn_response):
    return f"""
    Previous Check-In Report:
    {checkIn_response}

    User Check-In Data:
    - Meal Plan Last Week: {checkIn_info['mealPlanLastWeek']}
    - Workout Plan Last Week: {checkIn_info['userWorkoutDetailsLastWeek']}
    - Body Measurements Last Week: {checkIn_info['bodyMeasurementsLastWeek']}
    - Daily Reports Last Week: {checkIn_info['dailyReportsLastWeek']}
    - Exercise Log Last Week: {checkIn_info['exercisesLogLastWeek']}

    Analysis Task:
    Please analyze the user's latest check-in data and determine if adjustments are required in their workout or nutrition plan.

    If adjustments are necessary:
    1. Clearly explain whether the workout, nutrition, or both require changes, based on performance, progress, and adherence.
    2. Provide a fully updated workout plan if necessary, adjusting volume, intensity, exercise selection, or other relevant factors.
    3. Provide a fully updated nutrition plan if necessary, modifying macronutrient targets, caloric intake, or meal timing.
    4. The workout plan should start with "Workout Plan:", The meal plan should start with "Name of The Meal:"
    5. Ensure the format and structure are preserved exactly as shown in the example, with only the necessary changes being applied to improve the user's plan.
    6. Ensure the new plan follows the **exact format** of the user's previous plan (as shown in the check-in data), only applying necessary changes that have been decided after your analysis.

    Example of Workout Plan:
    #### **Day 1: Push Day (Chest & Triceps)**  
    - **Bench Press**  
      - Sets: 4  
      - Reps: 8  
      - Rest: 120 sec  
      - Intensity: High  
      - Notes: Keep elbows at a 45-degree angle to reduce shoulder strain.  

    - **Overhead Shoulder Press**  
      - Sets: 4  
      - Reps: 10  
      - Rest: 90 sec  
      - Intensity: Medium  
      - Notes: Keep core tight and avoid excessive back arching.  

    #### **Day 2: Rest Day**  
    *(No exercises. Full recovery day.)*  

    #### **Day 3: Pull Day (Back & Biceps)**  
    - **Deadlifts**  
      - Sets: 4  
      - Reps: 6  
      - Rest: 150 sec  
      - Intensity: High  
      - Notes: Engage your lats and keep a neutral spine.  

    #### **Day 4: Rest Day**  
    *(No exercises. Full recovery day.)*
    
    ---

    Example of Meal Plan:
    Name of The Meal: Structured Meal Plan  
    Description: This meal plan follows Dr. Mike Israetel’s (RP Strength) principles, ensuring optimal macronutrient intake for hypertrophy and strength.  

    Training Day Meals:

    MEAL 1: Breakfast (T) + 08:00  
    - Name: Scrambled Eggs  
    - Quantity: 3 eggs  
    - Name: Whole Wheat Toast  
    - Quantity: 2 slices  
    - Name: Avocado  
    - Quantity: 1/2  

    Nutritional Info:  
    - Protein: 20g  
    - Carbohydrates: 30g  
    - Fat: 22g  
    - Calories: 400 kcal  

    MEAL 2: Lunch (T) + 13:30  
    - Name: Grilled Chicken Breast  
    - Quantity: 150g  
    - Name: Quinoa  
    - Quantity: 100g  
    - Name: Steamed Broccoli  
    - Quantity: 1 cup  

    Nutritional Info:  
    - Protein: 35g  
    - Carbohydrates: 45g  
    - Fat: 8g  
    - Calories: 450 kcal  

    Total Daily Nutritional Intake (T):  
    Total-Protein-N: 198g  
    Total-Carbohydrates-N: 314g  
    Total-Fat-N: 91g  
    Total-Calories-N: 3170 kcal  

    Non-Training Day Meals:  

    MEAL 1: Lunch (NT) + 13:30  
    - Name: Grilled Chicken Breast  
    - Quantity: 150g  
    - Name: Quinoa  
    - Quantity: 80g  
    - Name: Steamed Broccoli  
    - Quantity: 1 cup  

    Nutritional Info:  
    - Protein: 35g  
    - Carbohydrates: 40g  
    - Fat: 10g  
    - Calories: 430 kcal  

    Total Daily Nutritional Intake (NT):  
    Total-Protein-NT: 190g  
    Total-Carbohydrates-NT: 250g  
    Total-Fat-NT: 100g  
    Total-Calories-NT: 3000 kcal

    Important:
    Your response must be plain text only, without any markdown, headings, or special formatting. All elements must be present from "-" to (NT) or (T). This is crucial for the parsing function, and the total daily nutrional intake and nutrional info must always be included. just simple as the example of format given
    """ 

    return f"""
    Previous Check-In Report:
    {checkIn_response}

    User Check-In Data:
    - Meal Plan Last Week: {checkIn_info['mealPlanLastWeek']}
    - Workout Plan Last Week: {checkIn_info['userWorkoutDetailsLastWeek']}
    - Body Measurements Last Week: {checkIn_info['bodyMeasurementsLastWeek']}
    - Daily Reports Last Week: {checkIn_info['dailyReportsLastWeek']}
    - Exercise Log Last Week: {checkIn_info['exercisesLogLastWeek']}

    Analysis Task:
    Please analyze the user's latest check-in data and determine if adjustments are required in their workout or nutrition plan.

    If adjustments are necessary:
    1. Clearly explain whether the workout, nutrition, or both require changes, based on performance, progress, and adherence.
    2. Provide a fully updated workout plan if necessary, adjusting volume, intensity, exercise selection, or other relevant factors.
    3. Provide a fully updated nutrition plan if necessary, modifying macronutrient targets, caloric intake, or meal timing.
    4. The workout plan should start with "Workout Plan:", The meal plan should start with "Name of The Meal:" 
    5. Ensure the format and structure are preserved exactly as shown in the example, with only the necessary changes being applied to improve the user's plan.
    6. Ensure the new plan follows the **exact format** of the user's previous plan (as shown in the check-in data), only applying necessary changes that have been decided after your analysis.


    Important:
    Your response must be **plain text only**, with no markdown, headings, or special formatting.
    """

async def adjust_plan_gpt(checkIn_info: dict, checkIn_response: str):
    reply = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_message_plan_adjustment},
            {"role": "user", "content": user_prompt_for_plan_adjustment(checkIn_info, checkIn_response)}
        ]
    )
    return reply.choices[0].message.content
