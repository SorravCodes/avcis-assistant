import unittest

import avcis


class ProjectBootstrapTests(unittest.TestCase):
    def test_package_version_is_available(self):
        self.assertEqual(avcis.__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()