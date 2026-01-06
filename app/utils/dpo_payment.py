# app/utils/dpo_payment.py

import requests
import xml.etree.ElementTree as ET
from datetime import date


class DPOPayment:
    def __init__(self):
        # Credentials statiques (tu pourras les mettre en .env plus tard)
        self.company_token = "8D3DA73D-9D7F-4E09-96D4-3D44E7A83EA3"
        self.service_id = "5525"
        self.api_endpoint = "https://secure.3gdirectpay.com/API/v6/"
        self.payment_url_base = "https://secure.3gdirectpay.com/payv2.php?ID="

    def _safe_text(self, root, path):
        """Récupère le texte d'un nœud XML de manière sécurisée"""
        node = root.find(path)
        return node.text if node is not None else None

    def create_payment_token(self, amount, currency, reference, redirect_url, back_url, 
                           customer_phone="", customer_email=""):
        """Crée un token de paiement DPO et retourne l'URL de paiement"""
        
        xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<API3G>
    <CompanyToken>{self.company_token}</CompanyToken>
    <Request>createToken</Request>
    <Transaction>
        <PaymentAmount>{amount:.2f}</PaymentAmount>
        <PaymentCurrency>{currency}</PaymentCurrency>
        <CompanyRef>{reference}</CompanyRef>
        <RedirectURL>{redirect_url}</RedirectURL>
        <BackURL>{back_url}</BackURL>
        <CompanyRefUnique>0</CompanyRefUnique>
        <PTL>5</PTL>
    </Transaction>
    <Services>
        <Service>
            <ServiceType>{self.service_id}</ServiceType>
            <ServiceDescription>Payment for {reference}</ServiceDescription>
            <ServiceDate>{date.today().strftime('%Y/%m/%d')}</ServiceDate>
        </Service>
    </Services>
</API3G>
"""

        try:
            response = requests.post(
                self.api_endpoint,
                data=xml_data.encode("utf-8"),
                headers={"Content-Type": "application/xml"},
                timeout=30
            )

            print(f"[DPO] Create Token Response: {response.text}")

            root = ET.fromstring(response.text)
            result = self._safe_text(root, ".//Result")
            explanation = self._safe_text(root, ".//ResultExplanation")

            if result != "000":
                return {
                    "success": False,
                    "error": explanation or "DPO API error",
                    "raw": response.text
                }

            trans_token = self._safe_text(root, ".//TransToken")
            trans_ref = self._safe_text(root, ".//TransRef")

            return {
                "success": True,
                "trans_token": trans_token,
                "trans_ref": trans_ref,
                "payment_url": f"{self.payment_url_base}{trans_token}"
            }

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] DPO API Request failed: {str(e)}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except ET.ParseError as e:
            print(f"[ERROR] DPO XML Parse error: {str(e)}")
            return {
                "success": False,
                "error": f"Invalid XML response: {str(e)}"
            }

    def verify_payment(self, trans_token):
        """Vérifie le statut d'un paiement DPO"""
        
        xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<API3G>
    <CompanyToken>{self.company_token}</CompanyToken>
    <Request>verifyToken</Request>
    <TransactionToken>{trans_token}</TransactionToken>
</API3G>
"""

        try:
            response = requests.post(
                self.api_endpoint,
                data=xml_data.encode("utf-8"),
                headers={"Content-Type": "application/xml"},
                timeout=30
            )

            print(f"[DPO] Verify Token Response: {response.text}")

            root = ET.fromstring(response.text)
            result = self._safe_text(root, ".//Result")
            result_explanation = self._safe_text(root, ".//ResultExplanation")

            if result != "000":
                return {
                    "success": False,
                    "status": "failed",
                    "error": result_explanation or "Verification failed"
                }

            return {
                "success": True,
                "status": "verified",
                "amount": self._safe_text(root, ".//TransactionAmount"),
                "currency": self._safe_text(root, ".//TransactionCurrency"),
                "company_ref": self._safe_text(root, ".//CompanyRef"),
                "customer_phone": self._safe_text(root, ".//CustomerPhone"),
                "customer_email": self._safe_text(root, ".//CustomerEmail"),
            }

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] DPO Verify Request failed: {str(e)}")
            return {
                "success": False,
                "status": "error",
                "error": f"Network error: {str(e)}"
            }
        except ET.ParseError as e:
            print(f"[ERROR] DPO Verify XML Parse error: {str(e)}")
            return {
                "success": False,
                "status": "error",
                "error": f"Invalid XML response: {str(e)}"
            }