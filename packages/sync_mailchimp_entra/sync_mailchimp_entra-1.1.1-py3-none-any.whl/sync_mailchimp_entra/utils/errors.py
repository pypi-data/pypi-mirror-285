import json


class Error:
    """Custom error to parse JSON one sent by MailChimp."""

    title: str
    status: int
    detail: str
    instance: str
    type: str
    errors: str

    def __init__(
        self,
        title: str,
        status: int,
        detail: str,
        instance: str,
        type: str = "",
        errors: str = "",
    ):
        self.title = title
        self.status = status
        self.detail = detail
        self.instance = instance
        self.type = type
        self.errors = errors



def deserial_error(error_json):
    return Error(**json.loads(error_json))
