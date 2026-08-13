import requests
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_config


class CloudflareVerifier:
    """Cloudflare API verifier for tunnel and account access."""
    
    def __init__(self, config_path=None, environment=None):
        """Initialize Cloudflare verifier.
        
        Args:
            config_path: Optional path to configuration file
            environment: Optional environment override
        """
        self.config = get_config(config_path, environment)
        self.headers = {
            "Authorization": f"Bearer {self.config.get('cloudflare.api_token')}"
        }
    
    def verify_all(self):
        """Verify all Cloudflare access.
        
        Returns:
            bool: True if all verifications pass
        """
        return (
            self.verify_zone() and
            self.verify_account()
        )
    
    def verify_zone(self):
        """Verify zone access.
        
        Returns:
            bool: True if zone access is valid
        """
        zone_id = self.config.get('cloudflare.zone_id')
        if not zone_id:
            return False
        
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}"
        try:
            r = requests.get(url, headers=self.headers)
            return r.json().get("success", False)
        except Exception:
            return False
    
    def verify_account(self):
        """Verify account access.
        
        Returns:
            bool: True if account access is valid
        """
        account_id = self.config.get('cloudflare.account_id')
        if not account_id:
            return False
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
        try:
            r = requests.get(url, headers=self.headers)
            return r.json().get("success", False)
        except Exception:
            return False
    
    def get_zone_info(self):
        """Get detailed zone information.
        
        Returns:
            dict: Zone information or None if failed
        """
        zone_id = self.config.get('cloudflare.zone_id')
        if not zone_id:
            return None
        
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}"
        try:
            r = requests.get(url, headers=self.headers)
            data = r.json()
            if data.get("success"):
                return data.get("result")
        except Exception:
            pass
        return None
    
    def get_account_info(self):
        """Get detailed account information.
        
        Returns:
            dict: Account information or None if failed
        """
        account_id = self.config.get('cloudflare.account_id')
        if not account_id:
            return None
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
        try:
            r = requests.get(url, headers=self.headers)
            data = r.json()
            if data.get("success"):
                return data.get("result")
        except Exception:
            pass
        return None
