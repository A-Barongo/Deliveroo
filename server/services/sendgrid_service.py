"""SendGrid email service for secure backend email functionality."""
import os
import requests
from flask import current_app
from typing import Dict, List, Optional

class SendGridService:
    """Secure SendGrid email service for backend."""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'deliveroo.dispatch@gmail.com')
        self.base_url = 'https://api.sendgrid.com/v3/mail/send'
        
        if not self.api_key:
            print("Warning: SENDGRID_API_KEY not found in environment variables")
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send email using SendGrid API."""
        if not self.api_key:
            print("Error: SendGrid API key not configured")
            return False
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'personalizations': [{'to': [{'email': to_email}]}],
            'from': {'email': self.from_email, 'name': 'Deliveroo Dispatch'},
            'subject': subject,
            'content': [{'type': 'text/html', 'value': html_content}]
        }
        
        # Add text content if provided
        if text_content:
            data['content'].append({'type': 'text/plain', 'value': text_content})
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            success = response.status_code == 202
            
            if not success:
                print(f"SendGrid API error: {response.status_code} - {response.text}")
            
            return success
        except Exception as e:
            print(f"SendGrid service error: {str(e)}")
            return False
    
    def send_parcel_created_email(self, user_email: str, parcel_data: Dict, username: str) -> bool:
        """Send parcel created email."""
        subject = f"Parcel #{parcel_data.get('id', 'N/A')} Created Successfully! 📦"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <h1 style="margin: 0;">🎉 Parcel Created!</h1>
                    <p style="margin: 10px 0;">Hello {username}, your parcel has been successfully created!</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <h2 style="color: #333; margin-top: 0;">📦 Parcel Details</h2>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Parcel ID:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('id', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Pickup Location:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('pickup_location_text', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Destination:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('destination_location_text', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Weight:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('weight', 'N/A')} kg</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Status:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('status', 'pending')}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/track/{parcel_data.get('id', '')}" 
                       style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        🚚 Track Your Parcel
                    </a>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 5px; font-size: 14px; color: #666;">
                    <p style="margin: 0;">Thank you for choosing Deliveroo! We'll keep you updated on your parcel's journey.</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_status_update_email(self, user_email: str, parcel_data: Dict, old_status: str, new_status: str) -> bool:
        """Send status update email."""
        subject = f"Parcel #{parcel_data.get('id', 'N/A')} Status Updated! 📊"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <h1 style="margin: 0;">📊 Status Update!</h1>
                    <p style="margin: 10px 0;">Your parcel status has been updated</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <h2 style="color: #333; margin-top: 0;">📦 Parcel Details</h2>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Parcel ID:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('id', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Previous Status:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{old_status}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>New Status:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #28a745; font-weight: bold;">{new_status}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/track/{parcel_data.get('id', '')}" 
                       style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        🚚 Track Your Parcel
                    </a>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_test_email(self, user_email: str) -> bool:
        """Send test email."""
        subject = "Test Email from Deliveroo 📧"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <h1 style="margin: 0;">✅ Test Email</h1>
                    <p style="margin: 10px 0;">This is a test email from your Deliveroo application</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <h2 style="color: #333; margin-top: 0;">🎉 Email Configuration Working!</h2>
                    <p>If you received this email, your SendGrid configuration is working correctly!</p>
                    <ul style="color: #666;">
                        <li>✅ SendGrid API connected</li>
                        <li>✅ Email templates working</li>
                        <li>✅ Backend email service active</li>
                    </ul>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 5px; font-size: 14px; color: #666;">
                    <p style="margin: 0;">This is a test email sent at {os.getenv('FRONTEND_URL', 'http://localhost:3000')}</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_parcel_cancelled_email(self, user_email: str, parcel_data: Dict, username: str) -> bool:
        """Send parcel cancelled email."""
        subject = f"Parcel #{parcel_data.get('id', 'N/A')} Cancelled! ❌"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <h1 style="margin: 0;">❌ Parcel Cancelled</h1>
                    <p style="margin: 10px 0;">Hello {username}, your parcel has been cancelled</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <h2 style="color: #333; margin-top: 0;">📦 Cancelled Parcel Details</h2>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Parcel ID:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('id', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Pickup Location:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('pickup_location_text', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Destination:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('destination_location_text', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Status:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #dc3545; font-weight: bold;">Cancelled</td>
                        </tr>
                    </table>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 5px; font-size: 14px; color: #666;">
                    <p style="margin: 0;">If you have any questions about this cancellation, please contact our support team.</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_location_update_email(self, user_email: str, parcel_data: Dict, old_location: str, new_location: str) -> bool:
        """Send location update email."""
        subject = f"Parcel #{parcel_data.get('id', 'N/A')} Location Updated! 📍"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <h1 style="margin: 0;">📍 Location Update!</h1>
                    <p style="margin: 10px 0;">Your parcel location has been updated</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <h2 style="color: #333; margin-top: 0;">📦 Parcel Details</h2>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Parcel ID:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('id', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Previous Location:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{old_location or 'Not set'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>New Location:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #17a2b8; font-weight: bold;">{new_location}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/track/{parcel_data.get('id', '')}" 
                       style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        🚚 Track Your Parcel
                    </a>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_destination_update_email(self, user_email: str, parcel_data: Dict, old_destination: str, new_destination: str) -> bool:
        """Send destination update email."""
        subject = f"Parcel #{parcel_data.get('id', 'N/A')} Destination Updated! 🎯"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <h1 style="margin: 0;">🎯 Destination Updated!</h1>
                    <p style="margin: 10px 0;">Your parcel destination has been updated</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <h2 style="color: #333; margin-top: 0;">📦 Parcel Details</h2>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Parcel ID:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{parcel_data.get('id', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Previous Destination:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{old_destination or 'Not set'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>New Destination:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #ffc107; font-weight: bold;">{new_destination}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/track/{parcel_data.get('id', '')}" 
                       style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        🚚 Track Your Parcel
                    </a>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)