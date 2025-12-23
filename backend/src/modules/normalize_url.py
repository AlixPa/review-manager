from src.models.github_url import GithubUrl


def normalize_github_url(url: str) -> GithubUrl | None:
    url = url.removeprefix("http://").removeprefix("https://")
    parts = url.split("/")
    if parts[0] != "github.com" or parts[3] != "pull":
        return None
    try:
        return GithubUrl(
            owner=parts[1], repo=parts[2], pull_request_number=int(parts[4])
        )
    except Exception:
        return None
