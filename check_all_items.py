import ast
from pathlib import Path

routes_file = Path('app/api/routes.py')
content = routes_file.read_text()

tree = ast.parse(content)

print(f"Total items in tree.body: {len(tree.body)}\n")

for i, item in enumerate(tree.body):
    print(f"{i+1}. {type(item).__name__}", end="")
    if hasattr(item, 'name'):
        print(f" - {item.name}", end="")
    if isinstance(item, ast.FunctionDef):
        print(f" [FUNCTION - {len(item.decorator_list)} decorators]", end="")
    print()
