#!/usr/bin/env python3
"""
Debug script to test Perplexity API connection
"""

import requests
import json
from utils import get_api_key

def test_api_connection():
    """Test the Perplexity API with a simple request"""

    # Get API key
    api_key = get_api_key()
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    # Simple test payload
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Respond with valid JSON only containing a 'response' field."
            },
            {
                "role": "user", 
                "content": "Say hello in JSON format"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 100,
    }
    
    print("Testing Perplexity API connection...")
    print(f"URL: {url}")
    print(f"API Key: {api_key[:10]}...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"\nFull Response: {json.dumps(response_data, indent=2)}")
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0]['message']['content']
                print(f"\nAI Response Content: {content}")
                
                # Try to parse as JSON
                try:
                    parsed_json = json.loads(content)
                    print(f"Successfully parsed JSON: {parsed_json}")
                except json.JSONDecodeError as e:
                    print(f"Failed to parse AI response as JSON: {e}")
            else:
                print("No choices found in response")
        else:
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_api_connection() 