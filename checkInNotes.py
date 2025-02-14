# THIS CLASS IS FOR CHECK IN OPTIMZATIONTHE ONLY ADDED TOPERVIOS IS STATUS AVELAUTOR, 



class RPAnalysisSystem:
    def __init__(self):
        self.body_analyzer = BodyCompositionAnalyzer()
        self.status_evaluator = TrainingStatusEvaluator()
        self.nutrition_calculator = NutritionCalculator()
        self.program_generator = ProgramGenerator()
        
    def analyze_client(self, client_data):
        # Stage 1: Body Analysis
        body_analysis = self.body_analyzer.analyze(
            client_data.measurements
        )
        
        # Stage 2: Status Evaluation
        training_status = self.status_evaluator.evaluate(
            client_data.training_history,
            body_analysis
        )
        
        # Stage 3: Nutrition Planning
        nutrition_plan = self.nutrition_calculator.create_plan(
            client_data.nutrition_info,
            training_status
        )
        
        # Stage 4: Program Design
        training_program = self.program_generator.create_program(
            body_analysis,
            training_status,
            nutrition_plan
        )
        
        return self._compile_final_report(
            body_analysis,
            training_status,
            nutrition_plan,
            training_program
        )
    

