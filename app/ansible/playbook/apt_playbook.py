apt_update_playbook = [
    {
        "name": "Update APT cache",
        "hosts": "all",
        "become": True,
        "tasks": [
            {"name": "Update APT cache", "ansible.builtin.apt": {"update_cache": True}}
        ],
    }
]


def new_remote_host_dict_apt_update_playbook(
    host: str,
    become: bool = True,
    become_user: str = "root",
    become_method: str = "sudo",
    become_pass: str = None,
    gather_facts: bool = True,
    tasks: list = None,
):
    if tasks is None:
        tasks = []
    return {
        "name": "Update APT cache",
        "hosts": host,
        "become": become,
        "become_user": become_user,
        "become_method": become_method,
        "become_pass": become_pass,
        "gather_facts": gather_facts,
        "tasks": tasks,
    }
