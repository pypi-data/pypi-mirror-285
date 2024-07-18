"""Data describing a File Change.
"""
from dataclasses import dataclass

from changelist_foci.format_options import FormatOptions


@dataclass(frozen=True)
class ChangeData:
    """The Change Information that is associated with a single file.

    Properties:
    - before_path (str | None): The initial path of the file.
    - before_dir (bool | None): Whether the initial file is a directory.
    - after_path (str | None): The final path of the file.
    - after_dir (bool | None): Whether the final path is a directory.
    """
    before_path: str | None = None
    before_dir: bool | None = None
    after_path: str | None = None
    after_dir: bool | None = None

    def get_subject(
        self,
        format_options: FormatOptions = FormatOptions()
    ) -> str:
        """
        Obtain the FOCI Subject, categorizing the change and applying Format Options.
        
        Parameters:
        - format_options (FormatOptions): A dataclass collection of format flags.

        Returns:
        str - The Subject Line for this Change Data.
        """
        if self.before_path is None:
            if self.after_path is None:
                return ''
            # Only the After Path exists
            return f"Create {format_options.format(self.after_path)}"
        # Process and Format the Before Path
        name_before = format_options.format(self.before_path)
        # Check for the After Path
        if self.after_path is None:
            return f"Remove {name_before}"
        # Compare Both Full Paths
        if self.before_path == self.after_path:
            return f"Update {name_before}"
        # Different Before and After Paths
        name_after = format_options.format(self.after_path)
        return f"Move {name_before} to {name_after}"
