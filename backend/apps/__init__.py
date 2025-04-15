"""AgentSphere applications package.

This package contains all the custom applications for the AgentSphere project.
It provides version information and serves as the root package for all app modules.
"""

# -----------------------------------------
# Version information
# -----------------------------------------

# Version string in semver format
__version__: str = "0.1.0"

# Version information as a tuple for programmatic access
__version_info__: tuple[int | str, ...] = tuple(
    int(num) if num.isdigit() else num for num in __version__.replace("-", ".", 1).split(".")
)
