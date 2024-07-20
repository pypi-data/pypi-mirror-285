import unittest
from ViteLicense.core import ViteLicense


class TestViteLicenseValidate(unittest.TestCase):
    def test(self):
        result = ViteLicense.validate('api_key', 'license_serial')

        # Checking the type of returned result
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()
