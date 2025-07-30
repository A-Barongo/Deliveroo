"""Email service for Deliveroo app."""
import os
from flask import current_app
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()

def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, html_body, text_body=None):
    """Send email using Flask-Mail."""
    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    if text_body:
        msg.body = text_body
    
    # Send email asynchronously
    Thread(target=send_async_email, args=(app, msg)).start()

def send_parcel_created_email(user_email, parcel_data):
    """Send email when parcel is created."""
    subject = f"Parcel #{parcel_data['id']} Created Successfully"
    html_body = f"""
    <html>
        <body>
            <h2>Your parcel has been created!</h2>
            <p><strong>Parcel ID:</strong> {parcel_data['id']}</p>
            <p><strong>Pickup Location:</strong> {parcel_data.get('pickup_location_text', 'N/A')}</p>
            <p><strong>Destination:</strong> {parcel_data.get('destination_location_text', 'N/A')}</p>
            <p><strong>Status:</strong> {parcel_data.get('status', 'pending')}</p>
            <p><strong>Created:</strong> {parcel_data.get('created_at', 'N/A')}</p>
            <br>
            <p>Track your parcel at: <a href="https://your-frontend-url.com/track/{parcel_data['id']}">Track Parcel</a></p>
        </body>
    </html>
    """
    send_email(subject, [user_email], html_body)

def send_status_update_email(user_email, parcel_data, old_status, new_status):
    """Send email when parcel status is updated."""
    subject = f"Parcel #{parcel_data['id']} Status Updated"
    html_body = f"""
    <html>
        <body>
            <h2>Your parcel status has been updated!</h2>
            <p><strong>Parcel ID:</strong> {parcel_data['id']}</p>
            <p><strong>Previous Status:</strong> {old_status}</p>
            <p><strong>New Status:</strong> {new_status}</p>
            <p><strong>Updated:</strong> {parcel_data.get('updated_at', 'N/A')}</p>
            <br>
            <p>Track your parcel at: <a href="https://your-frontend-url.com/track/{parcel_data['id']}">Track Parcel</a></p>
        </body>
    </html>
    """
    send_email(subject, [user_email], html_body)

def send_location_update_email(user_email, parcel_data, new_location):
    """Send email when parcel location is updated."""
    subject = f"Parcel #{parcel_data['id']} Location Updated"
    html_body = f"""
    <html>
        <body>
            <h2>Your parcel location has been updated!</h2>
            <p><strong>Parcel ID:</strong> {parcel_data['id']}</p>
            <p><strong>New Location:</strong> {new_location}</p>
            <p><strong>Updated:</strong> {parcel_data.get('updated_at', 'N/A')}</p>
            <br>
            <p>Track your parcel at: <a href="https://your-frontend-url.com/track/{parcel_data['id']}">Track Parcel</a></p>
        </body>
    </html>
    """
    send_email(subject, [user_email], html_body)

def send_parcel_cancelled_email(user_email, parcel_data):
    """Send email when parcel is cancelled."""
    subject = f"Parcel #{parcel_data['id']} Cancelled"
    html_body = f"""
    <html>
        <body>
            <h2>Your parcel has been cancelled!</h2>
            <p><strong>Parcel ID:</strong> {parcel_data['id']}</p>
            <p><strong>Status:</strong> Cancelled</p>
            <p><strong>Cancelled:</strong> {parcel_data.get('updated_at', 'N/A')}</p>
            <br>
            <p>If this was a mistake, please contact support.</p>
        </body>
    </html>
    """
    send_email(subject, [user_email], html_body)

def send_welcome_email(user_email, username):
    """Send welcome email to new users."""
    subject = "Welcome to Deliveroo!"
    html_body = f"""
    <html>
        <body>
            <h2>Welcome to Deliveroo, {username}!</h2>
            <p>Thank you for joining our parcel delivery platform.</p>
            <p>You can now:</p>
            <ul>
                <li>Create new parcels</li>
                <li>Track your deliveries</li>
                <li>Manage your account</li>
            </ul>
            <br>
            <p>Start by creating your first parcel!</p>
        </body>
    </html>
    """
    send_email(subject, [user_email], html_body)

def send_password_reset_email(user_email, reset_token):
    """Send password reset email."""
    subject = "Password Reset Request"
    html_body = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your Deliveroo account.</p>
            <p>Click the link below to reset your password:</p>
            <br>
            <a href="https://your-frontend-url.com/reset-password?token={reset_token}">Reset Password</a>
            <br>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """
    send_email(subject, [user_email], html_body)

def send_test_email(user_email):
    """Send test email."""
    subject = "Test Email from Deliveroo"
    html_body = f"""
    <html>
        <body>
            <h2>Test Email</h2>
            <p>This is a test email from your Deliveroo application.</p>
            <p>If you received this, your email configuration is working correctly!</p>
        </body>
    </html>
    """
    send_email(subject, [user_email], html_body) 