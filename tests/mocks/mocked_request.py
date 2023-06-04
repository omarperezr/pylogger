class MockedRequest:
    def __init__(
        self,
        url: str,
        method: str,
        body: bytes,
        content_type: str,
        headers: dict = {},
        authenticated_user=None,
    ) -> None:
        self.url = url
        self.method = method
        self.body = body
        self._logging_body = body
        self.content_type = content_type
        self.META = {}
        self.headers = headers

        if "Authorization" in headers:
            self.META["HTTP_AUTHORIZATION"] = headers["Authorization"]
        if authenticated_user:
            self.authenticated_user = authenticated_user

    def get_full_url(self) -> str:
        return self.url
