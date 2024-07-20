import unittest
import json
from ViteLicense.core import ViteLicense


class TestViteLicenseComputer(unittest.TestCase):

    def test(self):
        result = ViteLicense.computer()

        # Checking the type of returned result
        self.assertIsInstance(result, dict)

        # Checking if all necessary keys exist
        keys = ['uuid', 'system_uuid', 'name', 'public_ipaddress', 'hard_disk_serial', 'mainboard_serial', 'os_serial']
        for key in keys:
            self.assertIn(key, result)

        print(json.dumps(result, indent=4))


if __name__ == '__main__':
    unittest.main()
