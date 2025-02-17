from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv

@dataclass
class AnalysisSection:
    title: str
    key_findings: List[str]
    scientific_rationale: str
    implementation_guidelines: List[str]
    risk_factors: List[str]
    success_metrics: List[str]

@dataclass
class TrainingParameters:
    volume_tolerance: float  # 1-5 scale
    recovery_capacity: float  # 1-5 scale
    technical_proficiency: float  # 1-5 scale
    work_capacity: float  # 1-5 scale
    stress_load: float  # 1-5 scale

@dataclass
class ClientReport:
    client_name: str
    analysis_date: datetime
    training_parameters: TrainingParameters
    body_composition: AnalysisSection
    training_status: AnalysisSection
    program_design: AnalysisSection
    nutrition_recovery: AnalysisSection
    progress_projection: AnalysisSection
    recommendations: List[str]

class AnalysisSystem:
    """
    Enhanced report generation system with structured data types and robust error handling.
    """
    
    def __init__(self):
        self.system_message = """
        You are Dr. Mike Israetel creating a comprehensive training report that synthesizes 
        all client analyses into actionable recommendations. Your report should follow this 
        structured approach:

        1. EXECUTIVE SUMMARY
        - Key findings from body analysis
        - Critical client characteristics
        - Primary training considerations
        - Major limiting factors
        
        2. DETAILED ANALYSIS SYNTHESIS
        - Body composition evaluation
        - Training status assessment
        - Program design framework
        - Nutrition and recovery strategy
        
        For each section:
        1. Provide key findings
        2. Include scientific rationale
        3. List implementation guidelines
        4. Identify risk factors
        5. Define success metrics
        """
        
        # Initialize OpenAI client
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"


    async def extract_training_parameters(self, body_analysis: str, client_info: str) -> TrainingParameters:
        """Extract training parameters using chain-of-thought reasoning."""
        prompt = f"""
        Analyze the following data to determine training parameters (rate each 1-5):

        BODY ANALYSIS:
        {body_analysis}

        CLIENT INFO:
        {client_info}

        Think through each parameter:
        1. Volume Tolerance (considering training history, recovery ability)
        2. Recovery Capacity (sleep, stress, nutrition)
        3. Technical Proficiency (movement patterns, experience)
        4. Work Capacity (conditioning, endurance)
        5. Stress Load (life stress, work demands)

        Provide ratings in format:
        Volume Tolerance: X
        Recovery Capacity: X
        Technical Proficiency: X
        Work Capacity: X
        Stress Load: X
        """
        
        response = await self._call_llm(prompt)
        return self._parse_training_parameters(response)

    async def generate_analysis_section(self, 
                                      section_name: str, 
                                      data: Dict[str, Any], 
                                      parameters: TrainingParameters) -> AnalysisSection:
        """Generate a structured analysis section."""
        prompt = f"""
        Create detailed analysis for {section_name} section considering:
        
        DATA:
        {data}
        
        PARAMETERS:
        Volume Tolerance: {parameters.volume_tolerance}
        Recovery Capacity: {parameters.recovery_capacity}
        Technical Proficiency: {parameters.technical_proficiency}
        Work Capacity: {parameters.work_capacity}
        Stress Load: {parameters.stress_load}

        Provide:
        1. Key Findings (list 3-5 points)
        2. Scientific Rationale (paragraph)
        3. Implementation Guidelines (list 3-5 points)
        4. Risk Factors (list 2-3 points)
        5. Success Metrics (list 2-3 points)

        Format each section with headers:
        KEY FINDINGS:
        SCIENTIFIC RATIONALE:
        IMPLEMENTATION GUIDELINES:
        RISK FACTORS:
        SUCCESS METRICS:
        """
        
        response = await self._call_llm(prompt)
        return self._parse_analysis_section(section_name, response)

    async def generate_report(self, 
                            client_name: str,
                            body_analysis: str, 
                            client_info: str) -> ClientReport:
        """Generate complete client report with structured sections."""
        try:
            # Extract training parameters
            parameters = await self.extract_training_parameters(body_analysis, client_info)
            
            # Generate each analysis section
            data = {"body_analysis": body_analysis, "client_info": client_info}
            
            sections = {
                "body_composition": await self.generate_analysis_section("Body Composition", data, parameters),
                "training_status": await self.generate_analysis_section("Training Status", data, parameters),
                "program_design": await self.generate_analysis_section("Program Design", data, parameters),
                "nutrition_recovery": await self.generate_analysis_section("Nutrition & Recovery", data, parameters),
                "progress_projection": await self.generate_analysis_section("Progress Projection", data, parameters)
            }
            
            # Generate final recommendations
            recommendations = await self._generate_recommendations(sections, parameters)
            
            return ClientReport(
                client_name=client_name,
                analysis_date=datetime.now(),
                training_parameters=parameters,
                **sections,
                recommendations=recommendations
            )
            
        except Exception as e:
            # Fallback to default report if something fails
            return self._generate_default_report(client_name)

    async def _call_llm(self, prompt: str) -> str:
        """Helper function to call LLM with consistent system message."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    def _parse_training_parameters(self, response: str) -> TrainingParameters:
        """Parse LLM response into TrainingParameters object."""
        try:
            lines = response.split('\n')
            params = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':')
                    params[key.strip().lower().replace(' ', '_')] = float(value.strip())
            
            return TrainingParameters(**params)
        except Exception:
            # Return default parameters if parsing fails
            return TrainingParameters(
                volume_tolerance=3.0,
                recovery_capacity=3.0,
                technical_proficiency=3.0,
                work_capacity=3.0,
                stress_load=3.0
            )

    def _parse_analysis_section(self, title: str, response: str) -> AnalysisSection:
        """Parse LLM response into AnalysisSection object."""
        try:
            sections = response.split('\n\n')
            parsed = {'title': title}
            
            for section in sections:
                if 'KEY FINDINGS:' in section:
                    parsed['key_findings'] = self._extract_list(section)
                elif 'SCIENTIFIC RATIONALE:' in section:
                    parsed['scientific_rationale'] = section.split(':', 1)[1].strip()
                elif 'IMPLEMENTATION GUIDELINES:' in section:
                    parsed['implementation_guidelines'] = self._extract_list(section)
                elif 'RISK FACTORS:' in section:
                    parsed['risk_factors'] = self._extract_list(section)
                elif 'SUCCESS METRICS:' in section:
                    parsed['success_metrics'] = self._extract_list(section)
            
            return AnalysisSection(**parsed)
        except Exception:
            # Return default section if parsing fails
            return self._generate_default_section(title)

    def _extract_list(self, section: str) -> List[str]:
        """Extract list items from section text."""
        items = section.split(':')[1].strip().split('\n')
        return [item.strip('- ').strip() for item in items if item.strip()]

    async def _generate_recommendations(self, 
                                     sections: Dict[str, AnalysisSection], 
                                     parameters: TrainingParameters) -> List[str]:
        """Generate final recommendations based on analysis sections."""
        prompt = f"""
        Create prioritized recommendations based on analysis:
        
        {sections}
        
        Consider parameters:
        {parameters}
        
        Provide 5-7 specific, actionable recommendations.
        Format as numbered list:
        1. First recommendation
        2. Second recommendation
        etc.
        """
        
        response = await self._call_llm(prompt)
        return self._extract_list(response)

    def _generate_default_section(self, title: str) -> AnalysisSection:
        """Generate default analysis section if parsing fails."""
        return AnalysisSection(
            title=title,
            key_findings=["Requires further analysis"],
            scientific_rationale="Additional data needed for complete analysis",
            implementation_guidelines=["Follow standard protocols"],
            risk_factors=["Unknown factors due to incomplete analysis"],
            success_metrics=["Standard progression metrics"]
        )

    def _generate_default_report(self, client_name: str) -> ClientReport:
        """Generate default report if main generation fails."""
        return ClientReport(
            client_name=client_name,
            analysis_date=datetime.now(),
            training_parameters=TrainingParameters(
                volume_tolerance=3.0,
                recovery_capacity=3.0,
                technical_proficiency=3.0,
                work_capacity=3.0,
                stress_load=3.0
            ),
            body_composition=self._generate_default_section("Body Composition"),
            training_status=self._generate_default_section("Training Status"),
            program_design=self._generate_default_section("Program Design"),
            nutrition_recovery=self._generate_default_section("Nutrition & Recovery"),
            progress_projection=self._generate_default_section("Progress Projection"),
            recommendations=["Follow standard protocols until complete analysis is available"]
        )