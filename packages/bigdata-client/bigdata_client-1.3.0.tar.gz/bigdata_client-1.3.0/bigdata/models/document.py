from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Optional

from bigdata.api.knowledge_graph import ByIdsRequest
from bigdata.connection_protocol import BigdataConnectionProtocol
from bigdata.query_type import QueryType


@dataclass
class DocumentSource:
    """The source of a document"""

    key: str
    name: str
    rank: int


class DocumentScope(Enum):
    """
    The type of the document.
    """

    NEWS = "news"
    FILINGS = "filings"
    TRANSCRIPTS = "transcripts"
    FILES = "files"


@dataclass
class DocumentSentenceEntity:
    """
    A detection instance of an entity in a sentence
    """

    key: str
    start: int
    end: int
    query_type: QueryType


@dataclass
class DocumentSentence:
    paragraph: int
    sentence: int


@dataclass
class DocumentChunk:
    """
    A chunk of text representing a contextual unit within the document
    """

    text: str
    chunk: int
    entities: list[DocumentSentenceEntity]
    sentences: list[DocumentSentence]
    relevance: float
    sentiment: float
    section_metadata: Optional[list[str]]
    speaker: Optional[str]

    # Keeps track of the connection to Bigdata
    _api: BigdataConnectionProtocol

    @cached_property
    def resolved_speaker(self):
        if not self.speaker:
            return None

        by_ids_results = self._api.by_ids(
            ByIdsRequest.model_validate(
                [{"key": self.speaker, "queryType": QueryType.ENTITY}]
            )
        )
        speaker_entity = by_ids_results.root.get(self.speaker)
        return speaker_entity.name if speaker_entity else None
