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
            """
        }
        
        return TEMPLATES.get(template_name, "")