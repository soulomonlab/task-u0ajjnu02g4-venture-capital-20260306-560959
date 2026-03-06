import re
from datetime import datetime

# Sample response (page=1, per_page=10) — realistic data for QA validation
sample_response = {
    "items": [
        {
            "id": "vc_001",
            "name": "Nimbus AI",
            "logoUrl": "https://cdn.example.com/logos/nimbus.png",
            "stage": "Series A",
            "industries": ["AI", "SaaS"],
            "short_description": "AI-native analytics for enterprise teams.",
            "raised_amount_usd": 12000000,
            "last_updated": "2026-02-10T12:34:56Z"
        },
        {
            "id": "vc_002",
            "name": "GreenGrid Energy",
            "logoUrl": "https://cdn.example.com/logos/greengrid.png",
            "stage": "Seed",
            "industries": ["Energy", "Hardware"],
            "short_description": "Modular microgrid controllers for emerging markets.",
            "raised_amount_usd": 1500000.50,
            "last_updated": "2026-01-05T09:12:01Z"
        },
        {
            "id": "vc_003",
            "name": "MediLoop",
            "logoUrl": null,
            "stage": "Pre-seed",
            "industries": ["Healthcare", "SaaS"],
            "short_description": "Care coordination tools for clinics.",
            "raised_amount_usd": 250000,
            "last_updated": "2026-02-01T18:00:00Z"
        },
        {
            "id": "vc_004",
            "name": "ParcelFly",
            "logoUrl": "https://cdn.example.com/logos/parcelfly.png",
            "stage": "Series B",
            "industries": ["Logistics", "Transport"],
            "short_description": "Autonomous last-mile delivery robotics.",
            "raised_amount_usd": 45000000,
            "last_updated": "2026-02-08T07:45:30Z"
        },
        {
            "id": "vc_005",
            "name": "EduSpark",
            "logoUrl": "https://cdn.example.com/logos/eduspark.png",
            "stage": "Series A",
            "industries": ["EdTech"],
            "short_description": "Adaptive learning paths powered by ML.",
            "raised_amount_usd": 8000000,
            "last_updated": "2026-01-20T15:22:10Z"
        },
        {
            "id": "vc_006",
            "name": "FarmSense",
            "logoUrl": "https://cdn.example.com/logos/farmsense.png",
            "stage": "Seed",
            "industries": ["AgTech"],
            "short_description": "IoT soil sensors and analytics.",
            "raised_amount_usd": 600000,
            "last_updated": "2026-02-11T11:11:11Z"
        },
        {
            "id": "vc_007",
            "name": "ClearBank",
            "logoUrl": "https://cdn.example.com/logos/clearbank.png",
            "stage": "Series C",
            "industries": ["FinTech"],
            "short_description": "Embedded banking APIs for SMBs.",
            "raised_amount_usd": 98000000,
            "last_updated": "2026-02-09T20:00:00Z"
        },
        {
            "id": "vc_008",
            "name": "AquaPure",
            "logoUrl": null,
            "stage": "Seed",
            "industries": ["WaterTech", "Hardware"],
            "short_description": "Low-cost water purification modules.",
            "raised_amount_usd": 420000,
            "last_updated": "2026-02-02T08:08:08Z"
        },
        {
            "id": "vc_009",
            "name": "Shoply",
            "logoUrl": "https://cdn.example.com/logos/shoply.png",
            "stage": "Series A",
            "industries": ["E-commerce", "SaaS"],
            "short_description": "Checkout optimization for marketplaces.",
            "raised_amount_usd": 5000000,
            "last_updated": "2026-01-30T10:10:10Z"
        },
        {
            "id": "vc_010",
            "name": "BioNext",
            "logoUrl": "https://cdn.example.com/logos/bionext.png",
            "stage": "Series B",
            "industries": ["Biotech"],
            "short_description": "CRISPR-based therapeutic delivery platforms.",
            "raised_amount_usd": 30000000,
            "last_updated": "2026-02-07T14:00:00Z"
        }
    ],
    "total_count": 123,
    "page": 1,
    "per_page": 10
}


ISO8601_Z_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def test_fetchresult_keys_and_types():
    resp = sample_response
    assert isinstance(resp, dict), "FetchResult should be a dict/object"
    for k in ("items", "total_count", "page", "per_page"):
        assert k in resp, f"Missing key in FetchResult: {k}"

    assert isinstance(resp["items"], list), "items must be a list"
    assert isinstance(resp["total_count"], int), "total_count must be integer"
    assert isinstance(resp["page"], int) and resp["page"] >= 1, "page must be 1-based integer"
    assert isinstance(resp["per_page"], int) and resp["per_page"] >= 1, "per_page must be integer"


def test_venture_item_fields_and_types():
    items = sample_response["items"]
    assert len(items) <= sample_response["per_page"]

    for v in items:
        assert isinstance(v.get("id"), str), "id must be a string"
        assert isinstance(v.get("name"), str), "name must be a string"
        assert (v.get("logoUrl") is None) or isinstance(v.get("logoUrl"), str), "logoUrl must be string or null"
        assert isinstance(v.get("stage"), str), "stage must be a string"
        assert isinstance(v.get("industries"), list), "industries must be a list"
        for ind in v.get("industries", []):
            assert isinstance(ind, str), "industry entries must be strings"

        # short_description optional but if present must be string
        sd = v.get("short_description")
        assert (sd is None) or isinstance(sd, str), "short_description must be string or null"

        # raised_amount_usd: numeric (int/float) or null
        ra = v.get("raised_amount_usd")
        assert (ra is None) or isinstance(ra, (int, float)), "raised_amount_usd must be number (USD) or null"

        # last_updated: ISO-8601 Zulu format string
        lu = v.get("last_updated")
        assert isinstance(lu, str), "last_updated must be string"
        assert ISO8601_Z_REGEX.match(lu), f"last_updated not ISO-8601 Z format: {lu}"


def test_pagination_and_counts():
    assert 0 <= sample_response["total_count"]
    assert 1 <= sample_response["per_page"] <= 100, "per_page should be within reasonable bounds (1-100)"


if __name__ == "__main__":
    # quick local run
    import pytest
    pytest.main([__file__])
