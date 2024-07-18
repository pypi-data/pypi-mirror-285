import os
import time
from datetime import datetime
from typing import List, Optional, Union

import requests

from bigdata.api.uploads import ExtractorTypes, FileStatus, PostFileRequest
from bigdata.connection import BigdataConnection, UploadsConnection, upload_file
from bigdata.daterange import AbsoluteDateRange
from bigdata.models.uploads import File
from bigdata.pdf_utils import is_pdf_file


class Uploads:
    """For managing internal uploads. Searching will be done through content"""

    def __init__(self, uploads_api: UploadsConnection):
        self._uploads_api = uploads_api

    def get(self, id_, /) -> File:
        """Retrieve a file by its id."""
        response = None
        while response is None:
            try:
                response = self._uploads_api.get_file(id_)
            except requests.exceptions.HTTPError as e:
                # While unavailable, keep trying
                if e.response.status_code == 425:
                    time.sleep(1)
                    continue
                raise e
        return File(
            _uploads_api=self._uploads_api,
            id=response.id,
            name=response.name,
            status=response.status,
            uploaded_at=response.uploaded_at,
            raw_size=response.raw_size,
            folder_id=response.folder_id,
            tags=response.tags,
            company_shared_permission=response.company_shared_permission,
        )

    def _list(
        self,
        start_date: Optional[Union[datetime, str]] = None,
        end_date: Optional[Union[datetime, str]] = None,
        tags: Optional[list[str]] = None,
        status: Optional[FileStatus] = None,
        file_name: Optional[str] = None,
        folder_id: Optional[str] = None,
        page_size: Optional[int] = None,
        shared: Optional[bool] = None,
    ):
        date_range = (
            AbsoluteDateRange(start_date, end_date) if start_date or end_date else None
        )
        response = self._uploads_api.list_files(
            date_range=date_range,
            tags=tags,
            status=status,
            file_name=file_name,
            folder_id=folder_id,
            page_size=page_size,
            shared=shared,
        )
        docs = []
        for upload in response.results:
            doc = File(
                _uploads_api=self._uploads_api,
                id=upload.id,
                name=upload.name,
                status=upload.status,
                uploaded_at=upload.uploaded_at,
                raw_size=upload.raw_size,
                folder_id=upload.folder_id,
                tags=upload.tags,
                company_shared_permission=upload.company_shared_permission,
            )
            docs.append(doc)

        return docs

    def list(
        self,
        start_date: Optional[Union[datetime, str]] = None,
        end_date: Optional[Union[datetime, str]] = None,
        tags: Optional[list[str]] = None,
        status: Optional[FileStatus] = None,
        file_name: Optional[str] = None,
        folder_id: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> list[File]:
        """Retrieve all documents for the current user."""
        return self._list(
            start_date=start_date,
            end_date=end_date,
            tags=tags,
            status=status,
            file_name=file_name,
            folder_id=folder_id,
            page_size=page_size,
        )

    def list_shared(
        self,
        start_date: Optional[Union[datetime, str]] = None,
        end_date: Optional[Union[datetime, str]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[FileStatus] = None,
        file_name: Optional[str] = None,
        folder_id: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> List[File]:
        """Retrieve all documents shared with the user that do not belong to them."""

        return self._list(
            start_date=start_date,
            end_date=end_date,
            tags=tags,
            status=status,
            file_name=file_name,
            folder_id=folder_id,
            page_size=page_size,
            shared=True,
        )

    def upload_from_disk(
        self,
        path: str,
        /,
        provider_document_id: Optional[str] = None,
        provider_date_utc: Optional[Union[str, datetime]] = None,
    ) -> File:
        """Uploads a file to the bigdata platform."""
        filename = os.path.basename(path)

        properties = {}
        if provider_document_id is not None:
            properties["provider_document_id"] = provider_document_id
        if provider_date_utc is not None:
            if isinstance(provider_date_utc, datetime):
                provider_date_utc = provider_date_utc.strftime("%Y-%m-%d %H:%M:%S")
            properties["provider_date_utc"] = provider_date_utc
        if is_pdf_file(path):
            properties["extractor"] = ExtractorTypes.PDF_EXTRACTOR_1_0
        properties = properties or None

        # Pre-upload
        post_file_request = PostFileRequest(
            filename=filename,
            folder_id=None,
            source_url=None,
            upload_mode=None,
            properties=properties,
        )
        post_file_request = self._uploads_api.post_file(post_file_request)

        with open(path, "rb") as file:
            upload_file(post_file_request.location, file)
        return self.get(post_file_request.file_id)

    def delete(self, id_, /):
        """Delete a file by its id."""
        self._uploads_api.delete_file(id_)

    def share_with_company(self, id_: str):
        """Share with own company"""
        self._uploads_api.share_file_with_company(file_id=id_)

    def unshare_with_company(self, id_: str):
        """Stop sharing with own company"""
        self._uploads_api.unshare_file_with_company(file_id=id_)
