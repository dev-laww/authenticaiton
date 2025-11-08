class Constants:
    """
    A class to hold constant values for the whole application.
    """
    ROUTE_METADATA_ATTR = "__route_metadata__"
    VERSION_METADATA_ATTR = "__version_metadata__"

    SEMVER_REGEX = r"""
    v?                                  # optional 'v' prefix
    (?P<major>\d+)                      # major
    (?:\.(?P<minor>\d+))?               # optional minor
    (?:\.(?P<patch>\d+))?               # optional patch
    (?:-(?P<prerelease>[0-9A-Za-z.-]+))? # optional prerelease
    (?:\+(?P<build>[0-9A-Za-z.-]+))?    # optional build
    """

    # Compact version for embedding in other regexes (no VERBOSE whitespace)
    # Note: Build metadata is excluded when used in accept headers to avoid matching +json
    SEMVER_REGEX_COMPACT = (
        r"v?(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?"
        r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?(?:\+(?P<build>[0-9A-Za-z.-]+))?"
    )
    
    # Version pattern without build metadata for accept headers (to avoid matching +json)
    SEMVER_REGEX_ACCEPT_HEADER = (
        r"v?(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?"
        r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?"
    )

    ACCEPT_HEADER_VERSION_REGEX = (
        r"^application/vnd\.{vendor_prefix}\."
        r"(?P<version>v?(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?"
        r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?)(?:\+json)?$"
    )
