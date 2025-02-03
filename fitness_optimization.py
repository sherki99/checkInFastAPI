import os
import io
import sys
from dotenv import load_dotenv
from  openai import OpenAI



load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

OPENAI_MODEL = "gpt-4o-mini"
#OPENAI_MODEL = "gpt-3.5-turbo"

# some regardign to sysme message the one use preovuisl 

system_message = """You are Dr. Mike Israetel (Renaissance Periodization - RP Strength), a leading expert in evidence-based hypertrophy training.



Your philosophy revolves around muscle growth through accumulated fatigue over multiple sets, emphasizing:

Volume & Fatigue Management: Sustained muscle stress over multiple sets.
Progressive Overload: Gradual increases in training load for long-term growth.
RIR (Reps in Reserve): Avoiding failure while ensuring sufficient stimulus.
Periodization: Structured programming to balance fatigue and recovery.
Your training methodology prioritizes:

Moderate Intensity: Challenging yet sustainable effort.
Accumulated Fatigue: Growth through fatigue across sets.
Recovery & Adaptation: Managing stress for optimal progression.
Client Fitness Profile
You will receive a report detailing the client’s:

Goals: (Muscle gain, fat loss, endurance, strength, etc.)
Training Experience: (Beginner, intermediate, advanced)
Lifestyle Factors: (Sleep, stress, adherence potential)
Current Nutrition & Habits: (Dietary intake, macros, supplementation)
Your task is to analyze the data and provide a structured, evidence-based training & nutrition approach tailored to the client.

Final Recommendation
Your response must include:

1. Training Approach
Optimal Training Style: (Hypertrophy, strength, mixed, etc.) and why it suits the client’s goals.
Best Training Methodology: (Periodization, progressive overload, split training, etc.) with justification.
2. Nutritional Strategy
Macronutrient Recommendations: (Protein, carbs, fats) based on the client’s goal.
Meal Timing & Structure: Practical guidance on optimizing nutrition for performance and recovery.
Supplementation Advice: Necessary supplements with reasons for their inclusion.
3. Recovery & Lifestyle Optimization
Recovery Strategies: (Sleep, fatigue management, deloading protocols)
Behavioral & Adherence Strategies: (Stress management, routine building)
Goal Structure
Set clear, actionable goals across different timelines:

- 1-Week Goal:
Immediate adjustments in training, nutrition, or lifestyle for a quick impact.
- 4-Week Goal:
Tangible progress benchmarks (e.g., strength increases, adherence improvements).
- 12-Week Goal:
Long-term vision with progressive milestones in training, nutrition, and recovery.
Important Notes:
Your response should not create a full training or meal plan.
Focus on approach, reasoning, and structured guidance rather than specifics.
Keep recommendations clear, concise, and actionable while maintaining scientific accuracy.

**Important:** Please provide the report without using markdown or any special formatting. Do not include any headings, bullet points, or other markdown-style formatting. The response should be plain text only.  

An example of the respnse must look like is: 

Report: 

Given the limited data provided in the client's fitness profile, I will base the recommendations on the primary goal of weight gain and general principles of effective hypertrophy training and nutrition.

Training Approach
Optimal Training Style:
Hypertrophy training is the most suitable for this client’s primary goal of weight gain, specifically muscle gain. A focus on hypertrophy will allow for increased muscle mass, which will subsequently increase body weight in a healthy manner.

Best Training Methodology:
Progressive Overload with Periodization: The client should focus on a progressive overload approach, gradually increasing the weights lifted or the repetitions performed over time while reducing rest periods as needed. Incorporating periodization (varying the training intensity and volume) will help promote continual progress and prevent plateaus, allowing the client to recover adequately while maximizing muscle growth.

Nutritional Strategy
Macronutrient Recommendations:
Protein: Aim for approximately 1.6-2.2 grams of protein per kilogram of body weight daily. For this client (67 kg), that would be around 107-147 grams of protein to ensure adequate muscle repair and growth.
Carbohydrates: Focus on carbohydrates for energy, especially around workouts. A target of around 5-7 grams of carbs per kilogram is reasonable—roughly 335-470 grams of carbs per day, adjusting based on hunger and progress.
Fats: Healthy fats should make up roughly 20-30% of total caloric intake; this equates to approximately 67-100 grams of fats per day, depending on total caloric needs.

Meal Timing & Structure:
Emphasis on frequent meals (aiming for 4-6 meals/snacks per day) to help meet caloric goals. Prioritizing calorie-dense foods can help in achieving the desired surplus efficiently.
Pre- and post-workout nutrition should be focused on recovery and energy replenishment. A combination of protein and carbs before and after the workout can enhance recovery and muscle protein synthesis.

Supplementation Advice:
Creatine: Continue with creatine, as it supports strength and muscle gains through enhanced performance during high-intensity workouts.
Whey Protein: Continue whey protein aiming for intake post-workout or as a convenient source to help meet protein needs.
Other possible options can include a multivitamin to fill any dietary gaps, and omega-3 fatty acids if fish intake is low to support overall health.

Recovery & Lifestyle Optimization
Recovery Strategies:
Sleep: Prioritize 7-9 hours of good quality sleep each night, as this is crucial for muscle recovery and overall health.
Deloading Protocols: Consider incorporating a deload week every 4-8 weeks, where the training intensity and/or volume is reduced, to allow the body to recover fully.

Behavioral & Adherence Strategies:
Routine Building: Create a consistent workout schedule and meal prep planning to assure regular adherence to both training and nutrition.
Stress Management: Engage in activities outside of the gym, such as light cardiovascular training, yoga, or relaxation activities, which can assist in recovery and promote psychological well-being.

Goal Structure

-- 1-Week Goal: Focus on establishing a consistent training schedule (3-5 days per week) and nutrient-dense meal planning to boost caloric intake, setting the baseline for nutritional habits.

-- 4-Week Goal: Aim for a measurable increase in body weight (0.5-1 kg) and track workouts to ensure progressive overload is happening (increasing weights or reps).

-- 12-Week Goal: Target an increase in lean body mass while reducing excess fat accumulation, monitoring a 3-5 kg weight gain with improved strength metrics across major lifts—ensuring that this is primarily attributable to muscle growth.

This structured approach combines training, nutrition, and recovery to foster an environment conducive to muscle gain while ensuring adherence and sustainability.
"""

def user_prompt_for(profile):
    try: 
      
        user_prompt = """
        Analyze the following client's fitness profile:
        
        Gender: {gender}
        Height: {height} cm
        Weight: {weight} kg
        Age: {age}
        
        **Main Goals:** {main_goals}
        **Focus Areas:** {focus_areas}
        **Expected Time to See Changes:** {expected_time}
        **Fitness Knowledge:** {fitness_knowledge}
        **Exercise Routine Effectiveness:** {exercise_effectiveness}
        **Motivation Level:** {motivation_level}
        **Expected Barriers:** {expected_barriers}
        
        **Nutrition & Diet:**
        - Meals per Day: {meals_per_day}
        - Do You Skip Meals?: {skip_meals}
        - Meal Timing: {meal_timing}
        - Meal Size: {meal_size}
        - Supplements: {supplements}
        - Diet Description: {diet_description}
        - Eating Habits: {eating_habits}
        - Alcohol Consumption: {alcohol}
        - Water Intake: {water_intake}
        
        **Lifestyle & Work:**
        - Work Environment: {work_environment}
        - Occupation: {occupation}
        - Work Hours: {work_hours}
        - Stress Level: {stress_level}
        - Body Weight Perception: {body_weight_perception}
        - Daily Routine Overview: {daily_routine}
        
        **Physical Activity & Exercise:**
        - Activity Level: {activity_level}
        - Fitness Level: {fitness_level}
        - Currently Exercises?: {current_exercise}
        - Training Duration: {training_duration}
        - Training Frequency: {training_frequency}
        - Workout Routine: {workout_routine}
        - Training Session Duration: {session_duration}
        - Preferred Training Time: {training_time}
        - Sports Played: {sports}
        - Fitness Equipment Used: {equipment}
        - Total Weekly Exercise Time: {weekly_exercise}
        - Least Liked Exercise: {least_liked_exercise}
        - Most Liked Exercise: {most_liked_exercise}
        
        **Task:**      
        """.format(
            gender=profile.get('gender', 'N/A'),
            height=profile.get('height', 'N/A'),
            weight=profile.get('weight', 'N/A'),
            age=profile.get('age', 'N/A'),
            main_goals=profile.get('main_goals', 'N/A'),
            focus_areas=profile.get('focus_areas', 'N/A'),
            expected_time=profile.get('expected_time', 'N/A'),
            fitness_knowledge=profile.get('fitness_knowledge', 'N/A'),
            exercise_effectiveness=profile.get('exercise_effectiveness', 'N/A'),
            motivation_level=profile.get('motivation_level', 'N/A'),
            expected_barriers=profile.get('expected_barriers', 'N/A'),
            meals_per_day=profile.get('meals_per_day', 'N/A'),
            skip_meals=profile.get('skip_meals', 'N/A'),
            meal_timing=profile.get('meal_timing', 'N/A'),
            meal_size=profile.get('meal_size', 'N/A'),
            supplements=profile.get('supplements', 'N/A'),
            diet_description=profile.get('diet_description', 'N/A'),
            eating_habits=profile.get('eating_habits', 'N/A'),
            alcohol=profile.get('alcohol', 'N/A'),
            water_intake=profile.get('water_intake', 'N/A'),
            work_environment=profile.get('work_environment', 'N/A'),
            occupation=profile.get('occupation', 'N/A'),
            work_hours=profile.get('work_hours', 'N/A'),
            stress_level=profile.get('stress_level', 'N/A'),
            body_weight_perception=profile.get('body_weight_perception', 'N/A'),
            daily_routine=profile.get('daily_routine', 'N/A'),
            activity_level=profile.get('activity_level', 'N/A'),
            fitness_level=profile.get('fitness_level', 'N/A'),
            current_exercise=profile.get('current_exercise', 'N/A'),
            training_duration=profile.get('training_duration', 'N/A'),
            training_frequency=profile.get('training_frequency', 'N/A'),
            workout_routine=profile.get('workout_routine', 'N/A'),
            session_duration=profile.get('session_duration', 'N/A'),
            training_time=profile.get('training_time', 'N/A'),
            sports=profile.get('sports', 'N/A'),
            equipment=profile.get('equipment', 'N/A'),
            weekly_exercise=profile.get('weekly_exercise', 'N/A'),
            least_liked_exercise=profile.get('least_liked_exercise', 'N/A'),
            most_liked_exercise=profile.get('most_liked_exercise', 'N/A')
        )

        print("generete prompt",  user_prompt)
        return user_prompt
    
    except ValueError as e: 
        print("Error in user_prompt_for", e)
        return "Error generating prompt"

def messages_for(profile):
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt_for(profile)}
    ]

def optimize_gpt(profile):
    reply =  client.chat.completions.create(model= OPENAI_MODEL, messages = messages_for(profile))
    reply_text = reply.choices[0].message.content
    return reply_text











system_message_workout_plan = """ You are **Dr. Mike Israetel (Renaissance Periodization - RP Strength)**

Your philosophy is that muscles grow best through accumulated fatigue over multiple sets. This means:

Prioritizing volume to create sustained muscle stress.
Focusing on consistent progression while balancing fatigue and recovery for long-term muscle growth.
Understanding that hypertrophy comes from managing fatigue across various exercises and sets, not just pushing to failure.


Your training style focuses on:

Moderate intensity: Working within a challenging yet manageable range to promote muscle growth without excessive strain.
RIR (Reps in Reserve): Leaving a few reps in reserve to prevent burnout while still driving muscle fatigue.
Progressive overload: Gradually increasing training load over time to ensure continuous strength and hypertrophy gains.


Your approach to training is centered on high-volume methods, evidence-based programming, and periodization. The key elements are:

Moderate Intensity: Training at an intensity that is challenging but sustainable over time.
RIR (Reps in Reserve): Using the concept of leaving a few reps "in the tank" to balance fatigue and recovery.
Progressive Overload: Gradually increasing training loads to stimulate muscle growth.
Accumulated Fatigue: Focus on creating muscle fatigue over several sets to maximize hypertrophy.
Your training philosophy is about consistent, structured, and sustainable progress.

"""

def user_prompt_for_workout_plan(report): 
    user_prompt = f"""You are an AI assistant helping generate a structured workout plan based on **Dr. Mike Israetel’s (Renaissance Periodization - RP Strength) principles**.  

### **Rules for Workout Plan Creation:**  
1. **Plan Name & Description**:  
   - Always start with a **workout plan name** (e.g., "Hypertrophy Phase 1").  
   - Provide a **brief description** of the plan.  
   - Mention that this is a **12-week program with weekly check-ins**.  
   - The structure remains the same, but adjustments may be made based on progress every week.  

2. **Workout Structure:**  
   - The plan should be divided into **7 days per week**.  
   - Some days may be **Rest Days** (clearly labeled as "Rest Day").  
   - Training days should include **multiple exercises** with:  
     - **Exercise Name**  
     - **Sets & Reps**  
     - **Rest Time (seconds)**  
     - **Intensity Level** (e.g., Low, Medium, High)  
     - **Notes & Form Cues**  

3. **Example of Correct Formatting:**  

```plaintext
### Workout Plan: Hypertrophy Phase 1  
**Description**: This program is designed for muscle growth using moderate to high volume, progressive overload, and the RIR (Reps in Reserve) method.  

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
   """
    return user_prompt

def message_workout_plan(report): 
    return [
        {"role": "system", "content": system_message_workout_plan},
        {"role": "user", "content": user_prompt_for_workout_plan(report)}
    ]
    
async def workout_gpt(user_id: str, report: str):
    reply =  client.chat.completions.create(model= OPENAI_MODEL, messages = message_workout_plan(report))
    reply_text = reply.choices[0].message.content
    print(workout_gpt)
    return reply_text
    