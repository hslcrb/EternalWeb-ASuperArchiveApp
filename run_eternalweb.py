import sys
import os
from PySide6.QtWidgets import QApplication

# Add 'src' to path so we can import eternalweb
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from eternalweb.gui.app import main

if __name__ == "__main__":
    main()
