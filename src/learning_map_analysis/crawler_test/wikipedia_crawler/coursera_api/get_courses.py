import requests
import json

# Replace with your own API key
with open('local.json', 'r') as f:
    data = json.load(f)
API_KEY = data["api-key"]

# Base URL for Coursera's developer API
BASE_URL = 'https://api.coursera.org/api/courses.v1'

# Headers with API Key for authentication
headers = {
    'Authorization': f"Bearer {API_KEY}"
}

# Parameters for the API request
params = {
    'q': 'search',
    'fields': 'name,slug',
    'limit': 10  # Adjust this to get more or fewer courses
}

# Making the API call to fetch courses
response = requests.get(BASE_URL, headers=headers, params=params)

if response.status_code == 200:
    courses_data = response.json()
    if 'elements' in courses_data:
        print("Courses:")
        for course in courses_data['paging']['facets']["subdomains"]["facetEntries"]:
            print(f"- {course['name']} (Slug: {course['id']})")
    else:
        print("No courses found in the response.")
else:
    print(f"Failed to fetch courses: {response.status_code}")