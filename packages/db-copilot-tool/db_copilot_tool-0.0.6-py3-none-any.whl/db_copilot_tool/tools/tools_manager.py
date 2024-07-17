from pathlib import Path
import yaml


def list_package_tools():
    """List package tools"""

    yaml_dir = Path(__file__).parent / "yamls"

    tools = {}
    for f in Path(yaml_dir).glob("**/*.yaml"):
        with open(f, "r") as f:
            tools_in_file = yaml.safe_load(f)
            for identifier, tool in tools_in_file.items():
                tools[identifier] = tool
    return tools
