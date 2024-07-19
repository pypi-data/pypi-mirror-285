class Version:
    """
    Representation of a package version number.

    This resembles a semver scheme but doesn't necessarily
    follow one.

    Args:
        input (str): Version in string form x.y.zzzz
        scheme (str): The versioning scheme to use, 'semver' or 'date'

    Attributes:
        major (int): Major version number
        minor (int): Minor version number
        patch (int): Path version number
        scheme (str): Versioning scheme to use
    """

    def __init__(self, input: str = "", scheme="semver") -> None:
        self.major = 0
        self.minor = 0
        self.patch = 0
        self.scheme = scheme

        if input:
            self.read(input)

    def read(self, input: str):
        """Read the version details from the input string.

        String is of form x.y.zzzz (major.minor.patch), where
        'major', 'minor' etc are denoted as 'fields' of the
        version.

        Args:
            input (str): Version in string form x.y.zzzz
        """

        major, minor, patch = input.split(".")
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)

    def increment(self, field="patch"):
        """
        Increment the version number, depending on the provided field.

        Args:
            field (str): The field to increment, can be 'major', 'minor', 'patch'.
        """

        if self.scheme == "semver":
            if field == "patch":
                self.patch += 1
            elif field == "minor":
                self.patch = 0
                self.minor += 1
            elif field == "major":
                self.major += 1
                self.minor = 0
                self.patch = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
