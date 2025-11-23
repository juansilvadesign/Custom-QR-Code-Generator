import app
import json

# Create a test client
client = app.app.test_client()

# Mock data
data = {
    'content': 'Hello World',
    'backgroundColor': '#FFFFFF',
    'foregroundColor': '#000000',
    'errorLevel': 'M'
}

# Make a POST request
response = client.post('/api/generate', 
                       data=json.dumps(data),
                       content_type='application/json')

print(f"Status Code: {response.status_code}")
print(f"Response Data: {response.get_data(as_text=True)}")
