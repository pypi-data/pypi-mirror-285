from pih.consts.file import FILE

class PYTHON:
        EXECUTOR_ALIAS: str = "py"
        EXECUTOR: str = "python"
        EXECUTOR3: str = "python3"
        PIP: str = "pip"
        SEARCH_PATTERN: str = "\\Python\\Python"
        PACKAGE_EXTENSION: str = FILE.EXTENSION.WHEEL

        class COMMAND:
            VERSION: str = "--version"
            INSTALL: str = "install"
            UNINSTALL: str = "uninstall"
            SHOW: str = "show"
            FLAG: str = "-c"