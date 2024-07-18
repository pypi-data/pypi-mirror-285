from typing import Optional

from bigdata.api.knowledge_graph import (
    AutosuggestRequests,
    AutosuggestResponse,
    ByIdsRequest,
)
from bigdata.connection_protocol import BigdataConnectionProtocol
from bigdata.models.entities import (
    Company,
    Concept,
    MacroEntity,
    Organization,
    Person,
    Place,
    Product,
)
from bigdata.models.languages import Language
from bigdata.models.parse import (
    AutosuggestedSavedSearch,
    EntityTypes,
    KnowledgeGraphTypes,
)
from bigdata.models.sources import Source
from bigdata.models.topics import Topic
from bigdata.query_type import QueryType


class KnowledgeGraph:
    """For finding entities, sources and topics"""

    def __init__(self, api_connection: BigdataConnectionProtocol):
        self._api = api_connection

    def _autosuggest(self, values: list[str], limit: int) -> AutosuggestResponse:
        return self._api.autosuggest(
            AutosuggestRequests(root=values),
            limit=limit,
        )

    def autosuggest(
        self, values: list[str], /, limit: int = 20
    ) -> dict[str, list[KnowledgeGraphTypes]]:
        """
        Searches for entities, sources, topics, searches and watchlists

        Args:
            values: Searched items
            limit: Upper limit for each result

        Returns:
            Dictionary with the searched terms as keys each with a list of results.
        """

        api_response = self._autosuggest(values, limit)

        # Exclude macros and saved searches from response
        only_supported_entities = self._exclude_models(
            api_response, models=(MacroEntity, AutosuggestedSavedSearch)
        )

        return dict(only_supported_entities.root.items())

    def find_concepts(self, values: list[str], /, limit=20) -> dict[str, list[Concept]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a concept.

        Args:
            values: Searched items
            limit: Upper limit for each result before applying the filter

        Returns:
            Dictionary with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_models=(Concept,), values=values, limit=limit
        )

    def find_companies(
        self, values: list[str], /, limit=20
    ) -> dict[str, list[Company]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a company.

        Args:
            values: Searched items
            limit: Upper limit for each result before applying the filter

        Returns:
            Dictionary with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_models=(Company,), values=values, limit=limit
        )

    def find_people(self, values: list[str], /, limit=20):
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a person.

        Args:
            values: Searched items
            limit: Upper limit for each result before applying the filter

        Returns:
            Dictionary with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_models=(Person,), values=values, limit=limit
        )

    def find_places(self, values: list[str], /, limit=20) -> dict[str, list[Place]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a place.

        Args:
            values: Searched items
            limit: Upper limit for each result before applying the filter

        Returns:
            Dictionary with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_models=(Place,), values=values, limit=limit
        )

    def find_organizations(
        self, values: list[str], /, limit=20
    ) -> dict[str, list[Organization]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not an organization.

        Args:
            values: Searched items
            limit: Upper limit for each result before applying the filter

        Returns:
            Dictionary with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_models=(Organization,), values=values, limit=limit
        )

    def find_products(self, values: list[str], /, limit=20) -> dict[str, list[Product]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a product.

        Args:
            values: Searched items
            limit: Upper limit for each result before applying the filter

        Returns:
            Dictionary with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_models=(Product,), values=values, limit=limit
        )

    def find_sources(self, values: list[str], /, limit=20) -> dict[str, list[Source]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a source.

        Args:
            values: Searched items
            limit: Upper limit for each result before applying the filter

        Returns:
            Dictionary with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_models=(Source,), values=values, limit=limit
        )

    def find_topics(self, values: list[str], /, limit=20) -> dict[str, list[Topic]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a topic.

        Args:
            values: Searched items
            limit: Upper limit for each result before applying the filter

        Returns:
            Dictionary with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_models=(Topic,), values=values, limit=limit
        )

    def _autosuggest_and_filter(
        self, allowed_models: tuple, values: list[str], limit: int
    ) -> dict:
        api_response = self._autosuggest(values, limit)
        results = self._include_only_models(api_response, models=allowed_models)

        return dict(results.root.items())

    @staticmethod
    def _exclude_models(
        api_response: AutosuggestResponse, models: tuple
    ) -> AutosuggestResponse:
        """It will exclude the models from the response."""
        filtered_response = {}
        for key, key_results in api_response.root.items():
            filtered_response[key] = list(
                filter(
                    lambda result: not isinstance(result, models),
                    key_results,
                )
            )
        return AutosuggestResponse(root=filtered_response)

    @staticmethod
    def _include_only_models(
        api_response: AutosuggestResponse, models: tuple
    ) -> AutosuggestResponse:
        """It will include the models specified only"""
        filtered_response = {}
        for key, key_results in api_response.root.items():
            filtered_response[key] = list(
                filter(
                    lambda result: isinstance(result, models),
                    key_results,
                )
            )
        return AutosuggestResponse(root=filtered_response)

    def get_entities(self, ids: list[str], /) -> list[Optional[EntityTypes]]:
        """Retrieve a list of entities by their ids."""
        return self._get_by_ids(ids, QueryType.ENTITY)

    def get_sources(self, ids: list[str], /) -> list[Optional[Source]]:
        """Retrieve a list of sources by its ids."""
        return self._get_by_ids(ids, QueryType.SOURCE)

    def get_topics(self, ids: list[str], /) -> list[Optional[Topic]]:
        """Retrieve a list of topics by its ids."""
        return self._get_by_ids(ids, QueryType.TOPIC)

    def get_languages(self, ids: list[str], /) -> list[Optional[Language]]:
        """Retrieve a list of languages by its ids."""
        return self._get_by_ids(ids, QueryType.LANGUAGE)

    def _get_by_ids(self, ids: list[str], query_type: QueryType) -> list:
        api_response = self._api.by_ids(
            ByIdsRequest.model_validate(
                [{"key": id_, "queryType": query_type} for id_ in ids]
            )
        )
        return [api_response.root.get(id_) for id_ in ids]
