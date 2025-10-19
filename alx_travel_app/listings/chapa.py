#!/usr/bin/env python3
"""
Chapa Payment Gateway Integration Module
Handles payment initialization and verification with Chapa API
"""

import requests
import logging
from django.conf import settings
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ChapaPaymentError(Exception):
    """Custom exception for Chapa payment errors"""
    pass


class ChapaPaymentGateway:
    """
    Chapa Payment Gateway integration class.
    Handles communication with Chapa API for payment operations.
    """
    
    def __init__(self):
        self.secret_key = settings.CHAPA_SECRET_KEY
        self.base_url = settings.CHAPA_BASE_URL
        
        if not self.secret_key:
            raise ChapaPaymentError("CHAPA_SECRET_KEY not configured in settings")
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for Chapa API requests"""
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }
    
    def initialize_payment(
        self,
        amount: float,
        currency: str,
        email: str,
        first_name: str,
        last_name: str,
        tx_ref: str,
        callback_url: str,
        return_url: str,
        customization: Optional[Dict] = None
    ) -> Tuple[bool, Dict]:
        """
        Initialize a payment transaction with Chapa.
        
        Args:
            amount: Payment amount
            currency: Currency code (e.g., 'ETB', 'USD')
            email: Customer email
            first_name: Customer first name
            last_name: Customer last name
            tx_ref: Unique transaction reference
            callback_url: URL for payment notification callback
            return_url: URL to redirect after payment
            customization: Optional customization settings
        
        Returns:
            Tuple of (success: bool, response_data: dict)
        """
        url = f"{self.base_url}/transaction/initialize"
        
        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "return_url": return_url,
        }
        
        if customization:
            payload["customization"] = customization
        
        try:
            logger.info(f"Initializing payment for tx_ref: {tx_ref}")
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status') == 'success':
                logger.info(f"Payment initialized successfully: {tx_ref}")
                return True, response_data
            else:
                error_msg = response_data.get('message', 'Unknown error occurred')
                logger.error(f"Payment initialization failed: {error_msg}")
                return False, response_data
                
        except requests.exceptions.Timeout:
            logger.error("Chapa API request timed out")
            return False, {"error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Chapa API request failed: {str(e)}")
            return False, {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during payment initialization: {str(e)}")
            return False, {"error": str(e)}
    
    def verify_payment(self, tx_ref: str) -> Tuple[bool, Dict]:
        """
        Verify a payment transaction with Chapa.
        
        Args:
            tx_ref: Transaction reference to verify
        
        Returns:
            Tuple of (success: bool, response_data: dict)
        """
        url = f"{self.base_url}/transaction/verify/{tx_ref}"
        
        try:
            logger.info(f"Verifying payment for tx_ref: {tx_ref}")
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status') == 'success':
                logger.info(f"Payment verified successfully: {tx_ref}")
                return True, response_data
            else:
                error_msg = response_data.get('message', 'Verification failed')
                logger.error(f"Payment verification failed: {error_msg}")
                return False, response_data
                
        except requests.exceptions.Timeout:
            logger.error("Chapa API verification request timed out")
            return False, {"error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Chapa API verification request failed: {str(e)}")
            return False, {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during payment verification: {str(e)}")
            return False, {"error": str(e)}
    
    def get_transaction_status(self, tx_ref: str) -> Optional[str]:
        """
        Get the current status of a transaction.
        
        Args:
            tx_ref: Transaction reference
        
        Returns:
            Transaction status string or None if failed
        """
        success, data = self.verify_payment(tx_ref)
        
        if success and 'data' in data:
            return data['data'].get('status')
        
        return None


def initialize_chapa_payment(
    amount: float,
    email: str,
    first_name: str,
    last_name: str,
    tx_ref: str,
    callback_url: str,
    return_url: str,
    currency: str = 'ETB'
) -> Tuple[bool, Dict]:
    """
    Convenience function to initialize a Chapa payment.
    
    Args:
        amount: Payment amount
        email: Customer email
        first_name: Customer first name
        last_name: Customer last name
        tx_ref: Unique transaction reference
        callback_url: Callback URL for notifications
        return_url: Return URL after payment
        currency: Currency code (default: ETB)
    
    Returns:
        Tuple of (success: bool, response_data: dict)
    """
    gateway = ChapaPaymentGateway()
    return gateway.initialize_payment(
        amount=amount,
        currency=currency,
        email=email,
        first_name=first_name,
        last_name=last_name,
        tx_ref=tx_ref,
        callback_url=callback_url,
        return_url=return_url
    )


def verify_chapa_payment(tx_ref: str) -> Tuple[bool, Dict]:
    """
    Convenience function to verify a Chapa payment.
    
    Args:
        tx_ref: Transaction reference to verify
    
    Returns:
        Tuple of (success: bool, response_data: dict)
    """
    gateway = ChapaPaymentGateway()
    return gateway.verify_payment(tx_ref)
