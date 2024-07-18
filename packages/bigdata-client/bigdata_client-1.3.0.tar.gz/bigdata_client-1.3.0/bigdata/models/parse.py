from contextlib import suppress
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag, ValidationError

from bigdata.models.entities import (
    Company,
    Concept,
    Facility,
    Landmark,
    MacroEntity,
    Organization,
    OrganizationType,
    Person,
    Place,
    Product,
    ProductType,
)
from bigdata.models.languages import Language
from bigdata.models.sources import Source
from bigdata.models.topics import Topic
from bigdata.models.watchlists import Watchlist

MACRO_PREFIX = "macro_"


def get_discriminator_knowledge_graph_value(v: Any) -> Optional[str]:
    if isinstance(v, dict):
        return v.get(
            "entityType", v.get("entity_type", v.get("queryType", v.get("query_type")))
        )
    return getattr(v, "entity_type", getattr(v, "query_type", None))


class AutosuggestedSavedSearch(BaseModel):
    """Class used only to parse the output from the Autosuggestion"""

    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(validation_alias="key", default=None)
    name: Optional[str] = Field(default=None)
    query_type: Literal["savedSearch"] = Field(
        default="savedSearch", validation_alias="queryType"
    )


EntityTypes = Union[
    Company,
    Facility,
    Landmark,
    Organization,
    OrganizationType,
    Person,
    Place,
    Product,
    ProductType,
    Concept,
]

KnowledgeGraphTypes = Union[
    MacroEntity,
    Topic,
    Source,
    Language,
    Watchlist,
    AutosuggestedSavedSearch,
    EntityTypes,
]


class KnowledgeGraphAnnotated(BaseModel):
    root: Annotated[
        Union[
            Annotated[Company, Tag(Company.model_fields["entity_type"].default)],
            Annotated[Facility, Tag(Facility.model_fields["entity_type"].default)],
            Annotated[Landmark, Tag(Landmark.model_fields["entity_type"].default)],
            Annotated[
                Organization, Tag(Organization.model_fields["entity_type"].default)
            ],
            Annotated[
                OrganizationType,
                Tag(OrganizationType.model_fields["entity_type"].default),
            ],
            Annotated[Person, Tag(Person.model_fields["entity_type"].default)],
            Annotated[Place, Tag(Place.model_fields["entity_type"].default)],
            Annotated[Product, Tag(Product.model_fields["entity_type"].default)],
            Annotated[
                ProductType, Tag(ProductType.model_fields["entity_type"].default)
            ],
            Annotated[Source, Tag(Source.model_fields["entity_type"].default)],
            Annotated[Topic, Tag(Topic.model_fields["entity_type"].default)],
            Annotated[Language, Tag(Language.model_fields["query_type"].default)],
            Annotated[
                AutosuggestedSavedSearch,
                Tag(AutosuggestedSavedSearch.model_fields["query_type"].default),
            ],
            Annotated[Watchlist, Tag(Watchlist.model_fields["query_type"].default)],
        ],
        Discriminator(get_discriminator_knowledge_graph_value),
    ]


def parse_knowledge_graph_object(domain_obj: dict) -> KnowledgeGraphTypes:
    try:
        return KnowledgeGraphAnnotated.model_validate({"root": domain_obj}).root
    except ValidationError:
        # Macro keys are not part of KnowledGraphAnnotated, and we don't want them there to be visible to the user
        with suppress(ValidationError):
            if get_discriminator_knowledge_graph_value(domain_obj).startswith(
                MACRO_PREFIX
            ):
                return MacroEntity.model_validate(domain_obj)

        return Concept.model_validate(domain_obj)


# TODO: could somehow unify domain_types and Annotated[Union] in a single list?
# we have mypy to help. `poetry run task pre-commit`
