from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import aiohttp
from loguru import logger

YOUTRACK_API_TOKEN = "perm-YWRtaW4=.NDMtMA==.rVTg9Apd57WRW3UlE6luaUzC7J0yec"
YOUTRACK_HEADERS = {
    "Authorization": f"Bearer {YOUTRACK_API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


class AsyncClient:
    def __init__(self, session: aiohttp.ClientSession = None):
        self._session = session
        self._session_created = False

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._session_created = True
        return self._session

    async def get(self, url: str, **kwargs):
        async with self.session.get(url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    async def post(self, url: str, data=None, **kwargs):
        async with self.session.post(url, json=data, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    async def handler(self, method: str, url: str, **kwargs):
        handler = getattr(self, method.lower(), None)
        if handler:
            return await handler(url, **kwargs)
        raise ValueError(f"Unsupported method: {method}")

    async def close(self):
        if self._session_created and self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._session_created = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()


class IssueFields(Enum):
    ID = "id"
    SUMMARY = "summary"
    TAGS = "tags"
    PROJECT = "project"
    CREATED = "created"
    UPDATED = "updated"
    REPORTER = "reporter"
    DESCRIPTION = "description"


@dataclass
class IssueQueryParams:
    fields: List[IssueFields]
    query: Optional[str] = None
    top: Optional[int] = None
    skip: Optional[int] = None

    def to_query_string(self) -> str:
        params = []

        if self.fields:
            fields_str = ",".join([field.value for field in self.fields])
            params.append(f"fields={fields_str}")

        if self.query:
            params.append(f"query={self.query}")
        if self.top:
            params.append(f"$top={self.top}")
        if self.skip:
            params.append(f"$skip={self.skip}")

        return "&".join(params)


class YouTrackClient(AsyncClient):
    def __init__(self, session: aiohttp.ClientSession = None):
        super().__init__(session)
        self.headers = YOUTRACK_HEADERS
        self.base_url = "http://localhost:8080"

    async def get_issues(self, params: IssueQueryParams) -> dict:
        query_string = params.to_query_string()
        url = f"/api/issues?{query_string}"
        return await self.get(url)

    async def get(self, url: str, **kwargs):
        return await super().get(
            f"{self.base_url}{url}", headers=self.headers, **kwargs
        )

    async def post(self, url: str, data=None, **kwargs):
        return await super().post(
            f"{self.base_url}{url}", data=data, headers=self.headers, **kwargs
        )


async def main():
    query_params = IssueQueryParams(
        fields=[
            IssueFields.ID,
            IssueFields.SUMMARY,
            IssueFields.TAGS,
            IssueFields.PROJECT,
            IssueFields.CREATED,
            IssueFields.UPDATED,
            IssueFields.REPORTER,
            IssueFields.DESCRIPTION,
        ],
        top=1,
    )

    async with YouTrackClient() as client:
        issues = await client.get_issues(query_params)
        logger.debug(f"Получено issues: {len(issues)}")
        for issue in issues[:3]:
            for field in query_params.fields:
                logger.debug(f"{field.value}: {issue.get(field.value)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
