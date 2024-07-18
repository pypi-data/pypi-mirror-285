"""
Set up and runs the textual app for some FileTree.

It is not recommended to run any of the functions in this module.
Instead load a :class:`FileTree <file_tree.file_tree.FileTree>` and
then run :meth:`FileTree.run_app <file_tree.file_tree.FileTree.run_app>` and
"""
import itertools
from argparse import ArgumentParser
from functools import lru_cache

try:
    from rich.style import Style
    from rich.table import Table
    from rich.text import Text
    from rich.console import Group
    from textual.app import App, ComposeResult
    from textual.message import Message
    from textual.widgets import Header, Footer, Tree, Static
    from textual.widgets.tree import TreeNode
    from textual.containers import Horizontal
    from textual.binding import Binding
except ImportError:
    raise ImportError("Running the file-tree app requires rich and textual to be installed. Please install these using `pip/conda install textual`.")

from .file_tree import FileTree, Template


class TemplateSelect(Message, bubble=True):
    """Message sent when a template in the sidebar gets selected."""

    def __init__(self, sender, template: Template):
        """Create template selector."""
        self.template = template
        super().__init__(sender)


class TemplateTreeControl(Tree):
    """Sidebar containing all template definitions in FileTree."""
    current_node = None
    BINDINGS = [
        Binding("space", "toggle_node", "Collapse/Expand Node", show=True),
        Binding("up", "cursor_up", "Move Up", show=True),
        Binding("down", "cursor_down", "Move Down", show=True),
    ]

    def __init__(self, file_tree: FileTree, renderer, name: str = None):
        """
        Create a new template sidebar based on given FileTree.

        Args:
            tree: FileTree to interact with
            name: name of the sidebar within textual
        """
        self.file_tree = file_tree
        super().__init__("-", name=name)
        self.show_root = False
        self.find_children(self.root, self.file_tree.get_template(""))
        self.root.expand_all()
        self.renderer = renderer
        self.select_node(self.get_node_at_line(0))

    def on_mount(self, ):
        self.focus()

    def find_children(self, parent_node: TreeNode, template:Template):
        """
        Find all the children of a template and add them to the node.

        Calls itself recursively.
        """
        all_children = template.children(self.file_tree._templates.values())
        if len(all_children) == 0:
            parent_node.add_leaf(template.unique_part, template)
        else:
            this_node = parent_node.add(template.unique_part, template)
        children = set()
        for child in all_children:
            if child not in children:
                self.find_children(this_node, child)
                children.add(child)

    def render_label(self, node: TreeNode[Template], base_style, style):
        if node.data is None:
            return node.label
        label = _render_node_helper(self.file_tree, node).copy()
        if node is self.cursor_node:
            label.stylize("reverse")
        if not node.is_expanded and len(node.children) > 0:
            label = Text("📁 ") + label
        return label
    
    def on_tree_node_highlighted(self):
        if self.current_node is not self.cursor_node:
            self.current_node = self.cursor_node
            self.renderer.render_template(self.current_node.data)


@lru_cache(None)
def _render_node_helper(tree: FileTree, node: TreeNode[Template]):
    meta = {
        "@click": f"click_label({node.id})",
        "tree_node": node.id,
        #"cursor": node.is_cursor,
    }
    paths = tree.get_mult(
        _get_template_key(tree, node.data), filter=True
    ).data.flatten()
    existing = [p for p in paths if p != ""]
    color = "blue" if len(existing) == len(paths) else "yellow"
    if len(existing) == 0:
        color = "red"
    counter = f" [{color}][{len(existing)}/{len(paths)}][/{color}]"
    res = Text.from_markup(
        node.data.rich_line(tree._templates) + counter, overflow="ellipsis"
    )
    res.apply_meta(meta)
    return res


class FileTreeViewer(App):
    """FileTree viewer app."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    TITLE = "FileTree viewer"
    CSS_PATH = "css/app.css"

    def __init__(self, file_tree: FileTree):
        self.file_tree = file_tree.fill().update_glob(file_tree.template_keys(only_leaves=True))
        super().__init__()

    def compose(self) -> ComposeResult:
        renderer = TemplateRenderer(self.file_tree)
        yield Header()
        yield Horizontal(
            TemplateTreeControl(self.file_tree, renderer),
            renderer,
        )
        yield Footer()

    async def handle_template_select(self, message: TemplateSelect):
        """User has selected a template."""
        template = message.template
        self.app.sub_title = template.as_string
        await self.body.update(TemplateRenderer(template, self.file_tree))

    def action_toggle_dark(self):
        self.dark = not self.dark


def _get_template_key(tree, template):
    """Get key representing template with file-tree."""
    keys = {k for k, t in tree._templates.items() if t is template}
    return next(iter(keys))


class TemplateRenderer(Static):
    """
    Helper class to create a Rich rendering of a template.

    There are two parts:

        - a text file with the template
        - a table with the possible placeholder value combinations
          (shaded red for non-existing files)
    """

    def __init__(self, file_tree: FileTree):
        """Create new renderer for template."""
        self.file_tree = file_tree
        super().__init__()

    def on_mount(self):
        self.render_template(self.file_tree.get_template(""))

    def render_template(self, template: Template):
        """Render the template as rich text."""
        xr = self.file_tree.get_mult(
            _get_template_key(self.file_tree, template), filter=True
        )
        coords = sorted(xr.coords.keys())
        single_var_table = Table(*coords)
        for values in itertools.product(*[xr.coords[c].data for c in coords]):
            path = xr.sel(**{c: v for c, v in zip(coords, values)}).item()
            style = Style(bgcolor=None if path != "" else "red")
            single_var_table.add_row(*[str(v) for v in values], style=style)
        self.update(Group(
            template.as_string,
            single_var_table,
        ))


def run():
    """Start CLI interface to app."""
    parser = ArgumentParser(
        description="Interactive terminal-based interface with file-trees"
    )
    parser.add_argument("file_tree", help="Which file-tree to visualise")
    parser.add_argument("-d", "--directory", default=".", help="top-level directory")
    args = parser.parse_args()
    FileTree.read(args.file_tree, args.directory).run_app()
