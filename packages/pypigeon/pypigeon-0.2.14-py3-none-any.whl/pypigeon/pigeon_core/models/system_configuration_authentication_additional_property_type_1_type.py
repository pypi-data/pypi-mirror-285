from enum import Enum


class SystemConfigurationAuthenticationAdditionalPropertyType1Type(str, Enum):
    GITHUB = "github"

    def __str__(self) -> str:
        return str(self.value)
