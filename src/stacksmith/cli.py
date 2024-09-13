import sys
from .core import API, SubprocessHelpers

def print_usage():
    print("Usage: ss <command> [<args>]")
    print("\nCustom commands:")
    print("  anchor <branch_name>                  Anchor the stack onto a new branch")
    print("  create <branch_name>                  Push a new branch onto the stack")
    print("  pr [title]                            Create a pull request with automatic parent branch detection")
    print("  propagate                             Propagate commits from the current branch to all descendant branches")
    print("  publish                               Push all branches in the stack to remote")
    print("\nAll other commands are passed through to git.")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "anchor":
        if len(args) < 1:
            print("Error: Base branch is required for 'anchor' command.")
            sys.exit(1)
        API.anchor_stack(args[0])
    elif command == "create":
        if len(args) < 1:
            print("Error: Branch name is required for 'create' command.")
            sys.exit(1)
        API.create_branch(args[0])
    elif command == "pr":
        API.create_pr(args[0] if args else None)
    elif command == "propagate":
        API.propagate_changes()
    elif command == "publish":
        API.publish_stack()
    elif command in ["--help", "-h", "help"]:
        print_usage()
    else:
        # Passthrough to Git for unknown commands
        SubprocessHelpers.run_git_command([command] + args)

if __name__ == "__main__":
    main()