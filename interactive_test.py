import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_input(prompt, default=None):
    prompt_str = f"{prompt} [{default}]: " if default is not None else f"{prompt}: "
    val = input(prompt_str).strip()
    if not val and default is not None:
        return default
    return val if val else None

def show_menu():
    print("\n" + "="*50)
    print("      AGRICULTURE API INTERACTIVE CLIENT")
    print("="*50)
    print("1. GET /farms/summary")
    print("2. GET /farms/{farm_id}/performance")
    print("3. GET /farms/top")
    print("4. GET /farms/loss-analysis")
    print("5. GET /crops/yield-efficiency")
    print("6. GET /crops/seasonal-trend")
    print("7. GET /markets/price-comparison")
    print("8. GET /crops/quality-breakdown")
    print("9. Exit")
    print("="*50)

def main():
    while True:
        show_menu()
        choice = input("Select an option (1-9): ").strip()
        if choice == "9":
            print("Goodbye!")
            break
            
        if choice not in [str(i) for i in range(1, 9)]:
            print("Invalid choice, please select 1-9.")
            continue
            
        params = {}
        url = ""
        
        try:
            if choice == "1":
                url = f"{BASE_URL}/farms/summary"
                print("\nEnter filters (leave blank to skip):")
                region = get_input("Region (e.g. Dhaka, Rajshahi)")
                farm_type = get_input("Farm Type (Small, Medium, Large, Commercial)")
                year = get_input("Year (2022, 2023, 2024)")
                season = get_input("Season (e.g. Spring, Summer, Rabi, Kharif)")
                if region: params["region"] = region
                if farm_type: params["farm_type"] = farm_type
                if year: params["year"] = int(year)
                if season: params["season"] = season
                
            elif choice == "2":
                farm_id = get_input("Farm ID (integer)", default="1")
                url = f"{BASE_URL}/farms/{farm_id}/performance"
                print("\nEnter filters (leave blank to skip):")
                year = get_input("Year (2022, 2023, 2024)")
                crop_cat = get_input("Crop Category (e.g. Cereal, Vegetable)")
                m_type = get_input("Market Type (e.g. Wholesale, Local)")
                if year: params["year"] = int(year)
                if crop_cat: params["crop_category"] = crop_cat
                if m_type: params["market_type"] = m_type
                
            elif choice == "3":
                url = f"{BASE_URL}/farms/top"
                print("\nEnter filters (leave blank to skip):")
                metric = get_input("Metric (profit, revenue, yield)", default="profit")
                region = get_input("Region (e.g. Dhaka, Rajshahi)")
                farm_type = get_input("Farm Type (Small, Medium, Large, Commercial)")
                year = get_input("Year (2022, 2023, 2024)")
                limit = get_input("Limit (positive integer)", default="10")
                if metric: params["metric"] = metric
                if region: params["region"] = region
                if farm_type: params["farm_type"] = farm_type
                if year: params["year"] = int(year)
                if limit: params["limit"] = int(limit)
                
            elif choice == "4":
                url = f"{BASE_URL}/farms/loss-analysis"
                print("\nEnter filters (leave blank to skip):")
                region = get_input("Region (e.g. Dhaka, Rajshahi)")
                year = get_input("Year (2022, 2023, 2024)")
                season = get_input("Season (e.g. Spring, Summer, Rabi, Kharif)")
                grade = get_input("Quality Grade (A, B, C, D)")
                crop_cat = get_input("Crop Category (e.g. Cereal, Vegetable)")
                if region: params["region"] = region
                if year: params["year"] = int(year)
                if season: params["season"] = season
                if grade: params["quality_grade"] = grade
                if crop_cat: params["crop_category"] = crop_cat
                
            elif choice == "5":
                url = f"{BASE_URL}/crops/yield-efficiency"
                print("\nEnter filters (leave blank to skip):")
                crop_cat = get_input("Crop Category (e.g. Cereal, Vegetable)")
                season = get_input("Season (e.g. Spring, Summer, Rabi, Kharif)")
                year = get_input("Year (2022, 2023, 2024)")
                region = get_input("Region (e.g. Dhaka, Rajshahi)")
                water = get_input("Water Requirement (Low, Medium, High)")
                if crop_cat: params["crop_category"] = crop_cat
                if season: params["season"] = season
                if year: params["year"] = int(year)
                if region: params["region"] = region
                if water: params["water_requirement"] = water
                
            elif choice == "6":
                url = f"{BASE_URL}/crops/seasonal-trend"
                print("\nEnter filters (leave blank to skip):")
                crop_name = get_input("Crop Name (e.g. Aman Rice, Garlic)")
                crop_cat = get_input("Crop Category (e.g. Cereal, Vegetable)")
                year = get_input("Year (2022, 2023, 2024)")
                quarter = get_input("Quarter (1, 2, 3, 4)")
                m_type = get_input("Market Type (e.g. Wholesale, Local)")
                if crop_name: params["crop_name"] = crop_name
                if crop_cat: params["crop_category"] = crop_cat
                if year: params["year"] = int(year)
                if quarter: params["quarter"] = int(quarter)
                if m_type: params["market_type"] = m_type
                
            elif choice == "7":
                url = f"{BASE_URL}/markets/price-comparison"
                print("\nEnter filters (leave blank to skip):")
                m_type = get_input("Market Type (e.g. Wholesale, Local)")
                crop_cat = get_input("Crop Category (e.g. Cereal, Vegetable)")
                year = get_input("Year (2022, 2023, 2024)")
                season = get_input("Season (e.g. Spring, Summer, Rabi, Kharif)")
                tier = get_input("Price Tier (Low, Medium, High, Premium)")
                district = get_input("District (e.g. Dhaka, Dinajpur)")
                if m_type: params["market_type"] = m_type
                if crop_cat: params["crop_category"] = crop_cat
                if year: params["year"] = int(year)
                if season: params["season"] = season
                if tier: params["price_tier"] = tier
                if district: params["district"] = district
                
            elif choice == "8":
                url = f"{BASE_URL}/crops/quality-breakdown"
                print("\nEnter filters (leave blank to skip):")
                crop_id = get_input("Crop ID (integer)")
                crop_cat = get_input("Crop Category (e.g. Cereal, Vegetable)")
                year = get_input("Year (2022, 2023, 2024)")
                region = get_input("Region (e.g. Dhaka, Rajshahi)")
                m_type = get_input("Market Type (e.g. Wholesale, Local)")
                pest = get_input("Pesticide Residue (None, Trace, Low, High)")
                if crop_id: params["crop_id"] = int(crop_id)
                if crop_cat: params["crop_category"] = crop_cat
                if year: params["year"] = int(year)
                if region: params["region"] = region
                if m_type: params["market_type"] = m_type
                if pest: params["pesticide_residue"] = pest

            print(f"\nSending GET request to: {url}")
            print(f"Parameters: {params}")
            
            res = requests.get(url, params=params)
            print(f"Status Code: {res.status_code}")
            try:
                print(json.dumps(res.json(), indent=2))
            except Exception:
                print("Response content is not JSON:")
                print(res.text)
                
        except ValueError as ve:
            print(f"\nInput Error: {ve}. Please enter correct data types.")
        except Exception as e:
            print(f"\nRequest failed: {e}")

if __name__ == "__main__":
    main()
