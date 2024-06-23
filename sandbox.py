import requests

url = 'http://localhost:8000/register/'

# Making a POST request
response = requests.post(url)

# Printing the response
print(response.json())

# Printing cookies received
print("Cookies:", response.cookies.get_dict())