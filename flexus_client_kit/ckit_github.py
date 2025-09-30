import os
import time
import logging
from typing import Optional
import httpx
import jwt

logger = logging.getLogger(__name__)

EXTERNAL_GITHUB_CLIENT_ID = os.environ.get("EXTERNAL_GITHUB_CLIENT_ID")
EXTERNAL_GITHUB_APP_PRIVATE_KEY = os.environ.get("EXTERNAL_GITHUB_APP_PRIVATE_KEY")
if EXTERNAL_GITHUB_APP_PRIVATE_KEY is not None:
    with open(EXTERNAL_GITHUB_APP_PRIVATE_KEY, 'r') as f:
        EXTERNAL_GITHUB_APP_PRIVATE_KEY = f.read()


def _generate_github_app_jwt() -> str:
    if not EXTERNAL_GITHUB_CLIENT_ID or not EXTERNAL_GITHUB_APP_PRIVATE_KEY:
        raise RuntimeError("GitHub App credentials not configured: missing EXTERNAL_GITHUB_CLIENT_ID or EXTERNAL_GITHUB_APP_PRIVATE_KEY")
    now = int(time.time())
    payload = {'iat': now - 60, 'exp': now + 600, 'iss': EXTERNAL_GITHUB_CLIENT_ID}
    private_key = EXTERNAL_GITHUB_APP_PRIVATE_KEY.replace('\\n', '\n')
    return jwt.encode(payload, private_key, algorithm='RS256')


def extract_repo_path_from_url(repo_url: str) -> Optional[str]:
    if repo_url.startswith("https://github.com/"):
        repo_path = repo_url.replace("https://github.com/", "").split("#")[0].replace(".git", "")
    elif repo_url.startswith("git@github.com:"):
        repo_path = repo_url.replace("git@github.com:", "").replace(".git", "")
    else:
        logger.error(f"Unsupported repo URL format: {repo_url}")
        return None
    if "/" not in repo_path:
        return None
    return repo_path


async def _check_installation_repo_access(installation_id: str, target_repo_path: str) -> bool:
    install_token = await exchange_installation_id_to_token(installation_id)
    if not install_token:
        return False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.github.com/installation/repositories",
                headers={
                    "Authorization": f"Bearer {install_token}",
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


async def exchange_installation_id_to_token(installation_id: str) -> Optional[str]:
    app_jwt = _generate_github_app_jwt()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {app_jwt}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=5
            )
            if resp.status_code == 201:
                data = resp.json()
                return data.get("token")
            else:
                logger.error(f"Failed to get installation token: {resp.status_code} {resp.text}")
                return None
    except Exception as e:
        logger.exception(f"Error getting GitHub app installation token: {e}")
        return None


async def get_token_from_github_auth_cred(auth_json: dict, repo_name: str) -> Optional[str]:
    inst_id = await pick_working_installation_id(auth_json["installation_ids"], f"https://github.com/{repo_name}")
    if not inst_id:
        return None
    return await exchange_installation_id_to_token(inst_id)


