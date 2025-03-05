from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ProgressMetrics(BaseModel):
    """Comprehensive metrics tracking client's progress and performance."""
    weight_trend: str = Field(..., description="Overall weight progression trend")
    weight_change: float = Field(..., description="Total weight change over the period")
    performance_consistency: float = Field(..., description="Percentage of days with high performance")
    recovery_quality: str = Field(..., description="Assessment of recovery and rest quality")
    stress_management_score: float = Field(..., description="Quantitative score for stress management")
    sleep_quality_trend: str = Field(..., description="Trend in sleep length and efficiency")

class WeeklyProgressAnalysis(BaseModel):
    """Detailed analysis of client's weekly progress across multiple dimensions."""
    progress_metrics: ProgressMetrics = Field(..., description="Quantitative progress metrics")
    activity_level_insights: str = Field(..., description="Detailed insights into activity levels")
    nutrition_performance: str = Field(..., description="Overview of nutritional performance")
    training_intensity_observations: str = Field(..., description="Observations about training intensity")
    key_highlights: List[str] = Field(..., description="Most significant achievements or observations")
    improvement_areas: List[str] = Field(..., description="Areas requiring focused attention")
    recovery_recommendations: List[str] = Field(..., description="Specific recovery and adjustment recommendations")

class ReportMetricExtractor:
    """
    Extracts and analyzes client progress metrics from weekly and daily reports.
    
    This class processes weekly summary and daily reports to provide a comprehensive
    view of the client's progress, performance, and areas of potential improvement.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the ReportMetricExtractor with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def extract_report_metrics(
        self, 
        week_report: Dict[str, Any], 
        daily_reports: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process week report and daily reports to analyze progress metrics.
        
        Args:
            week_report: The client's weekly summary report
            daily_reports: List of daily progress reports
            
        Returns:
            A dictionary containing structured progress analysis
        """
        try:
            # Process using the schema-based approach
            schema_result = self._analyze_report_metrics_schema(week_report, daily_reports)
            
            return {
                "weekly_progress_analysis": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error analyzing report metrics: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in progress metrics analysis.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a performance and wellness coach specialized in tracking client progress. "
            "Your task is to comprehensively analyze a client's weekly progress based on their "
            "weekly summary and daily reports.\\n\\n"
            
            "Key analysis principles:\\n"
            "1. **Holistic Assessment**: Evaluate progress across physical, nutritional, and mental dimensions.\\n"
            "2. **Trend Analysis**: Identify patterns in weight, performance, recovery, and stress.\\n"
            "3. **Contextual Interpretation**: Consider the interplay between daily reports and weekly summary.\\n"
            "4. **Performance Tracking**: Assess consistency and intensity of training and lifestyle.\\n"
            "5. **Improvement Identification**: Highlight strengths and areas needing focused attention.\\n"
            "6. **Actionable Recommendations**: Provide clear, practical guidance for continued progress.\\n\\n"
            
            "Your analysis should be data-driven, insightful, and constructive, offering a clear "
            "picture of the client's weekly journey and potential next steps."
        )
    
    def _analyze_report_metrics_schema(
        self,
        week_report: Dict[str, Any],
        daily_reports: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze progress metrics using Pydantic schema validation.
        
        Args:
            week_report: The client's weekly summary report
            daily_reports: Daily progress reports from the client
            
        Returns:
            Structured progress analysis as a Pydantic model
        """
        # Ensure daily reports exist
        daily_reports = daily_reports or []
        
        # Extract key details from week report
        user_id = week_report.get('userId', 'Unknown')
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            f"Analyze the progress metrics for User {user_id} based on their weekly summary and daily reports.\\n\\n"
            
            f"WEEKLY SUMMARY:\\n{self._format_week_report(week_report)}\\n\\n"
            
            f"DAILY REPORTS:\\n{self._format_daily_reports(daily_reports)}\\n\\n"
            
            "Provide a comprehensive analysis that includes:\\n"
            "1. Quantitative progress metrics\\n"
            "2. Activity level and performance insights\\n"
            "3. Nutrition and training observations\\n"
            "4. Key highlights and achievements\\n"
            "5. Areas requiring improvement\\n"
            "6. Specific recovery and progress recommendations\\n\\n"
            
            "Create a detailed, actionable progress analysis that offers clear insights and guidance."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=WeeklyProgressAnalysis)
        return result
    
    def _format_week_report(self, week_report: Dict[str, Any]) -> str:
        """
        Format week report data as a readable string for inclusion in prompts.
        
        Args:
            week_report: Weekly report dictionary
            
        Returns:
            Formatted string representation
        """
        formatted = ""
        
        # Add key fields from week report
        fields_to_include = [
            'date', 'averageWeight', 'activityLevels', 'appearance', 
            'caffeineConsumption', 'digestion', 'recovery', 
            'stressManagement', 'trainingWeek', 'nutrition'
        ]
        
        for field in fields_to_include:
            value = week_report.get(field)
            if value is not None:
                formatted += f"  {field.replace('_', ' ').title()}: {value}\\n"
        
        # Add comments or highlights if present
        comments = week_report.get('comments', '')
        highlights = week_report.get('highlights', '')
        
        if comments:
            formatted += f"  Comments: {comments}\\n"
        if highlights:
            formatted += f"  Highlights: {highlights}\\n"
        
        return formatted
    
    def _format_daily_reports(self, reports: List[Dict[str, Any]]) -> str:
        """
        Format daily report data as a readable string for inclusion in prompts.
        
        Args:
            reports: List of daily report dictionaries
            
        Returns:
            Formatted string representation
        """
        if not reports:
            return "No daily reports available."
        
        formatted = ""
        for report in reports:
            date = report.get("date", "Unknown date")
            day = report.get("day", "")
            formatted += f"  Day {day} ({date}):\\n"
            
            # Key performance metrics
            formatted += f"    - Weight: {report.get('weight', 'N/A')} kg\\n"
            formatted += f"    - Performance: {report.get('performance', 'N/A')}\\n"
            
            # Sleep metrics
            sleep = report.get("sleep", {})
            formatted += f"    - Sleep Length: {sleep.get('length', 'N/A')} hours\\n"
            
            # Additional relevant data
            formatted += f"    - Steps: {report.get('steps', 'N/A')}\\n"
            formatted += f"    - RHR: {report.get('rhr', 'N/A')}\\n"
            
            # Notes and stressors
            notes = report.get("additionalNotes", "")
            stressors = report.get("stressors", "")
            
            if notes:
                formatted += f"    - Notes: {notes}\\n"
            if stressors:
                formatted += f"    - Stressors: {stressors}\\n"
        
        return formatted
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """
        Format a dictionary as a readable string for inclusion in prompts.
        
        Args:
            data: Dictionary to format
            
        Returns:
            Formatted string representation
        """
        try:
            return json.dumps(data, indent=2)
        except:
            # Fallback for non-serializable objects
            return str(data)