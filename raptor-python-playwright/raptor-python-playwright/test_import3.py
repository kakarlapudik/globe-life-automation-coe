import sys

# Try importing dependencies first
try:
    from raptor.core.element_manager import ElementManager
    print("✓ ElementManager imported")
except Exception as e:
    print(f"✗ ElementManager import failed: {e}")

try:
    from raptor.core.config_manager import ConfigManager
    print("✓ ConfigManager imported")
except Exception as e:
    print(f"✗ ConfigManager import failed: {e}")

try:
    from raptor.core.exceptions import ElementNotFoundException
    print("✓ Exceptions imported")
except Exception as e:
    print(f"✗ Exceptions import failed: {e}")

# Now try the full file
print("\nTrying to execute table_manager.py...")
try:
    with open('raptor/pages/table_manager.py', 'r') as f:
        code = f.read()
    exec(compile(code, 'raptor/pages/table_manager.py', 'exec'))
    print("✓ File executed successfully")
except Exception as e:
    print(f"✗ Execution failed: {e}")
    import traceback
    traceback.print_exc()
