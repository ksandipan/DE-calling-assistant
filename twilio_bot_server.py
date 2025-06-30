from flask import Flask, request, Response, session
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
import csv
import datetime
import os

app = Flask(__name__)
app.secret_key = "swiggy-secret"

# === OpenAI Setup ===
client = OpenAI(api_key="YOUR_ACTUAL_API_KEY")  # Replace with your actual API key

# === Load DE data ===
DE_DATA = {}
with open("Input_data.csv", newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        DE_DATA[row['DE_ID']] = row

# === Logging Setup ===
LOG_CSV = "call_logs.csv"
if not os.path.exists(LOG_CSV) or os.path.getsize(LOG_CSV) == 0:
    with open(LOG_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "DE_ID", "First_Name", "Caller", "Language", "Transcript", "Reason Category", "Follow-up", "Interest", "Raw GPT Response", "Followup_Tag"])

FOLLOW_UP_QUESTIONS = {
    "Health/Personal Emergency": {"en": "Are you feeling better now?", "hi": "क्या आप अब ठीक हैं?"},
    "Alternative Employment": {"en": "Is your new job permanent?", "hi": "क्या आपकी नई नौकरी स्थायी है?"},
    "Compensation Concerns": {"en": "Was the payout too low?", "hi": "क्या भुगतान बहुत कम था?"},
    "Insufficient Orders": {"en": "Were you getting enough deliveries?", "hi": "क्या आपको पर्याप्त डिलीवरी मिल रही थी?"},
    "Technical Issues": {"en": "Was the app or device giving trouble?", "hi": "क्या ऐप या डिवाइस में समस्या आ रही थी?"},
    "Temporary Break/Vacation": {"en": "Back soon or taking more time?", "hi": "क्या आप जल्द वापस आ रहे हैं या और समय लेंगे?"},
    "Dissatisfaction/Policy": {"en": "Did a recent policy bother you?", "hi": "क्या कोई हालिया नीति आपको परेशान कर रही थी?"},
    "Other/Unclear": {"en": "Would you like to tell us more?", "hi": "क्या आप कुछ और साझा करना चाहेंगे?"},
    "Error": {"en": "Can you say it again briefly?", "hi": "क्या आप इसे फिर से कह सकते हैं?"}
}

@app.route("/voice", methods=['POST'])
def voice():
    caller = request.form.get('From', 'Unknown')
    de_id = request.args.get('de_id')
    de = DE_DATA.get(de_id)

    if not de:
        return Response("<Response><Say>Invalid DE ID. Goodbye.</Say></Response>", mimetype='application/xml')

    preferred_lang = de.get('Preferred_language', 'english').lower()
    twilio_lang = 'hi-IN' if preferred_lang == 'hindi' else 'en-US'
    is_hindi = (preferred_lang == 'hindi')

    session['caller'] = caller
    session['de_id'] = de_id
    session['lang'] = twilio_lang
    session['is_hindi'] = is_hindi
    session['first_name'] = de['First_Name']
    session['tenure'] = de['Tenure_Months']
    session['rating'] = de['Rating']
    session['last_login'] = de['Last_Login_Days_Ago']

    if is_hindi:
        greeting = f"नमस्ते {de['First_Name']}! आप {de['Tenure_Months']} महीनों से हमारे साथ हैं और आपकी रेटिंग {de['Rating']} है। हमने देखा कि आपने {de['Last_Login_Days_Ago']} दिनों से लॉगिन नहीं किया है। कृपया बताएं कि आपने डिलीवरी क्यों बंद कर दी?"
    else:
        greeting = f"Hello {de['First_Name']}, you have been with us for {de['Tenure_Months']} months and have a rating of {de['Rating']}. We noticed you haven't logged in for {de['Last_Login_Days_Ago']} days. Can you please tell us why?"

    print("✅ Voice route for DE:", de_id)
    response = VoiceResponse()
    gather = Gather(input='speech', action='/gather', method='POST', timeout=8, speechTimeout='auto', language=twilio_lang)
    gather.say(greeting)
    response.append(gather)
    response.say("We didn't catch that. Goodbye!")
    response.hangup()
    return Response(str(response), mimetype='application/xml')

@app.route("/gather", methods=['POST'])
def gather():
    response = VoiceResponse()
    print("🔍 Request fields:", dict(request.form))

    speech_result = request.form.get('SpeechResult')
    if not speech_result:
        print("⚠️ No speech detected in /gather")
        response.say("हमें आपकी बात समझ नहीं आई। कृपया दोबारा कॉल करें।")
        response.hangup()
        return Response(str(response), mimetype='application/xml')

    speech_result = speech_result.strip()
    print(f"📞 Speech input received: {speech_result}")

    caller = session.get('caller', 'Unknown')
    lang = session.get('lang', 'en-US')
    is_hindi = session.get('is_hindi', False)
    de_id = session.get('de_id', '')
    de_name = session.get('first_name', '')

    reason_category = "Unclassified"
    raw_response = ""
    session['transcript'] = speech_result

    if speech_result:
        try:
            system_prompt = f"You are helping Swiggy classify inactivity reasons for a delivery executive. The DE has {session['tenure']} months tenure, {session['rating']} rating, and last logged in {session['last_login']} days ago. Categorize their reason into one of: [Health/Personal Emergency, Alternative Employment, Compensation Concerns, Insufficient Orders, Technical Issues, Temporary Break/Vacation, Dissatisfaction/Policy, Other/Unclear]."
            gpt_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": speech_result}
                ],
                max_tokens=20,
                temperature=0
            )
            reason_category = gpt_response.choices[0].message.content.strip()
            raw_response = reason_category
        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            reason_category = "Error"
            raw_response = str(e)

    session['reason'] = reason_category
    session['gpt_raw'] = raw_response

    response.say(f"Thanks. We noted: {reason_category}.")
    follow_up_q = FOLLOW_UP_QUESTIONS.get(reason_category, FOLLOW_UP_QUESTIONS["Other/Unclear"])
    question_to_say = follow_up_q['hi'] if is_hindi else follow_up_q['en']

    print(f"🔁 Asking follow-up question: {question_to_say}")

    try:
        gather2 = Gather(
            input='speech',
            action='/followup',
            method='POST',
            timeout=8,
            speechTimeout='auto',
            language=lang
        )
        gather2.say(question_to_say)
        response.append(gather2)
    except Exception as e:
        print(f"❌ Error in follow-up gather: {e}")
        response.say("There was an issue asking the next question. Goodbye.")
        response.hangup()

    print("📤 Response to /gather:", str(response))
    return Response(str(response), mimetype='application/xml')

@app.route("/followup", methods=['POST'])
def followup():
    response = VoiceResponse()
    is_hindi = session.get('is_hindi', False)

    speech_result = request.form.get('SpeechResult')
    if not speech_result:
        print("⚠️ No speech detected in /followup")
        if is_hindi:
            response.say("हम आपकी बात नहीं समझ पाए। धन्यवाद।")
        else:
            response.say("We couldn’t understand that. Thank you.")
        response.hangup()
        return Response(str(response), mimetype='application/xml')

    follow_up_response = speech_result.strip()
    print(f"🗣️ Follow-up response: {follow_up_response}")
    session['followup'] = follow_up_response

    response.say("Thanks for sharing.")
    gather3 = Gather(
        input='speech',
        action='/interest',
        method='POST',
        timeout=8,
        speechTimeout='auto',
        language=session.get('lang', 'en-US')
    )
    gather3.say("Would you like to come back and deliver with us?")
    response.append(gather3)
    return Response(str(response), mimetype='application/xml')

@app.route("/interest", methods=['POST'])
def interest():
    response = VoiceResponse()
    interest_reply = request.form.get('SpeechResult', '').strip()
    print(f"📌 Interest response: {interest_reply}")
    session['interest'] = interest_reply

    if "yes" in interest_reply.lower():
        response.say("That's great! We'll help you get started again.")
        interest_value = "Yes"
    elif "maybe" in interest_reply.lower():
        response.say("Noted. We'll reach out again soon.")
        interest_value = "Maybe"
    else:
        response.say("Understood. Thanks for your time.")
        interest_value = "No"

    response.say("Goodbye!")
    response.hangup()

    # Determine follow-up tag
    reason = session.get('reason', '').lower()
    tag_followup = (
        interest_value in ["No", "Maybe"]
        or reason in ["dissatisfaction/policy", "compensation concerns", "other/unclear", "error"]
    )

    # Final Logging
    with open(LOG_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            session.get('de_id', ''),
            session.get('first_name', ''),
            session.get('caller', 'Unknown'),
            session.get('lang', 'en-US'),
            session.get('transcript', ''),
            session.get('reason', ''),
            session.get('followup', ''),
            interest_value,
            session.get('gpt_raw', ''),
            "Yes" if tag_followup else "No"
        ])

    return Response(str(response), mimetype='application/xml')

if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    app.run(port=5000)