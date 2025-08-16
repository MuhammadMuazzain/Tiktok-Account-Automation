import os
from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import logging
from datetime import datetime
from anthropic import Anthropic

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN', 'your_verify_token')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your_webhook_secret')
WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Initialize Anthropic client
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode and token:
            if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
                logger.info('Webhook verified successfully')
                return challenge, 200
            else:
                logger.error('Webhook verification failed')
                return 'Forbidden', 403
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            signature = request.headers.get('X-Hub-Signature-256')
            if signature and WEBHOOK_SECRET:
                expected_signature = 'sha256=' + hmac.new(
                    WEBHOOK_SECRET.encode(),
                    request.data,
                    hashlib.sha256
                ).hexdigest()
                
                if signature != expected_signature:
                    logger.error('Invalid signature')
                    return 'Unauthorized', 401
            
            if 'entry' in data:
                for entry in data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if change.get('value', {}).get('messages'):
                                for message in change['value']['messages']:
                                    if message.get('type') == 'text':
                                        process_text_message(message)
            
            return jsonify({'status': 'ok'}), 200
            
        except Exception as e:
            logger.error(f'Error processing webhook: {str(e)}')
            return jsonify({'error': 'Internal server error'}), 500
    
    return 'Method not allowed', 405

def process_text_message(message):
    msg_id = message.get('id')
    sender = message.get('from')
    timestamp = message.get('timestamp')
    text = message.get('text', {}).get('body')
    
    logger.info(f'Text message from {sender}: {text}')
    
    # Get Claude's reply
    claude_response = get_claude_reply(text)
    
    # Send reply back to user
    if claude_response:
        send_reply_to_user(sender, claude_response)

def get_claude_reply(user_message):
    """Get a reply from Claude using Anthropic API"""
    try:
        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        reply = response.content[0].text
        logger.info(f'Claude reply: {reply}')
        return reply
        
    except Exception as e:
        logger.error(f'Error getting Claude reply: {str(e)}')
        return "Sorry, I'm having trouble processing your message right now."

def send_reply_to_user(recipient_phone, message_text):
    """Send a text message reply to WhatsApp user"""
    try:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {WHATSAPP_API_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_phone,
            "type": "text",
            "text": {
                "body": message_text
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            logger.info(f'Message sent successfully to {recipient_phone}')
        else:
            logger.error(f'Failed to send message: {response.status_code} - {response.text}')
            
    except Exception as e:
        logger.error(f'Error sending message: {str(e)}')

if __name__ == '__main__':
    # Check required environment variables
    required_vars = ['WHATSAPP_API_TOKEN', 'WHATSAPP_PHONE_NUMBER_ID', 'ANTHROPIC_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f'Missing required environment variables: {", ".join(missing_vars)}')
        logger.info('Please set the following environment variables:')
        logger.info('- WHATSAPP_API_TOKEN: Your WhatsApp Business API access token')
        logger.info('- WHATSAPP_PHONE_NUMBER_ID: Your WhatsApp phone number ID')
        logger.info('- ANTHROPIC_API_KEY: Your Anthropic API key')
        logger.info('- WEBHOOK_VERIFY_TOKEN: Token for webhook verification (optional)')
        logger.info('- WEBHOOK_SECRET: Secret for webhook signature validation (optional)')
    
    app.run(host='0.0.0.0', port=5000, debug=True)