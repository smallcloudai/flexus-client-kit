import os
import time
import logging
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
import httpx
import jwt
import gql
from flexus_client_kit import gql_utils

logger = logging.getLogger(__name__)

EXTERNAL_GITHUB_CLIENT_ID = os.environ.get("EXTERNAL_GITHUB_CLIENT_ID")
EXTERNAL_GITHUB_APP_PRIVATE_KEY = os.environ.get("EXTERNAL_GITHUB_APP_PRIVATE_KEY")
if EXTERNAL_GITHUB_APP_PRIVATE_KEY is not None:
    with open(EXTERNAL_GITHUB_APP_PRIVATE_KEY, 'r') as f:
        EXTERNAL_GITHUB_APP_PRIVATE_KEY = f.read()


@dataclass
class GhRepoToken:
    token: str
    expires_at: float


def _generate_github_app_jwt() -> str:
    if not EXTERNAL_GITHUB_CLIENT_ID or not EXTERNAL_GITHUB_APP_PRIVATE_KEY:
        raise RuntimeError("GitHub App credentials not configured: missing EXTERNAL_GITHUB_CLIENT_ID or EXTERNAL_GITHUB_APP_PRIVATE_KEY")
    now = int(time.time())
    payload = {'iat': now - 60, 'exp': now + 600, 'iss': EXTERNAL_GITHUB_CLIENT_ID}
    private_key = EXTERNAL_GITHUB_APP_PRIVATE_KEY.replace('\\n', '\n')
    return jwt.encode(payload, private_key, algorithm='RS256')


def extract_repo_path_from_url(repo_url: str) -> Optional[str]:
    if repo_url.startswith("https://"):
        if "@github.com/" in repo_url:
            repo_path = repo_url.split("@github.com/")[1].split("#")[0].replace(".git", "")
        else:
            repo_path = repo_url.replace("https://github.com/", "").split("#")[0].replace(".git", "")
    elif repo_url.startswith("git@github.com:"):
        repo_path = repo_url.replace("git@github.com:", "").replace(".git", "")
    else:
        return None
    if "/" not in repo_path:
        return None
    return repo_path

def extract_repo_name_from_url(repo_url: str) -> Optional[str]:
    repo_path = extract_repo_path_from_url(repo_url)
    return repo_path.split('/', 1)[1] if repo_path else None

async def _check_installation_repo_access(installation_id: str, target_repo_path: str) -> bool:
    if not (result := await exchange_installation_id_to_token(installation_id)):
        return False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.github.com/installation/repositories",
                headers={
                    "Authorization": f"Bearer {result.token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "Flexus-GitHub-Integration"
                },
                timeout=5
            )
            if resp.status_code == 200:
                repos_data = resp.json()
                for repo in repos_data.get("repositories", []):
                    repo_full_name = repo.get("full_name")
                    if repo_full_name and repo_full_name.lower() == target_repo_path.lower():
                        return True
            else:
                logger.warning(f"Failed to fetch repos for installation {installation_id}: {resp.status_code}")
    except Exception as e:
        logger.exception(f"Error checking repo access for installation {installation_id}: {e}")
    return False


async def pick_working_installation_id(installation_ids: list, repo_url: str) -> Optional[str]:
    target_repo_path = extract_repo_path_from_url(repo_url)
    if not target_repo_path:
        logger.error(f"Could not extract repo path from URL: {repo_url}")
        return None
    for inst in installation_ids:
        installation_id = inst.get("id")
        if not installation_id:
            raise RuntimeError(f"Critical error: installation_id is missing from GitHub installation data: {inst}")
        if await _check_installation_repo_access(installation_id, target_repo_path):
            return installation_id
    logger.error(f"No installation found with access to repo {target_repo_path}")
    return None


async def exchange_installation_id_to_token(installation_id: str, repo_name: Optional[str] = None) -> Optional[GhRepoToken]:
    app_jwt = _generate_github_app_jwt()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {app_jwt}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=5,
                json={"repositories": [repo_name]} if repo_name else None
            )
            if resp.status_code == 201:
                data = resp.json()
                if not (token := data.get("token")):
                    return None
                expires_at_ts = datetime.fromisoformat(data["expires_at"].replace('Z', '+00:00')).timestamp()
                return GhRepoToken(token=token, expires_at=expires_at_ts) # expires at 1 hour
            else:
                logger.error(f"Failed to get installation token: {resp.status_code} {resp.text}")
                return None
    except Exception as e:
        logger.exception(f"Error getting GitHub app installation token: {e}")
        return None


async def get_token_from_github_auth_cred(auth_json: dict, repo_name: str) -> Optional[GhRepoToken]:
    if not (inst_id := await pick_working_installation_id(auth_json["installation_ids"], f"https://github.com/{repo_name}")):
        return None
    return await exchange_installation_id_to_token(inst_id)


async def get_gh_repo_token_from_external_auth(fclient, auth_id: str, repo_uri: str) -> Optional[GhRepoToken]:
    http = await fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(f"""
                query GetGhRepoTokenFromExternalAuth($auth_id: String!, $repo_uri: String!) {{
                    get_gh_repo_token_from_external_auth(auth_id: $auth_id, repo_uri: $repo_uri) {{
                        {gql_utils.gql_fields(GhRepoToken)}
                    }}
                }}"""),
            variable_values={"auth_id": auth_id, "repo_uri": repo_uri},
        )
    if result := r.get("get_gh_repo_token_from_external_auth"):
        return gql_utils.dataclass_from_dict(result, GhRepoToken)
    return None


_token_cache: dict[tuple[str, str], GhRepoToken] = {} # (fgroup_id, repo_url)

async def get_github_token_with_cache(fclient, fgroup_id: str, repo_url: str) -> Optional[GhRepoToken]:
    import flexus_client_kit.ckit_devenv as ckit_devenv
    cache_key = (fgroup_id, repo_url)
    if cache_key in _token_cache:
        gh_token = _token_cache[cache_key]
        if gh_token.expires_at > time.time() + 60:
            return gh_token
    if not (target_repo := extract_repo_path_from_url(repo_url)):
        return None
    for devenv in await ckit_devenv.dev_environments_list_in_subgroups(fclient, fgroup_id):
        if extract_repo_path_from_url(devenv.devenv_repo_uri) == target_repo:
            if not devenv.devenv_auth_id:
                return None
            if not (gh_token := await get_gh_repo_token_from_external_auth(fclient, devenv.devenv_auth_id, repo_url)):
                return None
            _token_cache[cache_key] = gh_token
            return gh_token
    return None
