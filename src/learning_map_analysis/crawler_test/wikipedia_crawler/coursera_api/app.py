import requests
import json

# Replace with your own API key
with open('local.json', 'r') as f:
    data = json.load(f)
API_KEY = data["api-key"]
COURSE_SLUG = 'research-methods'  # Replace with the slug of the Coursera course

# Base URL for Coursera's developer API
BASE_URL = 'https://api.coursera.org/api'

# Function to fetch course details
def get_course_modules(api_key, course_slug):
    # Endpoint for the course
    course_url = f"{BASE_URL}/onDemandCourses.v1?q=slug&slug={course_slug}"
    
    # Headers with API Key for authentication
    headers = {
        'Authorization': f"Bearer {api_key}"
    }
    
    # Making the API call to fetch course information
    response = requests.get(course_url, headers=headers)
    
    if response.status_code == 200:
        course_data = response.json()
        print("data is")
        print(course_data)
        if 'elements' in course_data and len(course_data['elements']) > 0:
            course_id = course_data['elements'][0]['id']
            
            # Fetch course modules using the course ID
            modules_url = f"{BASE_URL}/onDemandModules.v1?q=courseId&courseId={course_id}&includes=lessons"
            response_modules = requests.get(modules_url, headers=headers)
            
            if response_modules.status_code == 200:
                modules_data = response_modules.json()
                
                # List of modules
                for module in modules_data['elements']:
                    module_title = module.get('name', 'Unnamed Module')
                    print(f"Module: {module_title}")
                    
                    # List lessons in the module
                    for lesson_id in module.get('lessonIds', []):
                        print(f"  Lesson ID: {lesson_id}")
            else:
                print(f"Failed to fetch modules: {response_modules.status_code}")
        else:
            print("Course not found or no elements in response.")
    else:
        print(f"Failed to fetch course: {response.status_code}")

# Call the function
get_course_modules(API_KEY, COURSE_SLUG)