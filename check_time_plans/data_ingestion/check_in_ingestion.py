# check_time_plans/data_ingestion/check_in_ingestion.py

import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class StandardizedMeasurement(BaseModel):
    current: float
    previous: float
    unit: str
    change: float

class StandardizedBodyMeasurements(BaseModel):
    dates: Dict[str, str]
    measurements: Dict[str, StandardizedMeasurement]

class MacroNutrients(BaseModel):
    carbs: int
    fats: int
    proteins: int

class SleepMetrics(BaseModel):
    length: float
    efficiency: Optional[int] = None

class DailyReport(BaseModel):
    day: int
    date: str
    timeOfWeighIn: Optional[str] = None
    weight: float
    macros: MacroNutrients
    performance: Optional[str] = None
    steps: Optional[int] = None
    cardio: Optional[int] = None
    sleep: Optional[SleepMetrics] = None
    rhr: Optional[int] = None
    appetite: Optional[str] = None
    stressors: Optional[str] = None
    additionalNotes: Optional[str] = None

class ExerciseEntry(BaseModel):
    date: str
    weight: float

class ExerciseLog(BaseModel):
    name: str
    entries: List[ExerciseEntry]

class MealItem(BaseModel):
    name: str
    quantity: str

class MealNutrition(BaseModel):
    protein: int
    carbohydrates: int
    fat: int
    calories: int

class Meal(BaseModel):
    name: str
    time: str
    items: List[MealItem]
    nutrition: MealNutrition

class TotalNutrition(BaseModel):
    protein: int
    carbohydrates: int
    fat: int
    calories: int

class MealPlan(BaseModel):
    name: str
    description: str
    totalDailyNutrition: TotalNutrition
    trainingDayMeals: List[Meal]
    nonTrainingDayMeals: List[Meal]

class Exercise(BaseModel):
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    rest: Optional[str] = None
    duration: Optional[str] = None
    intensity: Optional[str] = None
    notes: Optional[str] = None

class WorkoutDay(BaseModel):
    day: int
    type: Optional[str] = None
    exercises: Optional[List[Exercise]] = None

class WorkoutPlan(BaseModel):
    name: str
    description: str
    schedule: List[WorkoutDay]

class WeekReport(BaseModel):
    date: str
    activityLevels: Optional[str] = None
    appearance: Optional[str] = None
    averageWeight: Optional[float] = None
    caffeineConsumption: Optional[str] = None
    comments: Optional[str] = None
    digestion: Optional[str] = None
    highlights: Optional[str] = None
    nextWeek: Optional[str] = None
    nutrition: Optional[str] = None
    questions: Optional[str] = None
    recovery: Optional[str] = None
    stressManagement: Optional[str] = None
    supportWork: Optional[str] = None
    trainingWeek: Optional[str] = None
    userId: str

class Goals(BaseModel):
    weeklyGoal: str
    monthlyGoal: str
    quarterlyGoal: str

class StandardizedCheckInData(BaseModel):
    userId: str
    goals: Goals
    bodyMeasurements: StandardizedBodyMeasurements
    dailyReports: List[DailyReport]
    exerciseLogs: List[ExerciseLog]
    mealPlan: MealPlan
    workoutPlan: WorkoutPlan
    weekReport: WeekReport

class CheckInDataIngestionModule:
    """Module for processing and standardizing check-in data."""
    
    def process_check_in_data(self, raw_data: Dict[str, Any]) -> StandardizedCheckInData:
        """
        Process and standardize the raw check-in data.
        
        Args:
            raw_data: Raw check-in data received from the API
            
        Returns:
            StandardizedCheckInData: Processed and standardized data
        """
        try:
            # Parse JSON strings if they are passed as strings
            body_measurements = self._parse_json(raw_data.get('bodyMeasurementsLastWeek', '{}'))
            daily_reports = self._parse_json(raw_data.get('dailyReportsLastWeek', '[]'))
            exercise_logs = self._parse_json(raw_data.get('exercisesLogLastWeek', '[]'))
            meal_plan = self._parse_json(raw_data.get('mealPlanLastWeek', '{}'))
            workout_details = self._parse_json(raw_data.get('userWorkoutDetailsLastWeek', '{}'))
            week_report = self._parse_json(raw_data.get('weekReportLastWeek', '{}'))
            analysis_report = self._parse_json(raw_data.get('analysisReportStart', '{}'))
            
            # Process and standardize each section
            standardized_goals = self._process_goals(analysis_report)
            standardized_body = self._process_body_measurements(body_measurements)
            standardized_daily = self._process_daily_reports(daily_reports)
            standardized_exercises = self._process_exercise_logs(exercise_logs)
            standardized_meal = self._process_meal_plan(meal_plan)
            standardized_workout = self._process_workout_plan(workout_details)
            standardized_week_report = self._process_week_report(week_report)
            
            # Create the standardized data object
            return StandardizedCheckInData(
                userId=raw_data.get('userId', ''),
                goals=standardized_goals,
                bodyMeasurements=standardized_body,
                dailyReports=standardized_daily,
                exerciseLogs=standardized_exercises,
                mealPlan=standardized_meal,
                workoutPlan=standardized_workout,
                weekReport=standardized_week_report
            )
            
        except Exception as e:
            # Log the error and raise it for proper handling upstream
            print(f"Error processing check-in data: {str(e)}")
            raise
    
    def _parse_json(self, data: Any) -> Dict[str, Any]:
        """Parse JSON data if it's a string, otherwise return as is."""
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                # If not valid JSON, return the original data
                return data
        return data
    
    def _process_goals(self, analysis_report: Dict[str, Any]) -> Goals:
        """Process and standardize goals data."""
        # Extract goals from analysis report
        weekly_goal = "Not specified"
        monthly_goal = "Not specified"
        quarterly_goal = "Not specified"
        
        if isinstance(analysis_report, dict):
            weekly_goal = analysis_report.get('weeklyGoal', weekly_goal)
            monthly_goal = analysis_report.get('monthlyGoal', monthly_goal)
            quarterly_goal = analysis_report.get('quarterlyGoal', quarterly_goal)
        
        return Goals(
            weeklyGoal=weekly_goal,
            monthlyGoal=monthly_goal,
            quarterlyGoal=quarterly_goal
        )
    
    def _process_body_measurements(self, body_data: Dict[str, Any]) -> StandardizedBodyMeasurements:
        """Process and standardize body measurements data."""
        dates = {"current": "", "previous": ""}
        measurements = {}
        
        if "dates" in body_data:
            dates = body_data["dates"]
        
        if "measurements" in body_data:
            raw_measurements = body_data["measurements"]
            for key, value in raw_measurements.items():
                if isinstance(value, dict):
                    measurements[key] = StandardizedMeasurement(
                        current=value.get("current", 0.0),
                        previous=value.get("previous", 0.0),
                        unit=value.get("unit", "cm"),
                        change=value.get("change", 0.0)
                    )
        
        return StandardizedBodyMeasurements(
            dates=dates,
            measurements=measurements
        )
    
    def _process_daily_reports(self, daily_data: Any) -> List[DailyReport]:
        """Process and standardize daily reports data."""
        daily_reports = []
        
        if isinstance(daily_data, list):
            for report in daily_data:
                try:
                    # Extract and standardize sleep metrics
                    sleep_metrics = None
                    if "sleep" in report and isinstance(report["sleep"], dict):
                        sleep_metrics = SleepMetrics(
                            length=report["sleep"].get("length", 0.0),
                            efficiency=report["sleep"].get("efficiency")
                        )
                    elif "sleepLength" in report:
                        sleep_metrics = SleepMetrics(
                            length=float(report.get("sleepLength", 0.0)),
                            efficiency=report.get("sleepEfficiency")
                        )
                    
                    # Extract and standardize macros
                    macros = MacroNutrients(
                        carbs=int(report.get("carbs", 0)),
                        fats=int(report.get("fats", 0)),
                        proteins=int(report.get("proteins", 0))
                    )
                    if "macros" in report and isinstance(report["macros"], dict):
                        macros = MacroNutrients(
                            carbs=int(report["macros"].get("carbs", 0)),
                            fats=int(report["macros"].get("fats", 0)),
                            proteins=int(report["macros"].get("proteins", 0))
                        )
                    
                    # Create standardized daily report
                    daily_reports.append(
                        DailyReport(
                            day=report.get("day", 0),
                            date=report.get("date", ""),
                            timeOfWeighIn=report.get("timeOfWeighIn"),
                            weight=float(report.get("weight", 0.0)),
                            macros=macros,
                            performance=report.get("performance"),
                            steps=report.get("steps"),
                            cardio=report.get("cardio"),
                            sleep=sleep_metrics,
                            rhr=report.get("rhr"),
                            appetite=report.get("appetite"),
                            stressors=report.get("stressors"),
                            additionalNotes=report.get("additionalNotes")
                        )
                    )
                except Exception as e:
                    print(f"Error processing daily report: {str(e)}")
                    # Continue processing other reports
                    continue
        
        return daily_reports
    
    def _process_exercise_logs(self, exercise_data: Any) -> List[ExerciseLog]:
        """Process and standardize exercise logs data."""
        exercise_logs = []
        
        if isinstance(exercise_data, list):
            for exercise in exercise_data:
                entries = []
                
                if "entries" in exercise and isinstance(exercise["entries"], list):
                    for entry in exercise["entries"]:
                        entries.append(
                            ExerciseEntry(
                                date=entry.get("date", ""),
                                weight=float(entry.get("weight", 0.0))
                            )
                        )
                
                exercise_logs.append(
                    ExerciseLog(
                        name=exercise.get("name", "Undefined"),
                        entries=entries
                    )
                )
        
        return exercise_logs
    
    def _process_meal_plan(self, meal_data: Dict[str, Any]) -> MealPlan:
        """Process and standardize meal plan data."""
        training_day_meals = []
        non_training_day_meals = []
        
        # Process training day meals
        if "trainingDayMeals" in meal_data and isinstance(meal_data["trainingDayMeals"], list):
            for meal in meal_data["trainingDayMeals"]:
                items = []
                if "items" in meal and isinstance(meal["items"], list):
                    for item in meal["items"]:
                        items.append(
                            MealItem(
                                name=item.get("name", ""),
                                quantity=item.get("quantity", "1 serving")
                            )
                        )
                
                nutrition = MealNutrition(
                    protein=meal.get("nutrition", {}).get("protein", 0),
                    carbohydrates=meal.get("nutrition", {}).get("carbohydrates", 0),
                    fat=meal.get("nutrition", {}).get("fat", 0),
                    calories=meal.get("nutrition", {}).get("calories", 0)
                )
                
                training_day_meals.append(
                    Meal(
                        name=meal.get("name", "Unnamed Meal"),
                        time=meal.get("time", ""),
                        items=items,
                        nutrition=nutrition
                    )
                )
        
        # Process non-training day meals
        if "nonTrainingDayMeals" in meal_data and isinstance(meal_data["nonTrainingDayMeals"], list):
            for meal in meal_data["nonTrainingDayMeals"]:
                items = []
                if "items" in meal and isinstance(meal["items"], list):
                    for item in meal["items"]:
                        items.append(
                            MealItem(
                                name=item.get("name", ""),
                                quantity=item.get("quantity", "1 serving")
                            )
                        )
                
                nutrition = MealNutrition(
                    protein=meal.get("nutrition", {}).get("protein", 0),
                    carbohydrates=meal.get("nutrition", {}).get("carbohydrates", 0),
                    fat=meal.get("nutrition", {}).get("fat", 0),
                    calories=meal.get("nutrition", {}).get("calories", 0)
                )
                
                non_training_day_meals.append(
                    Meal(
                        name=meal.get("name", "Unnamed Meal"),
                        time=meal.get("time", ""),
                        items=items,
                        nutrition=nutrition
                    )
                )
        
        # Process total daily nutrition
        total_nutrition = TotalNutrition(
            protein=meal_data.get("totalDailyNutrition", {}).get("protein", 0),
            carbohydrates=meal_data.get("totalDailyNutrition", {}).get("carbohydrates", 0),
            fat=meal_data.get("totalDailyNutrition", {}).get("fat", 0),
            calories=meal_data.get("totalDailyNutrition", {}).get("calories", 0)
        )
        
        return MealPlan(
            name=meal_data.get("name", "Default Meal Plan"),
            description=meal_data.get("description", ""),
            totalDailyNutrition=total_nutrition,
            trainingDayMeals=training_day_meals,
            nonTrainingDayMeals=non_training_day_meals
        )
    
    def _process_workout_plan(self, workout_data: Dict[str, Any]) -> WorkoutPlan:
        """Process and standardize workout plan data."""
        schedule = []
        
        if "schedule" in workout_data and isinstance(workout_data["schedule"], list):
            for day_data in workout_data["schedule"]:
                exercises = []
                
                # Process day's exercises if available
                if "exercises" in day_data and isinstance(day_data["exercises"], list):
                    for ex in day_data["exercises"]:
                        exercises.append(
                            Exercise(
                                name=ex.get("name", "Undefined"),
                                sets=ex.get("sets"),
                                reps=ex.get("reps"),
                                rest=ex.get("rest"),
                                duration=ex.get("duration"),
                                intensity=ex.get("intensity"),
                                notes=ex.get("notes")
                            )
                        )
                
                # Handle rest days or days with exercises
                if day_data.get("type") == "Rest Day" or not exercises:
                    schedule.append(
                        WorkoutDay(
                            day=day_data.get("day", 0),
                            type=day_data.get("type", "Rest Day") if not exercises else "Training Day"
                        )
                    )
                else:
                    schedule.append(
                        WorkoutDay(
                            day=day_data.get("day", 0),
                            type="Training Day",
                            exercises=exercises
                        )
                    )
        
        return WorkoutPlan(
            name=workout_data.get("name", "Default Workout Plan"),
            description=workout_data.get("description", ""),
            schedule=schedule
        )
    
    def _process_week_report(self, report_data: Dict[str, Any]) -> WeekReport:
        """Process and standardize week report data."""
        return WeekReport(
            date=report_data.get("date", ""),
            activityLevels=report_data.get("activityLevels"),
            appearance=report_data.get("appearance"),
            averageWeight=report_data.get("averageWeight"),
            caffeineConsumption=report_data.get("caffeineConsumption"),
            comments=report_data.get("comments"),
            digestion=report_data.get("digestion"),
            highlights=report_data.get("highlights"),
            nextWeek=report_data.get("nextWeek"),
            nutrition=report_data.get("nutrition"),
            questions=report_data.get("questions"),
            recovery=report_data.get("recovery"),
            stressManagement=report_data.get("stressManagement"),
            supportWork=report_data.get("supportWork"),
            trainingWeek=report_data.get("trainingWeek"),
            userId=report_data.get("userId", "")
        )