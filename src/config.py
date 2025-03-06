import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration class"""
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5000')
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration variables are set"""
        required_vars = ['STRIPE_SECRET_KEY']
        missing_vars = [var for var in required_vars if not getattr(Config, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
