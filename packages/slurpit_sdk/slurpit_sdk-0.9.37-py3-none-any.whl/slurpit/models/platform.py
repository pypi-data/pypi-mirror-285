from slurpit.models.basemodel import BaseModel

class Platform(BaseModel):
    """
    This class represent platform status.

    Args:
        status (str): The status of the platform, indicating its current operational state.
    """
    def __init__(self, status: str):
        self.status = status  # Store the platform's status
