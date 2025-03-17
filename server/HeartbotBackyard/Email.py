import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

class EmailHandler:
    def __init__(self):
        self.client = None
        self.sender_email = None  # Initialize sender_email to None

    def init_app(self):
        # Initialize necessary configuration
        smtp_server = current_app.config.get('SMTP_SERVER', 'mail.privateemail.com')
        smtp_port = current_app.config.get('SMTP_PORT', 465)
        self.sender_email = current_app.config.get('SENDER_EMAIL', 'support@heartbot.gg')
        self.password = current_app.config.get('EMAIL_PASSWORD', 'baldybaldy6$')

        # Create the SSL context
        context = ssl.create_default_context()

        # Initialize and connect to the SMTP server using the connect() method
        self.client = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        self.client.connect(smtp_server, smtp_port)  # Explicitly call connect()

        # Log in to the SMTP server
        self.client.login(self.sender_email, self.password)

    def verify_email(self, email_to, otp, username):
        if not self.sender_email:
            raise ValueError("Email handler is not initialized. Please call init_app() first.")
        
        confirm_html = """
        <html>
          <head>
            <style>
              body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333333; margin: 0; padding: 0; }}
              .email-container {{ background-color: #ffffff; width: 100%; max-width: 600px; margin: 20px auto; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }}
              .email-header {{ text-align: center; margin-bottom: 20px; }}
              .email-header h1 {{ font-size: 24px; color: #2c3e50; margin: 0; }}
              .email-content {{ font-size: 16px; line-height: 1.6; margin: 20px 0; }}
              .otp-code {{ display: inline-block; background-color: #3498db; color: #ffffff; font-size: 20px; font-weight: bold; padding: 10px 20px; border-radius: 5px; text-align: center; }}
              .footer {{ text-align: center; font-size: 12px; color: #95a5a6; margin-top: 20px; }}
            </style>
          </head>
          <body>
            <div class="email-container">
              <div class="email-header">
                <h1>Account Verification</h1>
              </div>
              <div class="email-content">
                <p>Hello {0},</p>
                <p>Thank you for signing up with us. To complete your registration, please use the following code:</p>
                <div class="otp-code">{1}</div>
                <p>This code will expire in 10 minutes. If you did not request this, please ignore this email.</p>
              </div>
              <div class="footer">
                <p>&copy; 2025 Heartbot. All rights reserved.</p>
              </div>
            </div>
          </body>
        </html>
        """

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = email_to
        message["Subject"] = "Confirm Your Email"
        
        message.attach(MIMEText(confirm_html.format(username, otp), "html"))
        
        # Send email
        self.client.sendmail(self.sender_email, email_to, message.as_string())

    def password_reset(self, email_to, otp, username):
        if not self.sender_email:
            raise ValueError("Email handler is not initialized. Please call init_app() first.")
        
        reset_otp_html = """
        <html>
          <head>
            <style>
              body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333333; margin: 0; padding: 0; }}
              .email-container {{ background-color: #ffffff; width: 100%; max-width: 600px; margin: 20px auto; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }}
              .email-header {{ text-align: center; margin-bottom: 20px; }}
              .email-header h1 {{ font-size: 24px; color: #2c3e50; margin: 0; }}
              .email-content {{ font-size: 16px; line-height: 1.6; margin: 20px 0; }}
              .otp-code {{ display: inline-block; background-color: #3498db; color: #ffffff; font-size: 20px; font-weight: bold; padding: 10px 20px; border-radius: 5px; text-align: center; }}
              .footer {{ text-align: center; font-size: 12px; color: #95a5a6; margin-top: 20px; }}
            </style>
          </head>
          <body>
            <div class="email-container">
              <div class="email-header">
                <h1>Password Reset Request</h1>
              </div>
              <div class="email-content">
                <p>Hello {0},</p>
                <p>We received a request to reset your password. To complete this process, please use the following OTP:</p>
                <div class="otp-code">{1}</div>
                <p>This OTP will expire in 10 minutes. If you did not request this, please ignore this email.</p>
              </div>
              <div class="footer">
                <p>&copy; 2025 Heartbot. All rights reserved.</p>
              </div>
            </div>
          </body>
        </html>
        """

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = email_to
        message["Subject"] = "Password Reset OTP"
        
        message.attach(MIMEText(reset_otp_html.format(username, otp), "html"))
        
        # Send email
        self.client.sendmail(self.sender_email, email_to, message.as_string())

    def email_changed(self, email_to, username, new_email):
        if not self.sender_email:
            raise ValueError("Email handler is not initialized. Please call init_app() first.")

        email_change_html = """
        <html>
          <head>
            <style>
              body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333333; margin: 0; padding: 0; }}
              .email-container {{ background-color: #ffffff; width: 100%; max-width: 600px; margin: 20px auto; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }}
              .email-header {{ text-align: center; margin-bottom: 20px; }}
              .email-header h1 {{ font-size: 24px; color: #2c3e50; margin: 0; }}
              .email-content {{ font-size: 16px; line-height: 1.6; margin: 20px 0; }}
              .footer {{ text-align: center; font-size: 12px; color: #95a5a6; margin-top: 20px; }}
            </style>
          </head>
          <body>
            <div class="email-container">
              <div class="email-header">
                <h1>Email Change Notification</h1>
              </div>
              <div class="email-content">
                <p>Hello {0},</p>
                <p>We wanted to inform you that your email address is about to change.</p>
                <p><strong>Old Email:</strong> {1}</p>
                <p><strong>New Email:</strong> {2}</p>
                <p>If you did not request this change, please contact our support team immediately at <a href="mailto:support@heartbot.gg">support@heartbot.gg</a>.</p>
                <p>If this was you, no further action is needed.</p>
              </div>
              <div class="footer">
                <p>&copy; 2025 Heartbot. All rights reserved.</p>
              </div>
            </div>
          </body>
        </html>
        """

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = email_to
        message["Subject"] = "Notification: Your Email Address is Changing"
        
        message.attach(MIMEText(email_change_html.format(username, email_to, new_email), "html"))
        
        # Send email
        self.client.sendmail(self.sender_email, email_to, message.as_string())