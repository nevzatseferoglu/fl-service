
from typing import Annotated
from fastapi import APIRouter, Path

router = APIRouter(
    prefix="/check",
    tags=["check"],
)

state_install_aptitude: str
state_install_required_system_packages: str
state_add_docker_gpg_apt_key: str
state_add_docker_repository: str
state_update_apt_and_install_docker_ce: str
state_install_docker_module_for_python: str

@router.get("/docker/{task_name}", )
def check_docker(task_name: Annotated[str | None, Path()]):
    pass

