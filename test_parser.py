"""
Quick test to verify endpoint detection works
"""
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.parsers.python_parser import PythonParser

# Test on our own routes.py
routes_file = Path('app/api/routes.py')
if routes_file.exists():
    print(f"Testing parser on: {routes_file}")
    parser = PythonParser(routes_file)
    endpoints = parser.extract_endpoints()
    
    print(f"\n✅ Found {len(endpoints)} endpoints:\n")
    for i, endpoint in enumerate(endpoints, 1):
        print(f"{i}. {endpoint['method']} {endpoint['path']}")
        print(f"   Function: {endpoint['function_name']}")
        print(f"   Location: {endpoint.get('file_path', 'N/A')}, line {endpoint.get('line_number', 'N/A')}")
        print()
else:
    print(f"❌ File not found: {routes_file}")
