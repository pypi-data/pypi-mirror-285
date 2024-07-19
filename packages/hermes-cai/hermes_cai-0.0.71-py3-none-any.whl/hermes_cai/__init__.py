import os
import sys

# Dynamically add the package directory to sys.path
package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if package_path not in sys.path:
    sys.path.insert(0, package_path)
