import re
from urllib.parse import urlparse


_SEGMENT = re.compile(r"^[A-Za-z0-9_.-]+$")


def normalize_github_repo_url(value: str) -> str:
    """Return a canonical public GitHub repository URL or raise ValueError."""
    candidate = (value or "").strip()
    parsed = urlparse(candidate)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() != "github.com":
        raise ValueError("Only public https://github.com/owner/repository URLs are allowed")
    if parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment:
        raise ValueError("Repository URL must not contain credentials, ports, queries, or fragments")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        raise ValueError("Repository URL must contain exactly an owner and repository")
    owner, repository = parts
    if repository.endswith(".git"):
        repository = repository[:-4]
    if not owner or not repository or not _SEGMENT.fullmatch(owner) or not _SEGMENT.fullmatch(repository):
        raise ValueError("Repository owner and name contain unsupported characters")
    return f"https://github.com/{owner}/{repository}"
