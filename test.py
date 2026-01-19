import requests
import xml.etree.ElementTree as ET
import uuid
from datetime import datetime

API_URL = "https://secure.3gdirectpay.com/API/v6/"

COMPANY_TOKEN = "8D3DA73D-9D7F-4E09-96D4-3D44E7A83EA3"
SERVICE_ID = "5525"

# DPO requires YYYY-MM-DD format
today = datetime.today().strftime("%Y-%m-%d")

# Unique reference required in test mode
company_ref = f"TEST-{uuid.uuid4().hex[:8]}"

payload = f"""
<?xml version="1.0" encoding="utf-8"?>
<API3G>
    <CompanyToken>{COMPANY_TOKEN}</CompanyToken>
    <Request>createToken</Request>
    <Transaction>
        <PaymentAmount>1000.00</PaymentAmount>
        <PaymentCurrency>UGX</PaymentCurrency>
        <CompanyRef>{company_ref}</CompanyRef>
        <RedirectURL>https://example.com/success</RedirectURL>
        <BackURL>https://example.com/cancel</BackURL>
        <CompanyRefUnique>1</CompanyRefUnique>
        <PTL>5</PTL>
    </Transaction>
    <Services>
        <Service>
            <ServiceType>{SERVICE_ID}</ServiceType>
            <ServiceDescription>Test payment</ServiceDescription>
            <ServiceDate>{today}</ServiceDate>
        </Service>
    </Services>
</API3G>
"""

headers = {"Content-Type": "application/xml"}

response = requests.post(API_URL, data=payload.encode("utf-8"), headers=headers)

print("Raw response:")
print(response.text)

# Parse XML carefully
root = ET.fromstring(response.text)
trans_token = root.findtext(".//TransToken")

if trans_token:
    print("\n✅ Transaction created successfully!")
    print("Payment URL:")
    print(f"https://secure.3gdirectpay.com/payv2.php?ID={trans_token}")
else:
    print("\n❌ Failed to create transaction")
    fault = root.findtext(".//ResultExplanation")
    if fault:
        print("Reason:", fault)
