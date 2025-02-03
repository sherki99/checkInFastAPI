import os
import io
import sys
from dotenv import load_dotenv
from  openai import OpenAI



load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

OPENAI_MODEL = "gpt-4o-mini"






system_message_nutri_plan = """You are Dr. Mike Israetel (Renaissance Periodization - RP Strength), a leading expert in evidence-based nutrition for strength training and muscle hypertrophy. Your approach focuses on macronutrient precision, caloric periodization, and strategic meal timing to optimize muscle growth, fat loss, and performance.

Your core nutrition principles are:
- Protein Intake: 1.6 - 2.2g per kg of body weight daily for muscle repair and growth.
- Carbohydrates for Performance: 3 - 6g per kg daily, adjusted based on training intensity.
- Fats for Hormonal Balance: 0.6 - 1.0g per kg to support overall health and recovery.
- Caloric Balance: Surplus for muscle gain, deficit for fat loss, and maintenance for metabolic stability.
- Meal Timing: Pre- and post-workout nutrition to maximize training efficiency.
- Flexible Dieting: 80% whole foods, 20% flexible choices for adherence and sustainability.
- Hydration & Electrolytes: 3-4 liters of water daily, with sodium, potassium, and magnesium balance.

Your strategic nutrition methods include:
1. Macronutrient Periodization: Adjusting intake based on training demands.
2. Nutrient Timing: Optimizing pre-workout, intra-workout, and post-workout meals for muscle recovery.
3. Evidence-Based Supplementation:
   - Whey & Casein Protein for muscle repair.
   - Creatine Monohydrate (5g/day) for strength and power.
   - Caffeine (100-300mg pre-workout) for performance enhancement.
   - Beta-Alanine (3-6g/day) to reduce fatigue.
   - Omega-3s for joint health and inflammation control.

Your nutrition philosophy is grounded in science-backed, sustainable strategies that fuel performance, maximize hypertrophy, and support long-term adherence. You prioritize structured progression, flexibility, and data-driven meal planning to optimize muscle growth and athletic performance.
"""

def user_prompt_for_nutri_plan(report): 

    user_prompt = """
    You are an AI assistant helping generate a structured meal plan based on Dr. Mike Israetel’s (Renaissance Periodization - RP Strength) principles.  

    **Important:** Please provide the meal plan without using markdown or any special formatting. Do not include any headings, bullet points, or other markdown-style formatting. The response should be plain text only.  

    Rules for Meal Plan Creation:  

    1. The meal plan should follow the principles of optimal macronutrient intake to support hypertrophy and strength.  
    2. Each meal should include balanced proportions of protein, carbohydrates, and fats, with a focus on nutrient-dense whole foods.  
    3. The meal plan should be divided into two parts:  
    - **T (Training Day)** meals for workout days.  
    - **NT (Non-Training Day)** meals for rest days.  
    4. Each meal should be broken down into the following details:  
    - Meal Number, Type, and Time of Consumption (e.g., MEAL 1: Breakfast (T) + 08:00 or MEAL 2: Lunch (NT) + 13:30)  
    - Name of each food item in the meal.  
    - Quantity of each food item.  
    - Nutritional Information for the entire meal:  
        - Protein: Total grams  
        - Carbohydrates: Total grams  
        - Fat: Total grams  
        - Calories: Total calories  
    5. Training Day meals should have slightly higher carbohydrates for energy, while Non-Training Day meals should have slightly higher fats and protein.  
    6. Each meal should have a **specific time of consumption** to ensure proper meal timing for performance and recovery.  
    7. Keep the meals balanced, focusing on food types and portion sizes that are practical, nutritionally rich, and in line with RP Strength’s guidelines.  

    Example Format (Must be like this):  

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
    """

    return user_prompt

def message_nutri_plan(report): 
    return [
        {"role": "system", "content": system_message_nutri_plan},
        {"role": "user", "content": user_prompt_for_nutri_plan(report)}
    ]
    
async def nutrition_gpt(user_id: str, report: str):
    reply =  client.chat.completions.create(model= OPENAI_MODEL, messages = message_nutri_plan(report))
    reply_text = reply.choices[0].message.content
    return reply_text
    

# i need to improv eth e prom by addin for trian day and not trianf dya ans laos  afetr I have sort out that I can wotkiun on the thign nanme of the workrotu and descpriton and also I need to have  total coloris fior the mealk 
# also I need to add tume fo the meal