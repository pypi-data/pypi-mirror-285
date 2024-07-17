from slurpit.models.basemodel import BaseModel

class Device(BaseModel):
    """
    This class represents a network device with various attributes.

    Args:
        id (int): Unique identifier for the device.
        hostname (str): Hostname of the device.
        fqdn (str): Fully qualified domain name of the device.
        device_os (str): Operating system running on the device.
        disabled (int): Indicates whether the device is disabled (0 or 1).
        device_type (str, optional): Type of the device, such as 'router' or 'switch'.
        brand (str, optional): Brand of the device, e.g., 'Cisco'.
        added (str, optional): Date when the device was added to the system.
        last_seen (str, optional): Last date when the device was active or seen.
        createddate (str, optional): The date the device record was created.
        changeddate (str, optional): The date the device record was last modified.
        port (int, optional): Network port number primarily used by the device.
        ipv4 (str, optional): IPv4 address assigned to the device.
    """
        
    def __init__(
        self,
        id: int,
        hostname: str,
        fqdn: str,
        device_os: str,
        disabled: int,
        device_type: str = None,
        brand: str = None,
        added: str = None,
        last_seen: str = None,
        port: int = None,
        ipv4: str = None,
        createddate: str = None,
        changeddate: str = None,
    ):
        self.id = int(id)
        self.hostname = hostname
        self.fqdn = fqdn
        self.port = int(port) if port is not None else None
        self.ipv4 = ipv4
        self.device_os = device_os
        self.device_type = device_type
        self.brand = brand
        self.disabled = int(disabled)
        self.added = added
        self.last_seen = last_seen
        self.createddate = createddate
        self.changeddate = changeddate

class Vendor(BaseModel):
    """
    This class represents a vendor, defined primarily by the operating system and brand.

    Args:
        device_os (str): Operating system commonly associated with the vendor.
        brand (str): Brand name of the vendor, e.g., 'Apple' or 'Samsung'.
    """
    def __init__(
        self,
        device_os: str,
        brand: str
    ):
       
        self.device_os = device_os
        self.brand = brand
