import requests

def verify_images():
    base_url = "http://127.0.0.1:8000"
    print("Fetching nearby equipment...")
    try:
        # Use coordinates closer to seeded data (Kochi)
        resp = requests.get(f"{base_url}/uber/equipment/nearby", params={"lat": 9.93, "long": 76.26, "radius_km": 50})
        if resp.status_code != 200:
            print(f"Failed to get equipment: {resp.text}")
            return
        
        equipments = resp.json()
        if not equipments:
            print("No equipment found.")
            return

        print(f"Found {len(equipments)} equipment items.")
        
        for eq in equipments:
            print(f"Checking equipment: {eq['equipment_type']} - {eq['description']}")
            if eq.get("images"):
                img_data = eq["images"][0]
                if img_data.startswith("data:image/webp;base64,"):
                    print("  [PASS] Image is Base64 encoded webp.")
                    print(f"  Length: {len(img_data)} chars")
                elif img_data.startswith("http"):
                     print(f"  [WARN] Image is URL: {img_data}")
                else:
                    print(f"  [FAIL] Unknown image format: {img_data[:30]}...")
            else:
                print("  [WARN] No images found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_images()
