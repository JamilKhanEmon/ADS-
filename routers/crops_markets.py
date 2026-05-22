from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from database import get_df
from validators import (
    validate, VALID_CROP_CATEGORIES, VALID_SEASONS, VALID_YEARS,
    VALID_REGIONS, VALID_WATER_REQUIREMENTS, VALID_MARKET_TYPES,
    VALID_PRICE_TIERS, VALID_QUALITY_GRADES, VALID_PESTICIDE_RESIDUES,
    VALID_QUARTERS, VALID_GROWING_SEASONS
)

router = APIRouter(tags=["Crop & Market Intelligence"])


# ── Endpoint 5: Crop Yield Efficiency ────────────────────────────────────────
@router.get("/crops/yield-efficiency")
def yield_efficiency(
    crop_category: Optional[str] = Query(None, description="Filter by crop category. Values: Cereal, Vegetable, Fruit, Pulse, Oilseed, Cash Crop, Spice (case-insensitive)"),
    season: Optional[str] = Query(None, description="Filter by season. Values: Spring, Summer, Autumn, Winter, Rabi, Kharif, Zaid, Year-Round (case-insensitive)"),
    year: Optional[int] = Query(None, description="Filter by year. Values: 2022, 2023, 2024"),
    region: Optional[str] = Query(None, description="Filter by region. Values: Dhaka, Chittagong, Sylhet, Rajshahi, Khulna, Rangpur, Barisal, Mymensingh (case-insensitive)"),
    water_requirement: Optional[str] = Query(None, description="Filter by water requirement. Values: Low, Medium, High (case-insensitive)"),
):
    # Validate and normalize to proper case
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category")
    season = validate(season, VALID_SEASONS + VALID_GROWING_SEASONS, "season")
    year = validate(year, VALID_YEARS, "year")
    region = validate(region, VALID_REGIONS, "region")
    water_requirement = validate(water_requirement, VALID_WATER_REQUIREMENTS, "water_requirement")

    # Join with dim_crop to get actual benchmark yield (avg_yield_ton_per_ha) and water_requirement
    query = """
        SELECT 
            v.*,
            c.avg_yield_ton_per_ha AS yield_benchmark_ton_per_ha,
            c.water_requirement
        FROM vw_harvest_full v
        JOIN fact_harvest_sales f ON v.harvest_id = f.harvest_id
        JOIN dim_crop c ON f.crop_id = c.crop_id
    """
    df = get_df(query)

    filters_applied = {}
    if crop_category:
        df = df[df["crop_category"] == crop_category]
        filters_applied["crop_category"] = crop_category
    if season:
        if season in VALID_GROWING_SEASONS:
            df = df[df["growing_season"] == season]
        else:
            df = df[df["season"] == season]
        filters_applied["season"] = season
    if year:
        df = df[df["year"] == year]
        filters_applied["year"] = year
    if region:
        df = df[df["region"] == region]
        filters_applied["region"] = region
    if water_requirement:
        df = df[df["water_requirement"] == water_requirement]
        filters_applied["water_requirement"] = water_requirement

    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for the given filters.")

    # Calculate actual yield per ha for each harvest event
    df["yield_ton_per_ha"] = df["quantity_harvested_ton"] / df["area_planted_ha"]
    df["yield_ton_per_ha"] = df["yield_ton_per_ha"].fillna(0.0)

    # Group by crop
    grouped = df.groupby(["crop_name", "crop_category", "growing_season", "yield_benchmark_ton_per_ha"]).agg(
        actual_avg_yield=("yield_ton_per_ha", "mean"),
        total_area_planted_ha=("area_planted_ha", "sum"),
    ).reset_index()

    data = []
    for _, row in grouped.iterrows():
        benchmark = float(row["yield_benchmark_ton_per_ha"])
        actual = round(float(row["actual_avg_yield"]), 2)
        efficiency = round((actual / benchmark * 100) if benchmark > 0.0 else 0.0, 2)
        data.append({
            "crop_name": row["crop_name"],
            "crop_category": row["crop_category"],
            "avg_yield_benchmark_ton_per_ha": round(benchmark, 2),
            "actual_avg_yield_ton_per_ha": actual,
            "efficiency_pct": efficiency,
            "total_area_planted_ha": round(float(row["total_area_planted_ha"]), 2),
            "season": row["growing_season"],
        })

    return {"filters_applied": filters_applied, "data": data}


# ── Endpoint 6: Seasonal Revenue Trend ──────────────────────────────────────
@router.get("/crops/seasonal-trend")
def seasonal_trend(
    crop_name: Optional[str] = Query(None, description="Filter by crop name. Example: Potato, Rice, Wheat, Tomato (case-insensitive)"),
    crop_category: Optional[str] = Query(None, description="Filter by crop category. Values: Cereal, Vegetable, Fruit, Pulse, Oilseed, Cash Crop, Spice (case-insensitive)"),
    year: Optional[int] = Query(None, description="Filter by year. Values: 2022, 2023, 2024"),
    quarter: Optional[int] = Query(None, description="Filter by quarter. Values: 1, 2, 3, 4"),
    market_type: Optional[str] = Query(None, description="Filter by market type. Values: Local, Wholesale, Export, Retail, Government Procurement (case-insensitive)"),
):
    # Validate and normalize to proper case
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category")
    year = validate(year, VALID_YEARS, "year")
    quarter = validate(quarter, VALID_QUARTERS, "quarter")
    market_type = validate(market_type, VALID_MARKET_TYPES, "market_type")

    # Use vw_harvest_full directly because vw_revenue_by_crop_year lacks season/quarter details
    df = get_df("SELECT * FROM vw_harvest_full")

    filters_applied = {}
    if crop_name:
        # Case-insensitive match for crop_name
        df = df[df["crop_name"].str.lower() == crop_name.lower()]
        filters_applied["crop_name"] = crop_name
    if crop_category:
        df = df[df["crop_category"] == crop_category]
        filters_applied["crop_category"] = crop_category
    if year:
        df = df[df["year"] == year]
        filters_applied["year"] = year
    if quarter:
        df = df[df["quarter"] == quarter]
        filters_applied["quarter"] = quarter
    if market_type:
        df = df[df["market_type"] == market_type]
        filters_applied["market_type"] = market_type

    if df.empty:
        raise HTTPException(status_code=404, detail="No trend data found for the given filters.")

    grouped = df.groupby(["crop_name", "year", "quarter", "season"]).agg(
        total_quantity_sold_ton=("quantity_sold_ton", "sum"),
        total_revenue_bdt=("revenue_bdt", "sum"),
        num_harvests=("harvest_id", "count"),
    ).reset_index()

    # Sort results for cleaner presentation
    grouped = grouped.sort_values(["crop_name", "year", "quarter"])

    trend = []
    for _, row in grouped.iterrows():
        qty = float(row["total_quantity_sold_ton"])
        rev = float(row["total_revenue_bdt"])
        trend.append({
            "crop_name": row["crop_name"],
            "year": int(row["year"]),
            "quarter": int(row["quarter"]),
            "season": row["season"],
            "total_quantity_sold_ton": round(qty, 2),
            "total_revenue_bdt": round(rev, 2),
            "avg_price_per_ton_bdt": round(rev / qty, 2) if qty > 0.0 else 0.0,
            "num_harvests": int(row["num_harvests"]),
        })

    return {"filters_applied": filters_applied, "trend": trend}


# ── Endpoint 7: Market Price Comparison ─────────────────────────────────────
@router.get("/markets/price-comparison")
def price_comparison(
    market_type: Optional[str] = Query(None, description="Filter by market type. Values: Local, Wholesale, Export, Retail, Government Procurement (case-insensitive)"),
    crop_category: Optional[str] = Query(None, description="Filter by crop category. Values: Cereal, Vegetable, Fruit, Pulse, Oilseed, Cash Crop, Spice (case-insensitive)"),
    year: Optional[int] = Query(None, description="Filter by year. Values: 2022, 2023, 2024"),
    season: Optional[str] = Query(None, description="Filter by season. Values: Spring, Summer, Autumn, Winter, Rabi, Kharif, Zaid, Year-Round (case-insensitive)"),
    price_tier: Optional[str] = Query(None, description="Filter by price tier. Values: Low, Medium, High, Premium (case-insensitive)"),
    district: Optional[str] = Query(None, description="Filter by district. Example: Chittagong, Narayanganj, Dhaka (case-insensitive)"),
):
    # Validate and normalize to proper case
    market_type = validate(market_type, VALID_MARKET_TYPES, "market_type")
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category")
    year = validate(year, VALID_YEARS, "year")
    season = validate(season, VALID_SEASONS + VALID_GROWING_SEASONS, "season")
    price_tier = validate(price_tier, VALID_PRICE_TIERS, "price_tier")

    # Join with dim_market to get the market's district (which is different from the farm's district)
    query = """
        SELECT 
            v.*,
            m.district AS district
        FROM vw_harvest_full v
        JOIN fact_harvest_sales f ON v.harvest_id = f.harvest_id
        JOIN dim_market m ON f.market_id = m.market_id
    """
    df = get_df(query)

    filters_applied = {}
    if market_type:
        df = df[df["market_type"] == market_type]
        filters_applied["market_type"] = market_type
    if crop_category:
        df = df[df["crop_category"] == crop_category]
        filters_applied["crop_category"] = crop_category
    if year:
        df = df[df["year"] == year]
        filters_applied["year"] = year
    if season:
        if season in VALID_GROWING_SEASONS:
            df = df[df["growing_season"] == season]
        else:
            df = df[df["season"] == season]
        filters_applied["season"] = season
    if price_tier:
        df = df[df["price_tier"] == price_tier]
        filters_applied["price_tier"] = price_tier
    if district:
        df = df[df["district"].str.lower() == district.lower()]
        filters_applied["district"] = district

    if df.empty:
        raise HTTPException(status_code=404, detail="No market data found for the given filters.")

    grouped = df.groupby(["market_name", "market_type", "price_tier", "district", "crop_name"]).agg(
        total_quantity_sold_ton=("quantity_sold_ton", "sum"),
        total_revenue_bdt=("revenue_bdt", "sum"),
    ).reset_index()

    comparison = []
    for _, row in grouped.iterrows():
        qty = float(row["total_quantity_sold_ton"])
        rev = float(row["total_revenue_bdt"])
        comparison.append({
            "market_name": row["market_name"],
            "market_type": row["market_type"],
            "price_tier": row["price_tier"],
            "district": row["district"],
            "crop_name": row["crop_name"],
            "avg_price_per_ton_bdt": round(rev / qty, 2) if qty > 0.0 else 0.0,
            "total_quantity_sold_ton": round(qty, 2),
            "total_revenue_bdt": round(rev, 2),
        })

    return {"filters_applied": filters_applied, "comparison": comparison}


# ── Endpoint 8: Quality Grade Breakdown ─────────────────────────────────────
@router.get("/crops/quality-breakdown")
def quality_breakdown(
    crop_id: Optional[int] = Query(None, description="Filter by crop ID. Values: 1 to 20"),
    crop_category: Optional[str] = Query(None, description="Filter by crop category. Values: Cereal, Vegetable, Fruit, Pulse, Oilseed, Cash Crop, Spice (case-insensitive)"),
    year: Optional[int] = Query(None, description="Filter by year. Values: 2022, 2023, 2024"),
    region: Optional[str] = Query(None, description="Filter by region. Values: Dhaka, Chittagong, Sylhet, Rajshahi, Khulna, Rangpur, Barisal, Mymensingh (case-insensitive)"),
    market_type: Optional[str] = Query(None, description="Filter by market type. Values: Local, Wholesale, Export, Retail, Government Procurement (case-insensitive)"),
    pesticide_residue: Optional[str] = Query(None, description="Filter by pesticide residue. Values: None, Trace, Low, High (case-insensitive)"),
):
    # Validate and normalize to proper case
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category")
    year = validate(year, VALID_YEARS, "year")
    region = validate(region, VALID_REGIONS, "region")
    market_type = validate(market_type, VALID_MARKET_TYPES, "market_type")
    pesticide_residue = validate(pesticide_residue, VALID_PESTICIDE_RESIDUES, "pesticide_residue")

    # Join with fact_harvest_sales to get crop_id mapping
    query = """
        SELECT 
            v.*,
            f.crop_id
        FROM vw_harvest_full v
        JOIN fact_harvest_sales f ON v.harvest_id = f.harvest_id
    """
    df = get_df(query)

    filters_applied = {}
    if crop_id:
        df = df[df["crop_id"] == crop_id]
        filters_applied["crop_id"] = crop_id
    if crop_category:
        df = df[df["crop_category"] == crop_category]
        filters_applied["crop_category"] = crop_category
    if year:
        df = df[df["year"] == year]
        filters_applied["year"] = year
    if region:
        df = df[df["region"] == region]
        filters_applied["region"] = region
    if market_type:
        df = df[df["market_type"] == market_type]
        filters_applied["market_type"] = market_type
    if pesticide_residue:
        df = df[df["pesticide_residue"] == pesticide_residue]
        filters_applied["pesticide_residue"] = pesticide_residue

    if df.empty:
        raise HTTPException(status_code=404, detail="No quality data found for the given filters.")

    total = len(df)

    grade_dist = {}
    for grade in ["A", "B", "C", "D"]:
        subset = df[df["quality_grade"] == grade]
        count = len(subset)
        grade_dist[grade] = {
            "count": count,
            "pct": round(count / total * 100, 2) if total > 0 else 0.0,
            "avg_revenue_bdt": round(float(subset["revenue_bdt"].mean()), 2) if count > 0 else 0.0,
        }

    pesticide_dist = {}
    for level in ["None", "Trace", "Low", "High"]:
        subset = df[df["pesticide_residue"] == level]
        count = len(subset)
        pesticide_dist[level] = {
            "count": count,
            "pct": round(count / total * 100, 2) if total > 0 else 0.0,
        }

    return {
        "filters_applied": filters_applied,
        "total_records": total,
        "grade_distribution": grade_dist,
        "pesticide_residue_breakdown": pesticide_dist,
    }
