"""
Debug endpoint detection
"""
from pathlib import Path
import ast
import sys

sys.path.insert(0, str(Path(__file__).parent))

# Test on routes.py
routes_file = Path('app/api/routes.py')
content = routes_file.read_text()

tree = ast.parse(content)

print("=== Testing iter_child_nodes ===\n")

func_count = 0

def visit(node, level=0):
    global func_count
    indent = "  " * level
    
    if isinstance(node, ast.FunctionDef):
        func_count += 1
        print(f"{indent}✅ Function: {node.name} (line {node.lineno})")
        print(f"{indent}   Decorators: {len(node.decorator_list)}")
        
        for i, dec in enumerate(node.decorator_list, 1):
            print(f"{indent}   Decorator #{i}: {ast.dump(dec)[:100]}...")
    
    for child in ast.iter_child_nodes(node):
        visit(child, level + 1)

visit(tree)

print(f"\n✅ Total functions found: {func_count}")


