from pydantic import BaseModel, Field, HttpUrl
from pytimeparse import parse


class ApiConfiguration(BaseModel):
    base_url: HttpUrl = Field(..., description='The Base URL to use in the API calls.')
    default_headers: dict[str, str] = Field(default={}, description='The default Headers to append to all requests.')
    timeout: str = Field(
        default='10s',
        description='The timeout in annotation to wait for the request to complete',
    )

    @property
    def timeout_in_ms(self) -> int:
        return self.timeout_in_seconds * 1000

    @property
    def timeout_in_seconds(self) -> int:
        return parse(self.timeout)
