import sys
import subprocess
import chardet
from colorama import init
from termcolor import colored

from schema_entry import EntryPoint

init()


class Check(EntryPoint):
    """测试本项目."""
    _name = "example.py"


class Static(EntryPoint):
    """项目的静态类型检测,并输出到typecheck文件夹."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "package": {
                "type": "string",
                "default": "schema_entry",
                "description": "待检测的模块"
            },
            "output": {
                "type": "string",
                "default": "docs/typecheck",
                "description": "检测结果位置"
            }

        },
        "required": ["output"]
    }


class UnitTest(EntryPoint):
    """本项目的单元测试,并输出到文件夹."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "package": {
                "type": "string",
                "default": "schema_entry",
                "description": "待检测的模块"
            },
            "output": {
                "type": "string",
                "default": "docs/test_coverage",
                "description": "检测结果位置"
            }

        },
        "required": ["output"]
    }


root = Check()
static = root.regist_sub(Static)
utest = root.regist_sub(UnitTest)


@static.as_main
def do_static(package: str, output: str) -> None:
    cmd = f"mypy --ignore-missing-imports --show-column-numbers --follow-imports=silent --check-untyped-defs --disallow-untyped-defs --no-implicit-optional --warn-unused-ignores --html-report={output} {package}"
    res = subprocess.run(cmd, capture_output=True, shell=True)
    if res.returncode != 0:
        if res.stderr:
            encoding = chardet.detect(res.stderr).get("encoding")
            content = res.stderr.decode(encoding).strip()
        else:
            encoding = chardet.detect(res.stdout).get("encoding")
            content = res.stdout.decode(encoding).strip()
        print(colored(content, 'white', 'on_magenta'))
    else:
        content = ""
        if res.stdout:
            encoding = chardet.detect(res.stdout).get("encoding")
            content = res.stdout.decode(encoding).strip()
        print(colored(content, 'white', 'on_cyan'))


@utest.as_main
def do_utest(package: str, output: str) -> None:
    cmd = f"python -m coverage run --source={package} -m unittest discover -v -s . -p *test*.py"

    res = subprocess.run(cmd, capture_output=True, shell=True)
    if res.returncode != 0:
        if res.stderr:
            encoding = chardet.detect(res.stderr).get("encoding")
            content = res.stderr.decode(encoding).strip()
        else:
            encoding = chardet.detect(res.stdout).get("encoding")
            content = res.stdout.decode(encoding).strip()
        print(colored(content, 'white', 'on_magenta'))
    else:
        if res.stdout:
            encoding = chardet.detect(res.stdout).get("encoding")
            content = res.stdout.decode(encoding).strip()
        print(colored(content, 'white', 'on_cyan'))

        cmd = f"python -m coverage html -d {output}"
        res = subprocess.run(cmd, capture_output=True, shell=True)
        if res.returncode != 0:
            if res.stderr:
                encoding = chardet.detect(res.stderr).get("encoding")
                content = res.stderr.decode(encoding).strip()
            else:
                encoding = chardet.detect(res.stdout).get("encoding")
                content = res.stdout.decode(encoding).strip()
            print(colored(content, 'white', 'on_magenta'))
        else:
            if res.stdout:
                encoding = chardet.detect(res.stdout).get("encoding")
                content = res.stdout.decode(encoding).strip()
            print(colored(content, 'white', 'on_cyan'))


if __name__ == "__main__":
    root(sys.argv[1:])
