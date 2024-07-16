import gandai as ts
import requests
from gandai import models, secrets

HEADERS = {
    "Authorization": secrets.access_secret_version("GRATA_API_TOKEN"),
    "Content-Type": "application/json",
}


def find_similar(domain: str, search: models.Search) -> list:
    api_filters = _get_api_filter(search)
    similiar_filters = {
        "domain": domain,
        "grata_employees_estimates_range": api_filters[
            "grata_employees_estimates_range"
        ],
        "headquarters": api_filters["headquarters"],
        "ownership": api_filters["ownership"],
        "exclude": api_filters["exclude"],
    }
    # print(similiar_filters)
    response = requests.post(
        "https://search.grata.com/api/v1.3/search-similar/",
        headers=HEADERS,
        json=similiar_filters,
    )
    data = response.json()
    # print("find_similar:", data)
    data["companies"] = data.get("results", [])  # asking grata about this

    return data["companies"]


def find_by_criteria(search: models.Search) -> list:
    # rethink this
    # consider handling "25 skipped", etc

    pages = search.criteria.result_count / 25
    companies = []
    api_filters = _get_api_filter(search)

    def _find_by_criteria(api_filters: dict, page_token=None) -> dict:
        if page_token:
            api_filters["page_token"] = page_token
        response = requests.post(
            "https://search.grata.com/api/v1.3/search/",
            headers=HEADERS,
            json=api_filters,
        )
        data = response.json()
        return data

    print(api_filters)
    resp = _find_by_criteria(api_filters)
    page_token = resp.get("page_token")
    companies.extend(resp.get("companies", []))
    if pages > 1:
        for _ in range(1, int(pages)):
            resp = _find_by_criteria(api_filters, page_token)
            companies.extend(resp.get("companies", []))
            page_token = resp.get("page_token")
            if not page_token:
                break

    # should I return last page token?
    return companies


def enrich(domain: str) -> dict:
    response = requests.post(
        "https://search.grata.com/api/v1.3/enrich/",
        headers=HEADERS,
        json={"domain": domain},
    )
    data = response.json()
    data["linkedin"] = data.get("social_linkedin")
    data["ownership"] = data.get("ownership_status")
    return data


def _get_api_filter(search: models.Search) -> dict:
    def _hq_include() -> list:
        hq_include = []
        cities = search.criteria.inclusion.city
        states = search.criteria.inclusion.state
        countries = search.criteria.inclusion.country

        if len(cities) > 0:
            # front-end validates only one state when city selected
            state = ts.constants.STATES[states[0]]
            for city in cities:
                hq_include.append(
                    {"city": city, "state": state, "country": "United States"}
                )
            return hq_include

        if len(states) > 0:
            for state in states:
                hq_include.append({"state": ts.constants.STATES[state]})
        elif len(countries) > 0:
            for country in countries:
                hq_include.append({"country": ts.constants.COUNTRIES[country]})
        return hq_include

    def _hq_exclude() -> list:
        hq_exclude = []
        for state in search.criteria.exclusion.state:
            hq_exclude.append({"state": ts.constants.STATES[state]})
        return hq_exclude

    api_filters = {
        "op": search.criteria.operator,
        "include": search.criteria.inclusion.keywords,
        "exclude": search.criteria.exclusion.keywords,
        "grata_employees_estimates_range": search.criteria.inclusion.employees_range,
        "ownership": search.criteria.inclusion.ownership,
        "headquarters": {
            "include": _hq_include(),
            "exclude": _hq_exclude(),
        },
    }
    # print(api_filters)
    return api_filters
