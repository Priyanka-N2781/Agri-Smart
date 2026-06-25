#!/usr/bin/env python
"""Quick test to verify the app can be created"""

try:
    from agri_smart.web_app import create_app
    app = create_app()
    print("✓ App created successfully!")
    print("✓ Flask app is ready to run")
    print(f"✓ Template folder: {app.template_folder}")
    print(f"✓ Static folder: {app.static_folder}")
    print("\nThe project appears to be in a RUNNABLE state.")
    print("To run the app, execute: python app.py")
except Exception as e:
    print(f"✗ Error creating app: {e}")
    import traceback
    traceback.print_exc()
