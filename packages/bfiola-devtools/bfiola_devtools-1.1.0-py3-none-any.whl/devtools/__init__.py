#!/usr/bin/env python3
import contextlib
import io
import os
import pathlib
import pty
import select
import shlex
import subprocess
import sys
import tempfile
from typing import IO, Any, Generator, Literal, Union

import click
import packaging
import packaging.utils
import packaging.version
import pydantic
import toml

data_folder = pathlib.Path(__file__).parent.joinpath("data")


FD = int
Pty = tuple[FD, FD]


def log(message: str):
    click.echo(f"[log]: {message}", err=True)


@contextlib.contextmanager
def get_ptys() -> Generator[tuple[Pty, Pty], None, None]:
    """
    Gets a tuple of ptys (<stdout pty>, <stderr pty>)
    """
    try:
        stdout = pty.openpty()
        stderr = pty.openpty()
        yield stdout, stderr
    finally:
        for fd in [*stdout, *stderr]:
            try:
                os.close(fd)
            except OSError:
                continue


def get_reader(ins: tuple[FD, ...], outs: tuple[list[IO[str]], list[IO[str]]]):
    """
    Creates a read function.
    Will read from a tuple of input file descriptors, will write to a matching set of output buffers.

    Example: if ins[0] is read, the buffers of outs[0] will be written to.
    """

    def read():
        # find fds available to read from input fds
        readable, _, _ = select.select(ins, [], [], 0.1)
        while readable:
            # read from input fd
            fd = readable[-1]
            data = os.read(fd, 1024)
            if not data:
                # nothing to read
                readable.pop()
                continue

            # write to out buffers
            data = data.decode("utf-8")
            index = ins.index(fd)
            for out in outs[index]:
                out.write(data)

            # read complete
            readable.pop()

    return read


def run_cmd(cmd: list[str], **kwargs):
    """
    Helper method that runs a command.

    Accepts the same kwargs as `subprocess.Popen`.
    """
    # log command
    cmd_str = f"{shlex.join(cmd)}"
    if env := kwargs.get("env"):
        # if 'env' is defined, only log env overrides
        diff = {}
        for key, value in env.items():
            if os.environ.get(key) == value:
                continue
            diff[key] = value
        diff_str = " ".join(f"{k}={v}" for k, v in diff.items())
        if diff_str:
            cmd_str += f" (env: {diff_str})"
    if cwd := kwargs.get("cwd"):
        # if 'cwd' is defined, log cwd
        cmd_str += f" (cwd: {cwd})"
    click.echo(f"$ {cmd_str}", err=True)

    with get_ptys() as (stdout, stderr):
        # create reader
        out_stdout = io.StringIO()
        read = get_reader((stdout[0], stderr[0]), ([out_stdout, sys.stderr], [sys.stderr]))

        # create popen
        kwargs["encoding"] = "utf-8"
        kwargs["stdout"] = stdout[1]
        kwargs["stderr"] = stderr[1]
        popen = subprocess.Popen(cmd, **kwargs)

        # read until popen is complete
        while popen.poll() is None:
            read()
        read()

        # collect output
        out_stdout.seek(0)
        stdout = out_stdout.read()

    if popen.returncode != 0:
        # command failed
        error = f"Command '{shlex.join(cmd)}' exited with non-zero exit code {popen.returncode}"
        raise click.ClickException(error)

    return stdout


def validator(type: Any):
    """
    Uses pydantic to create a validator for an arbitrary type.

    Intended to be used with the `type` kwarg to click.argument/option.
    """

    def inner(value: str):
        return pydantic.TypeAdapter(type).validate_python(value)

    return inner


def main():
    try:
        grp_main()
    except Exception as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)


@click.group()
def grp_main():
    pass


Flavor = Union[Literal["python"], Literal["docker"]]


@grp_main.command("format", help="applies formatting rules to files")
@click.option("--check", is_flag=True, help="only check, do not overwrite files")
@click.argument("files", type=pathlib.Path, nargs=-1)
def cmd_format(*, check: bool = False, files: tuple[pathlib.Path]):
    files_ = list(files)
    stream_mode = len(files_) == 0

    with contextlib.ExitStack() as exit_stack:
        if stream_mode:
            temp_file_handle = exit_stack.enter_context(tempfile.NamedTemporaryFile())
            temp_file = pathlib.Path(temp_file_handle.name)
            temp_file.write_text(sys.stdin.read())
            files_.append(pathlib.Path(temp_file_handle.name))

        file_strs = list(map(str, files_))
        isort_config = data_folder.joinpath("isort.toml")
        isort_cmd = ["isort", f"--settings={isort_config}"]
        if check:
            isort_cmd.extend(["--check"])
        isort_cmd.extend(file_strs)
        run_cmd(isort_cmd)

        black_config = data_folder.joinpath("black.toml")
        black_cmd = ["black", f"--config={black_config}"]
        if check:
            black_cmd.extend(["--check"])
        black_cmd.extend(file_strs)
        run_cmd(black_cmd)

        if stream_mode:
            temp_file = files_[0]
            click.echo(temp_file.read_text())


@grp_main.command("publish-github-action", help="runs a 'publish' github action")
@click.argument("flavor", type=validator(Flavor))
@click.option("--token", required=True)
def cmd_publish_github_action(*, flavor: Flavor, token: str):
    pyproject_file = pathlib.Path.cwd().joinpath("pyproject.toml")
    if not pyproject_file.exists():
        raise click.ClickException(f"pyproject.toml not found")
    github_output_path = os.environ.get("GITHUB_OUTPUT")
    if not github_output_path:
        raise click.ClickException(f"github output env unset")

    with open(github_output_path, "a") as github_output:
        project_data = toml.loads(pyproject_file.read_text())
        name = project_data["project"]["name"]

        log("writing version")
        version = run_cmd(["devtools", "print-next-version"]).strip()
        log(f"version: {version}")
        project_data["project"]["version"] = version
        pyproject_file.write_text(toml.dumps(project_data))
        github_output.writelines([f"version={version}"])

        log("writing tag")
        tag = run_cmd(["devtools", "print-next-version", "--as-tag"]).strip()
        log(f"tag: {tag}")
        github_output.writelines([f"tag={tag}"])

        log(f"check formatting")
        run_cmd(["devtools", "format", "--check", "."])

        if flavor == "python":
            log("build python package")
            run_cmd(["python", "-m", "build"])
            log("publish python package")
            pkg_name = packaging.utils.canonicalize_name(name).replace("-", "_")
            pkg_version = packaging.utils.canonicalize_version(version, strip_trailing_zero=False)
            log(f"package name: {pkg_name}")
            log(f"package version: {pkg_version}")
            globs = [
                f"dist/{pkg_name}-{pkg_version}-*.whl",
                f"dist/{pkg_name}-{pkg_version}.tar.gz",
            ]
            files = []
            for glob in globs:
                files.extend(pathlib.Path.cwd().glob(glob))
            if not files:
                raise RuntimeError(f"unable to find wheel/sdist files: {globs}")
            run_cmd(
                [
                    "twine",
                    "--no-color",
                    "upload",
                    "--disable-progress-bar",
                    "--username=__token__",
                    f"--password={token}",
                    *list(map(str, files)),
                ]
            )
        elif flavor == "docker":
            log("log into docker")
            run_cmd(["docker", "login", "--username=benfiola", f"--password={token}"])
            log("build and publish docker image")
            base_image = f"docker.io/benfiola/{name}"
            publish_latest = not packaging.version.Version(version).is_prerelease
            image_version = version.replace("+", "-")
            log(f"image: {base_image}:{image_version}")
            log(f"publish latest: {publish_latest}")
            cmd = [
                "docker",
                "buildx",
                "build",
                "--platform=linux/arm64,linux/amd64",
                "--progress=plain",
                "--push",
                f"--tag={base_image}:{image_version}",
            ]
            if publish_latest:
                cmd.extend([f"--tag={base_image}:latest"])
            cmd.extend(["."])
            run_cmd(cmd)


@grp_main.command("print-next-version", help="prints the next version")
@click.option("--as-tag", is_flag=True)
def cmd_print_next_version(*, as_tag: bool = False):
    config = data_folder.joinpath("python-semantic-release.toml")
    command = [
        "python",
        "-m",
        "semantic_release",
        f"--config={config}",
        "--noop",
        "--strict",
        "version",
    ]
    if as_tag is True:
        command.extend(["--print-tag"])
    else:
        command.extend(["--print"])
    env = {"GH_TOKEN": "undefined", **os.environ}
    version = run_cmd(command, env=env).strip()
    click.echo(version)


if __name__ == "__main__":
    main()
