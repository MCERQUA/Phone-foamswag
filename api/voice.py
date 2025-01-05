from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

app = Flask(__name__)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "echosaisystems@gmail.com"
RECIPIENT_EMAIL = "echosaisystems@gmail.com"
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

def send_order_email(customer_data):
    """Send email with customer order details"""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = f"New Order from {customer_data.get('name', 'Customer')} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    body = f"""
    New Order Details:
    
    Customer Name: {customer_data.get('name', 'Not provided')}
    Email: {customer_data.get('email', 'Not provided')}
    Shipping Address: {customer_data.get('address', 'Not provided')}
    
    Order Details:
    {customer_data.get('order', 'No order details provided')}
    
    Call Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
            return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route("/")
def index():
    return "Echo Systems Phone Order System - Webhook Handler Running"

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()
    gather = Gather(input='speech', action='/collect_name', timeout=3)
    gather.say('Welcome to Echo Systems! I'm an AI assistant ready to help with your order. Could you please tell me your name?')
    response.append(gather)
    return str(response)

@app.route("/collect_name", methods=['POST'])
def collect_name():
    response = VoiceResponse()
    name = request.values.get('SpeechResult', '')
    
    gather = Gather(input='speech', action='/collect_email', timeout=3)
    gather.say(f'Thanks {name}! Could you please tell me your email address?')
    response.append(gather)
    return str(response)

@app.route("/collect_email", methods=['POST'])
def collect_email():
    response = VoiceResponse()
    gather = Gather(input='speech', action='/collect_address', timeout=3)
    gather.say('Great! Now, please tell me your complete shipping address.')
    response.append(gather)
    return str(response)

@app.route("/collect_address", methods=['POST'])
def collect_address():
    response = VoiceResponse()
    gather = Gather(input='speech', action='/collect_order', timeout=3)
    gather.say('Perfect! Now, what would you like to order today?')
    response.append(gather)
    return str(response)

@app.route("/collect_order", methods=['POST'])
def collect_order():
    response = VoiceResponse()
    customer_data = {
        'order': request.values.get('SpeechResult', ''),
        'name': request.values.get('name', ''),
        'email': request.values.get('email', ''),
        'address': request.values.get('address', '')
    }
    
    if send_order_email(customer_data):
        response.say("Thank you for your order! I've sent the details to our team, and they'll process it right away. Is there anything else you need help with?")
    else:
        response.say("I apologize, but I'm having trouble processing your order. Please try again later or contact our support team.")
    
    return str(response)

if __name__ == "__main__":
    app.run(debug=True)