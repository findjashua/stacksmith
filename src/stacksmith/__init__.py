from .core import API
from .cli import main

__all__ = ['create_branch', 'anchor_stack', 'create_pr', 'propagate_changes', 'publish_stack', 'main']

# Expose API methods at the package level
create_branch = API.create_branch
anchor_stack = API.anchor_stack
create_pr = API.create_pr
propagate_changes = API.propagate_changes
publish_stack = API.publish_stack