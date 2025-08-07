import requests
import json
import sys

def main():
    print("=== Starting API Test ===")
    print("Python version:", sys.version)
    print("Requests version:", requests.__version__)
    
    url = "http://localhost:8000/hackrx/run"
    print(f"\nTesting URL: {url}")
    
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60",
        "Content-Type": "application/json"
    }

    data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09:11:24Z&se=2027-07-05T09:11:00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT/jUHNO7HzQ=",
        "questions": ["What is the grace period for premium payment?"]
    }

    try:
        print("\nSending request to server...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("\n=== Response ===")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nError Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server. Is it running?")
        print("Make sure to run: uvicorn main:app --reload")
    except requests.exceptions.Timeout:
        print("\nError: Request timed out. The server took too long to respond.")
    except requests.exceptions.RequestException as e:
        print(f"\nError making request: {str(e)}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()