import re
import enum

VERSIONREGEX = re.compile(r"^v?[0-9]+.[0-9]+.[0-9]+(-a\d*|-b\d*)?$")

class releaseTypes(enum.StrEnum):
    BETA = "b"
    ALPHA = "a"
    RELEASE = "r"

class Version:
    def __init__(self, versionStr: str = "0.0.0") -> None:
        """Version constructor

        Args:
            versionStr (str): A version string such as "1.2.3", or "v1.2.3" or "1.2.3b1" etc.
        
        ### Versions System
        
        Versions have 3 main parts, separated by ".": Major.Minor.Patch
        
        You can also have appendages, such as, "1.1.1-b#", "1.1.1-a#", "1.1.1-b", etc. (where # is the number)
        
        Release types are Beta, Alpha, and Release (Release is the default, and  is only specified by a lack of beta or alpha in the version string)
        """
        
        self.major: int
        self.minor: int
        self.patch: int
        self.appendage: str
        self.releaseType: releaseTypes
        
        
        if not VERSIONREGEX.match(versionStr):
            print(VERSIONREGEX.match(versionStr))
            raise ValueError("Invalid version string")
        
        # Remove the "v" if it exists
        if versionStr[0] == "v":
            versionStr = versionStr[1:]
        
        # Split the version string into its parts Example using 1.2.3-a23
        parts = versionStr.split(".") # ["1", "2", "3-a23"]
        self.major = int(parts[0]) # 1
        self.minor = int(parts[1]) # 2
        if not "-" in parts[2]: # False
            self.patch = int(parts[2])
        else:
            self.patch = int(parts[2].split("-")[0]) # split: ["3", "a23"], then first item "3", then int conversion
        
        # Check for appendages
        if "-" in parts[2]:
            appendage = parts[2].split("-") # ["3", "a23"]
            self.appendage: str = appendage[1] # a23
            self.releaseType: releaseTypes = releaseTypes.BETA if self.appendage[0] == "b" else releaseTypes.ALPHA # first character is a, so ALPHA
            self.revision: int = int(appendage[1][1:]) if appendage[1][1:] else 0 # everything other than the first character, so "23", then type cast to int
        else:
            self.appendage = ""
            self.releaseType = releaseTypes.RELEASE
            self.revision = 0
        
        self.setWarningStr({})
        
    def __str__(self):
        """Converts the version object to a string"""
        appendage = ""
        if self.releaseType == releaseTypes.ALPHA:
            appendage = f" Alpha{f" {self.revision}" if not self.revision == 0 else ""}"
        elif self.releaseType == releaseTypes.BETA:
            appendage = f" Beta{f" {self.revision}" if not self.revision == 0 else ""}"
        else:
            appendage = ""
         
        return f"Version {self.major}.{self.minor}.{self.patch}" + appendage

    def __eq__(self, other: object) -> bool:
        """Checks if two versions are equal"""
        return self.major == other.major and self.minor == other.minor and self.patch == other.patch and self.releaseType == other.releaseType and self.revision == other.revision
    
    def __lt__(self, other: object) -> bool:
        """Checks if the version is less than another version"""
        if self.major < other.major:
            return True
        elif self.major == other.major:
            if self.minor < other.minor:
                return True
            elif self.minor == other.minor:
                if self.patch < other.patch:
                    return True
                elif self.patch == other.patch:
                    if self.appendage and not other.appendage:
                        return True
                    elif self.appendage and other.appendage:
                        if self.appendage < other.appendage:
                            return True
                        elif self.appendage == other.appendage:
                            if self.revision < other.revision:
                                return True
        return False
    
    def __gt__(self, other: object) -> bool:
        """Checks if the version is greater than another version"""
        if self.major > other.major:
            return True
        elif self.major == other.major:
            if self.minor > other.minor:
                return True
            elif self.minor == other.minor:
                if self.patch > other.patch:
                    return True
                elif self.patch == other.patch:
                    if not self.appendage and other.appendage:
                        return True
                    elif self.appendage and other.appendage:
                        if self.appendage > other.appendage:
                            return True
                        elif self.appendage == other.appendage:
                            if self.revision > other.revision:
                                return True
        return False
    
    def __le__(self, other: object) -> bool:
        """Checks if the version is less than or equal to another version"""
        return self == other or self < other
    
    def __ge__(self, other: object) -> bool:
        """Checks if the version is greater than or equal to another version"""
        return self == other or self > other
    
    def __ne__(self, other: object) -> bool:
        """Checks if the version is not equal to another version"""
        return not self == other
    
    def __repr__(self) -> str:
        """Returns a string representation of the object"""
        return f"{self.major}.{self.minor}.{self.patch}{f"-{self.releaseType}{self.revision}" if not self.releaseType == releaseTypes.RELEASE else ""}"
    
    def __hash__(self) -> int:
        """Returns a hash of the object"""
        return hash(str(self))

    def toDict(self) -> dict:
        """Converts the version object to a dictionary"""
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "releaseType": self.releaseType,
            "revision": self.revision
        }
    
    @staticmethod
    def fromDict(d: dict) -> object:
        """Converts a dictionary to a version object"""
        
        appendage = f'-{d['releaseType']}{d['revision']}' if d['releaseType'] != releaseTypes.RELEASE else ""
        
        return Version(
            f"{d['major']}.{d['minor']}.{d['patch']}{appendage}")
    
    def toTuple(self) -> tuple:
        """Converts the version object to a tuple"""
        return (self.major, self.minor, self.patch, self.appendage)
    
    @staticmethod
    def fromTuple(t: tuple) -> object:
        """Converts a tuple to a version object"""
        return Version(f"{t[0]}.{t[1]}.{t[2]}{f'-{t[3]}' if t[3] else ''}")
    
    def toList(self) -> list:
        """Converts the version object to a list"""
        return [self.major, self.minor, self.patch, self.appendage]
    
    @staticmethod
    def fromList(l: list) -> object:
        """Converts a list to a version object"""
        return Version(f"{l[0]}.{l[1]}.{l[2]}{f'-{l[3]}' if l[3] else ''}")
    
    def getWarning(self, other: object) -> str:
        if self > other:
            return self.tooNewWarning.replace("%CURRENT", str(self)).replace("%OLD", str(other))
        elif self < other:
            return self.tooOldWarning.replace("%CURRENT", str(self)).replace("%OLD", str(other))
        else:
            return ""
        
    def setWarningStr(self, strs: dict) -> None:
        """Sets warning strings for the version object

        Args:
            strs (dict): The warning strings to set, must contain "tooNew", "tooOld", and "diffRelease" keys

        Raises:
            ValueError: If the warning strings are invalid
        
        Use the following placeholders in the warning strings:
        
        %CURRENT - The current version
        
        %OLD - The version being compared to
        """
        
        if not strs:
            strs = {}
        
        
        if strs == {}:
            self.tooNewWarning = "%CURRENT is newer than %OLD"
            self.tooOldWarning = "%CURRENT is older than %OLD"
        else:
            try:
                self.tooNewWarning = strs["tooNew"]
                self.tooOldWarning = strs["tooOld"]
            except KeyError:
                raise ValueError("Invalid warning strings, must contain 'tooNew', 'tooOld' keys")
