from ipih import FACADE_FOLDER_NAME

from pih.tools import j

class FACADE:
    NAME: str = FACADE_FOLDER_NAME
    SERVICE_FOLDER_SUFFIX: str = "Service"
    
    @staticmethod
    def SERVICE_NAME(service_name: str) -> str:
        suffix: str = FACADE.SERVICE_FOLDER_SUFFIX
        return (
            j(
                (
                    service_name,
                    (None if service_name.endswith(suffix) else suffix),
                )
            )
        )
