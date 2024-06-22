from languru.server.build import create_app
from languru.server.config import ServerBaseSettings

app = create_app(settings=ServerBaseSettings())
