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
        # Get the API key from environment variables
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        
        if self.api_key:
            logging.info(f"Using Google API key: {self.api_key[:5]}...")
        else:
            logging.warning("No Google API key found.")
            
        self.client = None
        
        # Initialize Gemini client if API key is available
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Using gemini-1.5-pro which is the currently supported model
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                self.provider = AIProvider.GEMINI
                logger.info("Successfully initialized AI service with Gemini provider")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
                # Fallback to mock provider
                self.provider = AIProvider.MOCK
                logger.warning("Using mock AI provider as fallback")
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
                logger.warning("Using mock provider instead of real AI service")
                return {
                    "text": "AI analysis not available. Please configure Gemini API key.",
                    "is_mock": True
                }
            
            # Check API key again
            if not self.api_key:
                logger.error("API key is missing when trying to process text")
                return {
                    "error": "API key is missing",
                    "text": "The AI service is not properly configured. Please contact support.",
                    "is_mock": False
                }
            
            # Get config
            from pawpass.ai.model_config import ModelType, ModelConfig
            config = ModelConfig.get_config(ModelType.RECOMMENDATION)
            
            # Make API call - add extra debug logging
            logger.info(f"Making Gemini API call with API key starting with: {self.api_key[:5]}...")
            logger.debug(f"Sending prompt (first 100 chars): {prompt[:100]}...")
            
            # Initialize model again in case of any issues
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": config['temperature'],
                    "max_output_tokens": config['max_tokens'],
                }
            )
            
            # Check if response is valid
            if not response or not hasattr(response, 'text'):
                logger.error(f"Invalid response from Gemini: {response}")
                return {
                    "error": "Invalid response from AI service",
                    "text": "I received an incomplete response. Please try again.",
                    "is_mock": False
                }
            
            # Process response
            result = {
                "text": response.text,
                "model": "gemini-1.5-pro",
                "is_mock": False
            }
            
            logger.info("Successfully processed AI request")
            logger.debug(f"AI response (first 100 chars): {response.text[:100]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing text with AI: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return {
                "error": str(e),
                "text": "I encountered an error while processing your question. Please try again with a different question.",
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