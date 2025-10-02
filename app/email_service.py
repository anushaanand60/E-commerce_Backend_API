import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional

class EmailService:
    def __init__(self):
        self.smtp_server="smtp.gmail.com"
        self.smtp_port=587
        self.sender_email=os.getenv("SMTP_EMAIL", "test@yourapp.com")
        self.sender_password=os.getenv("SMTP_PASSWORD", "test_password")
    
    def send_order_confirmation(self, user_email: str, username: str, order_data: dict):
        """Send order confirmation email"""
        subject=f"Order Confirmation #{order_data['id']}"
        body=f"""
        <html>
        <body>
            <h2>Thank you for your order, {username}!</h2>
            <p>Your order has been confirmed and is being processed.</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>Order Details</h3>
                <p><strong>Order ID:</strong> #{order_data['id']}</p>
                <p><strong>Total Amount:</strong> ${order_data['total']}</p>
                <p><strong>Status:</strong> {order_data['status']}</p>
                <p><strong>Order Date:</strong> {order_data['created_at']}</p>
            </div>
            
            <h3>Order Items:</h3>
            <ul>
        """
        
        for item in order_data.get('items', []):
            body += f"<li>{item.get('quantity', 0)} x Product #{item.get('product_id')}</li>"
        
        body += """
            </ul>
            
            <p>We'll notify you when your order ships.</p>
            <p>Thank you for shopping with us!</p>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, body)
    
    def send_status_update(self, user_email: str, username: str, order_data: dict, old_status: str, new_status: str):
        """Send order status update email"""
        subject=f"Order #{order_data['id']} Status Updated"
        
        body=f"""
        <html>
        <body>
            <h2>Order Status Update</h2>
            <p>Hi {username}, your order status has been updated.</p>
            
            <div style="background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>Order #{order_data['id']}</h3>
                <p><strong>Previous Status:</strong> {old_status}</p>
                <p><strong>New Status:</strong> <span style="color: #1890ff; font-weight: bold;">{new_status}</span></p>
                <p><strong>Total:</strong> ${order_data['total']}</p>
            </div>
            
            <p>You can view your order details in your account.</p>
            <p>Thank you for your patience!</p>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, body)
    
    def _send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        """Internal method to send email"""
        try:
            message=MIMEMultipart()
            message["From"]=self.sender_email
            message["To"]=recipient_email
            message["Subject"]=subject
            
            message.attach(MIMEText(body, "html"))

            print(" = " * 50)
            print(f"EMAIL WOULD BE SENT TO: {recipient_email}")
            print(f"SUBJECT: {subject}")
            print(f"BODY: {body}")
            print(" = " * 50)
            
            """
            # Connect to server and send
            server=smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(message)
            server.quit()
            """
            
            return True
            
        except Exception as e:
            print(f"Email error: {e}")
            return False

email_service=EmailService()