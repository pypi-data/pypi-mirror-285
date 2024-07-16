import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlalchemy
from gandai.db import connect_with_connector

db = connect_with_connector()


def analyst_event_counts_by_type() -> pd.DataFrame:
    stmt = """
    SELECT
        s.label,
        e.search_uid,
        e.type,
        a.name as analyst,
        SUM(CASE WHEN e.created >= EXTRACT(EPOCH FROM NOW()) - 1 * 86400 THEN 1 ELSE 0 END) AS last_1_days,
        SUM(CASE WHEN e.created >= EXTRACT(EPOCH FROM NOW()) - 7 * 86400 THEN 1 ELSE 0 END) AS last_7_days,
        SUM(CASE WHEN e.created >= EXTRACT(EPOCH FROM NOW()) - 14 * 86400 THEN 1 ELSE 0 END) AS last_14_days,
        SUM(CASE WHEN e.created >= EXTRACT(EPOCH FROM NOW()) - 30 * 86400 THEN 1 ELSE 0 END) AS last_30_days,
        SUM(CASE WHEN e.created >= EXTRACT(EPOCH FROM NOW()) - 90 * 86400 THEN 1 ELSE 0 END) AS last_90_days
    FROM
        event e
    LEFT JOIN
        actor a ON a.key = e.actor_key
    LEFT JOIN
        search s ON s.uid = e.search_uid
    WHERE
        e.type in ('validate', 'reject','advance','send','buyer')
    GROUP BY
        s.label, e.search_uid, analyst, e.type
    ORDER BY
        last_30_days DESC
    ;
    """
    with db.connect() as conn:
        result = conn.execute(sqlalchemy.text(stmt))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        df = df[df["last_90_days"] > 0]
    return df


def search_target_count_by_stage() -> pd.DataFrame:
    stmt = """
    WITH RankedEvents AS (
        SELECT
            e.search_uid,
            s.label,
            e.domain,
            e.type AS stage,
            e.created,
            ROW_NUMBER() OVER(PARTITION BY e.search_uid, e.domain ORDER BY e.created DESC) AS rn
        FROM
            event e
        JOIN
            search s ON e.search_uid = s.uid
        JOIN
            company c ON e.domain = c.domain
        WHERE 
            e.type NOT IN ('comment','rating','criteria','update','review','mute','enrich')
    )
    SELECT
        re.search_uid,
        re.label,
        re.stage,
        COUNT(re.stage) AS stage_count
    FROM
        RankedEvents re
    WHERE
        re.rn = 1
    GROUP BY
        re.search_uid,
        re.label,
        re.stage
    ORDER BY
        re.search_uid,
        re.stage;
        """
    with db.connect() as conn:
        result = conn.execute(sqlalchemy.text(stmt))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    STAGE_MAP = {
        "land": "Landing",
        "create": "Inbox",
        "similar": "Similar",
        "advance": "Review",
        "hold": "Hold",
        "validate": "Validated",
        "send": "Client Inbox",
        "client_approve": "Client Approved",
        "sync": "Synced",
        "reject": "Reject",
        "conflict": "Conflict",
        "client_conflict": "Client Conflict",
        "client_reject": "Client Reject",
        "buyer": "Buyer",
    }

    stage_index_map = {stage: index for index, stage in enumerate(STAGE_MAP.keys())}

    df["stage_index"] = df["stage"].map(
        stage_index_map
    )  # maps to the index of the stage_map keys
    df["stage"] = df["stage"].map(STAGE_MAP)
    df = df.sort_values(by="stage_index").reset_index(drop=True)
    pivot_table = df.pivot_table(
        index="label", columns="stage", values="stage_count", fill_value=0
    )
    ordered_columns = [
        STAGE_MAP[stage]
        for stage in STAGE_MAP.keys()
        if STAGE_MAP[stage] in pivot_table.columns
    ]
    pivot_table = pivot_table[ordered_columns]
    return pivot_table.reset_index()


def weekly_cumulative_events(event_type="validate") -> pd.DataFrame:
    statement = """
    SELECT 
        e.*, 
        to_timestamp(e.created) as dt,  
        EXTRACT(DOW FROM TO_TIMESTAMP(e.created)) as dow,
        a.name, 
        s.label,
        COUNT(*) OVER (PARTITION BY e.actor_key ORDER BY date_trunc('minute', to_timestamp(e.created))) as cumulative_events
    FROM event e
    JOIN actor a on e.actor_key = a.key
    JOIN search s on e.search_uid = s.uid
    WHERE 
        to_timestamp(e.created) >= date_trunc('week', current_date)
        AND a.key not in ('grata','dealcloud')
        AND e.type = :event_type
    ORDER BY e.actor_key, date_trunc('minute', to_timestamp(e.created))
    """
    with db.connect() as conn:
        conn.execute(sqlalchemy.text("SET TIME ZONE 'America/Chicago'"))
        result = conn.execute(sqlalchemy.text(statement), {"event_type": event_type})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


def draw_weekly_cumulative(event_type: str) -> px.line:
    df = weekly_cumulative_events(event_type=event_type)
    return px.line(
        df,
        x="dt",
        y="cumulative_events",
        color="name",
        title=f"{event_type}",
    )


def draw_validation_per_day() -> pd.DataFrame:
    statement = """
    SELECT e.*, to_timestamp(e.created) as dt, a.name, s.label
    FROM event e
    JOIN actor a on e.actor_key = a.key
    JOIN search s on e.search_uid = s.uid
    WHERE to_timestamp(e.created) > now() - interval '14 day'
    and a.key not in ('grata','dealcloud')
    and e.type in ('validate')
    ORDER BY created
    """
    with db.connect() as conn:
        conn.execute(sqlalchemy.text("SET TIME ZONE 'America/Chicago'"))
        result = conn.execute(sqlalchemy.text(statement))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    df["date"] = df["dt"].dt.strftime("%Y-%m-%d")

    validations = (
        df.groupby(["name", "date", "label"])
        .size()
        .reset_index(name="count")
        .sort_values(by=["date"])
        .reset_index(drop=True)
    )

    fig = px.bar(
        validations,
        x="date",
        y="count",
        color="name",
        barmode="group",
        title="Validations per day by search by researcher | Trailing 7 days",
        hover_data=["label"],
    )
    return fig


def draw_leaderboard(window: str = "month", title: str = "") -> go.Figure:
    assert window in ["month", "week", "last_week"], "Invalid window"

    if window == "last_week":
        statement = f"""
            SELECT 
                a.name,
                e.type,
                count(DISTINCT e.domain) as count
            FROM event e
            JOIN actor a on e.actor_key = a.key
            WHERE 
                to_timestamp(e.created) >= date_trunc('week', current_date) - interval '1 week'
                AND to_timestamp(e.created) < date_trunc('week', current_date)
                AND e.type in ('validate','reject','send','client_approve','client_conflict','client_reject')
                AND a.type = 'research'
            GROUP BY a.name, e.type
            """
    else:
        statement = f"""
            SELECT 
                a.name,
                e.type,
                count(DISTINCT e.domain) as count
            FROM event e
            JOIN actor a on e.actor_key = a.key
            WHERE 
                to_timestamp(e.created) >= date_trunc('{window}', current_date)
                AND e.type in ('validate','reject','send','client_approve','client_conflict','client_reject')
                AND a.type = 'research'
            GROUP BY a.name, e.type
            """
    with db.connect() as conn:
        conn.execute(sqlalchemy.text("SET TIME ZONE 'America/Chicago'"))
        result = conn.execute(sqlalchemy.text(statement))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    pivot_df = (
        df.pivot(index="name", columns="type", values="count").fillna(0).reset_index()
    )
    cols = [
        "name",
        "validate",
        "reject",
        "send",
        "client_approve",
        "client_conflict",
        "client_reject",
    ]
    for col in cols:
        if col not in pivot_df.columns:
            pivot_df[col] = 0
    pivot_df = pivot_df[cols]
    pivot_df = pivot_df.sort_values(by="validate", ascending=False).reset_index(
        drop=True
    )
    pivot_df["numerator"] = pivot_df["client_approve"] + pivot_df["client_conflict"]
    pivot_df["denominator"] = (
        pivot_df["client_approve"]
        + pivot_df["client_conflict"]
        + pivot_df["client_reject"]
    )
    totals = pivot_df.sum(numeric_only=True)
    totals["name"] = "Total"  # Add a total label in the 'name' column
    totals_df = pd.DataFrame([totals], columns=pivot_df.columns)
    display_df = pd.concat([pivot_df, totals_df], ignore_index=True)
    display_df["approval_rating"] = round(
        display_df["numerator"] / display_df["denominator"], 2
    ).fillna(0)
    display_df

    ## render table
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=list(display_df.columns), align="left"),
                cells=dict(
                    values=[
                        display_df[col] for col in display_df.columns
                    ],  # Use display_df to include the totals
                    align="left",
                ),
            )
        ]
    )

    fig.update_layout(title_text=title, title_font=dict(size=24))
    return fig
