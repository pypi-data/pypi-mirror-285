import secrets
from src.providers import BaseProvider


class OAuthClient:

    def __init__(self, provider: BaseProvider):
        self.provider = provider
        self.state = None

    def prepare_auth_url(self):
        self.state = secrets.token_urlsafe(32)
