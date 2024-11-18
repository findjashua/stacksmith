import json
import re
import subprocess
import sys
from collections import deque
from typing import Callable, Optional


class SubprocessHelpers:
    @staticmethod
    def run_command(command: str) -> str:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        stdout, stderr = process.communicate()
        err = stderr.decode().strip()
        if process.returncode != 0 and err:
            print("\n".join(["ERROR:", err]))
            raise subprocess.CalledProcessError(process.returncode, command, err)
        return stdout.decode().strip()

    @staticmethod
    def run_git_command(args: list[str]) -> str:
        try:
            subprocess.run(["git"] + args, check=True, text=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)


class GitHelpers:
    @staticmethod
    def checkout_branch(branch_name: str) -> str:
        return SubprocessHelpers.run_command(f"git checkout {branch_name}")

    @staticmethod
    def create_branch(branch_name: str, parent_branch: str) -> str:
        return SubprocessHelpers.run_command(
            f'git checkout -b "{branch_name}" "{parent_branch}"'
        )

    @staticmethod
    def create_empty_commit(message: str) -> str:
        return SubprocessHelpers.run_command(f'git commit --allow-empty -m "{message}"')

    @staticmethod
    def create_pull_request(
        title: str, description: str, base_branch: Optional[str] = None
    ) -> str:
        base_branch_arg = f'--base "{base_branch}"' if base_branch is not None else ""
        return SubprocessHelpers.run_command(
            f'gh pr create {base_branch_arg} --title "{title}" --body "{description}" --draft'
        )

    @staticmethod
    def does_remote_branch_exist(branch: str) -> bool:
        try:
            SubprocessHelpers.run_command(
                f"git ls-remote --exit-code --heads origin {branch}"
            )
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def get_commit_message(commit_hash: str) -> str:
        return SubprocessHelpers.run_command(f"git log -1 --pretty=%B {commit_hash}")

    @staticmethod
    def get_commit_with_message(branch: str, message: str, max_count: int = 100) -> str:
        return SubprocessHelpers.run_command(
            f'git log {branch} --format=%H --max-count=1 --grep="{message}" -n {max_count}'
        )

    @staticmethod
    def get_current_branch() -> str:
        return SubprocessHelpers.run_command("git rev-parse --abbrev-ref HEAD")

    @staticmethod
    def get_local_branches() -> set[str]:
        return set(
            SubprocessHelpers.run_command(
                'git branch --format="%(refname:short)"'
            ).split("\n")
        )

    @staticmethod
    def get_pr_output(branch: str) -> str:
        return SubprocessHelpers.run_command(f"gh pr view {branch} --json url")

    @staticmethod
    def get_trunk_name() -> str:
        return SubprocessHelpers.run_command(
            'git remote show origin | sed -n "/HEAD branch/s/.*: //p"'
        )

    @staticmethod
    def push_and_set_upstream(branch: str, remote: str = "origin") -> str:
        return SubprocessHelpers.run_command(
            f"git push --set-upstream {remote} {branch}"
        )

    @staticmethod
    def push_with_lease(branch: str) -> str:
        return SubprocessHelpers.run_command(
            f"git push origin {branch} --force-with-lease"
        )

    @staticmethod
    def rebase_onto(base_branch: str, starting_commit: str, target_branch: str) -> str:
        return SubprocessHelpers.run_command(
            f"git rebase --onto {base_branch} {starting_commit}^ {target_branch}"
        )

    @staticmethod
    def update_commit_parent(commit_hash: str, new_parent: str) -> str:
        new_parent = new_parent.replace("/", r"\/")
        return SubprocessHelpers.run_command(
            f"git filter-branch -f --msg-filter 'sed -E \"s/(Branch .* extends ).*/\\1{new_parent}/\"' -- {commit_hash}^..HEAD"
        )


class TreeHelpers:
    @staticmethod
    def bfs_traversal(
        root: str,
        children_dict: dict[str, list[str]],
        process_node_and_children: Callable[[str, list[str]], None],
    ) -> None:
        queue = deque([root])
        while queue:
            current_node = queue.popleft()
            children = children_dict.get(current_node, [])
            process_node_and_children(current_node, children)
            queue.extend(children)


class InternalHelpers:
    @staticmethod
    def get_creation_commit(
        branch_name: str, max_search_depth: int = 100
    ) -> Optional[str]:
        grep_pattern = f"Branch {branch_name} extends"
        creation_commit = GitHelpers.get_commit_with_message(
            branch_name, grep_pattern, max_search_depth
        )
        return creation_commit.strip() if creation_commit else None

    @staticmethod
    def get_parent_branch(child_branch: str) -> Optional[str]:
        creation_commit = InternalHelpers.get_creation_commit(child_branch)
        if not creation_commit:
            return None

        commit_message = GitHelpers.get_commit_message(creation_commit)
        parent_match = re.search(r"Branch .* extends (.*)", commit_message)
        return parent_match.group(1) if parent_match else None

    @staticmethod
    def get_children_dict() -> dict[str, list[str]]:
        local_branches = GitHelpers.get_local_branches()
        children_dict: dict[str, list[str]] = {branch: [] for branch in local_branches}

        for local_branch in local_branches:
            parent_branch = InternalHelpers.get_parent_branch(local_branch)
            if parent_branch and parent_branch in local_branches:
                children_dict[parent_branch].append(local_branch)

        return children_dict

    @staticmethod
    def push_branch(branch: str) -> None:
        if GitHelpers.does_remote_branch_exist(branch):
            GitHelpers.push_with_lease(branch)
            print(f"Pushed updates to {branch}")
        else:
            GitHelpers.push_and_set_upstream(branch)
            print(f"Pushed new branch {branch} to remote")

    @staticmethod
    def recursive_rebase(root_branch: Optional[str] = None) -> None:
        current_branch, children_dict = (
            GitHelpers.get_current_branch(),
            InternalHelpers.get_children_dict(),
        )

        if root_branch:  # hoist
            children_dict[root_branch] = [current_branch]
        else:  # propagate
            root_branch = current_branch

        def rebase(branch: str, children: list[str]) -> None:
            for child_branch in children:
                creation_commit = InternalHelpers.get_creation_commit(
                    branch_name=child_branch
                )
                if not creation_commit:
                    raise Exception(
                        f"Creation commit not found for branch {child_branch}"
                    )
                GitHelpers.rebase_onto(branch, creation_commit, child_branch)
                print(f"Rebased {child_branch} onto {branch}")
                if (
                    child_branch == current_branch
                    and root_branch != InternalHelpers.get_parent_branch(child_branch)
                ):
                    print(f"Updating parent of {current_branch} to {root_branch}")
                    GitHelpers.update_commit_parent(
                        InternalHelpers.get_creation_commit(current_branch), root_branch
                    )

        TreeHelpers.bfs_traversal(root_branch, children_dict, rebase)
        GitHelpers.checkout_branch(current_branch)


class API:
    @staticmethod
    def create_branch(branch_name: str) -> None:
        parent_branch = GitHelpers.get_current_branch()
        GitHelpers.create_branch(branch_name, parent_branch)
        commit_message = f"Branch {branch_name} extends {parent_branch}"
        GitHelpers.create_empty_commit(commit_message)
        print(f"Created new branch {branch_name}")

    @staticmethod
    def publish_stack() -> None:
        def push_branch(branch: str, _: list[str]) -> None:
            InternalHelpers.push_branch(branch)

        TreeHelpers.bfs_traversal(
            GitHelpers.get_current_branch(),
            InternalHelpers.get_children_dict(),
            push_branch,
        )

    @staticmethod
    def create_pr(title: Optional[str] = None) -> None:
        current_branch = GitHelpers.get_current_branch()

        InternalHelpers.push_branch(current_branch)

        parent_branch = InternalHelpers.get_parent_branch(current_branch)
        base_branch = parent_branch.removeprefix("origin/") if parent_branch else None
        description = ""

        if base_branch and base_branch != GitHelpers.get_trunk_name():
            try:
                parent_pr_output = GitHelpers.get_pr_output(base_branch)
                parent_pr_url = json.loads(parent_pr_output)["url"]
                description = f"Depends on: {parent_pr_url}"
            except subprocess.CalledProcessError:
                return print(f"Please create pull request for branch: {base_branch}")

        title = title or f"Pull request for {current_branch}"
        output = GitHelpers.create_pull_request(title, description, base_branch)
        print(f"Successfully created draft PR: {output}")

    @staticmethod
    def hoist_stack(base_branch: str) -> None:
        InternalHelpers.recursive_rebase(base_branch)
        print(f"Hoisted stack onto {base_branch} successfully")

    @staticmethod
    def propagate_changes() -> None:
        InternalHelpers.recursive_rebase()
        print("Propagated changes successfully")

    @staticmethod
    def print_parent() -> None:
        print(InternalHelpers.get_parent_branch(GitHelpers.get_current_branch()) or "")

    @staticmethod
    def print_children() -> None:
        children_branches = InternalHelpers.get_children_dict().get(
            GitHelpers.get_current_branch(), []
        )
        print("\n".join(children_branches))
