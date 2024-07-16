from ciocore import data as coredata

PATH_COMPONENTS = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin".split(":")

def get_packages_data(software_list):
    """Get package IDs and env based on selected software.

    When making queries to the package tree, we must qualify host and plugin paths with the
    platform. The platform was previously stripped away because it was not needed in a single
    platform environment. We don't want to have the word linux next to every entry in the
    dropdown.

    * "maya 1.0.0" must be "maya 1.0.0 linux"
    * "maya 1.0.0 linux/arnold 5.0.0" must be "maya 1.0.0 linux/arnold 5.0.0 linux"
    """
    tree_data = coredata.data().get("software")

    package_ids = []
    environment = []
    environment.extend(
        [{"key": "[PATH]", "value": c} for c in PATH_COMPONENTS]
    )
    
    for package in filter(
        None, [tree_data.find_by_path(path) for path in software_list if path]
    ):
        if package:
            package_ids.append(package["package_id"])
            for entry in package["environment"]:
                if entry["merge_policy"].endswith("pend"):

                    environment.append(
                        {
                            "key": f"[{entry['name']}]",
                            "value": entry["value"],
                        }
                    )
                else:
                    environment.append(
                        {
                            "key": entry["name"],
                            "value": entry["value"],
                        }
                    )
    package_ids = list(set(package_ids))
    return package_ids, environment


def composeEnvVars(env_vars):
    """
    Processes a list of environment variables and composes a dictionary of key-value pairs.

    The function handles keys both with and without square brackets:
    - If a key is enclosed in square brackets and already exists in the result dictionary,
    the new value is concatenated to the existing value using a colon as a separator.
    - If a key is enclosed in square brackets and does not exist in the result dictionary,
    it is added without the brackets.
    - If a key is not enclosed in brackets, it is added to the dictionary directly, and any
    existing value under the same key is overwritten.

    Args:
        env_vars (list of dict): A list of dictionaries where each dictionary has a 'key' and 'value'
                                indicating the environment variable's name and value respectively.

    Returns:
        dict: A dictionary with environment variable keys as dictionary keys and the corresponding values.
            If keys are enclosed in brackets and repeated, their values are concatenated.

    Example:
        >>> composeEnvVars([{"key": "[PATH]", "value": "/usr/bin"}, {"key": "[PATH]", "value": "/bin"}])
        {'PATH': '/usr/bin:/bin'}
        >>> composeEnvVars([{"key": "USER", "value": "root"}, {"key": "SHELL", "value": "/bin/bash"}])
        {'USER': 'root', 'SHELL': '/bin/bash'}
    """
    result = {}
    for env_var in env_vars:
        key = env_var["key"]
        value = env_var["value"]

        if key.startswith("[") and key.endswith("]"):
            stripped_key = key[1:-1]
            if stripped_key in result:
                result[stripped_key] = f"{result[stripped_key]}:{value}"
            else:
                result[stripped_key] = value
        else:
            result[key] = value

    return result
