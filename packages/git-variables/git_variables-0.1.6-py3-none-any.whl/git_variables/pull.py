from typing import Dict, Any
from .utils import write_output_to_file
from .gitlab_api import GitLabManager

async def pull(options: Dict[str, Any]):

    try:
        manager = GitLabManager(
            access_token=options.get("access_token"),
            repository_url=options.get("repository_url"),
            scope=options.get("scope"),
        )

        env_vars = await manager.get_gitlab_env_vars()
        # Set output based on format
        output_str = ""
        if options.get("output_file"):
            write_output_to_file(options["output_file"], env_vars)
            print("Env variables pulled.")
        else:
            write_output_to_file(".env", env_vars)
            print("Env variables pulled.")
    except Exception as err:
        raise err


# To use this function:
# asyncio.run(pull(options))
