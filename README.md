# StackSmith: effortless Git branch stacking

StackSmith supercharges your Git workflow with powerful stacked branch management. Inspired by Facebook's Phabricator, it offers 5 core commands to create, update, and maintain interdependent branches effortlessly.

## Quickstart

Install StackSmith:

```bash
pip install stacksmith
```

## Five core commands

StackSmith uses `ss` as its base command:

1. **Create a branch**
   ```
   ss create <branch_name>
   ```
   Push a new branch onto the stack, with an empty commit used for tracking branch lineage. Do not delete or modify this commit.

2. **Publish changes**
   ```
   ss publish
   ```
   Push all branches in the stack to remote.

3. **Create a pull request**
   ```
   ss pr [title]
   ```
   Create a pull request with the parent branch as base, and a link to the PR of the parent branch.

4. **Propagate changes**
   ```
   ss propagate
   ```
   After addressing PR comments, propagate changes from current branch up the stack, maintaining consistency.

5. **Hoist a stack on top of another branch**
   ```
   ss hoist <base_branch>
   ```
   After merging the base branch of the stack, hoist the remaining stack onto the trunk, side-stepping conflicts caused by squash-and-merge
   
   Please note that after merging, you have to checkout the new base of the stack (child of the merged branch) and fetch origin before hoisting, like so:
   ```
   ss checkout <new_base> 
   ss fetch origin && ss hoist origin/<trunk_name>
   ```

## Bonus commands
1. **Print name of parent branch**
   ```
   ss parent
   ```

2. **Print names of children branches**
   ```
   ss children
   ```

## Git command passthrough

StackSmith supports Git command passthrough. Any Git command not recognized as a StackSmith command will be passed directly to Git. For example:

```bash
ss add --all
ss commit -m "Your commit message"
ss push origin your-branch
```

This allows you to use StackSmith seamlessly alongside your regular Git workflow.

## Why StackSmith?

- **Stacked Workflow**: Optimized for managing interdependent feature branches.
- **Effortless Updates**: Easily keep your entire branch stack up-to-date with the trunk.
- **Consistent History**: Maintain a clean, linear history across your stacked branches.
- **Simplified Collaboration**: Streamline code reviews with well-organized, incremental changes.
- **Conflict Avoidance**: Smartly side-steps conflicts arising from squash-and-merge operations.
- **Intelligent PRs**: Automatically sets correct PR base and maintains PR relationships.
- **Idempotent Operations**: All commands are idempotent, allowing for easy recovery from errors.

## Perfect for

- Feature decomposition and incremental development
- Managing long-running feature branches
- Collaborative development on complex features
- Maintaining a clean, reviewable commit history
- Teams using squash-and-merge for pull requests

## Key Concepts

### Side-stepping squash-and-merge conflicts

When using a squash-and-merge strategy for pull requests, conflicts typically arise in stacked branches. StackSmith's `hoist` command cleverly side-steps these conflicts, allowing your stacked branches to update smoothly without manual conflict resolution.

### Intelligent pull requests

StackSmith's `pr` command automatically sets the parent branch as the base for your pull request. It also adds a link to the parent PR in the description, maintaining the relationship between stacked branches in your PR chain.

### Idempotent operations

All StackSmith operations are designed to be idempotent. This means that in case of an error due to any issue (merge conflict, internet issue, etc.), you can simply resolve the issue and rerun the command. StackSmith will pick up where it left off, ensuring a smooth workflow even in the face of unexpected problems.

## Requirements

- Python 3.9+
- Git
- GitHub CLI (for pull requests)

## License

StackSmith is open source software licensed under the MIT License. See the LICENSE file for more details.

This project is not affiliated with or endorsed by GitHub or any Git project. Git is a trademark of Software Freedom Conservancy.