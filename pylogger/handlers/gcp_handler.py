from typing import Union

import google.cloud.logging
from google.auth.exceptions import DefaultCredentialsError
from google.cloud.logging_v2.handlers import CloudLoggingHandler


def get_gcp_handler(handler_name: str) -> Union[dict, None]:
    """Returns a dict containing a GCP logging sink and its format.

    Returns:
        list: A dict containing the 'sink' and 'format' keys.
    """
    try:
        client = google.cloud.logging.Client()
        gcp_handler = CloudLoggingHandler(client, name=handler_name)
        return {"sink": gcp_handler, "format": "<lvl>{message}</lvl>"}
    except DefaultCredentialsError:
        print("Unable to create GCP logging handler.")
        return None
