import os
from typing import Optional

from bigdata.auth import Auth, Proxy
from bigdata.connection import BigdataConnection, UploadsConnection
from bigdata.jwt_utils import get_token_claim
from bigdata.services.content_search import ContentSearch
from bigdata.services.knowledge_graph import KnowledgeGraph
from bigdata.services.uploads import Uploads
from bigdata.services.watchlists import Watchlists
from bigdata.settings import settings

JWT_CLAIM_ORGANIZATION_ID = "organization_id"


class Bigdata:
    """
    Represents a connection to RavenPack's Bigdata API.

    :ivar knowledge_graph: Proxy for the knowledge graph search functionality.
    :ivar search: Proxy object for the content search functionality.
    :ivar watchlists: Proxy object for the watchlist functionality.
    :ivar uploads: Proxy object for the internal content functionality.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        *,
        bigdata_api_url: Optional[str] = None,
        upload_api_url: Optional[str] = None,
        proxy: Optional[Proxy] = None,
    ):
        if password is None:
            password = os.environ.get("BIGDATA_PASSWORD")
        if username is None:
            username = os.environ.get("BIGDATA_USER")
        if username is None or password is None:
            raise ValueError("Username and password must be provided")
        auth = Auth.from_username_and_password(
            username,
            password,
            clerk_frontend_url=str(settings.CLERK_FRONTEND_URL),
            clerk_instance_type=settings.CLERK_INSTANCE_TYPE,
            proxy=proxy,
        )
        organization_id = get_token_claim(
            token=auth._token_manager.get_session_token(),
            claim=JWT_CLAIM_ORGANIZATION_ID,
        )

        if bigdata_api_url is None:
            bigdata_api_url = str(settings.BACKEND_API_URL)
        if upload_api_url is None:
            upload_api_url = str(settings.UPLOAD_API_URL)

        self._api = BigdataConnection(auth, bigdata_api_url)
        self._upload_api = UploadsConnection(
            auth, upload_api_url, organization_id=organization_id
        )

        # Start the different services
        self.knowledge_graph = KnowledgeGraph(self._api)
        self.search = ContentSearch(self._api)
        self.watchlists = Watchlists(self._api)
        self.uploads = Uploads(uploads_api=self._upload_api)
