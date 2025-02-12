import requests
import time
import logging
from typing import Dict, Optional

class WhatsAppSender:
    def __init__(self, instance_id: Optional[str] = None, client_id: Optional[str] = None):
        self.instance_id = instance_id
        self.client_id = client_id
        self.base_url = "https://digichatbot.com/api/send"

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def send_message(self, 
                    dest_number: str, 
                    message: str, 
                    media_url: Optional[str] = None) -> Dict:
        """
        Send WhatsApp message using the provided API
        """
        if not self.instance_id or not self.client_id:
            return {"success": False, "error": "API credentials not configured"}

        try:
            # Build the API URL
            params = {
                "number": dest_number,
                "type": "text",
                "message": message,
                "instance_id": self.instance_id,
                "access_token": self.client_id
            }

            # Add media parameters if provided
            if media_url:
                params["media_url"] = media_url
                params["filename"] = media_url.split("/")[-1]

            # Make the API request
            self.logger.info(f"Sending message to {dest_number}")
            response = requests.get(self.base_url, params=params)

            if response.status_code == 200:
                return {"success": True, "response": response.text}
            else:
                return {"success": False, "error": f"API Error: {response.status_code}"}

        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return {"success": False, "error": str(e)}