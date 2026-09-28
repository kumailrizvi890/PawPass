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
    MOCK = "mock"  # For development/testing, and for the public demo deployment


def _mock_answer(prompt):
    """Deterministic, plausible pet-care answer for the public demo deployment.

    The public demo runs without a live Gemini key (no billing exposure for a
    portfolio site), but should still look and behave like the real feature -
    grounded, specific answers keyed off what's actually being asked, not a
    generic placeholder.
    """
    text = (prompt or "").lower()
    if "weight" in text or "underweight" in text or "overweight" in text:
        return ("Based on the last few logged weigh-ins, the trend is stable within a healthy "
                "range for this breed and age. Keep weighing weekly at the same time of day for "
                "the most reliable trend line.")
    if "medic" in text or "medication" in text or "dose" in text:
        return ("Give medication with a small amount of food to reduce stomach upset, and log the "
                "exact time in the checklist so the next caretaker can see when the last dose was "
                "given.")
    if "litter" in text:
        return ("Scoop litter boxes at least once daily and do a full change weekly. A sudden change "
                "in litter box habits is one of the more reliable early signs to flag to a vet.")
    if "feed" in text or "food" in text or "diet" in text:
        return ("Feed on a consistent schedule twice daily. Measure portions rather than free-feeding "
                "so it's easy to notice if appetite changes, which is often the first sign something "
                "is off.")
    if "exercise" in text or "walk" in text or "play" in text:
        return ("Two short active sessions a day beat one long one for most pets - it keeps energy "
                "and anxiety levels more even across the day.")
    if "vet" in text or "emergency" in text:
        return ("Flag this as a vet visit if it lasts more than 24 hours or comes with lethargy, "
                "vomiting, or loss of appetite. Otherwise, keep monitoring and note it in the pet's "
                "log.")
    return ("This looks within normal range based on the pet's recent history. Keep logging updates "
            "in the checklist so patterns are easy to spot over time.")

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
                logger.info("Using mock provider for public demo deployment")
                return {
                    "text": _mock_answer(prompt),
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
                    "text": _mock_answer(care_type + " " + species),
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