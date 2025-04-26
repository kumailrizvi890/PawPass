"""
AI integration module for PawPass
"""
from pawpass.ai.pet_ai import (
    AIService,
    AIProvider
)

# Create a singleton instance of the AI service
ai_service = AIService()

# Export functions that use the singleton
def get_recommendations(pet_id, recommendation_type, recent_days=30):
    """Get care recommendations for a pet"""
    return ai_service.get_recommendations(pet_id, recommendation_type, recent_days)

def analyze_behavior(pet_id, timeframe="past_month"):
    """Analyze behavior patterns from updates"""
    return ai_service.analyze_behavior(pet_id, timeframe)

def process_text(update_text):
    """Process and analyze update text"""
    return ai_service.process_text(update_text)

__all__ = [
    'AIService',
    'AIProvider',
    'ai_service',
    'get_recommendations',
    'analyze_behavior',
    'process_text'
]