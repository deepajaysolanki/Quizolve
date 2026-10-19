import requests

# 1. PASTE YOUR CURRENT API KEY HERE DIRECTLY (Don't use .env for this test)
API_KEY = "AIzaSyCkCZiqTBPDHa8oLxG0UhqHqvIBlEIiU5Y"

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

print(f"Testing Key: {API_KEY[:5]}...{API_KEY[-4:]}")
response = requests.get(url)

if response.status_code == 200:
    print("\n✅ SUCCESS! Your key works. Here are the models you can use:")
    models = response.json().get('models', [])
    for m in models:
        # We only care about models that can 'generateContent'
        if "generateContent" in m['supportedGenerationMethods']:
            print(f" - {m['name']}")
else:
    print(f"\n❌ FAILURE (Error {response.status_code})")
    print("Your API Key is invalid or the Project does not have the API enabled.")
    print(f"Google says: {response.text}")