"""Exceptions for EcoPanel."""


class EcoPanelError(Exception):
    """Generic EcoPanel exception."""


class EcoPanelEmptyResponseError(EcoPanelError):
    """ "EcoPanel API response is empty exception"""


class EcoPanelConnectionError(EcoPanelError):
    """EcoPanel connection exception."""


class EcoPanelConnectionTimeoutError(EcoPanelConnectionError):
    """EcoPanel connection timeout exception."""


class EcoPanelConnectionClosed(EcoPanelConnectionError):
    """EcoPanel connection closed."""


class DeviceDictError(EcoPanelError):
    """Generic Device dictionary exception."""


class DeviceDictObjectEmpty(DeviceDictError):
    """Device dictionary object is empty."""


class DeviceDictEmpty(DeviceDictError):
    """Device dictionary itself is empty."""
