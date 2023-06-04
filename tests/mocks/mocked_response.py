class MockedResponse:
    def __init__(self, status_code: int, content: bytes, headers: dict) -> None:
        self.status_code = status_code
        self.content = content
        self.headers = headers
