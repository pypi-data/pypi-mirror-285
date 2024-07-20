import platform
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import requests
try:
    try:
        from subprocess import DEVNULL, CREATE_NO_WINDOW
    except ImportError:
        DEVNULL = os.open(os.devnull, os.O_RDWR)
        CREATE_NO_WINDOW = 0x08000000
except:
    DEVNULL = ''
    CREATE_NO_WINDOW = 0x08000000


def cmd(command: str):
    global DEVNULL, CREATE_NO_WINDOW
    if sys.platform == 'win32':
        return str(subprocess.check_output(command, shell=True, creationflags=CREATE_NO_WINDOW).decode().strip())
    return str(subprocess.check_output(command, shell=True).decode().strip())


class ViteLicense:
    def __init__(self):
        super().__init__(ViteLicense)

    @staticmethod
    def hash(data: dict):
        return str(hashlib.md5(hashlib.md5(base64.b64encode(json.dumps(data).encode('utf-8'))).hexdigest().encode('utf-8')).hexdigest()).upper()

    @staticmethod
    def computer():
        platforms = {
            'linux1': 'linux',
            'linux2': 'linux',
            'darwin': 'mac',
            'win32': 'win'
        }
        computer_platform = platforms[sys.platform]

        try:
            computer_name = str(re.sub("[^A-Za-z0-9]", "", str(platform.node()).replace(',', '').replace('-', '').replace('.', '')))
        except:
            computer_name = ''

        try:
            computer_public_ipaddress = requests.get('https://api.ipify.org').text
        except:
            computer_public_ipaddress = ''

        try:
            if computer_platform == 'win':
                computer_uuid = str(cmd('wmic csproduct get UUID')).replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
            elif computer_platform == 'mac':
                computer_uuid = str(cmd("ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'")).replace('.', '').replace('_', '').replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
            else:
                computer_uuid = str(cmd('cat /sys/class/dmi/id/product_uuid')).replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
        except Exception as e:
            print(e)
            computer_uuid = ''

        try:
            if computer_platform == 'win':
                computer_system_uuid = str(cmd('wmic path win32_computersystemproduct get uuid')).replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
            elif computer_platform == 'mac':
                computer_system_uuid = str(cmd('sysctl -a | grep kern.uuid')).replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1].split(': ')[-1]
            else:
                computer_system_uuid = str(cmd('wmic path win32_computersystemproduct get uuid')).replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
        except:
            computer_system_uuid = ''

        try:
            if computer_platform == 'win':
                computer_hard_disk_serial = str(cmd("wmic path win32_diskdrive where mediatype='Fixed hard disk media' get serialnumber")).replace('.', '').replace('_', '').replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
                if computer_hard_disk_serial == '':
                    computer_hard_disk_serial = str(cmd("wmic path win32_diskdrive where mediatype='External hard disk media' get serialnumber")).replace('.', '').replace('_', '').replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
            elif computer_platform == 'mac':
                computer_hard_disk_serial = str(cmd("ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformSerialNumber/{print $(NF-1)}'")).replace('.', '').replace('_', '').replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
            else:
                tmp = str(cmd('lsblk -o SERIAL')).replace('.', '').replace('_', '').replace('\r', '\n').replace('\n\n', '\n').split('\n')
                computer_hard_disk_serial = list(filter(None, tmp))[0]
        except:
            computer_hard_disk_serial = ''

        try:
            if computer_platform == 'win':
                computer_os_serial = str(cmd('wmic path win32_operatingsystem get serialnumber')).replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
            elif computer_platform == 'mac':
                computer_os_serial = str(cmd('system_profiler SPHardwareDataType | grep "Provisioning UDID"')).replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1].split(': ')[-1]
            else:
                computer_os_serial = str(cmd('cat /etc/machine-id')).replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
        except:
            computer_os_serial = ''
            
        try:
            if computer_platform == 'win':
                computer_mainboard_serial = str(cmd('wmic path win32_baseboard get SerialNumber')).replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
            elif computer_platform == 'mac':
                computer_mainboard_serial = str(cmd('system_profiler SPHardwareDataType | grep "Hardware UUID"')).replace('\r','\n').replace('\n\n', '\n').split('\n')[-1].split(': ')[-1]
            else:
                computer_mainboard_serial = str(cmd('cat /sys/class/dmi/id/board_serial')).replace('\r', '\n').replace('\n\n', '\n').split('\n')[-1]
        except:
            computer_mainboard_serial = ''

        computer = {
            'name': computer_name,
            'uuid': computer_uuid,
            'system_uuid': computer_system_uuid,
            'public_ipaddress': computer_public_ipaddress,
            'hard_disk_serial': computer_hard_disk_serial,
            'mainboard_serial': computer_mainboard_serial,
            'os_serial': computer_os_serial
        }

        return computer

    @staticmethod
    def validate(api_key: str, license: str):
        response = requests.post(
            headers={'user-agent': 'ViteLicense (+https://vitelicense.io)', 'x-api-key': api_key},
            url='https://vitelicense.io/api/licenses/verify',
            json={
                'api_key': api_key,
                'serial': license,
                'hash': ViteLicense.hash(ViteLicense.computer())
            },
            verify=True
        )

        return response.json()