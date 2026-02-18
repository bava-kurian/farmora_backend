import requests
import random
import time

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"  # Assuming local backend run
# Use the URL from .env if needed, but local is usually safer for seeding
# If using the tunnel URL, ensure it's accessible.
# Based on previous .env: https://315c8ggh-8000.inc1.devtunnels.ms
# Let's try localhost first as it's more reliable for scripts running on the same machine.

# Sample Users (Pseudo-random mobile numbers)
USERS = [
    {"name": "Ramesh Kumar", "mobile": "9876543210"},
    {"name": "Suresh Patel", "mobile": "9123456780"},
    {"name": "Anita Singh", "mobile": "9988776655"},
    {"name": "Vikram Reddy", "mobile": "9876500000"},
    {"name": "Meera Joshi", "mobile": "9112233445"},
]

# Sample Content
TOPICS = [
    {"title": "Best fertilizer for Wheat?", "content": "I am planning to sow wheat next week. What is the best fertilizer combination for sandy loam soil? I used DAP last year but yield was average.", "tags": ["wheat", "fertilizer", "soil"]},
    {"title": "Dealing with Aphids in Cotton", "content": "My cotton crop is infested with aphids. I tried neem oil but it's not working effectively. Any chemical suggestions that are safe?", "tags": ["cotton", "pests", "pest-control"]},
    {"title": "Drip irrigation subsidy in Maharashtra", "content": "Does anyone know the current subsidy percentage for drip irrigation installation for small farmers in Maharashtra? And what documents are required?", "tags": ["irrigation", "subsidy", "maharashtra"]},
    {"title": "Organic farming certification process", "content": "I want to switch to organic farming for my vegetable patch. How long does the certification process take and what are the costs involved?", "tags": ["organic", "certification", "vegetables"]},
    {"title": "Tractor maintenance tips", "content": "Sharing some tips for tractor maintenance: 1. Check oil levels daily. 2. Clean air filter weekly. 3. Greasing every 50 hours of operation. What else do you recommend?", "tags": ["tractor", "machinery", "maintenance"]},
    {"title": "Market price for Onion in Nashik", "content": "Hearing rumors that onion prices are going to crash next month. Should I sell my stock now or hold? Current mandates seem unstable.", "tags": ["onion", "market-price", "nashik"]},
    {"title": "Solar pump installation experience", "content": "Just installed a 5HP solar pump. It's working great for my 3 acre farm. No electricity bills! Highly recommend it if you have good sunlight.", "tags": ["solar", "pump", "irrigation"]},
    {"title": "Hydroponics feasibility for tomatoes", "content": "Is anyone doing hydroponic tomato farming? What is the initial setup cost for a 500 sq ft polyhouse?", "tags": ["hydroponics", "tomato", "technology"]},
    {"title": "New government scheme for seeds", "content": "Saw a news article about free high-yield seeds distribution. Anyone knows where to apply? Block office has no info yet.", "tags": ["schemes", "seeds", "government"]},
    {"title": "Rainwater harvesting techniques", "content": "With monsoon approaching, let's discuss simple rainwater harvesting methods for open wells. Recharge pits are cost effective.", "tags": ["water", "harvesting", "monsoon"]},
]

def create_user_if_needed(user):
    url = f"{BACKEND_URL}/register"
    payload = {"mobile_number": user["mobile"]}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Registered user: {user['name']} ({user['mobile']})")
        else:
            print(f"Failed to register user {user['name']}: {response.text}")
    except Exception as e:
        print(f"Error registering user {user['name']}: {e}")

def create_posts():
    print(f"Seeding posts to {BACKEND_URL}...")
    
    # Register users first
    for user in USERS:
        create_user_if_needed(user)
        
    for i, topic in enumerate(TOPICS):
        user = random.choice(USERS)
        
        headers = {
            "Content-Type": "application/json",
            "X-User-Phone": user["mobile"]
        }
        
        payload = {
            "title": topic["title"],
            "content": topic["content"],
            "tags": topic["tags"]
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/community/posts", json=payload, headers=headers)
            if response.status_code == 200:
                print(f"[{i+1}/{len(TOPICS)}] Created post: '{topic['title']}' by {user['name']}")
            else:
                print(f"Failed to create post: {response.text}")
        except Exception as e:
            print(f"Error connecting to backend: {e}")
            return

def main():
    create_posts()
    print("\nSeeding complete!")

if __name__ == "__main__":
    main()
