"""
AI model configuration for PawPass
"""
from enum import Enum

class ModelType(Enum):
    """Types of AI models used in the application"""
    NLP = "nlp"
    RECOMMENDATION = "recommendation"
    BEHAVIOR = "behavior"
    IMAGE = "image"

class ModelConfig:
    """Configuration for AI models"""
    
    DEFAULT_CONFIGS = {
        ModelType.NLP: {
            "model_name": "gemini-1.5-pro",
            "temperature": 0.0,
            "max_tokens": 150,
            "dimensions": 1536
        },
        ModelType.RECOMMENDATION: {
            "model_name": "gemini-1.5-pro",
            "temperature": 0.3,
            "max_tokens": 500
        },
        ModelType.BEHAVIOR: {
            "model_name": "gemini-1.5-pro",
            "temperature": 0.1,
            "max_tokens": 1000
        },
        ModelType.IMAGE: {
            "model_name": "gemini-1.5-pro",
            "size": "1024x1024",
            "quality": "standard",
            "style": "natural"
        }
    }
    
    PROMPT_TEMPLATES = {
        "care_summary": """
        Please analyze the following updates for {pet_name}, a {pet_species}, and provide a concise care summary.
        Focus on health trends, behavior patterns, medication compliance, and dietary observations.
        Keep your response under 300 words and organize it by topics.
        
        UPDATES:
        {updates}
        """,
        
        "weight_trend_analysis": """
        Please analyze the following weight records for {pet_name}, a {pet_species} (age: {pet_age}).
        Provide insights on:
        1. Overall weight trend (increasing, decreasing, stable)
        2. Rate of change
        3. Potential health implications
        4. Recommendations for monitoring
        
        Keep your response under 250 words, be factual, and highlight any concerning patterns.
        
        WEIGHT RECORDS:
        {weight_records}
        """,
        
        "care_instructions": {
            "feeding": """
            Provide evidence-based feeding guidelines for a {species}. Include information on:
            - Recommended food types
            - Portion sizes by weight/age
            - Feeding frequency
            - Common nutritional requirements
            - Foods to avoid
            - Signs of feeding issues to watch for
            
            Make this practical for an animal shelter or foster volunteer.
            """,
            
            "medication": """
            Provide general medication administration guidance for a {species}. Include:
            - Best practices for administering different medication types (pills, liquids, topicals)
            - Techniques for difficult animals
            - Common signs of adverse reactions
            - Medication tracking tips
            
            Make this practical for an animal shelter or foster volunteer.
            """,
            
            "litter_box": """
            Provide comprehensive litter box/bathroom management guidelines for a {species}. Include:
            - Recommended cleaning frequency
            - Ideal placement
            - Signs of potential health issues
            - Normal vs. abnormal bathroom behavior
            - How to handle accidents
            
            Make this practical for an animal shelter or foster volunteer.
            """,
            
            "exercise": """
            Provide guidelines for exercise and enrichment activities for a {species}. Include:
            - Age-appropriate exercise needs
            - Indoor and outdoor activity suggestions
            - Mental stimulation techniques
            - Signs of over-exertion
            - How to gauge appropriate exercise levels
            
            Make this practical for an animal shelter or foster volunteer.
            """
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
        if model_type in ModelConfig.DEFAULT_CONFIGS:
            return ModelConfig.DEFAULT_CONFIGS[model_type]
        else:
            raise ValueError(f"Invalid model type: {model_type}")
    
    @staticmethod
    def get_prompt_template(template_name, care_type=None):
        """
        Get a prompt template by name
        
        Args:
            template_name: Name of the template
            care_type: Type of care instructions if template_name is 'care_instructions'
            
        Returns:
            str: Prompt template text
        """
        if template_name == 'care_instructions':
            if care_type in ModelConfig.PROMPT_TEMPLATES[template_name]:
                return ModelConfig.PROMPT_TEMPLATES[template_name][care_type]
            else:
                raise ValueError(f"Invalid care type: {care_type}")
        elif template_name in ModelConfig.PROMPT_TEMPLATES:
            return ModelConfig.PROMPT_TEMPLATES[template_name]
        else:
            raise ValueError(f"Invalid template name: {template_name}")