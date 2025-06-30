import csv
from twilio.rest import Client

# === Twilio credentials ===
account_sid = "FROM TWILIO ACCOUNT"
auth_token = "FROM TWILIO ACCOUNT"
twilio_number = "FROM TWILIO ACCOUNT" # e.g., +1415xxxxxxx
verified_number = "local phone number mapped to TWILIO number" # e.g., +91xxxxxxxxxx

# === Your public ngrok voice webhook. This will change everytime the server gets restarted. Please update accordingly ===
voice_url_base = "https://727f-49-207-232-154.ngrok-free.app"

# === Read DE data from CSV ===
with open("Input_data.csv", newline='', encoding='utf-8') as f:
    reader = list(csv.DictReader(f))

# === Choose DE row ===
selected_index = 0  # 👈 Change this index to test different DEs
de = reader[selected_index]
de_id = de['DE_ID']
de_name = de['First_Name']

print(f"📞 Calling {de_name} (DE_ID: {de_id}) at {verified_number}")

# === Build Twilio client and trigger call ===
client = Client(account_sid, auth_token)

call = client.calls.create(
    to=verified_number,
    from_=twilio_number,
    url=f"{voice_url_base}/voice?de_id={de_id}"
)

print(f"✅ Call triggered. Call SID: {call.sid}")
