# 📧 Email Setup Guide for Deliveroo Backend

This guide explains how to set up email functionality for your Deliveroo Flask backend application.

## 🚀 **Email Features Implemented**

### **✅ Available Email Endpoints:**

1. **`POST /email/parcel-created`** - Send email when parcel is created
2. **`POST /email/status-update`** - Send email when parcel status changes
3. **`POST /email/location-update`** - Send email when parcel location updates
4. **`POST /email/parcel-cancelled`** - Send email when parcel is cancelled
5. **`POST /email/welcome`** - Send welcome email to new users
6. **`POST /email/password-reset`** - Send password reset email
7. **`POST /email/test`** - Send test email to verify configuration

## 🔧 **Email Configuration**

### **1. Environment Variables Setup**

Add these to your `.env` file:

```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### **2. Gmail Setup (Recommended)**

#### **Step 1: Enable 2-Factor Authentication**
1. Go to your Google Account settings
2. Enable 2-Factor Authentication

#### **Step 2: Generate App Password**
1. Go to Google Account → Security
2. Under "2-Step Verification" → "App passwords"
3. Generate a new app password for "Mail"
4. Use this password in `MAIL_PASSWORD`

#### **Step 3: Update .env File**
```bash
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-digit-app-password
```

## 📧 **Email Service Options**

### **Option 1: Gmail SMTP (Free)**
```python
# Already configured in email_service.py
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

### **Option 2: SendGrid (Recommended for Production)**
```python
# Update email_service.py to use SendGrid
import sendgrid
from sendgrid.helpers.mail import Mail as SendGridMail

def send_email_sendgrid(subject, recipients, html_body):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    message = SendGridMail(
        from_email='your-app@yourdomain.com',
        to_emails=recipients,
        subject=subject,
        html_content=html_body
    )
    sg.send(message)
```

### **Option 3: AWS SES (Scalable)**
```python
# Update email_service.py to use AWS SES
import boto3

def send_email_ses(subject, recipients, html_body):
    ses = boto3.client('ses', region_name='us-east-1')
    ses.send_email(
        Source='your-app@yourdomain.com',
        Destination={'ToAddresses': recipients},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Html': {'Data': html_body}}
        }
    )
```

## 🧪 **Testing Email Functionality**

### **1. Test Email Endpoint**
```bash
curl -X POST http://localhost:5000/email/test \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user_email": "test@example.com"
  }'
```

### **2. Test Parcel Created Email**
```bash
curl -X POST http://localhost:5000/email/parcel-created \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "parcel_id": 1,
    "user_email": "user@example.com"
  }'
```

## 🔄 **Integration with Frontend**

### **Frontend Email Service Example:**
```javascript
// src/services/emailService.js
class EmailService {
  async sendParcelCreatedEmail(parcelData) {
    try {
      const response = await fetch('/api/email/parcel-created', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          parcel_id: parcelData.id,
          user_email: user.email
        })
      });
      return response.json();
    } catch (error) {
      console.error('Email sending failed:', error);
    }
  }
}
```

## 📋 **Email Templates**

### **Parcel Created Email:**
```html
<h2>Your parcel has been created!</h2>
<p><strong>Parcel ID:</strong> {parcel_id}</p>
<p><strong>Pickup Location:</strong> {pickup_location}</p>
<p><strong>Destination:</strong> {destination}</p>
<p><strong>Status:</strong> {status}</p>
```

### **Status Update Email:**
```html
<h2>Your parcel status has been updated!</h2>
<p><strong>Parcel ID:</strong> {parcel_id}</p>
<p><strong>Previous Status:</strong> {old_status}</p>
<p><strong>New Status:</strong> {new_status}</p>
```

## 🚀 **Deployment Configuration**

### **For Render Deployment:**

1. **Add Environment Variables in Render Dashboard:**
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-app@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

2. **Update requirements.txt:**
   ```
   Flask-Mail==0.9.1
   ```

3. **Deploy to Render:**
   ```bash
   git add .
   git commit -m "Add email functionality"
   git push origin main
   ```

## 🔒 **Security Considerations**

### **1. Email Credentials**
- ✅ Use App Passwords, not regular passwords
- ✅ Store credentials in environment variables
- ✅ Never commit credentials to version control

### **2. Rate Limiting**
```python
# Add rate limiting to email endpoints
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/email/test')
@limiter.limit("5 per minute")
def test_email():
    # Email sending logic
```

### **3. Email Validation**
```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

## 🐛 **Troubleshooting**

### **Common Issues:**

1. **"Authentication failed"**
   - Check if 2FA is enabled
   - Verify app password is correct
   - Ensure MAIL_USERNAME is correct

2. **"Connection timeout"**
   - Check MAIL_SERVER and MAIL_PORT
   - Verify MAIL_USE_TLS is True
   - Check firewall settings

3. **"Email not received"**
   - Check spam folder
   - Verify recipient email is correct
   - Check email service logs

### **Debug Mode:**
```python
# Add to config.py for debugging
app.config['MAIL_DEBUG'] = True
```

## 📊 **Email Analytics (Optional)**

### **Track Email Metrics:**
```python
# Add to email_service.py
def track_email_sent(email_type, recipient, success):
    # Log email metrics
    print(f"Email {email_type} sent to {recipient}: {'SUCCESS' if success else 'FAILED'}")
```

## ✅ **Complete Setup Checklist**

- [ ] Environment variables configured
- [ ] Gmail 2FA enabled
- [ ] App password generated
- [ ] Email endpoints tested
- [ ] Frontend integration complete
- [ ] Error handling implemented
- [ ] Rate limiting added
- [ ] Security measures in place
- [ ] Deployment configuration updated

## 🎉 **Ready to Use!**

Your email functionality is now fully implemented and ready for production use. The system will automatically send emails for:

- ✅ Parcel creation
- ✅ Status updates
- ✅ Location updates
- ✅ Cancellations
- ✅ Welcome emails
- ✅ Password resets

All emails are sent asynchronously to avoid blocking the main application flow. 