"""The Options for Output Formatting.
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class FormatOptions:
    """
    Attributes:
    - full_path (bool): Whether to display the full path to the file.
    - no_file_ext (bool): Whether to filter file extensions (except move with different extensions).
    - file_name (bool): Whether to display the file name. Removes any parent directories.
    """
    full_path: bool = False
    no_file_ext: bool = False
    file_name: bool = False

    def format(self, path: str) -> str:
        """Format a Path String, applying the given options.

        Parameters:
        - path (str): The relative (project root) path string in Change Data.

        Returns:
        str - Formatted File Information.
        """
        if self.full_path:
            if self.no_file_ext:
                # Filter the File Ext
                return os.path.splitext(path)[0]
            # No Change Necessary
            return path
        if self.file_name:
            basename = os.path.basename(path)
            if self.no_file_ext:
                # Filter the File Ext
                return os.path.splitext(basename)[0]
            return basename
        # Remove the initial slash char
        path = path.lstrip('/')
        if self.no_file_ext:
            # Filter the File Ext
            return os.path.splitext(path)[0]    
        return path
