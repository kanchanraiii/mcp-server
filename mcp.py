import os
import json
import re
from openai import AzureOpenAI

endpoint="https://rajat-ma48g9h2-japaneast.cognitiveservices.azure.com/"
api_version="2024-12-01-preview"
subscription_key="9vEQoUBjg5Vr1SBSRDPU2HMcbq3EAjTbnMemi8IxtW2sP3ljy7rUJQQJ99BDACi0881XJ3w3AAAAACOG03WS"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key
)

DEPLOYMENT_NAME = "gpt-4o"
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

# === Step 2: Generate Farming Advice from LLM ===
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

# === Step 3: Main Logic ===
if __name__ == "__main__":
    # Step 3.1: Get user input for farming data
    crop = input("🌾 Crop name (e.g., Rice): ")
    rainfall = float(input("🌧️ Rainfall (in mm): "))
    temperature = float(input("🌡️ Temperature (in °C): "))
    soil_type = input("🧪 Soil Type (e.g., Loamy): ")
    region = input("🗺️ Region/State: ")
    month = int(input("📅 Month number (1–12): "))
    
    # Step 3.2: Determine the season based on month
    if month in [6, 7, 8, 9]:
        season = "Kharif"
    elif month in [10, 11, 12, 1]:
        season = "Rabi"
    else:
        season = "Zaid"
    
    # Step 3.3: Build MCP prompt
    user_task = {
        "crop": crop,
        "rainfall": rainfall,
        "temperature": temperature,
        "soil_type": soil_type,
        "region": region,
        "month": month
    }
    mcp = build_mcp_prompt(user_task, season)
    
    # Step 3.4: Generate farming advice from LLM
    farming_advice = generate_farming_advice(mcp)

    # Step 3.5: Display farming advice to the user
    print("\nFarming Advice Generated:")
    print(farming_advice)