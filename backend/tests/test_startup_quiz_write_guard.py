"""Exercise server startup registration without importing the database-backed app."""
import ast
import copy
from pathlib import Path


def test_deploy_does_not_register_quiz_cleanup_or_seeding():
    source = Path(__file__).resolve().parents[1] / 'server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    blocked = {
        'startup_strip_bad_screenshot_images',
        'startup_purge_private_images',
        'startup_seed_master_quiz_catalog',
    }
    definitions = []
    for node in tree.body:
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        startup = any(isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                      and d.func.attr == 'on_event' and d.args
                      and isinstance(d.args[0], ast.Constant) and d.args[0].value == 'startup'
                      for d in node.decorator_list)
        if startup or node.name in blocked:
            definition = copy.deepcopy(node)
            definition.body = [ast.Pass()]
            definitions.append(definition)
    registered = []

    class App:
        def on_event(self, event):
            def register(function):
                registered.append((event, function.__name__))
                return function
            return register

    module = ast.fix_missing_locations(ast.Module(body=definitions, type_ignores=[]))
    exec(compile(module, str(source), 'exec'), {'app': App()})
    names = {name for event, name in registered if event == 'startup'}
    assert not names.intersection(blocked)
    assert {'load_quiz_glossary_cache', 'ensure_indexes'} <= names
    assert blocked <= {node.name for node in definitions}
