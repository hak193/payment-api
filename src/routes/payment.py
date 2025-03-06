from flask import Blueprint, jsonify, request
import stripe
from src.config import Config
import logging

payment_bp = Blueprint('payment', __name__)
logger = logging.getLogger(__name__)

@payment_bp.route('/create-intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'currency']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=data['amount'],  # Amount in cents
            currency=data['currency'],
            automatic_payment_methods={'enabled': True},
            metadata={'integration_check': 'payment_processing_api'}
        )
        
        return jsonify({
            'clientSecret': intent.client_secret,
            'paymentIntentId': intent.id
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/<payment_id>', methods=['GET'])
def get_payment_status(payment_id):
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_id)
        return jsonify({
            'status': payment_intent.status,
            'amount': payment_intent.amount,
            'currency': payment_intent.currency
        })
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle specific event types
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            logger.info(f"Payment succeeded for intent: {payment_intent['id']}")
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            logger.error(f"Payment failed for intent: {payment_intent['id']}")
            
        return jsonify({'status': 'success'})
        
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500
