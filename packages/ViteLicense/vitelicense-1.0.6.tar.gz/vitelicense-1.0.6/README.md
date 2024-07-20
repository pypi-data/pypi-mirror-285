# vitelicense.io Python

The free Python module to help you validate devices with licenses on vitelicense.io

## Use Cases

- Get devices information
- Validate devices with licenses

## Features

- Dynamic vitelicense.io credentials
- Easy to validate your software licenses with a few lines of coding

## Requirements

- **Python**: 2.x or 3.x or higher

## Quick Start

If you prefer to install this package into your own Python project, please follow the installation steps below

## Installation

#### Require the current package using pip:

```bash
pip install vitelicense
```

## Testing

``` python
import json
from ViteLicense import ViteLicense

computer = ViteLicense.computer()
print('Computer: ', json.dumps(computer, indent=4))

hash = ViteLicense.hash(hash)
print('Computer Hash: ', hash)

response = ViteLicense.validate('api_key', 'license_serial')
print('Validate: ', json.dumps(response, indent=4))
```

## Contributing

Please see [CONTRIBUTING](CONTRIBUTING.md) for details.

### Security

If you discover any security related issues, please email contact@adminvitelicense.io or use the issue tracker.

## Credits

- [Vite., Ltd](https://github.com/vitegroupltd)
- [All Contributors](../../contributors)

## License

The MIT License (MIT). Please see [License File](LICENSE.md) for more information.
