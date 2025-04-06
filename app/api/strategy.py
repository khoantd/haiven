from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import re

from llms.llm_service import LLMService
from config_service import ConfigService

router = APIRouter()

class StrategyRequest(BaseModel):
    companyName: str
    focusArea: str
    timeframe: str
    additionalContext: Optional[str] = None

class StrategyResponse(BaseModel):
    market_analysis: str
    competitive_advantage: str
    growth_opportunities: str
    risk_assessment: str
    resource_requirements: str
    implementation_plan: str
    success_metrics: str

@router.post("/strategy")
async def generate_strategy(request: StrategyRequest):
    try:
        config_service = ConfigService()
        llm_service = LLMService(config_service)

        # Construct the prompt for strategy generation
        prompt = f"""Generate a comprehensive business strategy for {request.companyName} focusing on {request.focusArea} with a {request.timeframe} timeframe.
        
Additional Context: {request.additionalContext if request.additionalContext else 'None provided'}

Please provide a detailed analysis in the following areas:
1. Market Analysis
2. Competitive Advantage
3. Growth Opportunities
4. Risk Assessment
5. Resource Requirements
6. Implementation Plan
7. Success Metrics

Format the response as a JSON object with the following structure:
{{
    "market_analysis": "detailed market analysis...",
    "competitive_advantage": "competitive advantage analysis...",
    "growth_opportunities": "growth opportunities analysis...",
    "risk_assessment": "risk assessment...",
    "resource_requirements": "resource requirements...",
    "implementation_plan": "implementation plan...",
    "success_metrics": "success metrics..."
}}

Ensure the strategy is:
- Specific to the company and focus area
- Aligned with the specified timeframe
- Practical and actionable
- Based on current market trends and best practices

IMPORTANT: Your response must be a valid JSON object with the exact structure shown above. Do not include any additional text before or after the JSON object.
"""

        # Generate the strategy using the LLM service
        response = await llm_service.generate_response(prompt)
        
        # Parse and validate the response
        try:
            # Try to extract JSON from the response
            json_data = extract_json_from_response(response)
            
            if json_data:
                # Validate the parsed data against the expected schema
                strategy_response = StrategyResponse(**json_data)
                return {"data": strategy_response.dict()}
            else:
                # If no valid JSON found, create a structured response from the raw text
                print(f"No valid JSON found in response. Raw response: {response}")
                
                # Try to extract sections from the text using regex
                sections = extract_sections_from_text(response)
                
                strategy_response = StrategyResponse(
                    market_analysis=sections.get("market_analysis", "No market analysis provided."),
                    competitive_advantage=sections.get("competitive_advantage", "No competitive advantage analysis provided."),
                    growth_opportunities=sections.get("growth_opportunities", "No growth opportunities analysis provided."),
                    risk_assessment=sections.get("risk_assessment", "No risk assessment provided."),
                    resource_requirements=sections.get("resource_requirements", "No resource requirements provided."),
                    implementation_plan=sections.get("implementation_plan", "No implementation plan provided."),
                    success_metrics=sections.get("success_metrics", "No success metrics provided.")
                )
                return {"data": strategy_response.dict()}
        except Exception as e:
            print(f"Error parsing strategy response: {str(e)}")
            print(f"Raw response: {response}")
            
            # Create a default response with error information
            strategy_response = StrategyResponse(
                market_analysis=f"Error parsing response: {str(e)}",
                competitive_advantage="",
                growth_opportunities="",
                risk_assessment="",
                resource_requirements="",
                implementation_plan="",
                success_metrics=""
            )
            return {"data": strategy_response.dict()}

    except Exception as e:
        print(f"Error generating strategy: {str(e)}")
        return {"error": f"Error generating strategy: {str(e)}"}

def extract_json_from_response(response):
    """Extract JSON from the response text."""
    # Try to find JSON in the response
    json_pattern = r'\{[\s\S]*\}'
    match = re.search(json_pattern, response)
    
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to clean up the JSON string
            # Remove any markdown code block markers
            json_str = re.sub(r'```json\s*|\s*```', '', json_str)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
    
    return None

def extract_sections_from_text(text):
    """Extract sections from the text using regex patterns."""
    sections = {}
    
    # Define patterns for each section
    patterns = {
        "market_analysis": r"(?:Market Analysis|1\. Market Analysis)[:\s]+(.*?)(?=(?:Competitive Advantage|2\. Competitive Advantage)|$)",
        "competitive_advantage": r"(?:Competitive Advantage|2\. Competitive Advantage)[:\s]+(.*?)(?=(?:Growth Opportunities|3\. Growth Opportunities)|$)",
        "growth_opportunities": r"(?:Growth Opportunities|3\. Growth Opportunities)[:\s]+(.*?)(?=(?:Risk Assessment|4\. Risk Assessment)|$)",
        "risk_assessment": r"(?:Risk Assessment|4\. Risk Assessment)[:\s]+(.*?)(?=(?:Resource Requirements|5\. Resource Requirements)|$)",
        "resource_requirements": r"(?:Resource Requirements|5\. Resource Requirements)[:\s]+(.*?)(?=(?:Implementation Plan|6\. Implementation Plan)|$)",
        "implementation_plan": r"(?:Implementation Plan|6\. Implementation Plan)[:\s]+(.*?)(?=(?:Success Metrics|7\. Success Metrics)|$)",
        "success_metrics": r"(?:Success Metrics|7\. Success Metrics)[:\s]+(.*?)(?=$)"
    }
    
    # Extract each section
    for section, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[section] = match.group(1).strip()
    
    return sections 