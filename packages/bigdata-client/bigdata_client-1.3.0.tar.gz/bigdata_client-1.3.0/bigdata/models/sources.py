from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from bigdata.models.advanced_search_query import QueryComponent
from bigdata.models.advanced_search_query import Source as SourceQuery
from bigdata.models.search import Expression


class Source(BaseModel):
    """A source of news and information for RavenPack"""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
    id: str
    name: str
    volume: Optional[int] = None
    entity_type: Literal["SRCE"] = Field(default="SRCE")
    publication_type: str
    language: Optional[str] = Field(default=None)
    country: str
    source_rank: Optional[str] = Field(default=None)
    provider_id: str
    url: str

    @model_validator(mode="before")
    @classmethod
    def apply_second_alias_generator(cls, values):
        """
        Applied before validating to replace some alias in the input @values so
        we can make the model in 3 ways: snake_case/camel_case/alias. This is required because not
        all endpoints are resolving the groupN into the correct field name.
        """
        values = values.copy()  # keep original input unmutated for Unions
        autosuggest_validation_alias_map = {
            "key": "id",
            "group1": "publicationType",
            "group2": "language",
            "group3": "country",
            "group4": "sourceRank",
            "metadata1": "providerId",
            "metadata2": "url",
        }
        for key in autosuggest_validation_alias_map:
            if key in values:
                values[autosuggest_validation_alias_map[key]] = values.pop(key)
        return values

    # QueryComponent methods

    @property
    def _query_proxy(self):
        return SourceQuery(self.id)

    def to_expression(self) -> Expression:
        return self._query_proxy.to_expression()

    def __or__(self, other: QueryComponent) -> QueryComponent:
        return self._query_proxy | other

    def __and__(self, other: QueryComponent) -> QueryComponent:
        return self._query_proxy & other

    def __invert__(self) -> QueryComponent:
        return ~self._query_proxy

    def make_copy(self) -> QueryComponent:
        return self._query_proxy.make_copy()
