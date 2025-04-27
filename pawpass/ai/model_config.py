"""
AI model configuration for PawPass
"""
import os
from enum import Enum

class ModelType(Enum):
    """Types of AI models used in the application"""
    NLP = "nlp"
    RECOMMENDATION = "recommendation"
    BEHAVIOR = "behavior"
    IMAGE = "image"

class ModelConfig:
    """Configuration for AI models"""
    
    # Default model configurations
    DEFAULT_CONFIGS = {
        ModelType.NLP: {
            "model_name": "text-embedding-3-small",
            "temperature": 0.0,
            "max_tokens": 150,
            "dimensions": 1536
        },
        ModelType.RECOMMENDATION: {
            "model_name": "gpt-4o",
            "temperature": 0.3,
            "max_tokens": 500
        },
        ModelType.BEHAVIOR: {
            "model_name": "gpt-4o",
            "temperature": 0.1,
            "max_tokens": 1000
        },
        ModelType.IMAGE: {
            "model_name": "dall-e-3",
            "size": "1024x1024",
            "quality": "standard",
            "style": "natural"
        }
    }
    
    @staticmethod
    def get_config(model_type):
        """
        Get configuration for a specific model type
        
        Args:
            model_type: Type of model (ModelType enum)
            
        Returns:
            dict: Model configuration
        """
        # Get default config
        config = ModelConfig.DEFAULT_CONFIGS.get(model_type, {}).copy()
        
        # Override with environment variables if available
        env_prefix = f"AI_MODEL_{model_type.value.upper()}_"
        for key in config:
            env_var = env_prefix + key.upper()
            if env_var in os.environ:
                config[key] = os.environ[env_var]
                
                # Convert to appropriate type
                if isinstance(config[key], int):
                    config[key] = int(os.environ[env_var])
                elif isinstance(config[key], float):
                    config[key] = float(os.environ[env_var])
        
        return config

    @staticmethod
    def get_prompt_template(template_name):
        """
        Get a prompt template by name
        
        Args:
            template_name: Name of the template
            
        Returns:
            str: Prompt template text
        """
        # Basic prompt templates
        TEMPLATES = {
            "pet_recommendation": """
            Based on the following pet information and care history, provide care recommendations:
            
            Pet: {pet_name}
            Species: {pet_species}
            Age: {pet_age}
            Health conditions: {health_conditions}
            
            Recent care history:
            {care_history}
            
            Please provide specific recommendations for:
            - Diet
            - Exercise
            - Medication
            - Behavioral enrichment
            
            Format your response as a JSON object with the following structure:
            {
                "diet": [
                    {"recommendation": "string", "reason": "string", "importance": "high/medium/low"},
                    ...
                ],
                "exercise": [
                    {"recommendation": "string", "reason": "string", "importance": "high/medium/low"},
                    ...
                ],
                "medication": [
                    {"recommendation": "string", "reason": "string", "importance": "high/medium/low"},
                    ...
                ],
                "enrichment": [
                    {"recommendation": "string", "reason": "string", "importance": "high/medium/low"},
                    ...
                ],
                "summary": "A short summary of the key points"
            }
            """,
            
            "behavior_analysis": """
            Analyze the following pet updates to identify behavior patterns:
            
            Pet: {pet_name}
            Species: {pet_species}
            
            Updates:
            {updates}
            
            Please identify:
            - Recurring behaviors
            - Changes in behavior over time
            - Potential concerns
            - Improvement opportunities
            
            Format your response as a JSON object with the following structure:
            {
                "recurring_behaviors": [
                    {"behavior": "string", "frequency": "string", "context": "string"},
                    ...
                ],
                "behavior_changes": [
                    {"before": "string", "after": "string", "possible_cause": "string"},
                    ...
                ],
                "concerns": [
                    {"concern": "string", "reasoning": "string", "urgency": "high/medium/low"},
                    ...
                ],
                "opportunities": [
                    {"suggestion": "string", "benefit": "string", "implementation": "string"},
                    ...
                ],
                "summary": "A concise summary of the key behavior patterns and recommendations"
            }
            """,
            
            "update_analysis": """
            Analyze the following update from a volunteer:
            
            {update_text}
            
            Please extract:
            - Key activities performed
            - Pet's behavior
            - Health observations
            - Concerns or issues
            - Follow-up recommendations
            
            Format your response as a JSON object with the following structure:
            {
                "activities": [
                    {"activity": "string", "details": "string"},
                    ...
                ],
                "behaviors": [
                    {"behavior": "string", "context": "string"},
                    ...
                ],
                "health_observations": [
                    {"observation": "string", "significance": "string"},
                    ...
                ],
                "concerns": [
                    {"concern": "string", "urgency": "high/medium/low"},
                    ...
                ],
                "follow_up": [
                    {"recommendation": "string", "timeframe": "string"},
                    ...
                ],
                "summary": "A concise summary of the key information"
            }
            """,
            
            "care_summary": """
            Summarize the following pet care updates to provide a concise overview for handover between volunteers:
            
            Pet: {pet_name}
            Species: {pet_species}
            
            Updates (from most recent to oldest):
            {updates}
            
            Please create a concise summary that would be helpful for the next volunteer taking over care, including:
            - Key care routines established
            - Recent health observations
            - Behavioral notes
            - Important changes in the past few days
            - Current medication schedule (if any)
            - Feeding preferences and schedule
            - Special attention areas
            
            Format your response as a JSON object with the following structure:
            {
                "care_summary": "A concise overall summary (max 3 sentences)",
                "established_routines": [
                    {"routine": "string", "details": "string", "importance": "high/medium/low"},
                    ...
                ],
                "health_status": [
                    {"observation": "string", "action_needed": "string/null"},
                    ...
                ],
                "behavior_notes": [
                    {"behavior": "string", "handling_tip": "string"},
                    ...
                ],
                "feeding": {"schedule": "string", "preferences": "string", "restrictions": "string/null"},
                "medication": [
                    {"medication": "string", "schedule": "string", "instructions": "string", "last_given": "string"},
                    ...
                ],
                "priority_attention": {"area": "string", "reason": "string", "urgency": "high/medium/low"}
            }
            """,
            
            "weight_trend_analysis": """
            Analyze the following weight measurements for a pet:
            
            Pet: {pet_name}
            Species: {pet_species}
            Age: {pet_age}
            
            Weight records (from most recent to oldest):
            {weight_records}
            
            Please analyze the weight trends and provide insights:
            - Overall trend (gaining, losing, stable)
            - Rate of change
            - Healthiness of the current weight
            - Recommendations
            
            Format your response as a JSON object with the following structure:
            {
                "trend": "string (e.g., 'increasing', 'decreasing', 'stable')",
                "rate_of_change": "string (description of how quickly weight is changing)",
                "health_assessment": "string (assessment of whether current weight appears healthy)",
                "recommendations": [
                    {"recommendation": "string", "reasoning": "string", "priority": "high/medium/low"},
                    ...
                ],
                "summary": "A concise summary of the weight trend and key recommendations"
            }
            """
        }
        
        return TEMPLATES.get(template_name, "")