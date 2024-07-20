from typing import Dict, Any
from .utils import write_output_to_file
from .gitlab_api import GitLabManager

async def pull_vars(options: Dict[str, Any]):

    try:
        manager = GitLabManager(
            access_token=options.get("access_token"),
            repository_url=options.get("repository_url"),
            scope=options.get("scope"),
        )

        env_vars = await manager.get_gitlab_env_vars()
        # Set output based on format
        output_file = options.get("output_file") or ".env"
        write_output_to_file(options["output_file"], env_vars)
        print(f"Env variables pulled and stored in {output_file}")

    except Exception as err:
        raise err

