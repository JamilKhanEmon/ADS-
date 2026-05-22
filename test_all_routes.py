import requests
import json

base = 'http://localhost:8000'

tests = [
    ('1. GET /farms/summary', '/farms/summary?region=Dhaka&year=2023'),
    ('2. GET /farms/{farm_id}/performance', '/farms/1/performance?year=2023'),
    ('3. GET /farms/top', '/farms/top?metric=profit&limit=3'),
    ('4. GET /farms/loss-analysis', '/farms/loss-analysis?year=2023&season=Winter'),
    ('5. GET /crops/yield-efficiency', '/crops/yield-efficiency?crop_category=Cereal'),
    ('6. GET /crops/seasonal-trend', '/crops/seasonal-trend?year=2023&quarter=1'),
    ('7. GET /markets/price-comparison', '/markets/price-comparison?market_type=Export'),
    ('8. GET /crops/quality-breakdown', '/crops/quality-breakdown?region=Dhaka'),
]

print('=' * 60)
print('TESTING ALL 8 ENDPOINTS')
print('=' * 60)

passed = 0
failed = 0

for name, path in tests:
    try:
        r = requests.get(base + path)
        status = '[OK]' if r.status_code == 200 else '[FAIL]'
        
        if r.status_code == 200:
            passed += 1
        else:
            failed += 1
            
        print(f'\n{status} {name}')
        print(f'      URL: {path}')
        print(f'      Status: {r.status_code}')
        
        data = r.json()
        
        # Show result count based on response structure
        if 'total_farms' in data:
            print(f'      Result: {data["total_farms"]} farms')
        elif 'rankings' in data:
            print(f'      Result: {len(data["rankings"])} rankings')
        elif 'summary' in data and 'breakdown' in data:
            print(f'      Result: {len(data["breakdown"])} breakdown items')
        elif 'data' in data:
            print(f'      Result: {len(data["data"])} items')
        elif 'trend' in data:
            print(f'      Result: {len(data["trend"])} trends')
        elif 'comparison' in data:
            print(f'      Result: {len(data["comparison"])} comparisons')
        elif 'grade_distribution' in data:
            print(f'      Result: {data["total_records"]} records')
        elif 'performance' in data:
            print(f'      Result: {len(data["performance"])} performance records')
            
    except Exception as e:
        failed += 1
        print(f'\n[FAIL] {name} - ERROR: {e}')

print('\n' + '=' * 60)
print(f'RESULTS: {passed} passed, {failed} failed')
print('=' * 60)
