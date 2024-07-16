from dataclasses import asdict
from time import time

import gandai as ts
import requests
from dacite import from_dict
from gandai import secrets


def run_acquired_check(domain: str):
    company = ts.query.find_company_by_domain(domain)
    q = f"{company.name} was acquired"
    google_page_one = ts.google.search(q)  # top 10 results, could extend?
    messages = [
        {
            "role": "system",
            "content": f"We are considering buying this company, and want to know if its already been acquired: {asdict(company)}",
        },
        {
            "role": "system",
            "content": f"You searched google for '{q}' and got these results: {google_page_one.to_dict()}",
        },
        {
            "role": "system",
            "content": "You will be asked to answer Yes or No, and provide a justification for your answer. ",
        },
        {
            "role": "system",
            "content": "was_acquired will be one of 'Yes' or 'No'. You will capitalize the first letter of your answer.",
        },
        {
            "role": "system",
            "content": "You will respond with JSON, keys: 'was_acquired' and 'justification'.",
        },
        {
            "role": "user",
            "content": "Has this company recently been acquired?",
        },
    ]

    updates: dict = ts.gpt.ask_gpt4(messages)
    print(updates)
    company.meta = {**company.meta, **updates}
    # this is where I could also make a comment
    ts.query.update_company(company)


def run_similarity_search(search: ts.models.Search, domain: str) -> None:
    search.criteria = ts.query.find_search_criteria(search_uid=search.uid)
    grata_companies = ts.grata.find_similar(domain=domain, search=search)
    ts.query.insert_companies_as_targets(
        companies=grata_companies,
        search_uid=search.uid,
        actor_key="grata",
        # force=True # ok
        source=f"grata/{domain}",
        stage="similar",
    )


def run_criteria_search(search: ts.models.Search, event: ts.models.Event) -> None:
    # don't have to pass the event because the criteria
    # is the event that we're responding to
    search.criteria = from_dict(ts.models.Criteria, event.data)
    grata_companies = ts.grata.find_by_criteria(search)
    ts.query.insert_companies_as_targets(
        companies=grata_companies,
        search_uid=search.uid,
        actor_key="grata",
        force=True,
        source="grata/criteria",
        stage="create",
    )


def run_maps_search(search: ts.models.Search, event: ts.models.Event) -> None:
    existing_search_domains = ts.query.search_targets(search_uid=search.uid)[
        "domain"
    ].to_list()

    def build_place(place_id: str, search: ts.models.Search) -> None:
        resp = ts.google.gmaps.place(
            place_id=place_id, fields=["name", "website", "reviews"]
        )
        place = resp["result"]  # these reviews are valueable
        domain = ts.helpers.clean_domain(place.get("website"))
        if domain is None:
            return None
        if domain in existing_search_domains:
            print(f"domain {domain} already in search. skipping...")
            return None
        new_company = ts.models.Company(
            name=place["name"],
            domain=domain,
            source="Map API",
        )
        ts.query.insert_company(new_company)
        company = ts.query.find_company_by_domain(new_company.domain)

        event = ts.models.Event(
            search_uid=search.uid,
            type="create",
            domain=company.domain,
            actor_key="google",
            data={
                "place": place,  # could limit some
            },
        )

        ts.query.insert_event(event)

    q = event.data["query"]
    results = ts.google.get_google_places(q=q)
    print(results)
    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     executor.map(build_place, results['place_id'].tolist())
    for place in results["place_id"].tolist():
        build_place(place_id=place, search=search)


def run_google_search(search: ts.models.Search, event: ts.models.Event) -> None:
    q = event.data["q"]
    assert len(q) > 0, "q must be a non-empty string"
    results = ts.google.search(q=q, count=event.data.get("count", 10))
    results["domain"] = results["link"].apply(lambda x: ts.helpers.clean_domain(x))
    results = results.rename(columns={"snippet": "description"})
    print(results)
    ts.query.insert_companies_as_targets(
        companies=results[["domain", "description"]].to_dict(orient="records"),
        search_uid=event.search_uid,
        actor_key=event.actor_key,
        source="Google",
    )




def handle_prompt(event: ts.models.Event) -> None:
    print("prompt event:", event)
    messages = [
        {
            "role": "system",
            "content": ts.gpt.HOW_TO_RESPOND,
        },
        {
            "role": "system",
            "content": ts.gpt.HOW_TO_IMPORT,
        },
        {
            "role": "system",
            "content": ts.gpt.HOW_TO_TRANSITION,
        },
        {
            "role": "system",
            "content": ts.gpt.HOW_TO_GOOGLE,
        },
        {
            "role": "system",
            "content": ts.gpt.HOW_TO_GOOGLE_MAPS,
        },
        {
            "role": "system",
            "content": f"the search_uid is {event.search_uid}",
        },
        {
            "role": "system",
            "content": f"the actor_key is {event.actor_key}",
        },
        {"role": "user", "content": event.data["prompt"]},
    ]
    resp = ts.gpt.ask_gpt4(messages)

    print(resp)
    for new_event in resp["events"]:
        print("new event:", new_event)
        new_event["search_uid"] = event.search_uid
        e = from_dict(ts.models.Event, new_event)
        print(e)

        e.data["prompt"] = event.data["prompt"]
        ts.query.insert_event(e)


def enrich_with_gpt(company: ts.models.Company) -> None:
    print("enriching with gpt...")
    try:
        homepage_text = ts.helpers.get_homepage_text(company.domain)
    except Exception as e:
        print(e)
        homepage_text = "<could not fetch homepage>"
    messages = [
        {
            "role": "system",
            "content": f"You will help us evaluate {company.name} for acquisition.",
        },
        {
            "role": "system",
            "content": f"You will consider this existing information: {asdict(company)}",  # the existing (and grata) data
        },
        {
            "role": "system",
            "content": f"You will consider this copy from the company homepage as the most up to date. homepage_text: {homepage_text}",
        },
        {
            "role": "system",
            "content": "You will respond with only the JSON object.",
        },
        {
            "role": "user",
            "content": ts.gpt.HOW_TO_ENRICH,
        },
    ]

    resp = ts.gpt.ask_gpt4(messages)
    update_event = from_dict(ts.models.Event, resp)
    update_event.domain = company.domain
    update_event.data["gpt"] = int(time())
    print(update_event)
    ts.query.insert_event(update_event)
    return resp


def run_enrichment(event: ts.models.Event) -> None:
    domain = event.domain

    company = ts.query.find_company_by_domain(domain)
    if company.meta.get("company_uid"):
        print("company already exists. skipping enrichment...")
    else:
        resp = ts.grata.enrich(company.domain)
        company.name = company.name or resp.get("name")
        company.description = resp.get("description")
        company.meta = {**company.meta, **resp}
        ts.query.update_company(company)

    if company.meta.get("gpt_description"):
        print("company already enriched with gpt. skipping...")
    else:
        enrich_with_gpt(company=company)


def process_event(event_id: int) -> None:
    print("processing event_id: ", event_id)
    event: ts.models.Event = ts.query.find_event_by_id(event_id)
    print(event)
    search = ts.query.find_search(uid=event.search_uid)
    domain = event.domain
    if event.type == "land":
        run_enrichment(event=event)
    elif event.type == "create":
        run_enrichment(event=event)
    elif event.type == "similar":
        run_enrichment(event=event)
    elif event.type == "advance":
        run_enrichment(event=event)
    elif event.type == "validate":
        run_enrichment(event=event)
        run_acquired_check(domain=domain)
        run_similarity_search(search=search, domain=domain)
    elif event.type == "send":
        run_enrichment(event=event)
    elif event.type == "client_approve":
        run_enrichment(event=event)
        run_similarity_search(search=search, domain=domain)  # n=
    elif event.type == "reject":
        pass
    elif event.type == "client_reject":
        pass
    elif event.type == "conflict":
        run_enrichment(event=event)
        run_similarity_search(search=search, domain=domain)
    elif event.type == "client_conflict":
        pass

    elif event.type == "enrich":
        run_enrichment(event=event)
    ## actions
    elif event.type == "prompt":
        handle_prompt(event=event)
    elif event.type == "criteria":
        if len(event.data["inclusion"]["keywords"]) > 0:
            run_criteria_search(search=search, event=event)
    elif event.type == "maps":
        run_maps_search(search=search, event=event)
    elif event.type == "google":
        run_google_search(search=search, event=event)

    elif event.type == "grata_search":
        run_google_search(search=search, event=event)

    elif event.type == "import":
        ts.query.import_targets_from_event(event=event)



    elif event.type == "reset":
        print("💣 Resetting Inbox...")
        ts.query.reset_inbox(search_uid=search.uid)

    elif event.type == "rating":
        # handle rating
        print(event)
        rating = event.data["rating"]
        from_stage = event.data["currentView"]
        if rating == 1:
            ts.query.insert_event(
                ts.models.Event(
                    search_uid=search.uid,
                    type="reject",
                    domain=domain,
                    actor_key=event.actor_key,
                )
            )
        elif rating == 2:
            ts.query.insert_event(
                ts.models.Event(
                    search_uid=search.uid,
                    type="hold",
                    domain=domain,
                    actor_key=event.actor_key,
                )
            )
        elif from_stage in ["land", "create", "advance", "hold", "similar"]:
            ts.query.insert_event(
                ts.models.Event(
                    search_uid=search.uid,
                    type="validate",
                    domain=domain,
                    actor_key=event.actor_key,
                )
            )

    elif event.type == "update":
        if domain:
            company = ts.query.find_company_by_domain(domain)
            if event.data.get("name"):
                company.name = event.data["name"]
            company.meta = {**company.meta, **event.data}
            ts.query.update_company(company)
        else:
            search.meta = {**search.meta, **event.data}
            ts.query.update_search(search)

    elif event.type == "move":

        for domain in event.data["domains"]:
            print("moving domain:", domain)
            ts.query.insert_event(
                ts.models.Event(
                    search_uid=search.uid,
                    domain=domain,
                    type=event.data["stage"],
                    actor_key=event.actor_key,
                )
            )
