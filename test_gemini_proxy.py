import os
import asyncio
from openai import OpenAI
import google.generativeai as genai
from google.api_core.client_options import ClientOptions

# Configuration
PROXY_URL = "https://gemini-balance-do.dpathsg.workers.dev"
AUTH_KEY = "AIzaSyAy6PSYQnFw379t09Zl-SLVUVoVM3tEe5K"

def test_openai_client():
    print("-" * 50)
    print("Testing OpenAI Client...")
    print("-" * 50)
    
    # Configure OpenAI client to point to the proxy
    client = OpenAI(
        api_key=AUTH_KEY,
        base_url=f"{PROXY_URL}/v1"
    )

    try:
        response = client.chat.completions.create(
            model="gemini-3-flash-preview",  # Using gemini-3-flash-preview
            messages=[
                {"role": "user", "content": "Hello, can you confirm you are receiving this message through the OpenAI client?"}
            ]
        )
        print("OpenAI Response Success!")
        print("Response Content:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI Test Failed: {e}")

def test_genai_client():
    print("\n" + "-" * 50)
    print("Testing Google GenAI Client...")
    print("-" * 50)

    # Note: google-generativeai SDK is stricter about endpoints. 
    # We attempt to configure it to use the proxy via ClientOptions.
    # The worker forwards paths like /v1beta/models/... so we point the API endpoint to the worker domain.
    
    try:
        # Configure the library with the API key
        genai.configure(
            api_key=AUTH_KEY,
            transport="rest",
            client_options=ClientOptions(
                api_endpoint=PROXY_URL.replace("https://", "") # api_endpoint expects host, not full URL usually, but let's try strict host
            )
        )

        # However, the SDK constructs URLs like https://{api_endpoint}/v1beta/...
        # Our proxy expects https://gemini-balance-do.dpathsg.workers.dev/v1beta/...
        # So passing the host (without protocol) is usually correct for ClientOptions.

        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        response = model.generate_content("Hello, can you confirm you are receiving this message through the GenAI client?")
        
        print("GenAI Response Success!")
        print("Response Content:")
        print(response.text)
    except Exception as e:
        print(f"GenAI Test Failed: {e}")
        print("\nNote: The standard Google GenAI SDK might have trouble with custom endpoints depending on version.")
        print("Attempting fallback test using direct REST call to simulate GenAI SDK behavior...")
        
        # Fallback manual test if SDK fails (often due to SSL/Endpoint validation in the SDK)
        import requests
        url = f"{PROXY_URL}/v1beta/models/gemini-3-flash-preview:generateContent?key={AUTH_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": "Hello, this is a fallback REST check."}]
            }]
        }
        try:
            r = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            if r.status_code == 200:
                print("Fallback REST Response Success!")
                print(r.json()['candidates'][0]['content']['parts'][0]['text'])
            else:
                print(f"Fallback REST failed: {r.status_code} - {r.text}")
        except Exception as inner_e:
            print(f"Fallback failed: {inner_e}")

if __name__ == "__main__":
    print(f"Targeting Proxy: {PROXY_URL}")
    print(f"Using Key: {AUTH_KEY[:5]}...{AUTH_KEY[-5:]}")
    
    test_openai_client()
    test_genai_client()
