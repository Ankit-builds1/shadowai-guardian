from pydantic import BaseModel, Field


class PromptScanRequest(BaseModel):
    text: str = Field(min_length=1)
    target_tool: str | None = None
    source_type: str = "prompt"


class RewriteRequest(BaseModel):
    text: str = Field(min_length=1)
    entities: list[dict] | None = None


class RepoScanRequest(BaseModel):
    repo_url: str = Field(min_length=8)


class ProxyInspectRequest(BaseModel):
    text: str = Field(min_length=1)
    policy_mode: str = "developer"
    page_url: str | None = None
