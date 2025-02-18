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

















from  first_time_plans.dataIngestionModule import DataIngestionModule

class BaseModelForRequest(BaseModel):
    userId: str
    profile: Dict[str, Any]
    measurements: Dict[str, Any]

@app.post("/first_time/")
async def create_first_plan(base_model: BaseModelForRequest):
    try:
        client_data = base_model.dict()
        ingestion_module = DataIngestionModule()
        client_profile = ingestion_module.process(client_data)

        return {"profile": client_profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

