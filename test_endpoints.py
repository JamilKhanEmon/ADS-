from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_tests():
    print("[INFO] Starting endpoint testing...")
    
    # ── Test Endpoint 1: Farm Summary ──────────────────────────────────────────
    print("\n--- Testing GET /farms/summary ---")
    # Test without filters
    res = client.get("/farms/summary")
    print(f"No filters: status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  total_farms: {data.get('total_farms')}")
        print(f"  first farm: {data.get('data')[0] if data.get('data') else None}")
    
    # Test with valid filters
    res = client.get("/farms/summary?region=Dhaka&year=2023")
    print(f"Valid filters (region=Dhaka&year=2023): status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  total_farms: {data.get('total_farms')}")
        print(f"  filters_applied: {data.get('filters_applied')}")
        
    # Test with invalid filter value (should return 422)
    res = client.get("/farms/summary?region=InvalidCity")
    print(f"Invalid filter (region=InvalidCity): status={res.status_code}")
    if res.status_code == 422:
        print("  [OK] Correctly returned 422 for invalid filter value.")
    else:
        print(f"  [FAIL] Expected 422, got {res.status_code}. Response: {res.text}")

    # ── Test Endpoint 2: Single Farm Performance ─────────────────────────────────
    print("\n--- Testing GET /farms/{farm_id}/performance ---")
    # Test valid farm_id
    res = client.get("/farms/1/performance")
    print(f"Valid farm_id=1: status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  farm_name: {data.get('farm_name')}")
        print(f"  owner: {data.get('owner')}")
        print(f"  performance record count: {len(data.get('performance', []))}")
        
    # Test with filters
    res = client.get("/farms/1/performance?year=2023&crop_category=Cereal")
    print(f"Valid farm_id=1 with filters: status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  performance record count: {len(data.get('performance', []))}")

    # Test invalid farm_id (should return 404)
    res = client.get("/farms/999/performance")
    print(f"Invalid farm_id=999: status={res.status_code}")
    if res.status_code == 404:
        print("  [OK] Correctly returned 404 for missing farm_id.")
    else:
        print(f"  [FAIL] Expected 404, got {res.status_code}. Response: {res.text}")

    # ── Test Endpoint 3: Top Farms Ranking ──────────────────────────────────────
    print("\n--- Testing GET /farms/top ---")
    # Test default
    res = client.get("/farms/top")
    print(f"Default (metric=profit, limit=10): status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  metric: {data.get('metric')}")
        print(f"  rankings count: {len(data.get('rankings', []))}")
        if data.get('rankings'):
            print(f"  rank 1 farm: {data.get('rankings')[0]}")

    # Test with metric=yield and limit=5
    res = client.get("/farms/top?metric=yield&limit=5&region=Rajshahi")
    print(f"metric=yield & limit=5: status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  metric: {data.get('metric')}")
        print(f"  filters: {data.get('filters_applied')}")
        print(f"  rankings: {data.get('rankings')}")

    # Test invalid limit (should return 422)
    res = client.get("/farms/top?limit=-5")
    print(f"Invalid limit=-5: status={res.status_code}")
    if res.status_code == 422:
         print("  [OK] Correctly returned 422 for invalid limit.")

    # ── Test Endpoint 4: Loss Analysis ─────────────────────────────────────────
    print("\n--- Testing GET /farms/loss-analysis ---")
    res = client.get("/farms/loss-analysis?season=Kharif&year=2023&quality_grade=C")
    print(f"Filters applied: status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  summary: {data.get('summary')}")
        print(f"  breakdown count: {len(data.get('breakdown', []))}")
        if data.get('breakdown'):
            print(f"  first breakdown row: {data.get('breakdown')[0]}")

    # ── Test Endpoint 5: Crop Yield Efficiency ─────────────────────────────────
    print("\n--- Testing GET /crops/yield-efficiency ---")
    res = client.get("/crops/yield-efficiency?crop_category=Cereal&year=2023")
    print(f"Filters applied: status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  data count: {len(data.get('data', []))}")
        if data.get('data'):
            print(f"  first crop: {data.get('data')[0]}")

    # Test invalid water requirement filter (should return 422)
    res = client.get("/crops/yield-efficiency?water_requirement=VeryHigh")
    print(f"Invalid water_requirement=VeryHigh: status={res.status_code}")
    if res.status_code == 422:
         print("  [OK] Correctly returned 422 for invalid water requirement.")

    # ── Test Endpoint 6: Seasonal Revenue Trend ─────────────────────────────────
    print("\n--- Testing GET /crops/seasonal-trend ---")
    res = client.get("/crops/seasonal-trend?crop_category=Vegetable&year=2023")
    print(f"Filters applied: status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  trend count: {len(data.get('trend', []))}")
        if data.get('trend'):
            print(f"  first trend row: {data.get('trend')[0]}")

    # ── Test Endpoint 7: Market Price Comparison ───────────────────────────────
    print("\n--- Testing GET /markets/price-comparison ---")
    res = client.get("/markets/price-comparison?crop_category=Cereal&year=2023&market_type=Wholesale")
    print(f"Filters applied: status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  comparison count: {len(data.get('comparison', []))}")
        if data.get('comparison'):
            print(f"  first comparison row: {data.get('comparison')[0]}")

    # ── Test Endpoint 8: Quality Grade Breakdown ───────────────────────────────
    print("\n--- Testing GET /crops/quality-breakdown ---")
    res = client.get("/crops/quality-breakdown?crop_category=Fruit&year=2023&region=Rajshahi")
    print(f"Filters applied: status={res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"  total_records: {data.get('total_records')}")
        print(f"  grade_distribution: {data.get('grade_distribution')}")
        print(f"  pesticide_residue_breakdown: {data.get('pesticide_residue_breakdown')}")

    print("\n[INFO] Endpoint testing completed!")

if __name__ == "__main__":
    run_tests()
