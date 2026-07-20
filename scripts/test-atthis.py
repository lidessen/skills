#!/usr/bin/env python3
"""Integration probe for relocatable Atthis project resolution."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "atthis.py"


def run(home: Path, *arguments: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["python3", str(SCRIPT), "--home", str(home), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"expected {expect}, got {result.returncode}: {' '.join(arguments)}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}",
        )
    return result


def git(cwd: Path, *arguments: str) -> None:
    subprocess.run(["git", *arguments], cwd=cwd, check=True, stdout=subprocess.DEVNULL)


def create_repo(path: Path, remote: str | None) -> None:
    path.mkdir()
    git(path, "init")
    git(path, "config", "user.name", "Atthis Test")
    git(path, "config", "user.email", "atthis@example.test")
    (path / "README.md").write_text("# Test\n", encoding="utf-8")
    git(path, "add", "README.md")
    git(path, "commit", "-m", "initial")
    if remote:
        git(path, "remote", "add", "origin", remote)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="atthis-test-") as temporary:
        root = Path(temporary)
        home = root / "home"
        survey = root / "survey"
        meowask = root / "meowask"
        other = root / "other"
        same_repository = root / "same-repository"
        pool = root / "pool"
        late_pool = root / "late-pool"
        discovered = pool / "unregistered"
        local_only = pool / "local-only"
        empty = pool / "empty"
        credentialed = pool / "credentialed"
        late = late_pool / "late"
        remote = "https://example.test/lidessen/meowask.git"
        credentialed_remote = "https://user:secret@example.test/lidessen/credentialed.git?access_token=hidden#fragment"
        credential_free_remote = "https://example.test/lidessen/credentialed.git"

        create_repo(survey, remote)
        create_repo(other, "https://example.test/lidessen/other.git")
        create_repo(same_repository, "git@example.test:lidessen/meowask.git")
        pool.mkdir()
        create_repo(discovered, "https://example.test/lidessen/discovered.git")
        create_repo(local_only, None)
        empty.mkdir()
        git(empty, "init")
        create_repo(credentialed, credentialed_remote)
        run(home, "init", "--workspace-root", str(pool))
        run(home, "register", str(survey), "--id", "repository:1304098496", "--alias", "survey")

        indexed_credentialed = json.loads(run(home, "resolve", "credentialed").stdout)
        assert indexed_credentialed["workspace"]["origin"] == credential_free_remote
        assert "user:secret" not in (home / "cache" / "workspaces.json").read_text(encoding="utf-8")
        registered_credentialed = run(
            home,
            "register",
            str(credentialed),
            "--id",
            "repository:credentialed",
            "--alias",
            "credentialed",
        )
        assert "user:secret" not in registered_credentialed.stdout
        assert "access_token" not in registered_credentialed.stdout
        credentialed_resolution = json.loads(run(home, "resolve", "credentialed").stdout)
        assert credentialed_resolution["project"]["repository"] == credential_free_remote
        assert credentialed_resolution["workspace"]["origin"] == credential_free_remote
        assert "user:secret" not in (home / "config" / "projects.json").read_text(encoding="utf-8")

        project_list = json.loads(run(home, "project", "list").stdout)
        assert project_list["complete"] is True
        assert [entry["project"]["id"] for entry in project_list["projects"]] == [
            "repository:1304098496",
            "repository:credentialed",
        ]
        assert all(entry["status"] == "available" for entry in project_list["projects"])
        serialized_project_list = json.dumps(project_list)
        assert "user:secret" not in serialized_project_list
        assert "access_token" not in serialized_project_list

        rebound = run(home, "register", str(other), "--id", "repository:1304098496", expect=2)
        assert "refusing to rebind stable project id" in rebound.stderr
        colliding_id = run(home, "register", str(other), "--id", "survey", expect=2)
        assert "project lookup key" in colliding_id.stderr
        case_colliding_id = run(home, "register", str(other), "--id", "SURVEY", expect=2)
        assert "project lookup key" in case_colliding_id.stderr
        still_survey = json.loads(run(home, "resolve", "survey").stdout)
        assert still_survey["workspace"]["path"] == str(survey.resolve())
        assert still_survey["workspace"]["origin"] == remote

        survey.rename(meowask)
        stale = run(home, "resolve", "survey", expect=2)
        assert "workspace path does not exist" in stale.stderr
        partial = json.loads(run(home, "project", "list", expect=2).stdout)
        assert partial["complete"] is False
        assert {entry["status"] for entry in partial["projects"]} == {"available", "unverified"}
        unverified = next(entry for entry in partial["projects"] if entry["status"] == "unverified")
        assert unverified["project"]["id"] == "repository:1304098496"
        assert "workspace path does not exist" in unverified["error"]

        wrong = run(home, "attach", "survey", str(other), expect=2)
        assert "refusing to attach a different repository" in wrong.stderr

        run(home, "attach", "survey", str(meowask))
        resolved = json.loads(run(home, "resolve", "survey").stdout)
        assert resolved["project"]["id"] == "repository:1304098496"
        assert resolved["project"]["aliases"] == ["meowask", "survey"]
        assert resolved["workspace"]["path"] == str(meowask.resolve())
        assert resolved["workspace"]["origin"] == remote
        assert resolved["workspace"]["dirty"] is False
        assert resolved["workspace"]["orientationFiles"] == ["README.md"]

        run(home, "attach", "survey", str(same_repository))
        protocol_migrated = json.loads(run(home, "resolve", "survey").stdout)
        assert protocol_migrated["workspace"]["path"] == str(same_repository.resolve())
        run(home, "attach", "survey", str(meowask))

        indexed = json.loads(run(home, "resolve", "discovered").stdout)
        assert indexed["registration"] == "discovered"
        assert indexed["project"]["id"] is None
        assert indexed["workspace"]["path"] == str(discovered.resolve())
        local = json.loads(run(home, "resolve", "local-only").stdout)
        assert local["registration"] == "discovered"
        assert local["project"]["repository"] is None
        assert local["workspace"]["origin"] is None
        unborn = json.loads(run(home, "resolve", "empty").stdout)
        assert unborn["workspace"]["head"] is None

        late_pool.mkdir()
        create_repo(late, "https://example.test/lidessen/late.git")
        run(home, "root", "add", str(late_pool))
        late_result = json.loads(run(home, "resolve", "late").stdout)
        assert late_result["workspace"]["path"] == str(late.resolve())
        overlapping = json.loads(run(home, "root", "add", str(discovered)).stdout)
        assert overlapping["indexedWorkspaces"] == 5
        (home / "cache" / "workspaces.json").unlink()
        rebuilt = json.loads(run(home, "scan").stdout)
        assert rebuilt["indexedWorkspaces"] == 5
        projects = json.loads((home / "config" / "projects.json").read_text(encoding="utf-8"))
        assert [project["id"] for project in projects["projects"]] == ["repository:1304098496", "repository:credentialed"]
        projects["projects"].append({
            "id": "REPOSITORY:1304098496",
            "repository": "https://example.test/lidessen/other.git",
            "aliases": ["duplicate-id"],
        })
        (home / "config" / "projects.json").write_text(json.dumps(projects), encoding="utf-8")
        duplicate_id = run(home, "resolve", "survey", expect=2)
        assert "duplicate project id" in duplicate_id.stderr

    print("atthis resolver tests passed")


if __name__ == "__main__":
    main()
