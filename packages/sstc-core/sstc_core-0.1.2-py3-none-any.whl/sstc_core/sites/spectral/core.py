import os
from typing import List, Optional, Union


class Data:
    """
    Represents the data associated with a platform.

    Attributes:
        raw (dict): Raw data.
        processed (dict): Processed data with levels L0, L1, L2, and L3.
        legacy (dict): Legacy data.
        metadata (dict): Metadata information.
    """
    def __init__(self, raw: Optional[dict] = None, processed: Optional[dict] = None, legacy: Optional[dict] = None, metadata: Optional[dict] = None):
        self.raw = raw or {}
        self.processed = processed or {'L0': {}, 'L1': {}, 'L2': {}, 'L3': {}}
        self.legacy = legacy or {}
        self.metadata = metadata or {}

class Platform:
    """
    Represents a generic platform.

    Attributes:
        name (str): The name of the platform.
        description (str): The description of the platform.
        data (Data): The data associated with the platform.
    """
    def __init__(self, name: str, description: str, data: Data):
        self.name = name
        self.description = description
        self.data = data

class Phenocam(Platform):
    """Represents a phenocam platform."""
    pass

class FixedSensor(Platform):
    """Represents a fixed sensor platform."""
    pass

class UAV(Platform):
    """Represents a UAV platform."""
    pass

class Satellite(Platform):
    """Represents a satellite platform."""
    pass

class Location:
    """
    Represents a location containing various platforms.

    Attributes:
        name (str): The name of the location.
        id (str): The ID of the location.
        platforms (List[Platform]): A list of platforms at the location.
    """
    def __init__(self, name: str, loc_id: str, platforms: List[Platform]):
        self.name = name
        self.id = loc_id
        self.platforms = platforms

    def get_platforms_by_type(self, platform_type: Union[Phenocam, FixedSensor, UAV, Satellite]) -> List[Platform]:
        """
        Retrieves platforms of a specific type.

        Args:
            platform_type (Union[Phenocam, FixedSensor, UAV, Satellite]): The type of platform to retrieve.

        Returns:
            List[Platform]: A list of platforms of the specified type.
        """
        return [platform for platform in self.platforms if isinstance(platform, platform_type)]

class Station:
    """
    Represents a station containing multiple locations.

    Attributes:
        name (str): The name of the station.
        abbreviation (str): The abbreviation of the station.
        locations (List[Location]): A list of locations at the station.
    """
    def __init__(self, name: str, abbreviation: str, locations: List[Location]):
        self.name = name
        self.abbreviation = abbreviation
        self.locations = locations

class StationManager:
    """
    Manages operations related to the Station class, such as checking for existing folder structures and creating new ones.

    Attributes:
        base_path (str): The base directory where station data is stored.
    """
    def __init__(self, base_path: str):
        self.base_path = base_path

    def station_exists(self, station_name: str) -> bool:
        """
        Checks if a folder structure exists for a given station name.

        Args:
            station_name (str): The name of the station.

        Returns:
            bool: True if the folder structure exists, False otherwise.
        """
        return os.path.exists(os.path.join(self.base_path, station_name))

    def create_station_folders(self, station: Station) -> None:
        """
        Creates a folder structure for a given Station object.

        Args:
            station (Station): The Station object for which to create the folder structure.
        """
        station_path = os.path.join(self.base_path, station.name)
        os.makedirs(station_path, exist_ok=True)
        
        for location in station.locations:
            location_path = os.path.join(station_path, location.name)
            os.makedirs(location_path, exist_ok=True)
            
            for platform in location.platforms:
                platform_path = os.path.join(location_path, platform.name)
                os.makedirs(platform_path, exist_ok=True)
                
                # Create subfolders for data categories
                os.makedirs(os.path.join(platform_path, 'Raw'), exist_ok=True)
                os.makedirs(os.path.join(platform_path, 'Processed/L0'), exist_ok=True)
                os.makedirs(os.path.join(platform_path, 'Processed/L1'), exist_ok=True)
                os.makedirs(os.path.join(platform_path, 'Processed/L2'), exist_ok=True)
                os.makedirs(os.path.join(platform_path, 'Processed/L3'), exist_ok=True)
                os.makedirs(os.path.join(platform_path, 'Legacy'), exist_ok=True)
                os.makedirs(os.path.join(platform_path, 'Metadata'), exist_ok=True)

