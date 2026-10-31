from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route('/', methods=['GET'])
def home():
    return "Jarvis is Running!"

@app.route('/v1beta/models/<path:model_name>', methods=['POST'])
def proxy_groq(model_name):
    data = request.get_json()
    try:
        contents = data.get('contents', [])
        user_message = contents[-1].get('parts', [{}])[0].get('text', 'Hello') if contents else "Hello"
    except:
        user_message = "Hello"

    if not API_KEY:
        return jsonify({"candidates": [{"content": {"parts": [{"text": "Sir, API Key set nahi hai."}]}}]})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant", 
        "messages": [
            {"role": "system", "content": "You are JARVIS. Reply in Hinglish. Call user Sir."},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.6,
        "max_tokens": 200
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=15)
        response_data = response.json()
        if 'choices' in response_data:
            reply = response_data['choices'][0]['message']['content']
        else:
            reply = "Sir, API Error."
    except Exception as e:
        reply = "Sir, Network Error."

    return jsonify({"candidates": [{"content": {"parts": [{"text": reply}]}}]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
