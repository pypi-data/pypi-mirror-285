"""
    Copyright 2016 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""

import re
from collections import defaultdict

from inmanta.agent.handler import ResourceHandler, provider
from inmanta.export import dependency_manager
from inmanta.resources import Resource, resource


@dependency_manager
def yum_dependencies(config_model, resource_model):
    repo_files = defaultdict(list)
    pkgs = defaultdict(list)

    for _, rs in resource_model.items():
        if rs.id.entity_type == "fs::File" and rs.path.startswith("/etc/yum.repos.d"):
            repo_files[rs.id.agent_name].append(rs)

        elif rs.id.entity_type == "yum::Package":
            pkgs[rs.id.agent_name].append(rs)

    # they require the tenant to exist
    for hostname, pkgs in pkgs.items():
        for pkg in pkgs:
            for repo in repo_files[hostname]:
                pkg.requires.add(repo)


@resource("yum::Package", agent="host.name", id_attribute="name")
class Package(Resource):
    """
    A software package installed on an operating system.
    """

    fields = ("name", "state")


@provider("yum::Package", name="yum")
class YumPackage(ResourceHandler):
    """
    A Package handler that uses yum
    """

    def available(self, resource):
        return (
            self._io.file_exists("/usr/bin/rpm") or self._io.file_exists("/bin/rpm")
        ) and (
            self._io.file_exists("/usr/bin/yum") or self._io.file_exists("/usr/bin/dnf")
        )

    def _parse_fields(self, lines):
        props = {}
        key = ""
        old_key = None
        for line in lines:
            if line.strip() == "":
                continue

            if line.strip() == "Available Packages":
                break

            result = re.search(r"""^(.+) :\s+(.+)""", line)
            if result is None:
                continue

            key, value = result.groups()
            key = key.strip()

            if key == "":
                props[old_key] += " " + value
            else:
                props[key] = value
                old_key = key

        return props

    def _run_yum(self, args):
        # todo: cache value
        if self._io.file_exists("/usr/bin/dnf"):
            return self._io.run("/usr/bin/dnf", ["-d", "0", "-e", "1", "-y"] + args)
        else:
            return self._io.run("/usr/bin/yum", ["-d", "0", "-e", "1", "-y"] + args)

    def check_resource(self, ctx, resource):
        yum_output = self._run_yum(["info", resource.name])
        lines = yum_output[0].split("\n")

        output = self._parse_fields(lines[1:])
        # to decide if the package is installed or not, the "Repo" field can be used
        # from the yum info output (for e.g., CentOS 7)
        # the dnf info output (for e.g., CentOS 8) doesn't have this field, "Repository" can be used instead
        repo_keyword = (
            "Repo"
            if "Repo" in output
            else "Repository" if "Repository" in output else None
        )

        if not repo_keyword:
            return {"state": "removed"}

        state = "removed"

        if output[repo_keyword] == "installed" or output[repo_keyword] == "@System":
            state = "installed"

        # check if there is an update
        yum_output = self._run_yum(["check-update", resource.name])
        lines = yum_output[0].split("\n")

        data = {
            "state": state,
            "version": output["Version"],
            "release": output["Release"],
            "update": None,
        }

        if len(lines) > 0:
            parts = re.search(r"""([^\s]+)\s+([^\s]+)\s+([^\s]+)""", lines[0])
            if parts is not None and not lines[0].startswith("Security:"):
                version_str = parts.groups()[1]
                version, release = version_str.split("-")

                data["update"] = (version, release)

        return data

    def list_changes(self, ctx, resource):
        state = self.check_resource(ctx, resource)

        changes = {}
        if resource.state == "removed":
            if state["state"] != "removed":
                changes["state"] = (state["state"], resource.state)

        elif resource.state == "installed" or resource.state == "latest":
            if state["state"] != "installed":
                changes["state"] = (state["state"], "installed")

        if (
            "update" in state
            and state["update"] is not None
            and resource.state == "latest"
        ):
            changes["version"] = ((state["version"], state["release"]), state["update"])

        return changes

    def _result(self, output):
        stdout = output[0].strip()
        error_msg = output[1].strip()
        if output[2] != 0:
            raise Exception("Yum failed: stdout:" + stdout + " errout: " + error_msg)

    def do_changes(self, ctx, resource, changes):
        if "state" in changes:
            if changes["state"][1] == "removed":
                self._result(self._run_yum(["remove", resource.name]))
                ctx.set_purged()

            elif changes["state"][1] == "installed":
                self._result(self._run_yum(["install", resource.name]))
                self._result(self._run_yum(["update", resource.name]))
                ctx.set_created()

        elif "version" in changes:
            self._result(self._run_yum(["update", resource.name]))
            ctx.set_updated()
