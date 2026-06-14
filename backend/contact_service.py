from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

contact_router = APIRouter()

class LawyerContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    lawyer_type: str
    budget: str
    case_description: str

@contact_router.post("/contact_lawyer")
async def contact_lawyer(request: LawyerContactRequest):
    """Send lawyer contact request to admin email"""
    try:
        # Email configuration
        admin_email = "shankardarur158@gmail.com"
        
        # Create email content
        subject = f"New Lawyer Consultation Request - {request.lawyer_type}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                    <h2 style="color: #fbbf24; border-bottom: 2px solid #fbbf24; padding-bottom: 10px;">
                        New Lawyer Consultation Request
                    </h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 20px;">
                        <h3 style="color: #333; margin-top: 0;">Client Information</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px; font-weight: bold; width: 150px;">Name:</td>
                                <td style="padding: 8px;">{request.name}</td>
                            </tr>
                            <tr style="background-color: #f5f5f5;">
                                <td style="padding: 8px; font-weight: bold;">Email:</td>
                                <td style="padding: 8px;">{request.email}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Phone:</td>
                                <td style="padding: 8px;">{request.phone}</td>
                            </tr>
                            <tr style="background-color: #f5f5f5;">
                                <td style="padding: 8px; font-weight: bold;">Lawyer Type:</td>
                                <td style="padding: 8px;"><strong>{request.lawyer_type}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Budget:</td>
                                <td style="padding: 8px;"><strong>{request.budget}</strong></td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 15px;">
                        <h3 style="color: #333; margin-top: 0;">Case Description</h3>
                        <p style="white-space: pre-wrap; background: #f9f9f9; padding: 15px; border-left: 4px solid #fbbf24; border-radius: 4px;">
                            {request.case_description}
                        </p>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #fbbf24;">
                        <p style="margin: 0; font-size: 14px;">
                            <strong>Action Required:</strong> Please contact the client within 24 hours to discuss their case.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Try to send email notification
        try:
            import requests
            
            # Option 1: Try webhook notification (if configured)
            webhook_url = os.getenv("WEBHOOK_URL")
            
            if webhook_url:
                # Send to webhook (e.g., Discord, Slack, or custom endpoint)
                payload = {
                    "content": f"🔔 **New Lawyer Consultation Request**\n\n"
                               f"**Name:** {request.name}\n"
                               f"**Email:** {request.email}\n"
                               f"**Phone:** {request.phone}\n"
                               f"**Type:** {request.lawyer_type}\n"
                               f"**Budget:** {request.budget}\n"
                               f"**Description:** {request.case_description}"
                }
                
                response = requests.post(webhook_url, json=payload, timeout=5)
                
                if response.status_code == 200:
                    logger.info(f"Webhook notification sent for {request.email}")
                    return {
                        "success": True,
                        "message": "Your request has been sent successfully! We'll contact you within 24 hours."
                    }
            
            # Option 2: Email via SendGrid/Mailgun API (if configured)
            sendgrid_key = os.getenv("SENDGRID_API_KEY")
            
            if sendgrid_key:
                # Use SendGrid HTTP API
                response = requests.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {sendgrid_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "personalizations": [{"to": [{"email": admin_email}]}],
                        "from": {"email": "noreply@specter.app"},
                        "subject": subject,
                        "content": [{"type": "text/html", "value": html_content}]
                    },
                    timeout=10
                )
                
                if response.status_code == 202:
                    logger.info(f"SendGrid email sent for {request.email}")
                    return {
                        "success": True,
                        "message": "Your request has been sent successfully! We'll contact you within 24 hours."
                    }
            
            # Fallback: Log the request and send email to admin manually
            logger.warning("⚠️ EMAIL SERVICE NOT CONFIGURED - REQUEST LOGGED BELOW:")
            logger.info(f"""
            ═══════════════════════════════════════════════════════
            📧 NEW LAWYER CONSULTATION REQUEST
            ═══════════════════════════════════════════════════════
            Name: {request.name}
            Email: {request.email}
            Phone: {request.phone}
            Lawyer Type: {request.lawyer_type}
            Budget: {request.budget}
            Description: {request.case_description}
            ═══════════════════════════════════════════════════════
            """)
            
            return {
                "success": True,
                "message": "Your request has been received! We'll contact you within 24 hours."
            }
                
        except Exception as error:
            logger.error(f"Email service error: {error}")
            # Always log the request so you don't lose it
            logger.info(f"Lawyer Request (logged): {request.dict()}")
            return {
                "success": True,
                "message": "Your request has been received! We'll contact you soon."
            }
            
    except Exception as e:
        logger.error(f"Contact lawyer error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send request. Please try again.")
