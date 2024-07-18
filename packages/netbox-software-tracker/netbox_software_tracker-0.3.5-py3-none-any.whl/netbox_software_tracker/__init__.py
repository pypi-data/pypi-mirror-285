from netbox.plugins import PluginConfig

from .version import __version__


class NetBoxSoftwareTrackerConfig(PluginConfig):
    name = "netbox_software_tracker"
    verbose_name = "NetBox Software Tracker"
    description = "Assign golden images to device types, and track the upgrade progress"
    version = __version__
    author = "Patrick Falk Nielsen"
    author_email = "panie@jysk.com"
    required_settings = []


config = NetBoxSoftwareTrackerConfig # noqa E305
