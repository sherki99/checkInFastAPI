system_message = """
You are an expert fitness coach specializing in hypertrophy and bodybuilding training for males aged 16-40.
Your task is to analyze a client's fitness profile and determine their ideal training style, methodology, and nutritional approach.
Additionally, based on the analysis, recommend the most suitable online coach that aligns with their philosophy and goals.
Provide a structured breakdown of all relevant factors before giving a detailed final recommendation.
"""

def user_prompt_for(profile):
    user_prompt = """
    Analyze the following client's fitness profile and recommend an ideal training approach:
    
    **Personal Information:**
    - Gender: {gender}
    - Height: {height} cm
    - Weight: {weight} kg
    - Age: {age}
    
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
    1. Identify the client's best **training style** (High Volume, High Intensity, Biomechanics, Hybrid, etc.) based on their fitness level and goals.
    2. Determine which **methodologies** (Progressive Overload, Failure Training, Periodization, etc.) suit them best.
    3. Assess if they align more with **natural lifters' requirements** or **enhanced bodybuilding approaches**.
    4. Evaluate their **nutritional habits** to identify potential diet optimizations.
    5. Consider **lifestyle factors** that may affect their consistency and adherence.
    6. Provide a structured **final coaching recommendation** with clear, step-by-step reasoning.
    7. Based on the final assessment, suggest the best **online fitness coach** that matches their needs and approach.
    
    """.format(**profile)
    return user_prompt

def messages_for(profile):
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt_for(profile)}
    ]

def check_output(assessment): 
    pass

def optimize_gpt(profile):
    stream = openai.chat.completions.create(model=OPENAI_MODEL, messages=messages_for(profile))
    reply = ""
    for chunk in stream: 
        fragment = chunk.choices[0].delta.content or ""
        reply += fragment
        print(fragment, end="", flush=True)
    check_output(reply)
