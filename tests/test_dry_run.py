
import sys
import os
import unittest
from unittest.mock import MagicMock

# Path Setup
sys.path.append(os.path.abspath("src"))

class TestEternalWeb(unittest.TestCase):
    def test_imports(self):
        """Test if modules can be imported without error."""
        try:
            import eternalweb.gui.app
            import eternalweb.engine.engine
            print("✔ Module imports successful")
        except ImportError as e:
            self.fail(f"Import failed: {e}")

    def test_engine_init(self):
        """Test engine initialization logic."""
        from eternalweb.engine.engine import init_engine
        try:
            init_engine()
            print("✔ Engine initialized")
        except Exception as e:
            self.fail(f"Engine init failed: {e}")

    def test_archiver_logic(self):
        """Test archiver dispatch logic."""
        from eternalweb.engine.engine import Archiver
        archiver = Archiver()
        
        # Capture stdout to verify print outputs
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        url = "https://example.com"
        options = ["SingleFile", "WACZ"]
        archiver.archive_url(url, options)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        self.assertIn(f"엔진 디스패치: {url}", output)
        self.assertIn("SingleFile", output)
        self.assertIn("WACZ", output)
        print("✔ Archiver logic verification passed")

if __name__ == "__main__":
    unittest.main()
