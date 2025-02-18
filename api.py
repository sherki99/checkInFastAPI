from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Optional, Any
from fastapi.middleware.cors import CORSMiddleware
from fitness_optimization import optimize_gpt, workout_gpt
from nutri_optimization import nutrition_gpt
from checkIn_optimization import checkIn_gpt
from checkIn_fixPlans import adjust_plan_gpt
from firstPlanNote import RPAnalysisSystem


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)








user_infos: Dict[str, dict] = {}


class UserInfo(BaseModel):
    userId: str  # Required field

    # Optional fields
    age: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    fitnessKnowledge: Optional[str] = None
    exerciseRoutine: Optional[str] = None
    bodyParts: Optional[str] = None
    mealSize: Optional[str] = None
    mealsPerDay: Optional[str] = None
    mealTime: Optional[str] = None
    dietPreference: Optional[str] = None
    eatingHabits: Optional[str] = None
    alcoholUnits: Optional[str] = None
    supplements: Optional[str] = None
    motivationLevel: Optional[str] = None
    timeToSeeChanges: Optional[str] = None
    main_goals: Optional[str] = None
    waterIntake: Optional[str] = None
    activityLevel: Optional[str] = None
    currentlyExercise: Optional[str] = None
    exerciseTypeDoYouDo: Optional[str] = None
    exercise_leastLiked: Optional[str] = None
    exercise_mostLiked: Optional[str] = None
    expectedBarriers: Optional[str] = None
    fitnessEquipment: Optional[str] = None
    howDayLook: Optional[str] = None
    motivation: Optional[str] = None
    muscle_focus: Optional[str] = None
    previousExercise: Optional[str] = None
    rateYourFitnessLevel: Optional[str] = None
    skipMeals: Optional[str] = None
    sports: Optional[str] = None
    stressLevel: Optional[str] = None
    weeklyExerciseTime: Optional[str] = None
    workEnvironment: Optional[str] = None
    workHours: Optional[str] = None
    name: Optional[str] = None


class AnalysisReport(BaseModel):
    userId:  str
    report: str




@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


# **POST**: Save user info
@app.post("/save-user/")
async def save_user_info(user_info: UserInfo):
    user_infos[user_info.userId] = user_info.dict()
    return {"message": "User info saved successfully", "data": user_info}



@app.post("/run-optimization/")
async def run_optimization(user_info: UserInfo): 
    """
    This endpoint runs the optimization function, which analyzes the user's fitness profile.
    It uses the optimize_gpt function to get recommendations based on the profile.
    """

    user_infos[user_info.userId] = user_info.dict()
    result = optimize_gpt(user_infos[user_info.userId])
    
    if result:
        return {"message": "Optimization complete",  "result" : result}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate optimization")
    



@app.post("/workout-plan/")
async def workout_plan(analysis_report: AnalysisReport): 
    """
    This endpoint generates a workout plan based on the user's analysis report.
    The report contains the user's fitness data, preferences, and goals.
    """

    user_id = analysis_report.userId
    user_report = analysis_report.report 

    workout_plan =  await workout_gpt(user_id, user_report)
    return {"message": "Optimization complete",  "result" : workout_plan}



@app.post("/nutrition-plan/")
async def nutrition_plan(analysis_report: AnalysisReport): 
    """
    This endpoint generates a nutrition plan based on the user's analysis report.
    The report contains the user's dietary preferences, goals, and nutritional needs.
    """

    user_id = analysis_report.userId
    user_report = analysis_report.report 

    nutrition_plan = await nutrition_gpt(user_id, user_report)
    return {"message": "Optimization complete", "result": nutrition_plan}


# **GET**: Retrieve user info by userId
@app.get("/get-user/{user_id}")
async def get_user_info(user_id: str):
    if user_id in user_infos:
        return user_infos[user_id]
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/get-all-users/", response_model=Dict[str, UserInfo])
async def get_all_users():
    if user_infos:
        return user_infos
    raise HTTPException(status_code=404, detail="No users found")
    





# second part check in 
class CheckInData(BaseModel):
    userId: str
    mealPlanLastWeek: str
    analysisReportStart: str
    bodyMeasurementsLastWeek: str
    dailyReportsLastWeek: str
    exercisesLogLastWeek: str
    userWorkoutDetailsLastWeek: str


# return just the chekcIn report with update fo the workout
@app.post("/checkIn_optimization/")
async def receive_check_in(data: CheckInData):
    
    data_info =  data.dict()
    checkIn_response =  await checkIn_gpt(data_info)
    return {"message": "Check-in data received successfully!", "response": checkIn_response}


@app.post("/checkIn_adjustPlan/")
async def adjudst_plan_check_in(data: CheckInData):
    data_info = data.dict()
    
    # Call the AI function to analyze and optimize the check-in plan
    checkIn_response = await adjust_plan_gpt(data_info)
    
    return {
        "message": "Check-in data received successfully!",
        "response": checkIn_response
    }


@app.post("/checkIn_optimization_entire/")
async def receive_check_in(data: CheckInData):
    data_info = data.dict()
    
    # Generate check-in report
    checkIn_response = await checkIn_gpt(data_info)
    
    # Use check-in report for plan adjustment
    plan_adjustment_response = await adjust_plan_gpt(data_info, checkIn_response)
    
    return {
        "message": "Check-in and plan adjustment completed successfully!",
        "checkInReport": checkIn_response,
        "planAdjustment": plan_adjustment_response
    }



# digenstion model cna give worngh extart of code btu it is ok for now in case chaneg qyestiuonare bneed to change as well ù



from  first_time_plans.dataIngestionModule import DataIngestionModule
from  first_time_plans.clientProfileModule import ClientProfileModule
from  first_time_plans.goalClarificationModule import GoalClarificationModule
from  first_time_plans.bodyCompositionModule import BodyCompositionModule
from  first_time_plans.trainingHistory import TrainingHistoryModule



class BaseModelForRequest(BaseModel):
    userId: str
    profile: Dict[str, Any]
    measurements: Dict[str, Any]

"""{"standardized_profile": {"body_composition": {"arm_circumference": 24.7, "calf_circumference": 34, "chest_circumference": 81, "forearm_circumference": 23.2, "hip_circumference": 85.2, "mid_thigh_circumference": 43.8, "neck_circumference": 30.3, "thigh_circumference": 50.3, "waist_circumference": 68.7, "waist_to_hip_ratio": 0.81, "wrist_circumference": 15.1}, "fitness": {"activity_level": "Active", "available_equipment": [Array], "avoided_exercises": [Array], "exercise_routine": "Effective", "fitness_knowledge": "I am quite experienced", "preferred_exercises": [Array], "session_duration_hours": 1.5, "training_experience_years": 2, "training_frequency_per_week": 5, "weekly_exercise_hours": 7.5}, "goals": {"desired_timeframe_weeks": 4, "expected_barriers": "Occasional shoulder pain limits some movements, and balancing training with other responsibilities can be a challenge. Maintaining a strict diet is also sometimes difficult due to time constraints.", "main_goals": [Array], "motivation_level": 5}, "lifestyle": {"daily_work_hours": 5, "sports_background": "Football untill the age of 18 then played time tim", "stress_level": "Stressful", "work_environment": "Sitting"}, "measurement_date": "2024-09-17T11:37:30.217+00:00", "nutrition": {"alcohol_units_per_week": 1.5, "diet_preference": "I prefer a balanced diet with a mix of Mediterranean, Italian, and Moroccan influences. I enjoy whole foods like vegetables, lean meats, grains (like couscous and quinoa), and a moderate amount of dairy. I like to avoid processed foods and prefer home-cooked meals.", "meal_schedule": [Object], "meals_per_day": 5, "supplements": [Array], "water_intake_liters": 2.5}, "personal_info": {"age": 25, "bmi": 24.86, "gender": "Male", "height_cm": 186, "name": "Sherki", "weight_kg": 86}, "user_id": "66e037ef43e9199baf5d"}, "status": "success"}"""

@app.post("/first_time/")
async def create_first_plan(base_model: BaseModelForRequest):
    try:
        # Step 1:  Data Ingestion
        client_data = base_model.dict()
        ingestion_module = DataIngestionModule()
        standardized_profile = ingestion_module.process_data(client_data)


        # Step 2:  Client profile
        profile_module = ClientProfileModule()
        profile_analysis =  profile_module.process(standardized_profile)


        # step 3: Goal Clarrification
        goal_module  = GoalClarificationModule()
        goal_analysis = goal_module.process(standardized_profile) 

       # step 4: Composition Module
        body_composition =  BodyCompositionModule()
        body_analysis =  body_composition.process(standardized_profile)
    


       # step 5:  






        # The standardized profile would then be passed to subsequent modules
        # You would continue with the next steps in your processing pipeline here
        
        return {"status": "success", "standardized_profile": standardized_profile, "profile anal":  profile_analysis, "goalanal":  goal_analysis, "body_composition":  body_analysis}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

