import json
import subprocess
from typing import Optional

from .helpers import GitHelpers, InternalHelpers, TreeHelpers


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
    def checkout_parent() -> None:
        parent_branch_opt = InternalHelpers.get_parent_branch(
            GitHelpers.get_current_branch()
        )
        if parent_branch_opt:
            GitHelpers.checkout_branch(parent_branch_opt)
        else:
            print("Parent branch not found")

    @staticmethod
    def checkout_child() -> None:
        children_branches = InternalHelpers.get_children_dict().get(
            GitHelpers.get_current_branch(), []
        )
        if not children_branches:
            print("Child branch not found")
        elif len(children_branches) == 1:
            GitHelpers.checkout_branch(children_branches[0])
        else:
            print("\n".join(children_branches))