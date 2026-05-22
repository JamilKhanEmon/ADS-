from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from database import get_df
from validators import (
    validate, VALID_REGIONS, VALID_FARM_TYPES, VALID_SEASONS,
    VALID_YEARS, VALID_CROP_CATEGORIES, VALID_MARKET_TYPES,
    VALID_METRICS, VALID_QUALITY_GRADES, VALID_GROWING_SEASONS
)

router = APIRouter(prefix="/farms", tags=["Farm Performance"])


# ── Endpoint 1: Farm Summary ──────────────────────────────────────────────────
@router.get("/summary")
def farm_summary(
    region: Optional[str] = Query(None, description="Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh (case-insensitive, e.g. dhaka, DHAKA)"),
    farm_type: Optional[str] = Query(None, description="Small | Medium | Large | Commercial (case-insensitive, e.g. small, SMALL)"),
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024"),
    season: Optional[str] = Query(None, description="Spring | Summer | Autumn | Winter | Rabi | Kharif | Zaid | Year-Round (case-insensitive, e.g. summer, SUMMER)"),
):
    # Validate and normalize to proper case
    region = validate(region, VALID_REGIONS, "region")
    farm_type = validate(farm_type, VALID_FARM_TYPES, "farm_type")
    year = validate(year, VALID_YEARS, "year")
    season = validate(season, VALID_SEASONS + VALID_GROWING_SEASONS, "season")

    # Query vw_harvest_full because vw_farm_profitability lacks year and season columns
    df = get_df("SELECT * FROM vw_harvest_full")

    filters_applied = {}
    if region:
        df = df[df["region"] == region]
        filters_applied["region"] = region
    if farm_type:
        df = df[df["farm_type"] == farm_type]
        filters_applied["farm_type"] = farm_type
    if year:
        df = df[df["year"] == year]
        filters_applied["year"] = year
    if season:
        if season in VALID_GROWING_SEASONS:
            df = df[df["growing_season"] == season]
        else:
            df = df[df["season"] == season]
        filters_applied["season"] = season

    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for the given filters.")

    # Group by farm to aggregate total revenues, costs, profits and loss percentages
    grouped = df.groupby(["farm_name", "region", "farm_type"]).agg(
        total_revenue_bdt=("revenue_bdt", "sum"),
        total_cost_bdt=("input_cost_bdt", "sum"),
        net_profit_bdt=("net_profit_bdt", "sum"),
        quantity_lost_ton=("quantity_lost_ton", "sum"),
        quantity_harvested_ton=("quantity_harvested_ton", "sum"),
    ).reset_index()

    result = []
    for _, row in grouped.iterrows():
        harvested = float(row["quantity_harvested_ton"])
        lost = float(row["quantity_lost_ton"])
        avg_loss_pct = round((lost / harvested * 100), 2) if harvested > 0 else 0.0

        result.append({
            "farm_name": row["farm_name"],
            "region": row["region"],
            "farm_type": row["farm_type"],
            "total_revenue_bdt": round(float(row["total_revenue_bdt"]), 2),
            "total_cost_bdt": round(float(row["total_cost_bdt"]), 2),
            "net_profit_bdt": round(float(row["net_profit_bdt"]), 2),
            "avg_loss_pct": avg_loss_pct,
        })

    return {
        "total_farms": len(result),
        "filters_applied": filters_applied,
        "data": result,
    }


# ── Endpoint 3: Top Farms (must be before /{farm_id}) ─────────────────────────
@router.get("/top")
def top_farms(
    metric: Optional[str] = Query("profit", description="profit | revenue | yield (case-insensitive, e.g. Profit, PROFIT)"),
    region: Optional[str] = Query(None, description="Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh (case-insensitive, e.g. dhaka, DHAKA)"),
    farm_type: Optional[str] = Query(None, description="Small | Medium | Large | Commercial (case-insensitive, e.g. small, SMALL)"),
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024"),
    limit: Optional[int] = Query(10, description="Positive integer (default: 10)"),
):
    # Validate and normalize to proper case
    metric = validate(metric, VALID_METRICS, "metric")
    region = validate(region, VALID_REGIONS, "region")
    farm_type = validate(farm_type, VALID_FARM_TYPES, "farm_type")
    year = validate(year, VALID_YEARS, "year")
    
    if limit is not None and limit <= 0:
        raise HTTPException(status_code=422, detail="Limit must be a positive integer.")

    # Query joined tables to get farm details, crop benchmarks, and input fields
    query = """
        SELECT 
            v.farm_name,
            v.region,
            v.farm_type,
            v.year,
            v.revenue_bdt,
            v.net_profit_bdt,
            v.quantity_harvested_ton,
            v.area_planted_ha,
            c.avg_yield_ton_per_ha AS yield_benchmark_ton_per_ha
        FROM vw_harvest_full v
        JOIN fact_harvest_sales f ON v.harvest_id = f.harvest_id
        JOIN dim_crop c ON f.crop_id = c.crop_id
    """
    df = get_df(query)

    filters_applied = {"limit": limit}
    if region:
        df = df[df["region"] == region]
        filters_applied["region"] = region
    if farm_type:
        df = df[df["farm_type"] == farm_type]
        filters_applied["farm_type"] = farm_type
    if year:
        df = df[df["year"] == year]
        filters_applied["year"] = year

    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for the given filters.")

    # Calculate yield efficiency for each harvest record
    df["yield_efficiency"] = 0.0
    valid_mask = (df["area_planted_ha"] > 0) & (df["yield_benchmark_ton_per_ha"] > 0)
    df.loc[valid_mask, "yield_efficiency"] = (
        df.loc[valid_mask, "quantity_harvested_ton"] / 
        df.loc[valid_mask, "area_planted_ha"] / 
        df.loc[valid_mask, "yield_benchmark_ton_per_ha"]
    ) * 100

    # Group and aggregate metrics
    grouped = df.groupby(["farm_name", "region", "farm_type"]).agg(
        net_profit_bdt=("net_profit_bdt", "sum"),
        total_revenue_bdt=("revenue_bdt", "sum"),
        avg_yield_efficiency=("yield_efficiency", "mean"),
    ).reset_index()

    metric_col_map = {
        "profit": "net_profit_bdt",
        "revenue": "total_revenue_bdt",
        "yield": "avg_yield_efficiency",
    }
    sort_col = metric_col_map[metric]
    grouped = grouped.sort_values(sort_col, ascending=False).head(limit)

    rankings = []
    for rank, (_, row) in enumerate(grouped.iterrows(), start=1):
        rankings.append({
            "rank": rank,
            "farm_name": row["farm_name"],
            "region": row["region"],
            "farm_type": row["farm_type"],
            "net_profit_bdt": round(float(row["net_profit_bdt"]), 2),
            "total_revenue_bdt": round(float(row["total_revenue_bdt"]), 2),
        })

    return {"metric": metric, "filters_applied": filters_applied, "rankings": rankings}


# ── Endpoint 4: Loss Analysis ─────────────────────────────────────────────────
@router.get("/loss-analysis")
def loss_analysis(
    region: Optional[str] = Query(None, description="Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh (case-insensitive, e.g. dhaka, DHAKA)"),
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024"),
    season: Optional[str] = Query(None, description="Spring | Summer | Autumn | Winter | Rabi | Kharif | Zaid | Year-Round (case-insensitive, e.g. summer, SUMMER)"),
    quality_grade: Optional[str] = Query(None, description="A | B | C | D (case-insensitive, e.g. a, A)"),
    crop_category: Optional[str] = Query(None, description="Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice (case-insensitive, e.g. cereal, CEREAL)"),
):
    # Validate and normalize to proper case
    region = validate(region, VALID_REGIONS, "region")
    year = validate(year, VALID_YEARS, "year")
    season = validate(season, VALID_SEASONS + VALID_GROWING_SEASONS, "season")
    quality_grade = validate(quality_grade, VALID_QUALITY_GRADES, "quality_grade")
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category")

    df = get_df("SELECT * FROM vw_harvest_full")

    filters_applied = {}
    if region:
        df = df[df["region"] == region]
        filters_applied["region"] = region
    if year:
        df = df[df["year"] == year]
        filters_applied["year"] = year
    if season:
        if season in VALID_GROWING_SEASONS:
            df = df[df["growing_season"] == season]
        else:
            df = df[df["season"] == season]
        filters_applied["season"] = season
    if quality_grade:
        df = df[df["quality_grade"] == quality_grade]
        filters_applied["quality_grade"] = quality_grade
    if crop_category:
        df = df[df["crop_category"] == crop_category]
        filters_applied["crop_category"] = crop_category

    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for the given filters.")

    total_harvested = float(df["quantity_harvested_ton"].sum())
    total_lost = float(df["quantity_lost_ton"].sum())
    overall_loss_pct = round((total_lost / total_harvested * 100) if total_harvested else 0.0, 2)

    breakdown_df = df.groupby(["region", "crop_category", "quality_grade", "pesticide_residue"]).agg(
        total_lost_ton=("quantity_lost_ton", "sum"),
        total_harvested_ton=("quantity_harvested_ton", "sum"),
    ).reset_index()

    breakdown = []
    for _, row in breakdown_df.iterrows():
        harvested = float(row["total_harvested_ton"])
        lost = float(row["total_lost_ton"])
        loss_pct = round(lost / harvested * 100, 2) if harvested else 0.0
        breakdown.append({
            "region": row["region"],
            "crop_category": row["crop_category"],
            "quality_grade": row["quality_grade"],
            "total_lost_ton": round(lost, 2),
            "loss_pct": loss_pct,
            "pesticide_residue": row["pesticide_residue"],
        })

    return {
        "filters_applied": filters_applied,
        "summary": {
            "total_harvested_ton": round(total_harvested, 2),
            "total_lost_ton": round(total_lost, 2),
            "overall_loss_pct": overall_loss_pct,
        },
        "breakdown": breakdown,
    }


# ── Endpoint 2: Single Farm Performance (path param — keep last) ──────────────
@router.get("/{farm_id}/performance")
def farm_performance(
    farm_id: int,
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024"),
    crop_category: Optional[str] = Query(None, description="Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice (case-insensitive, e.g. cereal, CEREAL)"),
    market_type: Optional[str] = Query(None, description="Local | Wholesale | Export | Retail | Government Procurement (case-insensitive, e.g. local, LOCAL)"),
):
    # Validate and normalize to proper case
    year = validate(year, VALID_YEARS, "year")
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category")
    market_type = validate(market_type, VALID_MARKET_TYPES, "market_type")

    # Check if the farm exists in the database first
    farm_df = get_df(f"SELECT * FROM dim_farm WHERE farm_id = {farm_id}")
    if farm_df.empty:
        raise HTTPException(status_code=404, detail=f"Farm with ID {farm_id} not found.")

    farm_info = farm_df.iloc[0]

    # Join with fact table to get the farm_id mapping
    query = f"""
        SELECT v.*, f.farm_id 
        FROM vw_harvest_full v 
        JOIN fact_harvest_sales f ON v.harvest_id = f.harvest_id 
        WHERE f.farm_id = {farm_id}
    """
    df = get_df(query)

    filters_applied = {}
    if year:
        df = df[df["year"] == year]
        filters_applied["year"] = year
    if crop_category:
        df = df[df["crop_category"] == crop_category]
        filters_applied["crop_category"] = crop_category
    if market_type:
        df = df[df["market_type"] == market_type]
        filters_applied["market_type"] = market_type

    if df.empty:
        raise HTTPException(status_code=404, detail="No performance data found for the given filters.")

    performance = []
    for _, row in df.iterrows():
        performance.append({
            "crop_name": row["crop_name"],
            "year": int(row["year"]),
            "market_type": row["market_type"],
            "quantity_sold_ton": round(float(row["quantity_sold_ton"]), 2),
            "revenue_bdt": round(float(row["revenue_bdt"]), 2),
            "net_profit_bdt": round(float(row["net_profit_bdt"]), 2),
            "quality_grade": row["quality_grade"],
        })

    return {
        "farm_id": farm_id,
        "farm_name": farm_info["farm_name"],
        "owner": farm_info["owner_name"],
        "region": farm_info["region"],
        "filters_applied": filters_applied,
        "performance": performance,
    }
