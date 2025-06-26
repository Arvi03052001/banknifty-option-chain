import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """Configuration class that handles both local and production environments"""
    
    def __init__(self):
        self.fyers_token = None
        self.github_token = None
        
        # Fyers API Configuration - Updated with correct credentials
        self.CLIENT_ID = os.getenv('FYERS_CLIENT_ID', 'V6GL1Z0UPG-100')  # Your actual client ID
        self.SECRET_ID = os.getenv('FYERS_SECRET_ID', 'GAUU7TXF41')  # Your actual secret
        self.REDIRECT_URI = os.getenv('FYERS_REDIRECT_URI', 'https://www.google.com/')
        
        self.load_tokens()
    
    def load_tokens(self):
        """Load tokens from environment variables (production) or token.txt (local)"""
        
        # Try to load from environment variables first (for Render.com)
        self.fyers_token = os.getenv('FYERS_TOKEN')
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        # If environment variables are not set, try to load from token.txt (local development)
        if not self.fyers_token or not self.github_token:
            try:
                self._load_from_file()
            except Exception as e:
                logger.warning(f"Could not load tokens from file: {e}")
        
        # Validate tokens
        if not self.fyers_token:
            logger.error("FYERS_TOKEN not found in environment variables or token.txt")
        else:
            logger.info("FYERS token loaded successfully")
            
        if not self.github_token:
            logger.error("GITHUB_TOKEN not found in environment variables or token.txt")
        else:
            logger.info("GitHub token loaded successfully")
    
    def _load_from_file(self):
        """Load tokens from token.txt file (for local development)"""
        try:
            with open('token.txt', 'r') as f:
                lines = f.readlines()
            
            # First line is Fyers token
            if len(lines) > 0 and not self.fyers_token:
                self.fyers_token = lines[0].strip()
            
            # Look for GitHub token line
            if not self.github_token:
                for line in lines:
                    if line.startswith('github_token='):
                        self.github_token = line.split('=', 1)[1].strip()
                        break
                        
        except FileNotFoundError:
            logger.warning("token.txt file not found")
    
    @property
    def is_production(self):
        """Check if running in production environment"""
        return os.getenv('RENDER') is not None or os.getenv('PRODUCTION') is not None
    
    @property
    def port(self):
        """Get port for the web application"""
        return int(os.getenv('PORT', 5000))
    
    @property
    def host(self):
        """Get host for the web application"""
        return '0.0.0.0' if self.is_production else '127.0.0.1'

# Global config instance
config = Config()

# Backward compatibility - expose commonly used values
client_id = config.CLIENT_ID
CLIENT_ID = config.CLIENT_ID
SECRET_ID = config.SECRET_ID
REDIRECT_URI = config.REDIRECT_URI