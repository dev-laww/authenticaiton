import re
from typing import List, Optional, Set, Union

from semver import Version

from ...base import AppObject
from ...constants import Constants


def parse_version(version: str) -> Version:
    semver_regex = re.compile(Constants.SEMVER_REGEX, re.VERBOSE)

    match = semver_regex.match(version)
    if not match:
        raise ValueError(f"Invalid version string: {version}")

    major = match.group("major")
    minor = match.group("minor") or "0"
    patch = match.group("patch") or "0"
    prerelease = match.group("prerelease")
    build = match.group("build")

    normalized = f"{major}.{minor}.{patch}"
    if prerelease:
        normalized += f"-{prerelease}"
    if build:
        normalized += f"+{build}"

    return Version.parse(normalized)


class VersionRegistry(AppObject):
    """
    Singleton registry for managing application versions using semver.
    """

    _instance: Optional["VersionRegistry"] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of VersionRegistry exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the version registry."""
        if not self._initialized:
            self._versions: Set[Version] = set()
            self._default_version: Optional[Version] = None
            self._deprecated_versions: Set[Version] = set()
            self._initialized = True

    def add_version(
        self, version: Union[str, Version], set_default: bool = False
    ) -> bool:
        """
        Register a new version.

        Args:
            version: Version string (e.g., '1.0.0') or Version object
            set_default: Whether to set this as the default version

        Returns:
            True if version was added, False if it already exists
        """
        ver_obj = parse_version(version) if isinstance(version, str) else version

        if ver_obj in self._versions:
            return False

        self._versions.add(ver_obj)

        if set_default or self._default_version is None:
            self._default_version = ver_obj

        return True

    def remove_version(self, version: Union[str, Version]) -> bool:
        """Remove a version from the registry."""
        ver_obj = parse_version(version) if isinstance(version, str) else version

        if ver_obj not in self._versions:
            return False

        self._versions.discard(ver_obj)
        self._deprecated_versions.discard(ver_obj)

        if self._default_version == ver_obj:
            self._default_version = None

        return True

    def has_version(self, version: Union[str, Version]) -> bool:
        """Check if a version exists in the registry."""
        ver_obj = parse_version(version) if isinstance(version, str) else version
        return ver_obj in self._versions

    def is_valid(self, version: Union[str, Version]) -> bool:
        """Check if a version is registered and not deprecated."""
        ver_obj = parse_version(version) if isinstance(version, str) else version
        return ver_obj in self._versions and ver_obj not in self._deprecated_versions

    def get_versions(self, include_deprecated: bool = False) -> List[Version]:
        """Get all registered versions."""
        if include_deprecated:
            return sorted(self._versions)
        return sorted([v for v in self._versions if v not in self._deprecated_versions])

    @property
    def default_version(self) -> Optional[Version]:
        """Get or set the default version."""
        return self._default_version

    @default_version.setter
    def default_version(self, version: Union[str, Version]) -> None:
        """Set the default version."""
        ver_obj = parse_version(version) if isinstance(version, str) else version
        if ver_obj in self._versions:
            self._default_version = ver_obj
        else:
            raise ValueError(f"Version {ver_obj} not found in registry")

    @property
    def latest_version(self) -> Optional[Version]:
        """Get the latest (highest) version."""
        versions = self.get_versions(include_deprecated=False)
        return max(versions) if versions else None

    @property
    def latest_stable_version(self) -> Optional[Version]:
        """Get the latest stable version (no prerelease)."""
        versions = [v for v in self.get_versions() if not v.prerelease]
        return max(versions) if versions else None

    def deprecate_version(self, version: Union[str, Version]) -> bool:
        """Mark a version as deprecated."""
        ver_obj = parse_version(version) if isinstance(version, str) else version

        if ver_obj not in self._versions:
            return False

        self._deprecated_versions.add(ver_obj)
        return True

    def undeprecate_version(self, version: Union[str, Version]) -> bool:
        """Remove deprecation status from a version."""
        ver_obj = parse_version(version) if isinstance(version, str) else version

        if ver_obj not in self._versions:
            return False

        self._deprecated_versions.discard(ver_obj)
        return True

    def is_deprecated(self, version: Union[str, Version]) -> bool:
        """Check if a version is deprecated."""
        ver_obj = parse_version(version) if isinstance(version, str) else version
        return ver_obj in self._deprecated_versions

    def get_versions_in_range(
        self,
        min_version: Union[str, Version],
        max_version: Union[str, Version],
        include_deprecated: bool = False,
    ) -> List[Version]:
        """Get all versions within a range (inclusive)."""
        min_ver = (
            parse_version(min_version) if isinstance(min_version, str) else min_version
        )
        max_ver = (
            parse_version(max_version) if isinstance(max_version, str) else max_version
        )

        versions = self.get_versions(include_deprecated=include_deprecated)
        return [v for v in versions if min_ver <= v <= max_ver]

    def clear(self) -> None:
        """Clear all registered versions."""
        self._versions.clear()
        self._deprecated_versions.clear()
        self._default_version = None

    def count(self, include_deprecated: bool = False) -> int:
        """Get the number of registered versions."""
        if include_deprecated:
            return len(self._versions)
        return len([v for v in self._versions if v not in self._deprecated_versions])

    @property
    def all_versions(self) -> List[Version]:
        """Get all registered versions (sorted)."""
        return self.get_versions(include_deprecated=False)

    @property
    def deprecated_versions(self) -> List[Version]:
        """Get all deprecated versions (sorted)."""
        return sorted(self._deprecated_versions)

    @classmethod
    def get_instance(cls) -> "VersionRegistry":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __repr__(self) -> str:
        return f"<VersionRegistry versions={self.count()} default={self.default_version} latest={self.latest_version}>"
