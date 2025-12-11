import sys
import traceback

try:
    from raptor.pages.table_manager import TableManager
    print("TableManager imported successfully!")
    print(f"TableManager class: {TableManager}")
except Exception as e:
    print(f"Error importing TableManager: {e}")
    traceback.print_exc()
