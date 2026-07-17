import os
import sys
import requests
from dotenv import load_dotenv

def get_groq_response(api_key, user_input):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        "model": "llama-3.1-8b-instant",
        "stream": False,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with API: {e}")
        if 'response' in locals() and response is not None and response.text:
            print(f"Details: {response.text}")
        return None

def main():
    load_dotenv()
    print("--- Single Response Chatbot (powered by Groq) ---")
    
    # You can get your free API key at https://console.groq.com/keys
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        api_key = input("Please enter your Groq API Key (or set GROQ_API_KEY environment variable): ").strip()
    
    if not api_key:
        print("API Key is required to run the chatbot.")
        sys.exit(1)

    print("\nWhat would you like to ask?")
    user_input = input("You: ").strip()
    
    if not user_input or user_input.lower() in ['exit', 'quit']:
        print("Goodbye!")
        sys.exit(0)
        
    print("\nFetching response from Groq...")
    response = get_groq_response(api_key, user_input)
    
    if response:
        print(f"\nGroq: {response}\n")

if __name__ == "__main__":
    main()
