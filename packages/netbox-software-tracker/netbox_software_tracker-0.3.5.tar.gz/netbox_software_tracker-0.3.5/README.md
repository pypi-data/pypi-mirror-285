# Netbox Software Tracker

[Netbox](https://github.com/netbox-community/netbox) plugin that adds the capability to track software and assign golden images to devices




## Compatibility

This plugin in compatible with [NetBox](https://netbox.readthedocs.org/) 4.0 and later.

## Installation

If Netbox was installed according to the standard installation instructions. It may be necessary to activate the virtual environment.

```
source /opt/netbox/venv/bin/activate
```

The plugin is available as a Python package in pypi and can be installed with pip

```
pip install netbox-software-tracker
```
Enable the plugin in /opt/netbox/netbox/netbox/configuration.py:
```
PLUGINS = ["netbox-software-tracker"]
```
Restart NetBox and add `netbox-software-tracker` to your local_requirements.txt



## Contributing
Developing tools for this project based on [ntc-netbox-plugin-onboarding](https://github.com/networktocode/ntc-netbox-plugin-onboarding) repo.

Issues and pull requests are welcomed.
