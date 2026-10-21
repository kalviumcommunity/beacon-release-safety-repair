import unittest
from app import health

class HealthTest(unittest.TestCase):
    def test_health(self):
        self.assertEqual(health(), {"status": "ok", "version": "2.3.1"})

if __name__ == "__main__":
    unittest.main()
