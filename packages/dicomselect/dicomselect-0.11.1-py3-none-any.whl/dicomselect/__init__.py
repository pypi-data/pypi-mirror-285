from dicomselect.__version__ import __version__
from dicomselect.convert import CustomPostprocessFunction
from dicomselect.database import CustomHeaderFunction, Database
from dicomselect.reader import DICOMImageReader

version = __version__
DatabasePreferMode = Database.PreferMode
ReaderPreferMode = DICOMImageReader.PreferMode

__all__ = [
    "Database",
    "CustomHeaderFunction",
    "DatabasePreferMode",
    "ReaderPreferMode",
    "CustomPostprocessFunction",
    "__version__",
]
