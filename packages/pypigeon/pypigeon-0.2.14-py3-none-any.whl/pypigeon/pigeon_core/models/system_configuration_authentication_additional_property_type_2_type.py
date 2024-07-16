from enum import Enum


class SystemConfigurationAuthenticationAdditionalPropertyType2Type(str, Enum):
    GOOGLE = "google"

    def __str__(self) -> str:
        return str(self.value)
