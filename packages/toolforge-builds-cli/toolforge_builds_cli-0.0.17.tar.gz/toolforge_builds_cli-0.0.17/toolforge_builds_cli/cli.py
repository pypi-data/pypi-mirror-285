#!/usr/bin/env python3
from __future__ import annotations

import json as json_mod
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

import click
from tabulate import tabulate
from toolforge_weld.errors import ToolforgeError, ToolforgeUserError, print_error_context

from toolforge_builds_cli.build import BuildClient, BuildClientError
from toolforge_builds_cli.config import get_loaded_config

LOGGER = logging.getLogger("toolforge" if __name__ == "__main__" else __name__)
TOOLFORGE_BUG_URL = "https://w.wiki/6Zuu"

STATUS_STYLE = {
    "unknown": click.style("unknown", fg="yellow"),
    "running": click.style("running", fg="yellow"),
    "ok": click.style("ok", fg="green"),
    "cancelled": click.style("cancelled", fg="green"),
    "error": click.style("error", fg="red"),
    "timeout": click.style("timeout", fg="red"),
}


def _display_messages(messages: dict[str, list[str]]) -> None:
    # TODO: move this into toolforge-weld before using it in other clients once the POC is good to go
    error_messages = messages.get("error", [])
    for message in error_messages:
        click.echo(click.style(message, fg="red"), err=True)

    warning_messages = messages.get("warning", [])
    for message in warning_messages:
        click.echo(click.style(message, fg="yellow"), err=True)

    info_messages = messages.get("info", [])
    for message in info_messages:
        click.echo(click.style(message, fg="blue"), err=True)


def handle_error(e: Exception, debug: bool = False) -> None:
    user_error = isinstance(e, ToolforgeUserError)

    prefix = "Error: "
    if not user_error:
        prefix = f"{e.__class__.__name__}: "

    click.echo(click.style(f"{prefix}{e}", fg="red"))

    if debug:
        LOGGER.exception(e)

        if isinstance(e, ToolforgeError):
            print_error_context(e)
    elif not user_error:
        click.echo(
            click.style(
                f"Please report this issue to the Toolforge admins if it persists: {TOOLFORGE_BUG_URL}",
                fg="red",
            )
        )


def _format_build(build: Dict[str, Any]) -> Dict[str, Any]:
    start_time = build["start_time"] if build["start_time"] else "N/A"
    end_time = build["end_time"] if build["end_time"] else "N/A"
    ref = build["parameters"]["ref"] if build["parameters"]["ref"] else "N/A"
    if build["parameters"].get("envvars"):
        envvars = [f"{name}={value}" for name, value in build["parameters"]["envvars"].items()]
    else:
        envvars = ["N/A"]
    status = build["status"].split("_")[1].lower()
    if status == "success":
        status = "ok"
    elif status == "failure":
        status = "error"

    return {
        "build_id": build["build_id"],
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "message": build["message"],
        "ref": ref,
        "envvars": envvars,
        "source_url": build["parameters"]["source_url"],
        "destination_image": build["destination_image"],
    }


def _builds_to_table(builds: List[Dict[str, Any]]) -> List[Any]:
    headers = [
        "build_id",
        "status",
        "start_time",
        "end_time",
        "source_url",
        "ref",
        "envvars",
        "destination_image",
    ]
    headers = [click.style(header, bold=True) for header in headers]
    builds_values = []
    for build in builds:
        build_values = [
            build["build_id"],
            STATUS_STYLE[build["status"]],
            build["start_time"],
            build["end_time"],
            build["source_url"],
            build["ref"],
            "\n".join(build["envvars"]),
            build["destination_image"],
        ]
        builds_values.append(build_values)
    return [headers, builds_values]


def _get_formatted_build_str(build: Dict[str, Any]) -> str:
    build_str = ""
    build_str += f"{click.style('Build ID:', bold=True)} {click.style(build['build_id'], fg='blue')}\n"
    build_str += f"{click.style('Start Time:', bold=True)} {build['start_time']}\n"
    build_str += f"{click.style('End Time:', bold=True)} {build['end_time']}\n"
    build_str += f"{click.style('Status:', bold=True)} {STATUS_STYLE[build['status']]}\n"
    build_str += f"{click.style('Message:', bold=True)} {build['message']}\n"
    build_str += click.style("Parameters:\n", bold=True)
    build_str += f"    {click.style('Source URL:', bold=True)} {build['source_url']}\n"
    build_str += f"    {click.style('Ref:', bold=True)} {build['ref']}\n"
    envvars = "\n             ".join(build["envvars"])
    build_str += f"    {click.style('Envvars:', bold=True)} {envvars}\n"
    build_str += f"{click.style('Destination Image:', bold=True)} {build['destination_image']}"

    return build_str


@click.version_option(prog_name="Toolforge Builds CLI")
@click.group(name="build", help="Toolforge build command line")
@click.option(
    "-v",
    "--verbose",
    help="Show extra verbose output. NOTE: Do no rely on the format of the verbose output",
    is_flag=True,
    default=(os.environ.get("TOOLFORGE_VERBOSE", "0") == "1"),
    hidden=(os.environ.get("TOOLFORGE_CLI", "0") == "1"),
)
@click.option(
    "-d",
    "--debug",
    help="show logs to debug the toolforge-build-* packages. For extra verbose output, see --verbose",
    is_flag=True,
    default=(os.environ.get("TOOLFORGE_DEBUG", "0") == "1"),
    hidden=(os.environ.get("TOOLFORGE_CLI", "0") == "1"),
)
@click.pass_context
def toolforge_build(ctx: click.Context, verbose: bool, debug: bool) -> None:
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug
    ctx.obj["config"] = get_loaded_config()
    ctx.obj["client"] = BuildClient.from_config(config=ctx.obj["config"])
    pass


@toolforge_build.command(name="start", help="Start a pipeline to build a container image from source code")
@click.argument("SOURCE_GIT_URL", required=False)
@click.option(
    "--ref",
    help="Branch, tag or commit to build, by default will use the HEAD of the given repository.",
    show_default=True,
)
@click.option("-i", "--image-name", help="Name of the image to be built, by default will be the name of the tool.")
@click.option(
    "envvars",
    "-e",
    "--envvar",
    help="Environment variable and value to set during build (format `NAME=value`)",
    multiple=True,
)
@click.option(
    "--json",
    help="If set, will output in json format",
    is_flag=True,
)
@click.option("--detach", "-D", help="If set, will not stream build logs automatically", is_flag=True)
@click.pass_context
def build_start(
    ctx: click.Context,
    source_git_url: str,
    ref: Optional[str] = None,
    image_name: Optional[str] = None,
    json: bool = False,
    detach: bool = False,
    envvars: Optional[List[str]] = None,
) -> None:
    if not source_git_url:
        message = (
            f"{click.style('Error:', bold=True, fg='red')} Please provide a git url for your source code.\n"
            + f"{click.style('Example:', bold=True)}"
            + " toolforge build start 'https://gitlab.wikimedia.org/toolforge-repos/my-tool'"
        )
        click.echo(message)
        sys.exit(1)

    build_client = ctx.obj["client"]

    data: dict[str, Any] = {"source_url": source_git_url}
    if ref:
        data["ref"] = ref
    if image_name:
        data["image_name"] = image_name
    if envvars:
        data["envvars"] = {envvar_str.split("=", 1)[0]: envvar_str.split("=", 1)[-1] for envvar_str in envvars}

    start_response = build_client.post("/builds", json=data)

    new_build = start_response["new_build"]
    _display_messages(start_response["messages"])

    if not detach:
        return ctx.invoke(build_logs, build_name=new_build["name"], follow=True)

    if json:
        click.echo(json_mod.dumps(new_build, indent=4))
    else:
        click.echo(
            f"Building '{new_build['parameters']['source_url']}', build name is '{new_build['name']}'\n"
            f"You can see the status with:\n\ttoolforge build show"
        )


@toolforge_build.command(name="logs", help="Show the logs for a build")
@click.argument("BUILD_NAME", required=False)
@click.option(
    "--follow",
    "-f",
    help="Follow the logs",
    is_flag=True,
    default=False,
)
@click.pass_context
def build_logs(ctx: click.Context, build_name: Optional[str], follow: bool) -> None:
    click.secho("Waiting for the logs... if the build just started this might take a minute", err=True, fg="yellow")
    build_client = ctx.obj["client"]
    if not build_name:
        response = build_client.get("/builds/latest")
        _display_messages(response["messages"])
        build_name = response["build"]["build_id"]

    logs = build_client.get_raw_lines(f"/builds/{build_name}/logs?follow={follow}", timeout=None)
    for log in logs:
        line = json_mod.loads(log)
        if "message" in line:
            raise BuildClientError(line["message"])
        click.echo(line["line"])


@toolforge_build.command(name="list", help="List builds")
@click.option(
    "--json",
    help="If set, will output in json format",
    is_flag=True,
)
@click.pass_context
def build_list(ctx: click.Context, json: bool) -> None:
    build_client = ctx.obj["client"]
    list_response = build_client.get("/builds")

    builds = list_response["builds"]
    _display_messages(list_response["messages"])

    if len(builds) == 0:
        click.echo(
            click.style(
                (
                    "No builds found, you can start one using `toolforge build start`,"
                    + "run `toolforge build start --help` for more details"
                ),
                fg="yellow",
            )
        )
        return

    builds = [_format_build(build=build) for build in builds]
    if json:
        for build in builds:
            click.echo(json_mod.dumps(build, indent=4))
        return

    headers, data = _builds_to_table(builds=builds)
    click.echo(
        tabulate(
            data,
            headers=headers,
            tablefmt="plain",
        )
    )


@toolforge_build.command(name="cancel", help="Cancel a running build (does nothing for stopped ones)")
@click.option(
    "--all",
    help="Cancel all the current builds.",
    is_flag=True,
)
@click.option(
    "--yes-i-know",
    "-y",
    help="Don't ask for confirmation.",
    is_flag=True,
)
@click.argument(
    "build_ids",
    nargs=-1,
)
@click.pass_context
def build_cancel(ctx: click.Context, build_ids: List[str], all: bool, yes_i_know: bool) -> None:
    if not build_ids and not all:
        message = (
            f"{click.style('Error:', bold=True, fg='red')} No build passed to cancel.\n"
            + f"{click.style('Example:', bold=True)}"
            + " toolforge build cancel <build-id>"
        )
        click.echo(message)
        sys.exit(1)

    build_client = ctx.obj["client"]

    if not yes_i_know:
        click.confirm(f"I'm going to cancel {len(build_ids)} builds, continue?", abort=True)

    build_ids_count = len(build_ids)
    got_error = False
    for build_id in build_ids:
        try:
            cancel_response = build_client.put(f"/builds/{build_id}/cancel")
            result = cancel_response["id"]
            _display_messages(cancel_response["messages"])
            if not result:
                build_ids_count -= 1
        except Exception as e:
            handle_error(e, debug=ctx.obj["debug"])
            build_ids_count -= 1
            got_error = True

    click.echo(f"Cancelled {build_ids_count} builds")
    sys.exit(1 if got_error else 0)


@toolforge_build.command(name="delete", help="Delete a build")
@click.option(
    "--all",
    help="Delete all the current builds",
    is_flag=True,
)
@click.option(
    "--yes-i-know",
    "-y",
    help="Don't ask for confirmation",
    is_flag=True,
)
@click.argument(
    "build_ids",
    nargs=-1,
)
@click.pass_context
def build_delete(ctx: click.Context, build_ids: List[str], all: bool, yes_i_know: bool) -> None:
    if not build_ids and not all:
        message = (
            f"{click.style('Error:', bold=True, fg='red')} No build passed to delete.\n"
            + f"{click.style('Example:', bold=True)}"
            + " toolforge build delete <build-id>"
        )
        click.echo(message)
        sys.exit(1)

    build_client = ctx.obj["client"]

    if all:
        list_response = build_client.get("/builds")
        builds = list_response["builds"]
        _display_messages(list_response["messages"])

        build_ids = [build["build_id"] for build in builds]

    if not yes_i_know:
        click.confirm(f"I'm going to delete {len(build_ids)} builds, continue?", abort=True)

    got_error = False
    build_ids_count = len(build_ids)
    for build_id in build_ids:
        try:
            delete_response = build_client.delete(f"/builds/{build_id}")
            _display_messages(delete_response["messages"])
            result = delete_response["id"]
            if not result:
                build_ids_count -= 1
        except Exception as e:
            handle_error(e, debug=ctx.obj["debug"])
            build_ids_count -= 1
            got_error = True

    click.echo(f"Deleted {build_ids_count} builds")
    sys.exit(1 if got_error else 0)


@toolforge_build.command(name="show", help="Show details for a specific build")
@click.argument("BUILD_NAME", required=False)
@click.option(
    "--json",
    help="If set, will output in json format",
    is_flag=True,
)
@click.pass_context
def build_show(ctx: click.Context, build_name: Optional[str], json: bool) -> None:
    build_client = ctx.obj["client"]

    if build_name:
        response = build_client.get(f"/builds/{build_name}")
    else:
        response = build_client.get("/builds/latest")

    _display_messages(response["messages"])
    build = response["build"]

    build = _format_build(build=build)
    if json:
        click.echo(
            json_mod.dumps(
                build,
                indent=4,
            )
        )
    else:
        click.echo(_get_formatted_build_str(build=build))


@toolforge_build.command(name="quota", help="Display quota information")
@click.option("--json", is_flag=True, help="Display output in JSON format.")
@click.pass_context
def build_quota(ctx: click.Context, json: bool) -> None:
    build_client = ctx.obj["client"]
    quota_response = build_client.get("/quotas")
    _display_messages(quota_response["messages"])
    quota_info = quota_response["quota"]

    if json:
        click.echo(
            json_mod.dumps(
                quota_info,
                indent=4,
            )
        )
    else:
        for category in quota_info["categories"]:
            data = []
            for item in category["items"]:
                data.append([f"{item['name']}", ""])
                data.append(["-----------", ""])
                data.extend([[key.capitalize(), value] for key, value in item.items() if key != "name"])
                data.append(["", ""])  # Newline after each item

            click.echo(f"{category['name']}")
            click.echo("===================")

            click.echo(tabulate(data, tablefmt="plain"))


@toolforge_build.command(name="clean", help="Try to cleanup old artifacts and caches to free some quota.")
@click.option("--json", is_flag=True, help="Display output in JSON format.")
@click.option(
    "--yes-i-know",
    "-y",
    help="Don't ask for confirmation",
    is_flag=True,
)
@click.pass_context
def clean(ctx: click.Context, json: bool, yes_i_know: bool) -> None:
    if not yes_i_know:
        click.confirm(
            (
                "NOTE: This will remove all your built images to clean up space, you'll have to start a new build to "
                "create a new image before being able to restart any running webservice/job or start a new one, are "
                "you sure?"
            ),
            abort=True,
        )

    build_client = ctx.obj["client"]
    cleanup_response = build_client.post("/clean")
    message = cleanup_response["messages"]["info"][0]

    if json:
        click.echo(
            json_mod.dumps(
                cleanup_response,
                indent=4,
            )
        )
    else:
        click.echo(f"Result of the cleanup: {message}")
        click.echo(f"If you still need more space, please contact a toolforge maintainer ({TOOLFORGE_BUG_URL}).")


@toolforge_build.command(name="_commands", hidden=True)
def internal_commands():
    """Used internally for tab completion."""
    for name, command in sorted(toolforge_build.commands.items()):
        if command.hidden:
            continue
        click.echo(name)


def main() -> int:
    args = toolforge_build.parse_args(ctx=click.Context(command=toolforge_build), args=sys.argv)
    debug = "-d" in args or "--debug" in args
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    rc = 0
    try:
        toolforge_build()
    except subprocess.CalledProcessError as e:
        handle_error(e, debug=debug)
        rc = e.returncode
    except Exception as e:
        handle_error(e, debug=debug)
        rc = 1

    return rc


if __name__ == "__main__":
    sys.exit(main())
