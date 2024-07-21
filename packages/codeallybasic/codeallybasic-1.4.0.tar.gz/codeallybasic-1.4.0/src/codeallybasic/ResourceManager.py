
from logging import Logger
from logging import getLogger

from importlib.abc import Traversable

from importlib.resources import files


class ResourceManager:
    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    @classmethod
    def retrieveResourcePath(cls, bareFileName: str, resourcePath: str, packageName: str) -> str:
        """
        Assume we are in an app;  If not, then we are in development
        Args:
            bareFileName:  Simple filename
            resourcePath:  OS Path that matches the package name
            packageName:   The package from which to retrieve the resource

        Returns:  The fully qualified filename
        """
        try:
            from os import environ
            pathToResources: str = environ[f'{ResourceManager.RESOURCE_ENV_VAR}']
            fqFileName:      str = f'{pathToResources}/{resourcePath}/{bareFileName}'
        except KeyError:
            traversable: Traversable = files(packageName) / bareFileName
            fqFileName = str(traversable)

        return fqFileName
