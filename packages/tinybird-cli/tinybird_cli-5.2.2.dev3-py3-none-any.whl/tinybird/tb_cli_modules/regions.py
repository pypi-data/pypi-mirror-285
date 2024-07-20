from typing import List, Optional, TypedDict


class Region(TypedDict):
    name: str
    provider: str
    api_host: str
    host: str
    default_password: Optional[str]


# Maintain in sync with `production.ts`

regions_list: List[Region] = [
    {
        "name": "europe-west3",
        "provider": "gcp",
        "api_host": "https://api.tinybird.co",
        "host": "https://app.tinybird.co/gcp/europe-west3",
        "default_password": "",
    },
    {
        "name": "us-east4",
        "provider": "gcp",
        "api_host": "https://api.us-east.tinybird.co",
        "host": "https://app.tinybird.co/gcp/us-east4",
        "default_password": "",
    },
    {
        "name": "us-east-1",
        "provider": "aws",
        "api_host": "https://api.us-east.aws.tinybird.co",
        "host": "https://app.tinybird.co/aws/us-east-1",
        "default_password": "",
    },
    {
        "name": "us-west-2",
        "provider": "aws",
        "api_host": "https://api.us-west-2.aws.tinybird.co",
        "host": "https://app.tinybird.co/aws/us-west-2",
        "default_password": "",
    },
    {
        "name": "eu-central-1",
        "provider": "aws",
        "api_host": "https://api.eu-central-1.aws.tinybird.co",
        "host": "https://app.tinybird.co/aws/eu-central-1",
        "default_password": "",
    },
]


def regions_has_a_public_region(public_regions: List[Region], initial_regions: List[Region]) -> bool:
    in_a_public_region = False

    for region in initial_regions:
        existing_region = next(
            (
                public_region
                for public_region in public_regions
                if region["api_host"] == public_region["api_host"] or region["host"] == public_region["host"]
            ),
            None,
        )
        if existing_region:
            in_a_public_region = True
            break

    return in_a_public_region


def fill_with_public_regions(regions) -> List[Region]:
    initial_regions = regions.get("regions", [])
    if regions_has_a_public_region(regions_list, initial_regions):
        initial_regions += [
            region for region in regions_list if region["api_host"] not in [r["api_host"] for r in initial_regions]
        ]

    return initial_regions
