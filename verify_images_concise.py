import requests

def verify_images():
    base_url = "http://127.0.0.1:8000"
    try:
        resp = requests.get(f"{base_url}/uber/equipment/nearby", params={"lat": 9.93, "long": 76.26, "radius_km": 50})
        if resp.status_code != 200:
            print(f"Failed: {resp.status_code}")
            return
        
        equipments = resp.json()
        print(f"Count: {len(equipments)}")
        for eq in equipments:
            if eq.get("images"):
                img = eq["images"][0]
                if img.startswith("data:"):
                    print(f"Type: {eq['equipment_type']} | IMG: DATA-URI | Len: {len(img)}")
                # else:
                #     print(f"Type: {eq['equipment_type']} | IMG: URL | Val: {img[:30]}...")
            else:
                print(f"Type: {eq['equipment_type']} | IMG: NONE")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_images()
