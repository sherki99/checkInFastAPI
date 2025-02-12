import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

OPENAI_MODEL = "gpt-4o-mini"



def user_prompt_for_first_plan(planInfo):
    return f"""
    ## Weekly Check-In Summary:

    The Personal Information of the user:**
    {planInfo['question']}
     
    The body measurements of this user are
    {planInfo['bodyMeasurements']}

    create a plan for my self the end always write "it is done for you!!"
    ```
    """


system_message_first_plan = """You are Dr. Mike Israetel (Renaissance Periodization - RP Strength), 
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

async def firstCreate_gpt(planInfo : dict):
    reply = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_message_first_plan},
            {"role": "user", "content": user_prompt_for_first_plan(planInfo)}
        ]
    )
    return reply.choices[0].message.content


