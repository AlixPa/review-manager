from pydantic import BaseModel


class GithubUrl(BaseModel):
    owner: str
    repo: str
    pull_request_number: int
