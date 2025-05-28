"""
Debug utilities for VSCode integration
"""

def enable_debugging():
    """Enable remote debugging for VSCode"""
    try:
        # Try to import debugpy for remote debugging
        import debugpy
        
        # Check if debugger is already attached
        if not debugpy.is_client_connected():
            # Configure debugger
            debugpy.configure(subProcess=False)
            debugpy.listen(("localhost", 5678))
            print("🐛 Debugger listening on localhost:5678")
            print("   Attach VSCode debugger to connect")
            
            # Uncomment the next line if you want to wait for debugger to attach
            # debugpy.wait_for_client()
            
    except ImportError:
        print("⚠️  debugpy not installed. Install with: pip install debugpy")
    except Exception as e:
        print(f"⚠️  Could not start debugger: {e}")