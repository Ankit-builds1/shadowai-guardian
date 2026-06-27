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


class ToolRiskRequest(BaseModel):
    domain: str = Field(min_length=3)


class AgentRequest(BaseModel):
    text: str = Field(min_length=1)
