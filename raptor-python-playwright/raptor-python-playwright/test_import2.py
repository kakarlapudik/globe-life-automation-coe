import sys
import importlib.util

# Load the module directly
spec = importlib.util.spec_from_file_location(
    "table_manager",
    "raptor/pages/table_manager.py"
)
module = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(module)
    print("Module loaded successfully!")
    print(f"Module attributes: {dir(module)}")
    if hasattr(module, 'TableManager'):
        print("TableManager class found!")
    else:
        print("TableManager class NOT found!")
except Exception as e:
    print(f"Error loading module: {e}")
    import traceback
    traceback.print_exc()
