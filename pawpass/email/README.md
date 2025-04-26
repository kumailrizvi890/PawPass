# Email Processing Module

## Overview

The Email Processing module handles all email-related functionality in PawPass, including sending notifications, processing incoming emails, and managing email templates. This module ensures reliable and consistent email communication with users.

## Features

- Email notifications for key events
- Templated emails for consistent messaging
- Scheduled email reminders
- Email processing for commands (future)
- HTML and plain text email support

## Components

### Email Sending

- Notification emails for system events
- Scheduled reminders for pet care
- Administrative notifications

### Email Templates

- HTML templates for various email types
- Template rendering with dynamic content
- Branding and style consistency

### Email Processing (Future)

- Processing incoming emails
- Command extraction and execution
- Reply handling

## Usage

```python
from pawpass.email import send_notification, create_reminder, get_template

# Send a notification email
send_notification(
    recipient="volunteer@example.com",
    subject="New Pet Update Required",
    template="update_reminder",
    context={
        "pet_name": "Buddy",
        "last_update": "3 days ago",
        "volunteer_name": "Jane"
    }
)

# Schedule a reminder
create_reminder(
    recipient="volunteer@example.com",
    schedule="daily",
    pet_id=123,
    reminder_type="feeding"
)

# Get and render a template
template = get_template("welcome_email")
rendered_email = template.render(user_name="New Volunteer", shelter_name="Happy Paws")
```

## Email Templates

The module includes the following email templates:

- **Welcome**: Sent to new users when they register
- **Password Reset**: Sent when a user requests a password reset
- **Update Reminder**: Reminds volunteers to add updates for pets
- **New Pet**: Notifies volunteers about a new pet in the system
- **Emergency Alert**: Notifies volunteers about a pet with emergency status
- **Checklist Completion**: Confirms checklist completion to volunteers

## Integration Points

- Authentication module: For user verification emails
- Core application: For sending notifications about pets and updates
- Database: For retrieving pet and user information

## Configuration

Email sending is configured through environment variables:

- `EMAIL_PROVIDER`: The email service provider (smtp, sendgrid, mailgun)
- `EMAIL_FROM`: The sender email address
- `EMAIL_REPLY_TO`: The reply-to email address
- `EMAIL_API_KEY`: API key for the email service (if applicable)
- `EMAIL_SMTP_HOST`: SMTP host (if using SMTP)
- `EMAIL_SMTP_PORT`: SMTP port (if using SMTP)
- `EMAIL_SMTP_USER`: SMTP username (if using SMTP)
- `EMAIL_SMTP_PASSWORD`: SMTP password (if using SMTP)

## Delivery Tracking

Email delivery status is tracked in the database:

- Sent status
- Delivery confirmations
- Opens and clicks (if supported by provider)
- Bounces and failures