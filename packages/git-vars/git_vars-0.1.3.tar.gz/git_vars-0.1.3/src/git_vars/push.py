import os
from typing import Dict, Any, List
import sys
from pathlib import Path
from .utils import parse_data_from_env
from .gitlab_api import GitLabManager

# Get the absolute path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to sys.path
sys.path.append(parent_dir)

async def push_vars(options: Dict[str, Any]):
    try:
        manager = GitLabManager(
            access_token=options.get("access_token"),
            repository_url=options.get("repository_url"),
            scope=options.get("scope"),
        )

        file = options.get("env_vars")

        # Get env file variables
        if file:
            env_file_vars = parse_data_from_env(file)

        # Get env variables from GitLab
        gitlab_env_vars = await manager.get_gitlab_env_vars()

        # Synchronize env file variables to GitLab
        updated_env_vars = []
        deleted_env_vars = []
        gitlab_env_var_hashmap = {}

        # Filter updated and deleted env variables
        for env_var in gitlab_env_vars:
            if env_var["key"] in env_file_vars:
                if env_file_vars[env_var["key"]] != env_var["value"]:
                    updated_env_vars.append(
                        {
                            "key": env_var["key"],
                            "value": env_file_vars[env_var["key"]],
                        }
                    )
                del env_file_vars[env_var["key"]]
            else:
                deleted_env_vars.append(
                    {
                        "key": env_var["key"],
                        "value": env_var["value"],
                    }
                )
            gitlab_env_var_hashmap[env_var["key"]] = env_var["value"]

        # Filter new env variables
        new_env_vars = [
            {"key": key, "value": value}
            for key, value in env_file_vars.items()
            if key not in gitlab_env_var_hashmap
        ]

        # Perform API operations
        if new_env_vars:
            await manager.create_gitlab_env_variables(new_env_vars)
        if updated_env_vars:
            await manager.update_gitlab_env_variables(updated_env_vars)
        if deleted_env_vars:
            await manager.delete_gitlab_env_variables(deleted_env_vars)

        modified_count = (
            len(new_env_vars) + len(updated_env_vars) + len(deleted_env_vars)
        )
        if modified_count == 0:
            print("Already up-to-date")

    except Exception as err:
        raise err
