# app/utils/dpo_payment.py

import requests
import xml.etree.ElementTree as ET
from datetime import datetime


class DPOPayment:
    def __init__(self):
        #self.company_token = "D56DE103-2570-4C0A-9A50-DD12EF18C5AA"
        self.company_token = "8D3DA73D-9D7F-4E09-96D4-3D44E7A83EA3"
        #self.service_id = "108375"
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

        # Format de date YYYY-MM-DD (comme dans ton script de test qui marche)
        today = datetime.today().strftime("%Y-%m-%d")

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
        <CompanyRefUnique>1</CompanyRefUnique>
        <PTL>5</PTL>
    </Transaction>
    <Services>
        <Service>
            <ServiceType>{self.service_id}</ServiceType>
            <ServiceDescription>Payment for {reference}</ServiceDescription>
            <ServiceDate>{today}</ServiceDate>
        </Service>
    </Services>
</API3G>
"""

        try:
            print(f"[DPO] Sending request to DPO API")
            print(f"[DPO] Amount: {amount} {currency}")
            print(f"[DPO] Reference: {reference}")
            print(f"[DPO] Date: {today}")

            response = requests.post(
                self.api_endpoint,
                data=xml_data.encode("utf-8"),
                headers={"Content-Type": "application/xml"},
                timeout=30
            )

            print(f"[DPO] Response Status: {response.status_code}")
            print(f"[DPO] Response Body (FULL):")
            print("="*80)
            print(response.text)
            print("="*80)

            root = ET.fromstring(response.text)
            result = self._safe_text(root, ".//Result")
            explanation = self._safe_text(root, ".//ResultExplanation")

            if result != "000":
                print(f"[DPO] DPO Error - Code: {result}, Message: {explanation}")
                return {
                    "success": False,
                    "error": explanation or "DPO API error",
                    "result_code": result,
                    "raw": response.text
                }

            trans_token = self._safe_text(root, ".//TransToken")
            trans_ref = self._safe_text(root, ".//TransRef")

            if not trans_token:
                print(f"[DPO] No TransToken in response")
                return {
                    "success": False,
                    "error": "No TransToken returned from DPO",
                    "raw": response.text
                }

            payment_url = f"{self.payment_url_base}{trans_token}"
            print(f"[DPO] Token created successfully")
            print(f"[DPO] TransToken: {trans_token}")
            print(f"[DPO] Payment URL: {payment_url}")

            return {
                "success": True,
                "trans_token": trans_token,
                "trans_ref": trans_ref,
                "payment_url": payment_url
            }

        except requests.exceptions.RequestException as e:
            print(f"[DPO] Network error: {str(e)}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except ET.ParseError as e:
            print(f"[DPO] XML Parse error: {str(e)}")
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
            print(f"[DPO] Verifying token: {trans_token}")

            response = requests.post(
                self.api_endpoint,
                data=xml_data.encode("utf-8"),
                headers={"Content-Type": "application/xml"},
                timeout=30
            )

            print(f"[DPO] Verify Response Status: {response.status_code}")

            # Détecter les erreurs 429 (Too Many Requests)
            if response.status_code == 429:
                print(f"[DPO] 429 Too Many Requests - Rate limited")
                return {
                    "success": False,
                    "status": "rate_limited",
                    "error": "Rate limit exceeded, retry later"
                }

            # Vérifier si la réponse est du HTML (erreur DPO)
            if response.text.strip().startswith("<!DOCTYPE") or response.text.strip().startswith("<html"):
                print(f"[DPO] HTML response received (likely 429 or error page)")
                return {
                    "success": False,
                    "status": "rate_limited",
                    "error": "DPO returned HTML instead of XML (rate limited)"
                }

            print(f"[DPO] Verify Response: {response.text[:500]}")

            root = ET.fromstring(response.text)
            result = self._safe_text(root, ".//Result")
            result_explanation = self._safe_text(root, ".//ResultExplanation")

            # Result = 000 → Transaction payée
            if result == "000":
                print(f"[DPO] Payment verified successfully")
                return {
                    "success": True,
                    "status": "verified",
                    "result_code": result,
                    "amount": self._safe_text(root, ".//TransactionAmount"),
                    "currency": self._safe_text(root, ".//TransactionCurrency"),
                    "company_ref": self._safe_text(root, ".//CompanyRef"),
                    "customer_phone": self._safe_text(root, ".//CustomerPhone"),
                    "customer_email": self._safe_text(root, ".//CustomerEmail"),
                }

            # Result = 900 → Transaction en attente
            if result == "900":
                print(f"[DPO] Transaction pending (900)")
                return {
                    "success": False,
                    "status": "pending",
                    "result_code": result,
                    "error": result_explanation or "Transaction pending"
                }

            # Autre code d'erreur → considérer comme pending (ne jamais fail)
            print(f"[DPO] Unknown result code: {result}")
            return {
                "success": False,
                "status": "pending",
                "result_code": result,
                "error": result_explanation or f"Unknown status (code {result})"
            }

        except requests.exceptions.Timeout:
            print(f"[DPO] Verify timeout")
            return {
                "success": False,
                "status": "error",
                "error": "Request timeout"
            }
        except requests.exceptions.RequestException as e:
            print(f"[DPO] Verify network error: {str(e)}")
            return {
                "success": False,
                "status": "error",
                "error": f"Network error: {str(e)}"
            }
        except ET.ParseError as e:
            print(f"[DPO] Verify XML parse error (likely HTML 429): {str(e)}")
            return {
                "success": False,
                "status": "rate_limited",
                "error": "XML parse error (DPO rate limit or HTML response)"
            }