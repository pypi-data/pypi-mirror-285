import logging

import jwt
from posthog import Posthog

from launchflow import __version__, lf_config

# NOTE: We do not have any retries since this is best effort usage statistics.
# If the user doesnt' have an internect connection we don't want things to fail
# or to have noisy logs.
posthog = Posthog('phc_Df3dveOW6gG1ERjM1TQ8qBp7BRwEvLCjiB2FPUJPSwj', max_retries=0)
posthog_logger = logging.getLogger("posthog")
posthog_logger.setLevel(logging.CRITICAL)
backoff_logger = logging.getLogger("backoff")
backoff_logger.setLevel(logging.CRITICAL)

def record_event(cli_action: str):
    # First we try to identify the user with their email if the user
    # is using LaunchFlow Cloud.
    # If that fails we identify them with a uuid associated with their session
    try:
        access_token = lf_config.get_access_token()
        payload = jwt.decode(access_token, options={"verify_signature": False})
        distinct_id = payload["email"]
    except Exception:
        distinct_id = lf_config.session.session_id
    posthog.capture(distinct_id, f"cli_{cli_action}", {"version": __version__})
