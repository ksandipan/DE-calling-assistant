AI-Powered Voice Assistant for Re-engaging Delivery Executives

🚀 Overview

This project is a prototype of an AI-powered voice calling assistant designed to re-engage inactive delivery executives (DEs). It uses Twilio to make phone calls, OpenAI's GPT model to classify reasons for inactivity, and logs the entire conversation for future action or human follow-up.

📌 Problem Statement

Swiggy and similar delivery platforms face high churn among DEs. The business needs a scalable, low-cost, and personalized way to:
- Understand why DEs become inactive
- Re-engage them with empathy
- Flag conversations that need manual follow-up

💡 Solution

This prototype simulates a personalized outbound call from Swiggy's assistant. The assistant:
- Reads DE details from a CSV file
- Calls the DE via Twilio
- Speaks in English or Hindi based on DE preference
- Listens to voice response and classifies the reason using OpenAI
- Asks a follow-up question
- Gauges interest to return
- Logs the entire interaction to a CSV, tagging records for human follow-up

🧱 Tech Stack
- Python (Flask)
- Twilio Voice API (Programmable Voice)
- OpenAI GPT-3.5 (via openai SDK)
- ngrok (for local tunneling to Twilio)
- CSV files (for input and output)

📁 Project Structure
de-calling-assistant/
├── README.md
├── Input_data.csv             # Input DE details
├── call_driver.py             # Script to trigger call
├── twilio_bot_server.py       # Flask voice assistant
├── call_logs.csv              # Output logs (generated after first run)
├── requirements.txt           # Python dependencies

🔧 Setup Instructions

1. Clone the repo
git clone https://github.com/ksandipan/DE-calling-assistant.git
cd DE-calling-assistant

2. Install dependencies
pip install -r requirements.txt

3. Setup environment
- Add your OpenAI API key
- Create a Twilio account and get:
- Account SID
- Auth Token
- A verified phone number
- Update these in the scripts as required.

4. Run ngrok to expose Flask app
- ngrok http 5000
- Copy the HTTPS URL shown (e.g., https://abc123.ngrok.io) and configure it in your Twilio number's webhook under Voice > A Call Comes In.

5. Start the Flask assistant server
- python twilio_bot_server.py

6. Trigger a call to a DE
- python call_driver.py
- This will call the DE defined in Input_data.csv. The assistant will converse and log the result.

📊 Logging Output
- A call_logs.csv is generated with:
- DE ID, Name, Language
- Transcript of DE speech
- GPT-classified reason
- Follow-up response
- Rejoin interest
- Flag for human follow-up

🧠 AI + Voice Highlights
- Supports multi-turn voice conversation
- Recognizes speech in English and Hindi
- GPT handles classification reliably
- Custom prompts and multilingual TTS response

📊 Key Metrics to Evaluate Effectiveness

Sl No. Metric - Why it Matters
1. Call Connection Rate - % of calls successfully connected to DEs
2. Response Rate - % of calls where a meaningful response is recorded
3. Classification Confidence - GPT’s ability to classify reasons clearly
4. Re-engagement Interest - % of DEs showing interest to return
5. Follow-up Conversion - % of follow-up tagged DEs who rejoin
6. Call Duration - Should stay under ~1 min for cost-effectiveness
7. Multilingual Accuracy - Speech recognition quality across languages
8. % of DEs returning to job after calling

🧪 Testing Methodology Before Deployment

Step - Description
✅ Unit Testing - Validated Flask routes, Twilio XML (TwiML), GPT prompts
✅ Simulated Calls - Tested calls locally and via verified Twilio number
✅ Language Testing - Hindi/English speech-to-text accuracy evaluated
✅ GPT Response QA - Validated GPT's classification across ~10 test cases
✅ CSV Logging - Verified log completeness and tagging logic
✅ Error Handling - Ensured silent failover and graceful fallback voice messages

🚀 Scaling Strategy If Pilot Succeeds

Area - Action
🧩 Whisper Integration - Improve voice input accuracy, esp. in Indian languages
📊 Dashboard - Live monitoring of calls, classifications, and follow-ups
📬 Follow-up Automation - SMS or agent escalation for tagged DEs
🌎 Regional Rollout - Add support for Bengali, Tamil, Telugu etc.
☁️ Cloud Deployment - Host on secure backend, use cloud functions for calls
🔁 CRM Integration - Push logs directly into DE CRM or internal BI tools

📝 Known issues + What's Next
- Add support for other Indian languages
- Reduce latency
- Improve transcription, accent
- Improve capability to capture local accents, dialects
- Intelligent logic for human follow up
- Edge cases (e.g. handling profanity, long answers, odd reactions, silences etc)
- Secrets need to be managed in secure way

👤 Author
Sandipan Kumar
Email: ksandipan@gmail.com
Github: https://github.com/ksandipan

