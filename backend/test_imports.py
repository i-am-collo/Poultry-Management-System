#!/usr/bin/env python
# Test imports
try:
    import app.main
    print("✓ Imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
