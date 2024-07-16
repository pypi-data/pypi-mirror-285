from base64 import urlsafe_b64decode, urlsafe_b64encode
from uuid import UUID

import typer

app = typer.Typer()


@app.command()
def encode(uuid_id: UUID):
    print(urlsafe_b64encode(uuid_id.bytes).decode("UTF-8").strip("="))


@app.command()
def decode(base64_encoded_uuid: str):
    print(UUID(bytes=urlsafe_b64decode(base64_encoded_uuid + "==")))
