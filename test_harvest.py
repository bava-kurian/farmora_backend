import httpx
import asyncio
from datetime import date, timedelta

async def test_harvest():
    url = "http://127.0.0.1:8000/api/harvest-predict"
    
    # Test Case 1: Wheat sown 110 days ago (Maturity should be high)
    sowing_date = date.today() - timedelta(days=110)
    payload = {
        "crop_type": "Wheat",
        "sowing_date": str(sowing_date),
        "location": "Mumbai"
    }
    
    print(f"Testing with payload: {payload}")
    
    # We can't actually hit the running server unless we start it.
    # But since we are in the agent environment, we might not be able to start uvicorn in background easily 
    # and hit it from the same process without complex setup.
    # Instead, let's just import the router and call the function directly? 
    # No, that requires mocking request objects.
    
    # Better approach for Agent: 
    # 1. Start uvicorn in background using run_command
    # 2. Run this script
    # 3. Kill uvicorn
    
    # For now, this script Just defines the test. I will run it via command.
    async with httpx.AsyncClient() as client:
        for i in range(5):
            try:
                print(f"Attempt {i+1} to connect...")
                response = await client.post(url, json=payload, timeout=30.0)
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.json()}")
                break
            except Exception as e:
                print(f"Failed to connect: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_harvest())
