import requests
import xml.etree.ElementTree as ET

API_URL = "https://secure.3gdirectpay.com/API/v6/"

COMPANY_TOKEN = "8D3DA73D-9D7F-4E09-96D4-3D44E7A83EA3"
SERVICE_ID = "5525"

payload = f"""
<?xml version="1.0" encoding="utf-8"?>
<API3G>
    <CompanyToken>{COMPANY_TOKEN}</CompanyToken>
    <Request>createToken</Request>
    <Transaction>
        <PaymentAmount>4.00</PaymentAmount>
        <PaymentCurrency>USD</PaymentCurrency>
        <CompanyRef>TEST123</CompanyRef>
        <RedirectURL>https://example.com/success</RedirectURL>
        <BackURL>https://example.com/cancel</BackURL>
        <CompanyRefUnique>0</CompanyRefUnique>
        <PTL>5</PTL>
    </Transaction>
    <Services>
        <Service>
            <ServiceType>{SERVICE_ID}</ServiceType>
            <ServiceDescription>Test payment</ServiceDescription>
            <ServiceDate>2026/01/05</ServiceDate>
        </Service>
    </Services>
</API3G>
"""

headers = {"Content-Type": "application/xml"}

response = requests.post(API_URL, data=payload.encode("utf-8"), headers=headers)

print("Raw response:")
print(response.text)

# Parse XML
root = ET.fromstring(response.text)
trans_token = root.findtext("TransToken")

if trans_token:
    print("\n✅ Transaction created")
    print("Payment URL:")
    print(f"https://secure.3gdirectpay.com/payv2.php?ID={trans_token}")
else:
    print("\n❌ Failed to create transaction")
