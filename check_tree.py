import ast
from pathlib import Path

routes_file = Path('app/api/routes.py')
content = routes_file.read_text()

print(f"File length: {len(content)} chars")
print(f"Lines: {len(content.splitlines())}")
print()

try:
    tree = ast.parse(content)
    print(f"✅ Parse successful")
    print(f"Tree type: {type(tree)}")
    print(f"Tree body length: {len(tree.body)}")
    print()
    
    print("Top-level items:")
    for i, item in enumerate(tree.body[:10]):
        print(f"  {i+1}. {type(item).__name__}", end="")
        if hasattr(item, 'name'):
            print(f" - {item.name}", end="")
        print()
        
except Exception as e:
    print(f"❌ Parse failed: {e}")
