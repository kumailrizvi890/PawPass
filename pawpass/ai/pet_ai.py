"""
AI integration module for PawPass
"""
import logging
import os
import json
from enum import Enum
from datetime import datetime, timedelta
from openai import OpenAI
from .model_config import ModelType, ModelConfig

# Setup logging
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """AI service provider options"""
    OPENAI = "openai"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    MOCK = "mock"  # For development/testing

class AIService:
    """AI service for pet care recommendations and analysis"""
    
    def __init__(self):
        """Initialize the AI service with configuration from environment variables"""
        self.provider = os.environ.get("AI_PROVIDER", AIProvider.OPENAI.value)
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        
        # Initialize OpenAI client if we have an API key
        self.client = None
        if self.api_key and self.provider == AIProvider.OPENAI.value:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        else:
            logger.warning("OpenAI client not initialized (no API key or different provider)")
        
        logger.info(f"AI service initialized with provider: {self.provider}")
    
    def get_recommendations(self, pet_id, recommendation_type, recent_days=30):
        """
        Get care recommendations for a pet
        
        Args:
            pet_id: ID of the pet
            recommendation_type: Type of recommendation to get (diet, activity, etc.)
            recent_days: Number of recent days to consider
            
        Returns:
            list: List of recommendation objects
        """
        logger.debug(f"Getting {recommendation_type} recommendations for pet {pet_id}")
        
        try:
            # Import here to avoid circular imports
            from models import Pet, PetUpdate
            from app import app
            
            with app.app_context():
                # Get pet data
                pet = Pet.query.get(pet_id)
                if not pet:
                    logger.error(f"Pet with ID {pet_id} not found")
                    return []
                
                # Get recent updates
                cutoff_date = datetime.now() - timedelta(days=recent_days)
                updates = PetUpdate.query.filter(
                    PetUpdate.pet_id == pet_id,
                    PetUpdate.created_at >= cutoff_date
                ).order_by(PetUpdate.created_at.desc()).all()
                
                update_texts = [f"Date: {u.update_date} Time: {u.update_time} - {u.update_text}" for u in updates]
                
                # Prepare prompt
                prompt = ModelConfig.get_prompt_template("pet_recommendation").format(
                    pet_name=pet.name,
                    pet_species=pet.species,
                    pet_age=pet.age or "Unknown",
                    health_conditions=pet.description or "No health conditions noted",
                    care_history="\n".join(update_texts) or "No recent care history"
                )
                
                # Get recommendations from OpenAI
                if self.client:
                    config = ModelConfig.get_config(ModelType.RECOMMENDATION)
                    response = self.client.chat.completions.create(
                        model=config["model_name"],
                        temperature=config["temperature"],
                        max_tokens=config["max_tokens"],
                        messages=[
                            {"role": "system", "content": "You are a veterinary care expert providing helpful recommendations for pet care."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    
                    try:
                        return json.loads(response.choices[0].message.content)
                    except json.JSONDecodeError:
                        # If not valid JSON, return as plain text
                        return {"text": response.choices[0].message.content}
                else:
                    logger.error("OpenAI client not initialized, cannot get recommendations")
                    return {"error": "AI service unavailable"}
                
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return {"error": str(e)}
    
    def analyze_behavior(self, pet_id, timeframe="past_month"):
        """
        Analyze behavior patterns from updates
        
        Args:
            pet_id: ID of the pet
            timeframe: Timeframe to analyze
            
        Returns:
            dict: Analysis results
        """
        logger.debug(f"Analyzing behavior for pet {pet_id} over {timeframe}")
        
        try:
            # Import here to avoid circular imports
            from models import Pet, PetUpdate
            from app import app
            
            with app.app_context():
                # Get pet data
                pet = Pet.query.get(pet_id)
                if not pet:
                    logger.error(f"Pet with ID {pet_id} not found")
                    return {"error": "Pet not found"}
                
                # Get updates based on timeframe
                days = 30  # default to 30 days
                if timeframe == "past_week":
                    days = 7
                elif timeframe == "past_month":
                    days = 30
                elif timeframe == "past_quarter":
                    days = 90
                
                cutoff_date = datetime.now() - timedelta(days=days)
                updates = PetUpdate.query.filter(
                    PetUpdate.pet_id == pet_id,
                    PetUpdate.created_at >= cutoff_date
                ).order_by(PetUpdate.created_at).all()
                
                if not updates:
                    return {"summary": "No updates available for analysis"}
                
                update_texts = [f"Date: {u.update_date} Time: {u.update_time} - {u.update_text}" for u in updates]
                
                # Prepare prompt
                prompt = ModelConfig.get_prompt_template("behavior_analysis").format(
                    pet_name=pet.name,
                    pet_species=pet.species,
                    updates="\n".join(update_texts)
                )
                
                # Get analysis from OpenAI
                if self.client:
                    config = ModelConfig.get_config(ModelType.BEHAVIOR)
                    response = self.client.chat.completions.create(
                        model=config["model_name"],
                        temperature=config["temperature"],
                        max_tokens=config["max_tokens"],
                        messages=[
                            {"role": "system", "content": "You are a pet behavior analyst providing insights based on pet care records."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    
                    try:
                        return json.loads(response.choices[0].message.content)
                    except json.JSONDecodeError:
                        # If not valid JSON, return as plain text
                        return {"text": response.choices[0].message.content}
                else:
                    logger.error("OpenAI client not initialized, cannot analyze behavior")
                    return {"error": "AI service unavailable"}
                
        except Exception as e:
            logger.error(f"Error analyzing behavior: {e}")
            return {"error": str(e)}
    
    def process_text(self, update_text):
        """
        Process and analyze update text
        
        Args:
            update_text: Text to analyze
            
        Returns:
            dict: Analysis results
        """
        logger.debug(f"Processing text: '{update_text[:50]}...'")
        
        try:
            if not update_text or len(update_text.strip()) < 10:
                return {"error": "Text too short for analysis"}
            
            # Prepare prompt
            prompt = ModelConfig.get_prompt_template("update_analysis").format(
                update_text=update_text
            )
            
            # Get analysis from OpenAI
            if self.client:
                config = ModelConfig.get_config(ModelType.NLP)
                response = self.client.chat.completions.create(
                    model=config["model_name"],
                    temperature=config["temperature"],
                    max_tokens=config["max_tokens"],
                    messages=[
                        {"role": "system", "content": "You are an assistant that extracts key information from pet care updates."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                try:
                    return json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    # If not valid JSON, return as plain text
                    return {"text": response.choices[0].message.content}
            else:
                logger.error("OpenAI client not initialized, cannot process text")
                return {"error": "AI service unavailable"}
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return {"error": str(e)}
            
    def get_care_instructions(self, species, care_type):
        """
        Get care instructions for a specific pet species and care type
        
        Args:
            species: Pet species (dog, cat, etc.)
            care_type: Type of care (litter_box, feeding, etc.)
            
        Returns:
            dict: Care instructions
        """
        logger.debug(f"Getting {care_type} instructions for {species}")
        
        try:
            # Prepare prompt
            prompt = f"""
            Provide detailed care instructions for a {species} regarding {care_type}.
            Include step-by-step instructions, best practices, and common mistakes to avoid.
            Format your response as a helpful guide for a pet caretaker who may be new to this responsibility.
            """
            
            # Get instructions from OpenAI
            if self.client:
                config = ModelConfig.get_config(ModelType.RECOMMENDATION)
                response = self.client.chat.completions.create(
                    model=config["model_name"],
                    temperature=0.5,
                    max_tokens=800,
                    messages=[
                        {"role": "system", "content": "You are a veterinary expert providing helpful pet care instructions."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                try:
                    return json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    # If not valid JSON, return as plain text
                    return {"text": response.choices[0].message.content}
            else:
                logger.error("OpenAI client not initialized, cannot get care instructions")
                return {"error": "AI service unavailable"}
                
        except Exception as e:
            logger.error(f"Error getting care instructions: {e}")
            return {"error": str(e)}