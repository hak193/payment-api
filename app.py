from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import stripe
from src.routes.payment import payment_bp
from src.config import Config

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load configuration
app.config.from_object(Config)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Register blueprints
app.register_blueprint(payment_bp, url_prefix='/api/v1/payment')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
