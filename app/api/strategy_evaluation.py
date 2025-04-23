# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import re
import logging

from llms.llm_service import LLMService
from config_service import ConfigService
from llms.model_config import ModelConfig

router = APIRouter()
logger = logging.getLogger(__name__)

class StrategyEvaluationRequest(BaseModel):
    companyName: str
    frameworks: List[str]
    strategy: Optional[str] = None
    additionalContext: Optional[str] = None
    document: Optional[str] = None

class StrategyEvaluationResponse(BaseModel):
    swot: Optional[dict] = None
    pestel: Optional[dict] = None
    ansoff: Optional[dict] = None
    bcg: Optional[dict] = None
    value_proposition: Optional[dict] = None
    value_chain: Optional[dict] = None
    five_forces: Optional[dict] = None
    comparative_advantage: Optional[dict] = None

@router.post("/strategy/evaluate")
async def evaluate_strategy(request: StrategyEvaluationRequest):
    try:
        config_service = ConfigService()
        
        # Get the Perplexity model configuration
        perplexity_model_config = config_service.get_model("perplexity-sonar-pro")
        if not perplexity_model_config:
            logger.error("Perplexity model configuration not found")
            raise HTTPException(
                status_code=500,
                detail="Perplexity model configuration not found"
            )
            
        # Initialize LLMService with the Perplexity model configuration
        llm_service = LLMService(config_service)
        llm_service.model_config = perplexity_model_config
        llm_service.chat_client = llm_service.chat_client_factory.new_chat_client(perplexity_model_config)

        # Construct the prompt for strategy evaluation
        strategy_context = f"""
Strategy to evaluate:
{request.strategy if request.strategy else 'No specific strategy provided. Please analyze the company based on available information.'}
""" if request.strategy else ""

        prompt = f"""You are a business strategy expert. Evaluate {request.companyName} using the following frameworks: {', '.join(request.frameworks)}.

{strategy_context}
Additional Context: {request.additionalContext if request.additionalContext else 'None provided'}

Please provide a comprehensive evaluation using the selected frameworks. For each framework, analyze the company and provide detailed insights based on current market trends, industry best practices, and real-world examples.

Format the response as a JSON object with the following structure:
{{
    "swot": {{
        "strengths": ["strength1", "strength2", ...],
        "weaknesses": ["weakness1", "weakness2", ...],
        "opportunities": ["opportunity1", "opportunity2", ...],
        "threats": ["threat1", "threat2", ...]
    }},
    "pestel": {{
        "political": ["factor1", "factor2", ...],
        "economic": ["factor1", "factor2", ...],
        "social": ["factor1", "factor2", ...],
        "technological": ["factor1", "factor2", ...],
        "environmental": ["factor1", "factor2", ...],
        "legal": ["factor1", "factor2", ...]
    }},
    "ansoff": {{
        "market_penetration": ["strategy1", "strategy2", ...],
        "market_development": ["strategy1", "strategy2", ...],
        "product_development": ["strategy1", "strategy2", ...],
        "diversification": ["strategy1", "strategy2", ...]
    }},
    "bcg": {{
        "stars": ["product1", "product2", ...],
        "question_marks": ["product1", "product2", ...],
        "cash_cows": ["product1", "product2", ...],
        "dogs": ["product1", "product2", ...]
    }},
    "value_proposition": {{
        "customer_profile": {{
            "jobs": ["job1", "job2", ...],
            "pains": ["pain1", "pain2", ...],
            "gains": ["gain1", "gain2", ...]
        }},
        "value_map": {{
            "products_services": ["product1", "product2", ...],
            "pain_relievers": ["reliever1", "reliever2", ...],
            "gain_creators": ["creator1", "creator2", ...]
        }}
    }},
    "value_chain": {{
        "primary_activities": ["activity1", "activity2", ...],
        "support_activities": ["activity1", "activity2", ...]
    }},
    "five_forces": {{
        "threat_of_new_entrants": ["factor1", "factor2", ...],
        "bargaining_power_of_suppliers": ["factor1", "factor2", ...],
        "bargaining_power_of_buyers": ["factor1", "factor2", ...],
        "threat_of_substitutes": ["factor1", "factor2", ...],
        "competitive_rivalry": ["factor1", "factor2", ...]
    }},
    "comparative_advantage": {{
        "resources": ["resource1", "resource2", ...],
        "capabilities": ["capability1", "capability2", ...],
        "competitive_advantages": ["advantage1", "advantage2", ...]
    }}
}}

IMPORTANT: 
1. Your response must be a valid JSON object with the exact structure shown above.
2. Only include the frameworks that were requested in the evaluation.
3. Do not include any additional text before or after the JSON object.
4. Provide specific, actionable insights based on current market data and trends.
5. Include relevant examples and case studies where applicable.
6. Consider the company's industry, market position, and competitive landscape.
7. If no specific strategy is provided, analyze the company based on available information and market research.
"""

        # Generate the evaluation using the Perplexity model
        try:
            response = await llm_service.generate_response(prompt)
            logger.info("Successfully generated response from Perplexity model")
        except Exception as e:
            logger.error(f"Error generating response from Perplexity model: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating response from Perplexity model: {str(e)}"
            )
        
        # Parse and validate the response
        try:
            # Try to extract JSON from the response
            json_data = extract_json_from_response(response)
            
            if json_data:
                # Filter the response to only include requested frameworks
                filtered_data = {}
                for framework in request.frameworks:
                    if framework in json_data:
                        filtered_data[framework] = json_data[framework]
                
                return {"data": filtered_data}
            else:
                logger.error("Failed to parse evaluation response - no valid JSON found")
                logger.debug(f"Raw response: {response}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to parse evaluation response - no valid JSON found"
                )
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.debug(f"Raw response: {response}")
            raise HTTPException(
                status_code=500,
                detail=f"Error parsing evaluation response: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {str(e)}")
            logger.debug(f"Raw response: {response}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error parsing evaluation response: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating strategy: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating strategy: {str(e)}"
        )

def extract_json_from_response(response):
    """Extract JSON from the response text."""
    if not response:
        return None
        
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
            # Remove any leading/trailing whitespace
            json_str = json_str.strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error after cleanup: {str(e)}")
                logger.debug(f"Cleaned JSON string: {json_str}")
                return None
    
    return None 