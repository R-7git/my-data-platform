import requests
from airflow.models import Variable

def notify_slack_on_failure(context):
    """
    Sends a red alert to Slack when a DAG fails.
    """
    # 1. Get the Webhook URL (We will set this Variable in Airflow UI next)
    # or hardcode it here for testing: "https://hooks.slack.com/..."
    webhook_url = Variable.get("slack_webhook_secret", default_var=None)

    if not webhook_url:
        print("No Slack Webhook found. Skipping alert.")
        return

    # 2. Extract useful info from the Airflow 'context'
    task_instance = context.get('task_instance')
    task_name = task_instance.task_id
    dag_name = task_instance.dag_id
    log_url = task_instance.log_url
    exception = context.get('exception')

    # 3. Construct the payload
    payload = {
        "text": f":red_circle: **Pipeline Failure Detected**",
        "attachments": [
            {
                "color": "#FF0000",
                "fields": [
                    {"title": "DAG", "value": dag_name, "short": True},
                    {"title": "Task", "value": task_name, "short": True},
                    {"title": "Error", "value": str(exception), "short": False},
                ],
                "actions": [
                    {
                        "type": "button",
                        "text": "View Logs",
                        "url": log_url
                    }
                ]
            }
        ]
    }

    # 4. Send Request
    requests.post(webhook_url, json=payload)
