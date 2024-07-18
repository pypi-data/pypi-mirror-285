from pydantic import BaseModel, Field, SecretStr


class ConsulConfiguration(BaseModel):
    host: str = Field(default='localhost', description='The consul host')
    port: int = Field(default=8500, description='The consul port')
    token: SecretStr | None = Field(default=None, description='The consul token')
    scheme: str = Field(default='http', description='The consul scheme [http, https]')
