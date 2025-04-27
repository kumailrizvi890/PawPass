"""
AI integration module for PawPass
"""
import os
import json
import logging
from enum import Enum
import google.generativeai as genai

# Setup logging
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """AI service provider options"""
    GEMINI = "gemini"
    MOCK = "mock"  # For development/testing

class AIService:
    """AI service for pet care recommendations and analysis"""
    
    def __init__(self):
        """Initialize the AI service with configuration from environment variables"""
        self.api_key = os.environ.get("GOOGLE_API_KEY") or "AIzaSyDpNepFSAbJ832pxUH_qpmDBsjpXaw1K2c"
        self.client = None
        
        # Initialize Gemini client if API key is available
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.provider = AIProvider.GEMINI
            logger.info("Initialized AI service with Gemini provider")
        else:
            self.provider = AIProvider.MOCK
            logger.warning("No Gemini API key found. Using mock AI provider")
    
    def process_text(self, prompt):
        """
        Process and analyze text with AI
        
        Args:
            prompt: Text to analyze
            
        Returns:
            dict: Analysis results
        """
        try:
            if self.provider == AIProvider.MOCK:
                return {
                    "text": "AI analysis not available. Please configure Gemini API key.",
                    "is_mock": True
                }
            
            # Get config
            from pawpass.ai.model_config import ModelType, ModelConfig
            config = ModelConfig.get_config(ModelType.RECOMMENDATION)
            
            # Make API call
            logger.info("Making Gemini API call")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": config['temperature'],
                    "max_output_tokens": config['max_tokens'],
                }
            )
            
            # Process response
            result = {
                "text": response.text,
                "model": "gemini-pro",
                "is_mock": False
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing text with AI: {e}")
            return {
                "error": str(e),
                "text": "Error analyzing text. Please try again later.",
                "is_mock": False
            }
    
    def get_care_instructions(self, species, care_type):
        """
        Get care instructions for a specific pet species and care type
        
        Args:
            species: Pet species (dog, cat, etc.)
            care_type: Type of care (litter_box, feeding, etc.)
            
        Returns:
            dict: Care instructions
        """
        try:
            if self.provider == AIProvider.MOCK:
                return {
                    "text": f"Care instructions for {species} ({care_type}) not available. Please configure Gemini API key.",
                    "is_mock": True
                }
            
            # Get template
            from pawpass.ai.model_config import ModelConfig
            template = ModelConfig.get_prompt_template("care_instructions", care_type)
            prompt = template.format(species=species.lower())
            
            # Process with AI
            return self.process_text(prompt)
            
        except Exception as e:
            logger.error(f"Error getting care instructions: {e}")
            return {
                "error": str(e),
                "text": f"Error getting care instructions for {species} ({care_type}). Please try again later.",
                "is_mock": False
            }