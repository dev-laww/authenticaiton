class Constants:
    """
    A class to hold constant values for whole application.
    """
    ROUTE_METADATA_ATTR = "__route_metadata__"
    VERSION_METADATA_ATTR = "__version_metadata__"

    SEMVER_REGEX = r"""
    ^v?                                  # optional 'v' prefix
    (?P<major>\d+)                       # major
    (?:\.(?P<minor>\d+))?                # optional minor
    (?:\.(?P<patch>\d+))?                # optional patch
    (?:-(?P<prerelease>[0-9A-Za-z.-]+))? # optional prerelease
    (?:\+(?P<build>[0-9A-Za-z.-]+))?     # optional build
    $
    """
