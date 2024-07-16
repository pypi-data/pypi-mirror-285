import hashlib
import json
from dataclasses import asdict
from time import time
from typing import Any, List

import pandas as pd
import sqlalchemy
from dacite import from_dict
from dotenv import load_dotenv

load_dotenv()

import gandai as ts
from gandai import helpers
from gandai.db import connect_with_connector
from gandai.models import Actor, Company, Criteria, Event, Search

db = connect_with_connector()


### WRITES ###


def insert_event(event: Event) -> Event:
    with db.connect() as con:
        statement = sqlalchemy.text(
            """
                INSERT INTO event (search_uid, domain, actor_key, type, data) 
                VALUES(:search_uid, :domain, :actor_key, :type, :data)
                ON CONFLICT DO NOTHING
                RETURNING id
            """
        )
        obj = asdict(event)
        obj["data"] = json.dumps(obj["data"])
        result = con.execute(statement, obj)
        # print(result.first())
        _id = result.first()
        event.id = _id[0] if _id else None

        if event.type == "comment":
            con.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW comment"))
        elif event.type == "rating":
            con.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW rating"))

        elif event.type == "criteria":
            con.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW criteria"))
        con.commit()

    ts.trigger_process_event(event_id=event.id)
    return event


def insert_company(company: Company) -> ts.models.Company:
    with db.connect() as con:
        statement = sqlalchemy.text(
            """
                INSERT INTO company (domain, name, description, source) 
                VALUES(:domain, :name, :description, :source)
                ON CONFLICT DO NOTHING
            """
        )
        con.execute(statement, asdict(company))
        con.commit()
    return company  # todo this should return the id


def insert_actor(actor: Actor) -> Actor:
    with db.connect() as con:
        statement = sqlalchemy.text(
            """
                INSERT INTO actor (key, type, name, email) 
                VALUES(:key, :type, :name, :email)
                ON CONFLICT DO NOTHING
            """
        )
        obj = asdict(actor)
        con.execute(statement, obj)
        con.commit()
    return actor


def insert_search(search: Search) -> Search:
    with db.connect() as con:
        statement = sqlalchemy.text(
            """
                INSERT INTO search (uid, label, meta) 
                VALUES(:uid, :label, :meta)
                ON CONFLICT DO NOTHING
            """
        )
        obj = asdict(search)
        obj["meta"] = json.dumps(obj["meta"])
        con.execute(statement, obj)
        con.commit()
    return search





def import_targets_from_event(event: ts.models.Event) -> None:

    source = event.data.get("source")
    targets = search_targets(search_uid=event.search_uid)
    stage_dict = targets.set_index("domain")["stage"].to_dict()

    def get_stage(domain):
        stage_key = stage_dict.get(domain, "Unknown")
        return ts.constants.LABEL_MAP.get(stage_key, "Unknown")

    domains: list = event.data["domains"]

    new_event_ids = []
    with db.connect() as con:
        with con.begin():
            for domain in domains:
                # should these be in same transaction?
                domain = ts.helpers.clean_domain(domain)

                con.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO company (domain, source) 
                        VALUES(:domain, :source)
                        ON CONFLICT (domain) DO UPDATE
                        SET source = EXCLUDED.source
                        """
                    ),
                    {"domain": domain, "source": source},
                )

                result = con.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO event (search_uid, domain, actor_key, type) 
                        VALUES(:search_uid, :domain, :actor_key, :type)
                        ON CONFLICT DO NOTHING
                        RETURNING id
                        """
                    ),
                    {
                        "search_uid": event.search_uid,
                        "actor_key": event.actor_key,
                        "domain": domain,
                        "type": event.data.get("stage", "create"),
                    },
                )

                new_event_id = result.scalar_one()
                if new_event_id is not None:
                    new_event_ids.append(new_event_id)

                if stage_dict.get(domain) is not None:
                    comment = ts.models.Event(
                        search_uid=event.search_uid,
                        actor_key=event.actor_key,  # todo this should be the system
                        domain=domain,
                        type="comment",
                        data={
                            "comment": f"{get_stage(domain)} → {ts.constants.LABEL_MAP[event.data.get('stage')]}"
                        },
                    )
                    ts.query.insert_event(comment)

    for event_id in new_event_ids:
        ts.trigger_process_event(event_id=event_id)

    # resp = {
    #     "inserted": domains,
    #     "protected": list(new_domains.intersection(protected_domains)),
    # }
    # return resp


def insert_companies_as_targets(
    companies: List[Any],
    search_uid: int,
    actor_key: str,
    force: bool = True,
    source: str = None,
    stage: str = "create",
) -> None:
    print(f"Inserting {len(companies)} companies as targets...")

    targets = search_targets(search_uid=search_uid)

    if force:
        # "New keywords should look at companies that were previously rejected"

        targets = targets[targets["stage"] != "reject"]
        protected_domains = targets["domain"].tolist()
    else:
        protected_domains = targets["domain"].tolist()

    ## idea, insert "search" comment for what happened

    inserted = 0
    skipped = 0
    start = time()

    new_event_ids = []
    with db.connect() as con:
        with con.begin():
            for company in companies:
                print(company)
                if helpers.domain_is_none(company.get("domain")):
                    print(f"Missing domain: {company}. Skipping")
                    continue
                # elif company["domain"] in targets["domain"]:
                elif company["domain"] in protected_domains:
                    # print(f"Skipping {company['domain']} as already a target")
                    skipped += 1
                    continue
                else:
                    inserted += 1
                    # print(f"Adding {company['domain']} as target")

                con.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO company (domain, name, description, source) 
                        VALUES(:domain, :name, :description, :source)
                        ON CONFLICT DO NOTHING
                        """
                    ),
                    {
                        "domain": company.get("domain"),
                        "name": company.get("name"),
                        "description": company.get("description"),
                        "source": company.get("source", source),
                    },
                )

                result = con.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO event (search_uid, domain, actor_key, type) 
                        VALUES(:search_uid, :domain, :actor_key, :type)
                        ON CONFLICT DO NOTHING
                        RETURNING id
                        """
                    ),
                    {
                        "search_uid": search_uid,
                        "actor_key": actor_key,
                        "domain": company.get("domain"),
                        "type": stage,
                    },
                )

                # Get the newly inserted ID
                # huh I need to look more into this one
                # but handling as such for now
                print(result)
                try:
                    new_event_id = result.scalar_one()
                    if new_event_id is not None:
                        new_event_ids.append(new_event_id)
                except Exception as e:
                    print(e)

    print(new_event_ids)
    for event_id in new_event_ids:
        ts.trigger_process_event(event_id=event_id)
    print(f"Inserted {inserted}. Skipped {skipped}. Took {time() - start} seconds")


### READS ###
## returns dataframes ##


def searches_query() -> pd.DataFrame:
    statement = f"""
    SELECT 
        s.uid,
        s.label,
        s.updated,
        s.meta->>'type' as type,
        s.meta->>'notes' as notes,
        s.meta->>'products' as products,
        s.meta->>'services' as services,
        s.meta->>'customers' as customers,
        s.meta->>'end_customer' as end_customer,
        s.meta->>'last_list' as last_list,
        s.meta->>'next_due_date' as next_due_date,
        s.meta->>'geographies' as geographies,
        s.meta->>'week' as week,
        s.meta->>'day' as day,
        COALESCE(s.meta->>'search_status', 'active') as search_status
    FROM search s
    ORDER BY updated
    """
    with db.connect() as conn:
        result = conn.execute(sqlalchemy.text(statement))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    df["client"] = df["label"].str.split(" - ").str[0]

    return df


def average_rating_per_search_query():
    query = """
       SELECT
        search_uid,
        AVG(rating::int) AS rating_avg,
        COUNT(rating) as rating_count
    FROM rating 
    GROUP BY search_uid
    """
    return pd.read_sql(query, db)


def validation_history() -> pd.DataFrame:
    stmt = """
    WITH RankedEvents AS (
        SELECT
            e.search_uid,
            a.name as analyst,
            SUM(CASE WHEN e.created >= EXTRACT(EPOCH FROM NOW()) - 1 * 86400 THEN 1 ELSE 0 END) AS last_1_days,
            SUM(CASE WHEN e.created >= EXTRACT(EPOCH FROM NOW()) - 7 * 86400 THEN 1 ELSE 0 END) AS last_7_days,
            SUM(CASE WHEN e.created >= EXTRACT(EPOCH FROM NOW()) - 30 * 86400 THEN 1 ELSE 0 END) AS last_30_days,
            SUM(CASE WHEN e.created >= EXTRACT(EPOCH FROM NOW()) - 90 * 86400 THEN 1 ELSE 0 END) AS last_90_days,
            SUM(CASE WHEN e.type = 'validate' THEN 1 ELSE 0 END) AS total_validations,
            RANK() OVER (PARTITION BY e.search_uid ORDER BY SUM(CASE WHEN e.created >= EXTRACT(EPOCH FROM NOW()) - 30 * 86400 THEN 1 ELSE 0 END) DESC) as rank
        FROM
            event e
        LEFT JOIN
            actor a ON a.key = e.actor_key
        WHERE
            e.type = 'validate'
        GROUP BY
            e.search_uid, analyst
    )
    SELECT
        search_uid,
        analyst,
        last_1_days,
        last_7_days,
        last_30_days,
        last_90_days,
        total_validations
    FROM
        RankedEvents
    WHERE
        rank = 1
        AND last_30_days > 0
    ;
    """
    with db.connect() as conn:
        result = conn.execute(sqlalchemy.text(stmt))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        df["total_validations_pct"] = round(df["total_validations"] / 300, 2)
    return df


def searches_comment_counts():
    statement = f"""
        SELECT 
            e.search_uid as uid,
            COUNT(*) as comment_count
        FROM event e
        WHERE 
            e.type = 'comment'
            AND e.domain is null
            -- last 30 days
            AND e.created >= EXTRACT(EPOCH FROM NOW()) - 30 * 86400
        GROUP BY e.search_uid
        """
    with db.connect() as conn:
        result = conn.execute(sqlalchemy.text(statement))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    return df


def enriched_searches_query():
    searches = searches_query()

    recent_event_count = validation_history()

    df = searches.merge(
        recent_event_count, left_on="uid", right_on="search_uid", how="left"
    )

    df["last_1_days"] = df["last_1_days"].fillna(0)
    df["last_7_days"] = df["last_7_days"].fillna(0)
    df["last_30_days"] = df["last_30_days"].fillna(0)
    df["last_90_days"] = df["last_90_days"].fillna(0)

    df = df.merge(searches_comment_counts(), on="uid", how="left")
    df["comment_count"] = df["comment_count"].fillna(0)

    return df


def actor() -> pd.DataFrame:
    with db.connect() as conn:
        result = conn.execute(
            sqlalchemy.text(
                """
                SELECT * FROM actor
                """
            )
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        df = df.drop(columns=["id", "created", "updated"])
        return df


def buyer() -> pd.DataFrame:
    with db.connect() as conn:
        result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 
                    e.id,
                    e.domain,
                    e.created as updated,
                    a.name as updated_by, 
                    to_char(to_timestamp(e.created), 'YYYY-MM-DD') as change_date,
                    c.name, 
                    c.description,
                    c.source,
                    c.meta->>'ownership' as ownership, 
                    c.meta->>'headquarters' as headquarters,
                    c.meta->>'city' as city,
                    c.meta->>'state' as state,
                    c.meta->>'designation' as designation,
                    c.meta->>'products' as products,
                    c.meta->>'services' as services,
                    c.meta->>'end_customer' as end_customer,
                    c.meta->>'geographies' as geographies,
                    c.meta->>'was_acquired' as was_acquired,
                    c.meta->>'justification' as justification,
                    c.meta->>'year_founded' as year_founded,
                    c.meta->>'linkedin' as linkedin,
                    c.meta->>'linkedin_range' as linkedin_range,
                    c.meta->>'primary_contact' as primary_contact,
                    c.meta->>'industry' as industry,
                    c.meta->>'revenue_estimates' as revenue_estimates,
                    c.meta->>'location_count' as location_count,
                    c.meta->>'business_models' as business_models,
                    c.meta->>'facility_size' as facility_size,
                    c.meta,
                    COALESCE(co.comments, '[]'::jsonb) as comments
                FROM event e
                LEFT JOIN actor a ON e.actor_key = a.key
                LEFT JOIN company c ON e.domain = c.domain
                LEFT JOIN comment co ON e.domain = co.domain
                WHERE e.type = 'buyer'
                """
            )
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    def get_employees(meta):
        if meta.get("employees"):
            # should pull "confirmed employees"
            try:
                return int(meta["employees"])
            except:
                return None
        elif meta.get("grata_employee_estimates"):
            return meta["grata_employee_estimates"].get("count")
        else:
            return None

    df["employees"] = df["meta"].apply(get_employees)
    return df


# def other_searches(search_uid: int) -> pd.DataFrame:
#     query = """
#     SELECT
#         t.domain,
#         jsonb_agg(
#             jsonb_build_object(
#                 'search_uid', t.search_uid,
#                 'domain', t.domain,
#                 'stage', t.stage,
#                 'created', t.created,
#                 'label', t.label
#             )
#         ) AS searches
#     FROM
#         target t
#     LEFT JOIN
#         target tt ON tt.domain = t.domain
#     WHERE
#         tt.search_uid = :search_uid
#         AND t.search_uid != :search_uid
#         AND t.stage != 'reject'
#     GROUP BY
#         t.domain
#         ;
#     """

#     with db.connect() as conn:
#         result = conn.execute(
#             sqlalchemy.text(query),
#             {"search_uid": search_uid},
#         )
#         df = pd.DataFrame(result.fetchall(), columns=result.keys())
#     return df


def search_targets(search_uid: int):
    # arguably the most important query

    statement = """
    WITH RankedEvents AS (
        SELECT *,
            ROW_NUMBER() OVER(PARTITION BY search_uid, domain ORDER BY created DESC) AS rn
        FROM event
        WHERE 
            domain is not null
            AND search_uid = :search_uid
            AND type NOT IN ('comment','rating','criteria','update','review','mute','enrich')
    )
    SELECT 
        e.search_uid, 
        e.domain, 
        e.type as stage, 
        e.created as updated, 
        to_char(to_timestamp(e.created), 'YYYY-MM-DD') as change_date,
        a.name as updated_by, 
        c.name, 
        -- c.description as grata_description,
        c.meta->>'description' as grata_description,
        c.meta->>'gpt_description' as gpt_description,
        c.source,
        -- uh is this necessary?
        c.meta->>'ownership' as ownership, 
        c.meta->>'headquarters' as headquarters,
        c.meta->>'city' as city,
        c.meta->>'state' as state,
        c.meta->>'designation' as designation,
        c.meta->>'products' as products,
        c.meta->>'services' as services,
        c.meta->>'end_customer' as end_customer,
        c.meta->>'geographies' as geographies,
        c.meta->>'was_acquired' as was_acquired,
        c.meta->>'justification' as justification,
        c.meta->>'year_founded' as year_founded,
        c.meta->>'linkedin' as linkedin,
        c.meta->>'linkedin_range' as linkedin_range,
        c.meta->>'primary_contact' as primary_contact,
        c.meta->>'industry' as industry,
        c.meta->>'revenue_estimates' as revenue_estimates,
        c.meta->>'location_count' as location_count,
        c.meta->>'business_models' as business_models,
        c.meta->>'facility_size' as facility_size,
        c.meta->>'contact_name' as contact_name,
        c.meta->>'contact_title' as contact_title,
        c.meta->>'contact_email' as contact_email,
        c.meta->>'contact_phone' as contact_phone,
        c.meta->>'contact_address' as contact_address,
        c.meta->>'gpt' as gpt,
        c.meta,
        r.rating::int, 
        COALESCE(co.comments, '[]'::jsonb) as comments
    FROM RankedEvents e
    LEFT JOIN actor a ON e.actor_key = a.key
    LEFT JOIN company c ON e.domain = c.domain
    LEFT JOIN comment co ON e.search_uid = co.search_uid AND e.domain = co.domain
    LEFT JOIN rating r ON e.search_uid = r.search_uid AND e.domain = r.domain
    
    WHERE 
        e.rn = 1
        AND e.domain != ''
    ;
    """

    with db.connect() as conn:
        result = conn.execute(
            sqlalchemy.text(statement),
            {"search_uid": search_uid},
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    def list_to_csv(list_str) -> str:
        # Convert the string representation of the list to a Python list
        try:
            list_data = json.loads(list_str)

            # Join the elements with a comma
            csv_str = ", ".join(list_data)

            return csv_str
        except:
            return ""

    def get_employees(meta):
        if meta.get("employees"):
            # should pull "confirmed employees"
            try:
                return int(meta["employees"])
            except:
                return None
        elif meta.get("grata_employee_estimates"):
            return meta["grata_employee_estimates"].get("count")
        else:
            return None

    def get_ownership(ownership):
        if ownership == "Bootstrapped":
            return "Private"
        elif ownership == "Investor Backed":
            return "Venture Capital"
        else:
            return ownership

    def get_state(row):
        if row.get("state"):
            return row["state"]
        elif row.get("headquarters"):
            state_name = row["headquarters"].split(",")[-1].strip()
            state_code = ts.constants.STATE_NAMES.get(state_name, "")
            return state_code
        else:
            return None

    def get_city(row):
        if row.get("city"):
            return row["city"]
        elif row.get("headquarters"):
            city_name = row["headquarters"].split(",")[0].strip()
            return city_name
        else:
            return None

    df["end_customer"] = df["end_customer"].apply(list_to_csv)
    df["employees"] = df["meta"].apply(get_employees)
    df["ownership"] = df["ownership"].apply(get_ownership)
    df["state"] = df.apply(get_state, axis=1)
    df["city"] = df.apply(get_city, axis=1)

    return df


def search_comments(search_uid: int) -> pd.DataFrame:
    statement = """
    SELECT 
        e.*,
        a.name as author
    FROM event e
    LEFT JOIN actor a ON e.actor_key = a.key
    WHERE
        e.type = 'comment'
        AND e.domain is null
        AND search_uid = :search_uid
    """

    with db.connect() as conn:
        result = conn.execute(
            sqlalchemy.text(statement),
            {"search_uid": search_uid},
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


def event(search_uid: int) -> pd.DataFrame:
    with db.connect() as conn:
        statement = """
                SELECT *
                FROM event
                WHERE search_uid = :search_uid
            """
        result = conn.execute(sqlalchemy.text(statement), {"search_uid": search_uid})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


def event_history(search_uid: int) -> pd.DataFrame:
    assert isinstance(search_uid, int)
    statement = """
    SELECT 
        e.id,
        e.type as event_type,
        s.label as search_label,
        e.search_uid,
        e.domain,
        e.data,
        a.type as actor_type,
        a.key as actor_key,
        a.name,
        to_timestamp(e.created) as created 
    FROM event e
    JOIN actor a on e.actor_key = a.key
    JOIN search s on e.search_uid = s.uid
    WHERE 
        e.search_uid = :search_uid
        AND e.type != 'mute'
    ORDER BY created DESC
    ;

    """
    with db.connect() as conn:
        result = conn.execute(sqlalchemy.text(statement), {"search_uid": search_uid})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


def search_criteria_history(search_uid: int) -> pd.DataFrame:

    statement = """
    SELECT 
        e.type as event_type,
        s.label as search_label,
        e.search_uid,
        e.data,
        -- a.type as actor_type,
        a.name,
        to_timestamp(e.created) as created 
    FROM event e
    JOIN actor a on e.actor_key = a.key
    JOIN search s on e.search_uid = s.uid
    WHERE 
        e.search_uid = :search_uid
        AND e.type in ('import', 'criteria','google','google_maps','import_searches')
    ORDER BY created DESC
    ;
    """
    with db.connect() as conn:
        result = conn.execute(sqlalchemy.text(statement), {"search_uid": search_uid})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


### FINDERS -> dataclass ###


def find_search(uid: int) -> ts.models.Search:
    with db.connect() as conn:
        statement = """
            SELECT 
                uid, 
                label, 
                meta 
            FROM search
            
            WHERE uid = :uid
            """
        result = conn.execute(sqlalchemy.text(statement), {"uid": uid})

        row = result.fetchone()
        if row is None:
            return None

        obj = dict(zip(result.keys(), row))
        search = from_dict(ts.models.Search, obj)
        search.meta["client"] = search.label.split(" - ")[0]

    return search


def find_search_by_label(label: str) -> ts.models.Search:
    with db.connect() as conn:
        statement = """
            SELECT 
                uid, 
                label, 
                meta 
            FROM search
            
            WHERE label = :label
            """
        result = conn.execute(sqlalchemy.text(statement), {"label": label})

        row = result.fetchone()
        if row is None:
            return None

        obj = dict(zip(result.keys(), row))
        search = from_dict(ts.models.Search, obj)
        # search.meta["client"] = search.label.split(" - ")[0]

    return search


def find_company_by_domain(domain: str) -> Company:
    with db.connect() as conn:
        statement = """
                SELECT *
                FROM company
                WHERE domain = :domain
            """
        result = conn.execute(sqlalchemy.text(statement), {"domain": domain})
        # obj = dict(zip(result.keys(), result.fetchone()))
    if result.rowcount == 0:
        return None
    else:
        obj = dict(zip(result.keys(), result.fetchone()))
        return from_dict(Company, obj)


def find_actor_by_email(email: str) -> Company:
    with db.connect() as conn:
        statement = """
                SELECT *
                FROM actor
                WHERE email = :email
            """
        result = conn.execute(sqlalchemy.text(statement), {"email": email})
        # obj = dict(zip(result.keys(), result.fetchone()))
    if result.rowcount == 0:
        return None
    else:
        obj = dict(zip(result.keys(), result.fetchone()))
        return from_dict(ts.models.Actor, obj)


def find_event_by_id(event_id: int) -> Event:
    with db.connect() as conn:
        statement = """
                SELECT *
                FROM event
                WHERE id = :event_id
            """
        result = conn.execute(sqlalchemy.text(statement), {"event_id": event_id})
        # obj = dict(zip(result.keys(), result.fetchone()))
    if result.rowcount == 0:
        return None
    else:
        obj = dict(zip(result.keys(), result.fetchone()))
        return from_dict(Event, obj)


def find_search_criteria(search_uid: int) -> Criteria:
    ## finds last criteria event
    with db.connect() as conn:
        statement = """
                SELECT *
                FROM event
                WHERE search_uid = :search_uid
                AND type = 'criteria'
                ORDER BY created DESC
                LIMIT 1
            """
        result = conn.execute(sqlalchemy.text(statement), {"search_uid": search_uid})
        # obj = dict(zip(result.keys(), result.fetchone()))
    if result.rowcount == 0:
        return None
    else:
        obj = dict(zip(result.keys(), result.fetchone()))
        return from_dict(Criteria, obj.get("data"))


### UPDATE ###


def update_company(company: Company) -> None:
    with db.connect() as conn:
        statement = """
            UPDATE company
            SET
                uid = :uid,
                name = :name,
                description = :description,
                source = :source,
                meta = :meta,
                updated = FLOOR(EXTRACT(EPOCH FROM NOW()))
            WHERE domain = :domain
            """

        conn.execute(
            sqlalchemy.text(statement),
            {
                "uid": company.uid,
                "name": company.name,
                "description": company.description,
                "domain": company.domain,
                "source": company.source,
                "meta": json.dumps(company.meta),
            },
        )
        # conn.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW target"))
        conn.commit()


def update_search(search: Search) -> None:
    with db.connect() as conn:
        conn.execute(
            sqlalchemy.text(
                """
                UPDATE search
                SET
                    meta = :meta,
                    updated = FLOOR(EXTRACT(EPOCH FROM NOW()))
                WHERE uid = :uid
                """
            ),
            {
                "meta": json.dumps(search.meta),
                "uid": search.uid,
            },
        )
        conn.commit()


### SOFT DELETE ###


def mute_event(event_id: int) -> None:
    # aka soft delete
    with db.connect() as conn:
        conn.execute(
            sqlalchemy.text(
                """
                UPDATE event
                SET
                    type = 'mute'
                WHERE id = :event_id
                """
            ),
            {
                "event_id": event_id,
            },
        )
        conn.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW comment"))
        conn.commit()


### DELETE ###


def delete_comment(comment_id: int) -> None:
    with db.connect() as conn:
        statement = """
                DELETE FROM event
                WHERE id = :comment_id
            """
        conn.execute(sqlalchemy.text(statement), {"comment_id": comment_id})
        conn.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW comment"))
        conn.commit()


def reset_inbox(search_uid: int) -> None:
    # this is rather blunt, as it deletes the provenance event
    # consider select the target query first, then deleting only events in the inbox

    with db.connect() as conn:
        conn.execute(
            sqlalchemy.text(
                """
                DELETE FROM event
                WHERE search_uid = :search_uid
                and type = 'create'
                """
            ),
            {"search_uid": search_uid},
        )
        conn.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW comment"))
        conn.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW rating"))

        # conn.execute(sqlalchemy.text("REFRESH MATERIALIZED VIEW criteria"))
        conn.commit()
