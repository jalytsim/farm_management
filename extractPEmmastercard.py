from oauth1.authenticationutils import load_signing_key
from oauth1.oauth import OAuth
from OpenSSL import crypto
import os

P12_FILE = r'D:\project\Brian\farm_management\nkusu-sandbox-signing.p12'  # Update path as necessary
KEYSTORE_PASSWORD = 'yqH@PsdtJUEwtX2202020'   # Ensure this is securely handled in production
CONSUMER_KEY = 'WuDbmdAgqcton7BAuryeQQ1tknF-PUAOrmN8rSNy34f38c77!83643f5df5e5445aa20e9e3d0413f62c0000000000000000'  # Ensure security

# Load the API signing key
try:
    signing_key = load_signing_key(P12_FILE, KEYSTORE_PASSWORD)
except Exception as e:
    print(f"Error loading signing key: {e}")
    signing_key = None  # Handle this appropriately in production

def get_private_key_pem():
    """
    Get the private key from P12 (for use in JWT)
    """
    try:
        with open(P12_FILE, "rb") as file:
            p12 = crypto.load_pkcs12(file.read(), KEYSTORE_PASSWORD)
            return crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
    except Exception as e:
        print(f"Error retrieving private key: {e}")
        return None

def get_auth_header(uri, method='GET', payload=None):
    """
    Create Auth header for an API request
    """
    if not signing_key:
        print("Signing key not loaded.")
        return None
    oauth = OAuth()  # Ideally, pass in the consumer_key and signing_key during initialization if required
    return oauth.get_authorization_header(uri, method, payload, CONSUMER_KEY, signing_key)
