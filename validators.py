from fastapi import HTTPException

VALID_REGIONS = ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Rangpur", "Barisal", "Mymensingh"]
VALID_FARM_TYPES = ["Small", "Medium", "Large", "Commercial"]
VALID_CROP_CATEGORIES = ["Cereal", "Vegetable", "Fruit", "Pulse", "Oilseed", "Cash Crop", "Spice"]
VALID_SEASONS = ["Spring", "Summer", "Autumn", "Winter"]
VALID_GROWING_SEASONS = ["Rabi", "Kharif", "Zaid", "Year-Round"]
VALID_MARKET_TYPES = ["Local", "Wholesale", "Export", "Retail", "Government Procurement"]
VALID_PRICE_TIERS = ["Low", "Medium", "High", "Premium"]
VALID_QUALITY_GRADES = ["A", "B", "C", "D"]
VALID_PESTICIDE_RESIDUES = ["None", "Trace", "Low", "High"]
VALID_WATER_REQUIREMENTS = ["Low", "Medium", "High"]
VALID_YEARS = [2022, 2023, 2024]
VALID_QUARTERS = [1, 2, 3, 4]
VALID_METRICS = ["profit", "revenue", "yield"]


def validate(value, valid_list, field_name):
    """Validate and return normalized value (case-insensitive for strings)"""
    if value is None:
        return None
    
    # For integers, check directly
    if isinstance(value, int):
        if value not in valid_list:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid value '{value}' for '{field_name}'. Accepted: {valid_list}"
            )
        return value
    
    # For strings, do case-insensitive matching
    value_lower = str(value).lower()
    for valid_value in valid_list:
        if str(valid_value).lower() == value_lower:
            return valid_value  # Return the properly cased version
    
    raise HTTPException(
        status_code=422,
        detail=f"Invalid value '{value}' for '{field_name}'. Accepted: {valid_list}"
    )
