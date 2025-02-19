from typing import Dict, Any, List, Set
from first_time_plans.call_llm_class import SimpleLLMClient


class GoalClarificationModule:
    def __init__(self, llm_client: SimpleLLMClient):
        self.llm_client = llm_client
    
    def _analyze_goals(self, profile: Dict[str, Any]):
        """LLM-based analysis using systematic chain-of-thought reasoning."""
        # This function orchestrates the implicit goal analysis process
        context_analysis = self._perform_context_analysis(profile)
        goal_patterns = self._recognize_goal_patterns(profile, context_analysis)
        goal_hierarchy = self._determine_goal_hierarchy(goal_patterns)
        goal_interactions = self._analyze_goal_interactions(goal_hierarchy)
        achievement_analysis = self._analyze_achievement_feasibility(profile, goal_hierarchy)
        final_goal_structure = self._construct_final_goal_structure(
            goal_hierarchy, 
            goal_interactions, 
            achievement_analysis
        )
        
        return self._parse_goal_analysis(final_goal_structure)
    
    def _perform_context_analysis(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes the user's context including training history, body composition, and lifestyle."""
        system_message = """
        You are a specialized fitness analysis system focused on understanding user context.
        Your task is to carefully analyze training history, body composition, and lifestyle patterns.
        Provide detailed, evidence-based analysis following the exact format requested.
        Be specific, objective, and thorough in your assessment.
        """
        
        user_prompt = f"""
        Analyze the following user profile to understand their context:
        
        {profile}
        
        Focus on:
        1. TRAINING HISTORY REVIEW
           - Current training frequency and volume
           - Exercise selection patterns
           - Progress patterns
           - Document specific behavioral indicators
        
        2. BODY COMPOSITION CONTEXT
           - Current measurements and ratios
           - Historical changes
           - Identify composition-related behavioral patterns
        
        3. LIFESTYLE PATTERN REVIEW
           - Daily schedule and constraints
           - Sleep and recovery patterns
           - Stress levels and management
           - Nutrition habits and preferences

        Return your analysis in this exact JSON format:
        {{
            "training_history": {{
                "frequency": str,
                "volume": str,
                "exercise_patterns": [str],
                "progress_indicators": [str],
                "behavioral_indicators": [str]
            }},
            "body_composition": {{
                "current_state": dict,
                "historical_patterns": [str],
                "behavioral_indicators": [str]
            }},
            "lifestyle_patterns": {{
                "schedule_constraints": [str],
                "sleep_quality": str,
                "recovery_capacity": str,
                "stress_factors": [str],
                "nutrition_habits": [str]
            }}
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List, Dict, Any
        
        class BodyComposition(BaseModel):
            current_state: Dict[str, Any]
            historical_patterns: List[str]
            behavioral_indicators: List[str]
        
        class TrainingHistory(BaseModel):
            frequency: str
            volume: str
            exercise_patterns: List[str]
            progress_indicators: List[str]
            behavioral_indicators: List[str]
        
        class LifestylePatterns(BaseModel):
            schedule_constraints: List[str]
            sleep_quality: str
            recovery_capacity: str
            stress_factors: List[str]
            nutrition_habits: List[str]
        
        class ContextAnalysis(BaseModel):
            training_history: TrainingHistory
            body_composition: BodyComposition
            lifestyle_patterns: LifestylePatterns
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, ContextAnalysis)
    
    def _recognize_goal_patterns(self, profile: Dict[str, Any], context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Identifies patterns indicating potential goals."""
        system_message = """
        You are a specialized goal pattern recognition system with expertise in fitness psychology.
        Your task is to identify potential fitness and health goals by analyzing direct statements,
        behavioral indicators, and indirect signals from user data.
        Follow a systematic approach and provide evidence for each potential goal you identify.
        """
        
        user_prompt = f"""
        Analyze the following user profile and context analysis to identify potential goals:
        
        USER PROFILE:
        {profile}
        
        CONTEXT ANALYSIS:
        {context_analysis}
        
        Identify goal patterns using these specific indicators:
        
        1. DIRECT STATEMENTS
           - Explicit mentions
           - Related terminology
           - Context of statements
        
        2. BEHAVIORAL INDICATORS
           - Training choices
           - Exercise preferences
           - Avoided activities
           - Time allocation
        
        3. INDIRECT SIGNALS
           - Measurement focus areas
           - Progress tracking methods
           - Supplementation choices
           - Recovery priorities

        Return your analysis in this exact JSON format:
        {{
            "potential_goals": [{{
                "category": str,
                "direct_evidence": [str],
                "behavioral_evidence": [str],
                "indirect_evidence": [str],
                "confidence_score": float
            }}]
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List
        
        class PotentialGoal(BaseModel):
            category: str
            direct_evidence: List[str]
            behavioral_evidence: List[str]
            indirect_evidence: List[str]
            confidence_score: float
        
        class GoalPatternRecognition(BaseModel):
            potential_goals: List[PotentialGoal]
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, GoalPatternRecognition)
    
    def _determine_goal_hierarchy(self, goal_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Determines the hierarchy and prioritization of identified goals."""
        system_message = """
        You are a specialized goal prioritization system with expertise in behavioral psychology.
        Your task is to evaluate and prioritize fitness and health goals based on frequency of mention,
        emotional investment, resource allocation, and behavioral consistency.
        Provide evidence-based prioritization and realistic timeline estimates.
        """
        
        user_prompt = f"""
        Analyze the following goal patterns to determine goal hierarchy and prioritization:
        
        GOAL PATTERNS:
        {goal_patterns}
        
        For each identified goal, determine:
        
        1. PRIORITY ASSESSMENT
           - Frequency of mention
           - Emotional investment indicators
           - Resource allocation
           - Behavioral consistency
        
        2. TIMELINE ANALYSIS
           - Stated timeframes
           - Realistic achievement windows
           - Required commitment level
           - Progressive milestone structure

        Return your analysis in this exact JSON format:
        {{
            "prioritized_goals": [{{
                "category": str,
                "priority_score": float,
                "priority_evidence": [str],
                "estimated_timeline_weeks": int,
                "timeline_evidence": [str]
            }}]
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List
        
        class PrioritizedGoal(BaseModel):
            category: str
            priority_score: float
            priority_evidence: List[str]
            estimated_timeline_weeks: int
            timeline_evidence: List[str]
        
        class GoalHierarchy(BaseModel):
            prioritized_goals: List[PrioritizedGoal]
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, GoalHierarchy)
    
    def _analyze_goal_interactions(self, goal_hierarchy: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes how different goals interact with each other."""
        system_message = """
        You are a specialized goal interaction analysis system with expertise in exercise physiology.
        Your task is to identify synergistic and competing relationships between different fitness goals.
        Provide specific analysis of resource sharing, timeline compatibility, and potential conflicts.
        """
        
        user_prompt = f"""
        Analyze the following goal hierarchy to identify interactions between goals:
        
        GOAL HIERARCHY:
        {goal_hierarchy}
        
        Analyze goal interactions using these specific methods:
        
        1. SYNERGISTIC GOALS
           - Complementary objectives
           - Shared resources
           - Timeline compatibility
        
        2. COMPETING GOALS
           - Resource conflicts
           - Timeline conflicts
           - Recovery demands
           - Adaptive interference

        Return your analysis in this exact JSON format:
        {{
            "synergistic_pairs": [{{
                "goals": [str, str],
                "synergy_type": str,
                "synergy_strength": float,
                "leverage_strategy": str
            }}],
            "competing_pairs": [{{
                "goals": [str, str],
                "conflict_type": str,
                "conflict_severity": float,
                "mitigation_strategy": str
            }}]
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List, Tuple
        
        class SynergisticPair(BaseModel):
            goals: List[str]
            synergy_type: str
            synergy_strength: float
            leverage_strategy: str
        
        class CompetingPair(BaseModel):
            goals: List[str]
            conflict_type: str
            conflict_severity: float
            mitigation_strategy: str
        
        class GoalInteractions(BaseModel):
            synergistic_pairs: List[SynergisticPair]
            competing_pairs: List[CompetingPair]
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, GoalInteractions)
    
    def _analyze_achievement_feasibility(self, profile: Dict[str, Any], goal_hierarchy: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes the feasibility of achieving the identified goals."""
        system_message = """
        You are a specialized achievement feasibility analysis system with expertise in training science.
        Your task is to evaluate the realistic achievement potential of fitness goals based on
        resource requirements, prerequisites, and risk factors.
        Provide evidence-based feasibility scores and specific mitigation strategies.
        """
        
        user_prompt = f"""
        Analyze the feasibility of achieving the following goals based on the user profile:
        
        USER PROFILE:
        {profile}
        
        GOAL HIERARCHY:
        {goal_hierarchy}
        
        For each goal, analyze:
        
        1. RESOURCE REQUIREMENTS
           - Time commitment
           - Recovery demands
           - Nutritional needs
           - Equipment/facility needs
        
        2. PREREQUISITE ANALYSIS
           - Required skill levels
           - Baseline capacity needs
           - Progressive development steps
        
        3. RISK FACTOR ASSESSMENT
           - Technical skill gaps
           - Recovery limitations
           - Time constraints
           - Lifestyle conflicts

        Return your analysis in this exact JSON format:
        {{
            "goal_feasibility": [{{
                "category": str,
                "resource_requirements": dict,
                "prerequisites": [str],
                "risk_factors": [{{
                    "factor": str,
                    "severity": float,
                    "mitigation": str
                }}],
                "overall_feasibility_score": float
            }}]
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List, Dict, Any
        
        class RiskFactor(BaseModel):
            factor: str
            severity: float
            mitigation: str
        
        class GoalFeasibility(BaseModel):
            category: str
            resource_requirements: Dict[str, Any]
            prerequisites: List[str]
            risk_factors: List[RiskFactor]
            overall_feasibility_score: float
        
        class FeasibilityAnalysis(BaseModel):
            goal_feasibility: List[GoalFeasibility]
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, FeasibilityAnalysis)
    
    def _construct_final_goal_structure(
        self, 
        goal_hierarchy: Dict[str, Any], 
        goal_interactions: Dict[str, Any], 
        achievement_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Constructs the final goal structure with implementation framework."""
        system_message = """
        You are a specialized goal structure optimization system with expertise in program design.
        Your task is to create a coherent, structured goal framework that maximizes success potential.
        Select primary and secondary goals, resolve conflicts, and create a detailed implementation framework.
        """
        
        user_prompt = f"""
        Construct a final goal structure based on the following analyses:
        
        GOAL HIERARCHY:
        {goal_hierarchy}
        
        GOAL INTERACTIONS:
        {goal_interactions}
        
        ACHIEVEMENT ANALYSIS:
        {achievement_analysis}
        
        Construct the final goal structure using these specific methods:
        
        1. PRIMARY GOAL SELECTION
           - Highest priority goal
           - Supporting evidence
           - Required focus areas
        
        2. SECONDARY GOAL ORGANIZATION
           - Complementary goals
           - Sequential ordering
           - Resource allocation
        
        3. IMPLEMENTATION FRAMEWORK
           - Key milestones
           - Progress metrics
           - Adjustment triggers
           - Success indicators

        Return your analysis in this exact JSON format:
        {{
            "primary_goal": {{
                "category": str,
                "evidence": [str],
                "priority_score": float,
                "timeline_weeks": int
            }},
            "secondary_goals": [{{
                "category": str,
                "evidence": [str],
                "priority_score": float,
                "timeline_weeks": int
            }}],
            "goal_conflicts": [{{
                "goals": [str],
                "conflict_type": str,
                "severity": float,
                "mitigation_strategy": str
            }}],
            "implementation_structure": {{
                "milestones": [str],
                "metrics": [str],
                "adjustment_triggers": [str]
            }}
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List, Dict
        
        class PrimaryGoal(BaseModel):
            category: str
            evidence: List[str]
            priority_score: float
            timeline_weeks: int
        
        class SecondaryGoal(BaseModel):
            category: str
            evidence: List[str]
            priority_score: float
            timeline_weeks: int
        
        class GoalConflict(BaseModel):
            goals: List[str]
            conflict_type: str
            severity: float
            mitigation_strategy: str
        
        class ImplementationStructure(BaseModel):
            milestones: List[str]
            metrics: List[str]
            adjustment_triggers: List[str]
        
        class FinalGoalStructure(BaseModel):
            primary_goal: PrimaryGoal
            secondary_goals: List[SecondaryGoal]
            goal_conflicts: List[GoalConflict]
            implementation_structure: ImplementationStructure
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, FinalGoalStructure)

    def _analyze_timeframe_and_motivation(self, 
        profile: Dict[str, Any],
        explicit_goals: List[GoalCategory],
        implicit_goals: List[GoalCategory]
    ) -> Dict[str, Any]:
        """Analyzes appropriate timeframes and motivation using systematic reasoning."""
        # This function orchestrates the timeframe and motivation analysis process
        baseline_assessment = self._assess_baseline_capacity(profile)
        goal_timelines = self._determine_goal_specific_timelines(profile, explicit_goals, implicit_goals)
        motivation_structure = self._analyze_motivation_structure(profile, explicit_goals, implicit_goals)
        adherence_patterns = self._analyze_adherence_patterns(profile)
        integrated_timeline = self._construct_integrated_timeline(
            baseline_assessment,
            goal_timelines,
            motivation_structure,
            adherence_patterns
        )
        
        return integrated_timeline
    
    def _assess_baseline_capacity(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assesses the user's baseline capacity for training and lifestyle factors."""
        system_message = """
        You are a specialized baseline capacity assessment system with expertise in exercise physiology.
        Your task is to evaluate current training status and lifestyle capacity to determine realistic training limits.
        Provide specific, evidence-based assessments of volume tolerance, technical proficiency, and recovery capacity.
        """
        
        user_prompt = f"""
        Assess the baseline capacity of the following user profile:
        
        USER PROFILE:
        {profile}
        
        Assess baseline capacity using these specific methods:
        
        1. TRAINING STATUS
           - Current volume tolerance
           - Technical proficiency
           - Recovery capacity
           - Adaptation rate indicators
        
        2. LIFESTYLE CAPACITY
           - Available time
           - Recovery quality
           - Stress management
           - Support systems

        Return your assessment in this exact JSON format:
        {{
            "training_capacity": {{
                "volume_tolerance": str,
                "technical_proficiency": str,
                "recovery_capacity": str,
                "adaptation_rate": str
            }},
            "lifestyle_capacity": {{
                "available_time_weekly": int,
                "recovery_quality_score": float,
                "stress_management_score": float,
                "support_systems": [str]
            }}
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List
        
        class TrainingCapacity(BaseModel):
            volume_tolerance: str
            technical_proficiency: str
            recovery_capacity: str
            adaptation_rate: str
        
        class LifestyleCapacity(BaseModel):
            available_time_weekly: int
            recovery_quality_score: float
            stress_management_score: float
            support_systems: List[str]
        
        class BaselineCapacity(BaseModel):
            training_capacity: TrainingCapacity
            lifestyle_capacity: LifestyleCapacity
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, BaselineCapacity)
    
    def _determine_goal_specific_timelines(
        self, 
        profile: Dict[str, Any],
        explicit_goals: List[GoalCategory],
        implicit_goals: List[GoalCategory]
    ) -> Dict[str, Any]:
        """Determines specific timelines for each identified goal."""
        system_message = """
        You are a specialized timeline determination system with expertise in training periodization.
        Your task is to determine realistic minimum and optimal timelines for fitness goals based on
        physiological requirements, skill development needs, and adaptation windows.
        Provide evidence-based timeline estimates with specific progression recommendations.
        """
        
        user_prompt = f"""
        Determine specific timelines for the following goals based on the user profile:
        
        USER PROFILE:
        {profile}
        
        EXPLICIT GOALS:
        {explicit_goals}
        
        IMPLICIT GOALS:
        {implicit_goals}
        
        For each goal, determine:
        
        1. MINIMUM EFFECTIVE TIMELINE
           - Physiological requirements
           - Skill development needs
           - Resource availability
           - Adaptation windows
        
        2. OPTIMAL TIMELINE
           - Peak adaptation rate
           - Recovery optimization
           - Skill mastery progression
           - Sustainable progression

        Return your analysis in this exact JSON format:
        {{
            "goal_timelines": [{{
                "category": str,
                "minimum_timeline_weeks": int,
                "optimal_timeline_weeks": int,
                "physiological_requirements": [str],
                "skill_requirements": [str],
                "recommended_progression": [str]
            }}]
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List
        
        class GoalTimeline(BaseModel):
            category: str
            minimum_timeline_weeks: int
            optimal_timeline_weeks: int
            physiological_requirements: List[str]
            skill_requirements: List[str]
            recommended_progression: List[str]
        
        class GoalTimelines(BaseModel):
            goal_timelines: List[GoalTimeline]
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, GoalTimelines)
    
    def _analyze_motivation_structure(
        self,
        profile: Dict[str, Any],
        explicit_goals: List[GoalCategory],
        implicit_goals: List[GoalCategory]
    ) -> Dict[str, Any]:
        """Analyzes the user's motivation structure for identified goals."""
        system_message = """
        You are a specialized motivation analysis system with expertise in behavioral psychology.
        Your task is to identify intrinsic and extrinsic motivational factors related to fitness goals.
        Provide evidence-based assessment of motivation strengths and specific leverage strategies.
        """
        
        user_prompt = f"""
        Analyze the motivation structure for the following user and goals:
        
        USER PROFILE:
        {profile}
        
        EXPLICIT GOALS:
        {explicit_goals}
        
        IMPLICIT GOALS:
        {implicit_goals}
        
        Analyze motivation structure using these specific methods:
        
        1. INTRINSIC FACTORS
           - Personal values alignment
           - Autonomy indicators
           - Mastery orientation
           - Purpose connection
        
        2. EXTRINSIC FACTORS
           - Social support
           - Environmental facilitators
           - Reward sensitivity
           - Accountability needs

        Return your analysis in this exact JSON format:
        {{
            "intrinsic_motivators": [{{
                "factor": str,
                "strength": float,
                "evidence": [str],
                "leverage_strategy": str
            }}],
            "extrinsic_motivators": [{{
                "factor": str,
                "strength": float,
                "evidence": [str],
                "leverage_strategy": str
            }}],
            "motivation_profile": {{
                "primary_driver_type": str,
                "secondary_driver_type": str,
                "recommended_reinforcement": [str]
            }}
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List
        
        class Motivator(BaseModel):
            factor: str
            strength: float
            evidence: List[str]
            leverage_strategy: str
        
        class MotivationProfile(BaseModel):
            primary_driver_type: str
            secondary_driver_type: str
            recommended_reinforcement: List[str]
        
        class MotivationStructure(BaseModel):
            intrinsic_motivators: List[Motivator]
            extrinsic_motivators: List[Motivator]
            motivation_profile: MotivationProfile
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, MotivationStructure)
    
    def _analyze_adherence_patterns(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes historical adherence patterns and predicts future challenges."""
        system_message = """
        You are a specialized adherence pattern analysis system with expertise in behavioral consistency.
        Your task is to evaluate historical training adherence patterns and predict future challenges.
        Provide evidence-based assessment of consistency factors and specific mitigation strategies.
        """
        
        user_prompt = f"""
        Analyze adherence patterns for the following user profile:
        
        USER PROFILE:
        {profile}
        
        Analyze adherence patterns using these specific methods:
        
        1. HISTORICAL ADHERENCE
           - Past consistency
           - Dropout triggers
           - Success patterns
           - Challenge responses
        
        2. PREDICTED CHALLENGES
           - Time pressure points
           - Energy fluctuations
           - Recovery demands
           - Technical barriers

        Return your analysis in this exact JSON format:
        {{
            "historical_patterns": {{
                "consistency_score": float,
                "dropout_triggers": [str],
                "success_factors": [str],
                "challenge_response_profile": str
            }},
            "predicted_challenges": [{{
                "challenge_type": str,
                "likelihood": float,
                "impact": float,
                "mitigation_strategy": str
            }}]
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List
        
        class HistoricalPatterns(BaseModel):
            consistency_score: float
            dropout_triggers: List[str]
            success_factors: List[str]
            challenge_response_profile: str
        
        class PredictedChallenge(BaseModel):
            challenge_type: str
            likelihood: float
            impact: float
            mitigation_strategy: str
        
        class AdherenceAnalysis(BaseModel):
            historical_patterns: HistoricalPatterns
            predicted_challenges: List[PredictedChallenge]
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, AdherenceAnalysis)
    
    def _construct_integrated_timeline(
        self,
        baseline_assessment: Dict[str, Any],
        goal_timelines: Dict[str, Any],
        motivation_structure: Dict[str, Any],
        adherence_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Constructs an integrated timeline with phases and motivation strategy."""
        system_message = """
        You are a specialized timeline integration system with expertise in program periodization.
        Your task is to create a comprehensive phased timeline that optimizes progress and adherence.
        Provide specific phase structures, motivation strategies, and adherence support plans.
        """
        
        user_prompt = f"""
        Construct an integrated timeline based on the following analyses:
        
        BASELINE ASSESSMENT:
        {baseline_assessment}
        
        GOAL TIMELINES:
        {goal_timelines}
        
        MOTIVATION STRUCTURE:
        {motivation_structure}
        
        ADHERENCE PATTERNS:
        {adherence_patterns}
        
        Construct an integrated timeline using these specific methods:
        
        1. PHASE STRUCTURE
           - Initial adaptation
           - Progressive overload
           - Plateau management
           - Peak achievement
        
        2. MILESTONE FRAMEWORK
           - Early wins
           - Critical checkpoints
           - Adaptation markers
           - Ultimate targets

        Return your analysis in this exact JSON format:
        {{
            "optimal_timeline": {{
                "total_weeks": int,
                "phases": [{{
                    "name": str,
                    "duration_weeks": int,
                    "focus_areas": [str],
                    "success_criteria": [str]
                }}]
            }},
            "motivation_strategy": {{
                "primary_drivers": [str],
                "support_needs": [str],
                "risk_factors": [str],
                "mitigation_approaches": [str]
            }},
            "adherence_plan": {{
                "critical_checkpoints": [str],
                "adjustment_triggers": [str],
                "support_systems": [str]
            }}
        }}
        """
        
        from pydantic import BaseModel, Field
        from typing import List
        
        class Phase(BaseModel):
            name: str
            duration_weeks: int
            focus_areas: List[str]
            success_criteria: List[str]
        
        class OptimalTimeline(BaseModel):
            total_weeks: int
            phases: List[Phase]
        
        class MotivationStrategy(BaseModel):
            primary_drivers: List[str]
            support_needs: List[str]
            risk_factors: List[str]
            mitigation_approaches: List[str]
        
        class AdherencePlan(BaseModel):
            critical_checkpoints: List[str]
            adjustment_triggers: List[str]
            support_systems: List[str]
        
        class IntegratedTimeline(BaseModel):
            optimal_timeline: OptimalTimeline
            motivation_strategy: MotivationStrategy
            adherence_plan: AdherencePlan
        
        return self.llm_client.analyze_with_json(user_prompt, system_message, IntegratedTimeline)
    
    def _parse_goal_analysis(self, response: Dict[str, Any]) -> List[GoalCategory]:
        """Parses the goal analysis response into GoalCategory objects."""
        # Implementation for parsing the response
        pass
    
    def _parse_timeframe_motivation(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parses the timeframe and motivation analysis response."""
        # Implementation for parsing the response
        pass