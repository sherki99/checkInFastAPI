from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class RecoveryMarkers(BaseModel):
    """Detailed recovery markers and metrics."""
    avg_sleep_hours: float = Field(..., description="Average sleep hours per night")
    avg_sleep_efficiency: Optional[float] = Field(None, description="Average sleep efficiency percentage")
    avg_rhr: Optional[float] = Field(None, description="Average resting heart rate")
    avg_stress_level: Optional[float] = Field(None, description="Average stress level on 0-10 scale")
    sleep_quality_score: float = Field(..., description="Sleep quality score on 0-100 scale")
    recovery_score: float = Field(..., description="Overall recovery score on 0-100 scale")
    energy_trend: str = Field(..., description="Energy trend: improving, declining, or stable")
    sleep_consistency: float = Field(..., description="Sleep consistency score on 0-100 scale")
    main_recovery_issues: List[str] = Field(..., description="List of main recovery issues identified")
    recovery_recommendations: List[str] = Field(..., description="List of actionable recovery recommendations")

class SleepAnalysis(BaseModel):
    """Detailed sleep metrics analysis."""
    avg_hours: float = Field(..., description="Average sleep duration")
    consistency_score: float = Field(..., description="Sleep consistency score (0-100)")
    quality_assessment: str = Field(..., description="Qualitative assessment of sleep quality")
    efficiency_analysis: Optional[str] = Field(None, description="Analysis of sleep efficiency if available")
    scientific_basis: str = Field(..., description="Scientific rationale for sleep assessment")

class StressAndRecoveryAnalysis(BaseModel):
    """Analysis of stress levels and recovery markers."""
    stress_patterns: str = Field(..., description="Identified stress patterns")
    rhr_analysis: Optional[str] = Field(None, description="Analysis of resting heart rate trends")
    recovery_quality: str = Field(..., description="Overall recovery quality assessment")
    physiological_markers: List[str] = Field(..., description="Key physiological recovery markers identified")
    scientific_basis: str = Field(..., description="Scientific rationale for recovery assessment")

class PerformanceTrendAnalysis(BaseModel):
    """Analysis of performance and energy trends."""
    energy_trend: str = Field(..., description="Overall energy trend direction")
    performance_pattern: str = Field(..., description="Identified performance patterns")
    fatigue_indicators: List[str] = Field(..., description="Key fatigue indicators identified")
    scientific_basis: str = Field(..., description="Scientific basis for performance trend assessment")

class ComprehensiveRecoveryAnalysis(BaseModel):
    """Complete recovery analysis with recommendations."""
    client_name: str = Field(..., description="Client's name")
    recovery_period: str = Field(..., description="Time period covered by analysis")
    recovery_score: float = Field(..., description="Overall recovery score (0-100)")
    sleep_analysis: SleepAnalysis = Field(..., description="Detailed sleep analysis")
    stress_recovery_analysis: StressAndRecoveryAnalysis = Field(..., description="Stress and recovery analysis")
    performance_analysis: PerformanceTrendAnalysis = Field(..., description="Performance trend analysis")
    main_recovery_issues: List[str] = Field(..., description="Main recovery issues identified")
    recovery_recommendations: List[str] = Field(..., description="Actionable recovery recommendations")
    scientific_foundation: str = Field(..., description="Scientific foundation for recommendations")
    adaptation_strategies: List[str] = Field(..., description="Strategies for improving recovery")

class RecoveryMarkersExtractor:
    """
    Module for extracting recovery markers from standardized check-in data using LLM analysis.
    
    This class leverages an LLM to analyze daily reports and recovery metrics,
    providing evidence-based recovery insights and recommendations.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the RecoveryMarkersExtractor with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def extract_recovery_markers(self, daily_reports: List[Any], week_report: Any = None) -> Dict[str, Any]:
        """
        Extracts recovery markers from daily reports and week report data using LLM analysis.
        
        Args:
            daily_reports: List of standardized daily reports
            week_report: Optional weekly report for additional recovery context
            
        Returns:
            Dictionary containing structured recovery analysis
        """
        try:
            # Process using the schema-based approach
            schema_result = self._analyze_recovery_markers_schema(
                daily_reports, week_report
            )
            
            return {
                "recovery_analysis": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error analyzing recovery markers: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in recovery analysis.
        
        The system message establishes the context and criteria for analyzing
        recovery metrics according to scientific principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are an expert in exercise physiology and recovery science with "
            "specialized knowledge in sleep analysis, stress management, and athletic recovery. "
            "Your task is to analyze client recovery data and provide evidence-based insights "
            "and recommendations.\n\n"
            
            "Apply these scientific principles when analyzing recovery markers:\n"
            "1. **Sleep Quality Analysis**: Evaluate based on duration, efficiency, and consistency:\n"
            "   - Optimal sleep: 7-9 hours for most adults\n"
            "   - Sleep efficiency > 85% indicates quality sleep\n"
            "   - Consistent sleep/wake times improve overall recovery\n"
            "2. **Physiological Markers**: Interpret resting heart rate (RHR) and other metrics:\n"
            "   - Elevated RHR (+5 bpm above baseline) may indicate incomplete recovery\n"
            "   - RHR patterns can indicate overtraining or illness\n"
            "3. **Stress Evaluation**: Analyze reported stress levels and patterns:\n"
            "   - Chronic elevated stress impairs recovery and adaptation\n"
            "   - Stress accumulation effects on performance and recovery\n"
            "4. **Performance Trends**: Identify patterns in performance reports:\n"
            "   - Declining performance may indicate need for additional recovery\n"
            "   - Consistent performance improvements suggest adequate recovery\n"
            "5. **Individual Factors**: Consider individual response patterns and history\n\n"
            
            "Your analysis should include a complete recovery score, identification of key issues, "
            "and evidence-based recommendations for improving recovery metrics."
        )
    
    def _analyze_recovery_markers_schema(
        self,
        daily_reports: List[Any],
        week_report: Any = None
    ) -> Dict[str, Any]:
        """
        Analyze recovery markers using Pydantic schema validation and LLM processing.
        
        Args:
            daily_reports: List of standardized daily reports
            week_report: Optional weekly report for additional recovery context
            
        Returns:
            Structured recovery analysis as a Pydantic model
        """
        # Extract relevant data for prompt construction
        client_name = "Client"
        if daily_reports and len(daily_reports) > 0 and hasattr(daily_reports[0], "client_name"):
            client_name = daily_reports[0].client_name
        
        # Process daily reports into summarized format for prompt
        sleep_data = []
        rhr_data = []
        stress_data = []
        performance_data = []
        dates = []
        
        for report in daily_reports:
            report_date = None
            if hasattr(report, "date"):
                report_date = report.date
                dates.append(report_date)
            
            sleep_entry = {"date": report_date}
            if hasattr(report, "sleep") and report.sleep:
                sleep_entry["length"] = report.sleep.length if hasattr(report.sleep, "length") else None
                sleep_entry["efficiency"] = report.sleep.efficiency if hasattr(report.sleep, "efficiency") else None
                sleep_entry["quality"] = report.sleep.quality if hasattr(report.sleep, "quality") else None
            sleep_data.append(sleep_entry)
            
            if hasattr(report, "rhr"):
                rhr_data.append({"date": report_date, "rhr": report.rhr})
                
            if hasattr(report, "stressors"):
                stress_data.append({"date": report_date, "stressors": report.stressors})
                
            if hasattr(report, "performance"):
                performance_data.append({"date": report_date, "performance": report.performance})
        
        # Format week report if available
        weekly_summary = None
        if week_report:
            weekly_summary = {
                "recovery": week_report.recovery if hasattr(week_report, "recovery") else None,
                "fatigue": week_report.fatigue if hasattr(week_report, "fatigue") else None,
                "overview": week_report.overview if hasattr(week_report, "overview") else None
            }
        
        # Determine date range for analysis
        date_range = "Unknown period"
        if dates and len(dates) > 0:
            try:
                sorted_dates = sorted(dates)
                date_range = f"{sorted_dates[0]} to {sorted_dates[-1]}"
            except:
                # Fallback if dates can't be sorted
                date_range = f"Last {len(dates)} reports"
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Analyze this client's recovery markers based on scientific principles "
            "of exercise physiology and sleep science. Create a complete recovery analysis "
            "that evaluates sleep quality, stress levels, resting heart rate patterns, "
            "and performance trends.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Name: {client_name}\n"
            f"- Analysis Period: {date_range}\n"
            f"- Number of Daily Reports: {len(daily_reports)}\n\n"
            
            f"SLEEP DATA:\n{self._format_dict(sleep_data)}\n\n"
            f"RESTING HEART RATE DATA:\n{self._format_dict(rhr_data)}\n\n"
            f"STRESS REPORTS:\n{self._format_dict(stress_data)}\n\n"
            f"PERFORMANCE REPORTS:\n{self._format_dict(performance_data)}\n\n"
            
            f"WEEKLY REPORT:\n{self._format_dict(weekly_summary) if weekly_summary else 'No weekly report available'}\n\n"
            
            "Your recovery analysis should include:\n"
            "1. Overall recovery score based on all available metrics\n"
            "2. Detailed sleep analysis with quality and consistency scoring\n"
            "3. Stress and recovery marker analysis with physiological interpretation\n"
            "4. Performance trend analysis with energy and fatigue patterns\n"
            "5. Main recovery issues identified from the data\n"
            "6. Evidence-based recommendations for improving recovery\n"
            "7. Scientific foundation for all evaluations and recommendations\n\n"
            
            "Create a complete recovery analysis with evidence-based insights "
            "and actionable recommendations."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=ComprehensiveRecoveryAnalysis)
        
        # Convert comprehensive analysis to simple RecoveryMarkers for compatibility
        simple_markers = RecoveryMarkers(
            avg_sleep_hours=result.sleep_analysis.avg_hours,
            avg_sleep_efficiency=None,  # Will be calculated from the analysis if possible
            avg_rhr=None,  # Will be calculated from the analysis if possible
            avg_stress_level=None,  # Will be calculated from the analysis if possible
            sleep_quality_score=float(result.sleep_analysis.consistency_score),
            recovery_score=float(result.recovery_score),
            energy_trend=result.performance_analysis.energy_trend.lower(),
            sleep_consistency=float(result.sleep_analysis.consistency_score),
            main_recovery_issues=result.main_recovery_issues,
            recovery_recommendations=result.recovery_recommendations
        )
        
        return {
            "recovery_markers": simple_markers,
            "comprehensive_analysis": result
        }
    
    def _format_dict(self, data: Any) -> str:
        """
        Format a dictionary or list as a readable string for inclusion in prompts.
        
        Args:
            data: Dictionary or list to format
            
        Returns:
            Formatted string representation
        """
        try:
            return json.dumps(data, indent=2, default=str)
        except:
            # Fallback for non-serializable objects
            return str(data)