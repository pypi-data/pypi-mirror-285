import semver

class Version:
    def __init__(self, version: str):
        self.__version = self.__parse(version)

    def __parse(self, version: str):
        parts = version.split(".")

        if (len(parts) == 3):
            return semver.Version.parse(version)
        if (len(parts) == 2):
            return semver.Version.parse(f"{parts[0]}.{parts[1]}.0")
        return semver.Version.parse(f"{parts[0]}.0.0")

    def __convert_caret_range(self, range_str: str):
        range = self.__parse(range_str)
        if (range.major > 0):
            upper_version = f"{range.major + 1}.0.0"
        elif (range.minor > 0):
            upper_version = f"0.{range.minor + 1}.0"
        else:
            upper_version = f"0.0.{range.patch +1}"

        return f">={range},<{upper_version}"

    def __convert_tilde_range(self, range_str: str):
        range = self.__parse(range_str)
        if (range.patch != 0):
            upper_version = f"{range.major}.{range.minor +1}.0"
        elif (range.minor != 0):
            upper_version = f"{range.major}.{range.minor +1}.0"
        else:
            upper_version = f"{range.major +1}.0.0"

        return f">={range},<{upper_version}"

    def __is_x_range(self, range_str: str):
        return any(part == "x" or part == "*" for part in range_str.split("."))

    def __convert_x_range(self, range_str:str):
        parts = range_str.split(".")
        if (len(parts) == 1):
            if (parts[0] == "x" or parts[0] == "*"):
                return ">=0.0.0"
            major = int(parts[0])
            return f">={major}.0.0,<{major +1}.0.0"
        if (len(parts) == 2):
            major = int(parts[0])
            if (parts[1] == "x" or parts[1] == "*"):
                return f">={major}.0.0,<{major +1}.0.0"

        major = int(parts[0])
        minor = int(parts[1])
        if (parts[2] == "x" or parts[2] == "*"):
            return f">={major}.{minor}.0,<{major,minor+1}.0"

        patch = int(parts[2])
        return f">={major}.{minor}.{patch},<{major}.{minor +1}.0"

    def __convert_hyphen_range(self, range_str: str):
        min_version_str, max_version_str = range_str.split("-")
        min_version_str = min_version_str.strip()
        max_version_str = max_version_str.strip()
        min_version = self.__parse(min_version_str)
        max_version = self.__parse(max_version_str)

        if (min_version.patch is None):
            min_version_str += ".0"

        if (max_version.patch is None):
            max_version_str += ".0"

        return f">={min_version_str},<={max_version_str}"

    def satisfies(self, range: str):
        if (range.startswith("^")):
            range = self.__convert_caret_range(range.lstrip("^"))
        elif (range.startswith("~")):
            range = self.__convert_tilde_range(range.lstrip("~"))
        elif (self.__is_x_range(range) or len(range.split(".")) < 3):
            range = self.__convert_x_range(range)

        if ("-" in range):
            range = self.__convert_hyphen_range(range)

        return all(self.__version.match(part) for part in range.split(","))
