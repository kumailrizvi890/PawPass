"""
Utility functions for the PawPass application
"""
import os
import logging
import json
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from PIL import Image

# Setup logging
logger = logging.getLogger(__name__)

def create_default_enhanced_checklist_items(db, EnhancedChecklistItem):
    """Create default enhanced checklist items if none exist"""
    if EnhancedChecklistItem.query.count() == 0:
        default_items = [
            # Medication items
            EnhancedChecklistItem(
                description="Morning Medication",
                item_type="medication",
                is_default=True,
                options=json.dumps(["Given", "Not Required", "Refused"]),
                frequency="daily"
            ),
            EnhancedChecklistItem(
                description="Evening Medication",
                item_type="medication",
                is_default=True,
                options=json.dumps(["Given", "Not Required", "Refused"]),
                frequency="daily"
            ),
            EnhancedChecklistItem(
                description="Special Medication",
                item_type="medication",
                is_default=True,
                options=json.dumps(["Given", "Not Required", "Refused"]),
                frequency="as needed"
            ),
            
            # Feeding items
            EnhancedChecklistItem(
                description="Morning Feed",
                item_type="feeding",
                is_default=True,
                options=json.dumps(["All Eaten", "Partially Eaten", "Not Eaten", "Not Required"]),
                unit="cups",
                frequency="daily"
            ),
            EnhancedChecklistItem(
                description="Evening Feed",
                item_type="feeding",
                is_default=True,
                options=json.dumps(["All Eaten", "Partially Eaten", "Not Eaten", "Not Required"]),
                unit="cups",
                frequency="daily"
            ),
            EnhancedChecklistItem(
                description="Treats/Supplements",
                item_type="feeding",
                is_default=True,
                options=json.dumps(["Given", "Not Required"]),
                frequency="as needed"
            ),
            
            # Water intake
            EnhancedChecklistItem(
                description="Water Intake",
                item_type="water",
                is_default=True,
                options=json.dumps(["Normal", "Increased", "Decreased", "None"]),
                frequency="daily"
            ),
            EnhancedChecklistItem(
                description="Water Bowl Cleaned",
                item_type="water",
                is_default=True,
                options=json.dumps(["Yes", "No"]),
                frequency="daily"
            ),
            
            # Litter/bathroom items
            EnhancedChecklistItem(
                description="Litter Box Cleaned",
                item_type="litter",
                is_default=True,
                options=json.dumps(["Yes", "No", "Not Applicable"]),
                species_applicable="cat",
                frequency="daily"
            ),
            EnhancedChecklistItem(
                description="Bathroom Break",
                item_type="bathroom",
                is_default=True,
                options=json.dumps(["Normal", "Diarrhea", "Constipation", "Not Observed"]),
                frequency="daily"
            ),
            EnhancedChecklistItem(
                description="Urination",
                item_type="bathroom",
                is_default=True,
                options=json.dumps(["Normal", "Frequent", "Infrequent", "Difficult", "Not Observed"]),
                frequency="daily"
            ),
            
            # Exercise/Enrichment
            EnhancedChecklistItem(
                description="Exercise Session",
                item_type="exercise",
                is_default=True,
                options=json.dumps(["Completed", "Partial", "Refused", "Not Required"]),
                frequency="daily"
            ),
            EnhancedChecklistItem(
                description="Enrichment Activity",
                item_type="enrichment",
                is_default=True,
                options=json.dumps(["Completed", "Partial", "Refused", "Not Required"]),
                frequency="daily"
            ),
            
            # Grooming
            EnhancedChecklistItem(
                description="Grooming",
                item_type="grooming",
                is_default=True,
                options=json.dumps(["Completed", "Partial", "Not Required"]),
                frequency="weekly"
            ),
        ]
        
        for item in default_items:
            db.session.add(item)
        
        try:
            db.session.commit()
            logger.info(f"Added {len(default_items)} default enhanced checklist items")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding default enhanced checklist items: {e}")


def generate_ai_summary(pet, days=7):
    """Generate an AI summary of recent pet updates"""
    try:
        from models import PetUpdate
        from pawpass.ai.pet_ai import AIService
        
        ai_service = AIService()
        
        # Get recent updates
        cutoff_date = datetime.now().date() - timedelta(days=days)
        updates = PetUpdate.query.filter(
            PetUpdate.pet_id == pet.id,
            PetUpdate.update_date >= cutoff_date
        ).order_by(PetUpdate.update_date.desc(), PetUpdate.update_time.desc()).all()
        
        if not updates:
            return {"error": "No recent updates found for AI summary"}
        
        update_texts = [f"Date: {u.update_date} Time: {u.update_time} - {u.update_text}" for u in updates]
        
        # Get care summary from AI
        template_args = {
            "pet_name": pet.name,
            "pet_species": pet.species,
            "updates": "\n".join(update_texts)
        }
        
        # Get prompt template
        from pawpass.ai.model_config import ModelConfig
        prompt = ModelConfig.get_prompt_template("care_summary").format(**template_args)
        
        # Make API call
        result = ai_service.process_text(prompt)
        return result
        
    except Exception as e:
        logger.error(f"Error generating AI summary: {e}")
        return {"error": str(e)}


def analyze_weight_trend(pet):
    """Analyze weight trend for a pet"""
    try:
        from models import WeightRecord
        from pawpass.ai.pet_ai import AIService
        
        ai_service = AIService()
        
        # Get weight records
        weight_records = WeightRecord.query.filter(
            WeightRecord.pet_id == pet.id
        ).order_by(WeightRecord.record_date.desc(), WeightRecord.record_time.desc()).all()
        
        if not weight_records or len(weight_records) < 2:
            return {"error": "Not enough weight records for analysis"}
        
        record_texts = [f"Date: {w.record_date} - Weight: {w.weight}kg" for w in weight_records]
        
        # Get weight trend analysis from AI
        template_args = {
            "pet_name": pet.name,
            "pet_species": pet.species,
            "pet_age": pet.age or "Unknown",
            "weight_records": "\n".join(record_texts)
        }
        
        # Get prompt template
        from pawpass.ai.model_config import ModelConfig
        prompt = ModelConfig.get_prompt_template("weight_trend_analysis").format(**template_args)
        
        # Make API call
        result = ai_service.process_text(prompt)
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing weight trend: {e}")
        return {"error": str(e)}


def get_pet_care_instructions(species, care_type):
    """Get AI-generated care instructions for a pet"""
    try:
        from pawpass.ai.pet_ai import AIService
        
        ai_service = AIService()
        return ai_service.get_care_instructions(species, care_type)
        
    except Exception as e:
        logger.error(f"Error getting care instructions: {e}")
        return {"error": str(e)}