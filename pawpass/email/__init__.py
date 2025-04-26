"""
Email service module for PawPass
"""
from pawpass.email.email_service import (
    EmailService, 
    EmailTemplate, 
    EmailProvider
)

# Create a singleton instance of the email service
email_service = EmailService()

# Export functions that use the singleton
def send_notification(recipient, subject, template, context=None):
    """Send a notification email"""
    return email_service.send_notification(recipient, subject, template, context)

def create_reminder(recipient, schedule, pet_id, reminder_type):
    """Schedule a reminder email"""
    return email_service.create_reminder(recipient, schedule, pet_id, reminder_type)

def get_template(template_name):
    """Get an email template by name"""
    return email_service.get_template(template_name)

__all__ = [
    'EmailService',
    'EmailTemplate',
    'EmailProvider',
    'email_service',
    'send_notification',
    'create_reminder',
    'get_template'
]