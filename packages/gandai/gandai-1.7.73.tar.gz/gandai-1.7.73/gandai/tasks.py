import json
import os
from threading import Thread

import gandai as ts
from gandai import main
from google.cloud import tasks_v2


def trigger_process_event(event_id: int) -> None:
    if os.getenv("TASKS") == "local":
        # main.process_event(event_id=event_id)
        Thread(target=main.process_event, kwargs={"event_id": event_id}).start()
    else:
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(
            project=os.getenv("GOOGLE_CLOUD_PROJECT", "targetselect-staging"),
            location="us-central1",
            queue="event",
        )
        task = {
            "app_engine_http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "app_engine_routing": {"service": "api"},
                "relative_uri": "/process_event",
                "headers": {"Content-type": "application/json"},
                "body": json.dumps({"event_id": event_id}).encode(),
            }
        }
        print(task)
        response = client.create_task(parent=parent, task=task)
        return response
