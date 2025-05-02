import json
from flask import Flask, request, jsonify
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
from flask_cors import CORS
load_dotenv()
API_KEY = os.getenv("API_KEY")
AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


endpoint = "AZURE_OPENAI_ENDPOINT"
api_version = "2024-12-01-preview"
subscription_key = "API_KEY"
DEPLOYMENT_NAME = "gpt-4o"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key
)


def build_mcp_prompt(data, season):
    return {
        "version": "1.0",
        "context": {
            "role": "agriculture-advisor",
            "memory": [],
            "tools": ["provide_farming_advice"]
        },
        "task": {
            "crop": data['crop'],
            "rainfall": data['rainfall'],
            "temperature": data['temperature'],
            "soil_type": data['soil_type'],
            "region": data['region'],
            "month": data['month'],
            "season": season
        }
    }

# Generate farming advice
def generate_farming_advice(mcp_prompt):
    system_prompt = (
        "You are an agriculture expert and advisor. Your task is to provide simple, friendly, and easy-to-understand advice "
        "for a local farmer. Use a conversational tone, avoid technical jargon, and give practical, actionable suggestions. "
        "Make sure to include easy-to-follow steps for the farmer to follow. Use clear examples if necessary and keep the advice "
        "positive and encouraging."
    )
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(mcp_prompt)}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    return response.choices[0].message.content

@app.route('/')
def index():
    return jsonify({"message": "MCP Server is running!"})

@app.route('/generate-advice', methods=['POST'])
def get_advice():
    data = request.json

    try:
        month = int(data['month'])
        if month in [6, 7, 8, 9]:
            season = "Kharif"
        elif month in [10, 11, 12, 1]:
            season = "Rabi"
        else:
            season = "Zaid"

        mcp = build_mcp_prompt(data, season)
        advice = generate_farming_advice(mcp)

        return jsonify({"farming_advice": advice})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Run Flask App ===
if __name__ == '__main__':
    app.run(debug=True)
