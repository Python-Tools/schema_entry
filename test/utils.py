from pathlib import Path
from typing import Optional

def _find_parent_as_project_home(nowpath: Path,project_home: str)->Path:
    parent = nowpath.parent
    if parent.name == project_home:
        return parent.resolve()
    else:
        return _find_parent_as_project_home(parent,project_home)


def find_module_import_path(nowpath: Path, project_home: str, package_dir: Optional[str] = None)->Path:
    """从指定位置找到项目模块源码路径.

    Args:
        nowpath (Path): [description]
        project_home (str): [description]
        package_dir (Optional[str], optional): [description]. Defaults to None.

    Returns:
        Path: [description]
    """
    project_home_path = _find_parent_as_project_home(nowpath,project_home)
    if package_dir:
        return project_home_path.joinpath(package_dir)
    else:
        return project_home_path