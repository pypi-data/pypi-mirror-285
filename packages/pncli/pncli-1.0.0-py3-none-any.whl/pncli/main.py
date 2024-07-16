import sys
from base64 import urlsafe_b64decode, urlsafe_b64encode
from uuid import UUID
from typing_extensions import Annotated

import typer

app = typer.Typer()


def try_uuid(maybe_uuid: str) -> bool:
    try:
        uuid_id = UUID(maybe_uuid)
        print(urlsafe_b64encode(uuid_id.bytes).decode("UTF-8").strip("="))
        return True
    except:
        return False


def try_base64(maybe_base64: str) -> bool:
    try:
        print(UUID(bytes=urlsafe_b64decode(maybe_base64 + "==")))
        return True
    except:
        return False


@app.command(help="귀여운 강아지에게 말을 시킵니다.")
def dogsay(msg: str):
    print(f"""
     |\_/|                  
     | @ @   {msg} 
     |   <>              _  
     |  _/\------____ ((| |))
     |               `--' |   
 ____|_       ___|   |___.' 
/_/_____/____/_______|
    """)


@app.command(help="UUID를 ClientID로, ClientID를 UUID로 변환합니다.")
def cvid(maybe_id: str):
    if try_uuid(maybe_id):
        return
    if try_base64(maybe_id):
        return

    print("Invalid input: '" + maybe_id +
          "' is Not a valid UUID or URL-safe Base64 (use '-' instead of '+' and '_' instead of '/')",
          file=sys.stderr)
