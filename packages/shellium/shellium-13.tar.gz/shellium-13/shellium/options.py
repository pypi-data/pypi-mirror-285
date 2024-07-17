from pathlib import Path
from undetected_chromedriver.options \
    import ChromeOptions
from urllib.parse import urlparse

__all__ = ['ChromeOptions', 'UndetectedOptions']


class UndetectedOptions:
    def __init__(self, **kwargs):
        self.user_data_dir = kwargs.get(
            'user_data_dir',
            Path.home() / 'AppData/Local/Google/Chrome/User Data'
        )
        self.driver_executable_path = kwargs.get(
            'driver_executable_path',
            Path.cwd() / 'chromedriver.exe'
        )
        self.browser_executable_path = kwargs.get(
            'browser_executable_path',
            'C:/Program Files/Google/Chrome/Application/chrome.exe'
        )
        self.port = kwargs.get('port', 0)
        self.enable_cdp_events = kwargs.get('enable_cdp_events', False)
        self.desired_capabilities = kwargs.get('desired_capabilities', None)
        self.advanced_elements = kwargs.get('advanced_elements', False)
        self.keep_alive = kwargs.get('keep_alive', True)
        self.log_level = kwargs.get('log_level', 0)
        self.headless = kwargs.get('headless', False)
        self.version_main = kwargs.get('version_main', None)
        self.patcher_force_close = kwargs.get('patcher_force_close', False)
        self.suppress_welcome = kwargs.get('suppress_welcome', True)
        self.use_subprocess = kwargs.get('use_subprocess', True)
        self.debug = kwargs.get('debug', False)
        self.no_sandbox = kwargs.get('no_sandbox', True)
        self.user_multi_procs = kwargs.get('user_multi_procs', False)
        self.proxy_server = kwargs.get('proxy_server', None)

    @property
    def user_data_dir(self) -> str:
        return self._user_data_dir

    @user_data_dir.setter
    def user_data_dir(
            self,
            value: (str | Path)
    ):
        if not isinstance(value, (str, Path)):
            raise TypeError(
                'The "user_data_dir" must be a "str" or "Path".'
            )
        self._user_data_dir = str(Path(value).resolve())

    @property
    def driver_executable_path(self) -> str:
        return self._driver_executable_path

    @driver_executable_path.setter
    def driver_executable_path(
            self,
            value: (str, Path)
    ):
        if not isinstance(value, (str | Path)):
            raise TypeError(
                'The "driver_executable_path" must be a "str" or "Path".'
            )
        self._driver_executable_path = str(Path(value).resolve())

    @property
    def browser_executable_path(self) -> str:
        return self._browser_executable_path

    @browser_executable_path.setter
    def browser_executable_path(
            self,
            value: (str | Path)
    ):
        if not isinstance(value, (str, Path)):
            raise TypeError(
                'The "browser_executable_path" must be a "str" or "Path".'
            )
        self._browser_executable_path = str(Path(value).resolve())

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, value: int):
        if not isinstance(value, int):
            raise TypeError(
                'The "port" must be a "int".'
            )
        if not (0 <= value <= 65535):
            raise ValueError(
                'The "port" must be a valid port number (0 - 65535).'
            )
        self._port = value

    @property
    def enable_cdp_events(self) -> bool:
        return self._enable_cdp_events

    @enable_cdp_events.setter
    def enable_cdp_events(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                'The "enable_cdp_events" must be a "bool".'
            )
        self._enable_cdp_events = value

    @property
    def desired_capabilities(self) -> dict:
        return self._desired_capabilities

    @desired_capabilities.setter
    def desired_capabilities(self, value: dict):
        if not (isinstance(value, dict) or value is None):
            raise TypeError(
                'The "desired_capabilities" must be a "dict".'
            )
        self._desired_capabilities = value

    @property
    def advanced_elements(self) -> bool:
        return self._advanced_elements

    @advanced_elements.setter
    def advanced_elements(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                'The "advanced_elements" must be a "bool".'
            )
        self._advanced_elements = value

    @property
    def keep_alive(self) -> bool:
        return self._keep_alive

    @keep_alive.setter
    def keep_alive(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                'The "keep_alive" must be a "bool".'
            )
        self._keep_alive = value

    @property
    def log_level(self) -> int:
        return self._log_level

    @log_level.setter
    def log_level(self, value: int):
        if not isinstance(value, int):
            raise TypeError(
                'The "log_level" must be a "int".'
            )
        if value not in (0, 10, 20, 30, 40, 50):
            raise ValueError(
                "The value should be one of 0, 10, 20, 30, 40, or 50."
            )
        self._log_level = value

    @property
    def headless(self) -> bool:
        return self._headless

    @headless.setter
    def headless(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                'The "headless" must be a "bool".'
            )
        self._headless = value

    @property
    def version_main(self):
        return self._version_main

    @version_main.setter
    def version_main(self, value):
        self._version_main = value

    @property
    def patcher_force_close(self):
        return self._patcher_force_close

    @patcher_force_close.setter
    def patcher_force_close(self, value):
        self._patcher_force_close = value

    @property
    def suppress_welcome(self) -> bool:
        return self._suppress_welcome

    @suppress_welcome.setter
    def suppress_welcome(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                'The "suppress_welcome" must be a "bool".'
            )
        self._suppress_welcome = value

    @property
    def use_subprocess(self) -> bool:
        return self._use_subprocess

    @use_subprocess.setter
    def use_subprocess(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                'The "use_subprocess" must be a "bool".'
            )
        self._use_subprocess = value

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                'The "debug" must be a "bool".'
            )
        self._debug = value

    @property
    def no_sandbox(self) -> bool:
        return self._no_sandbox

    @no_sandbox.setter
    def no_sandbox(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                'The "no_sandbox" must be a "bool".'
            )
        self._no_sandbox = value

    @property
    def user_multi_procs(self) -> bool:
        return self._user_multi_procs

    @user_multi_procs.setter
    def user_multi_procs(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                'The "user_multi_procs" must be a "bool".'
            )
        self._user_multi_procs = value

    @property
    def proxy_server(self) -> str | None:
        return self._proxy_server

    @proxy_server.setter
    def proxy_server(self, value: str | None):
        if value is None:
            self._proxy_server = None
            return
        if not isinstance(value, str):
            raise TypeError(
                'The "proxy_server" must be a "str".'
            )
        result = urlparse(value)
        if result.scheme != 'http':
            raise ValueError(
                'The "scheme" must be a "http".'
            )
        if result.port is None:
            raise ValueError(
                'The "port" cannot be empty.'
            )
        self._proxy_server = value

    def __iter__(self):
        for attr, value in self.__dict__.items():
            if attr.startswith('_') and callable(value):
                continue
            yield attr.lstrip('_'), value

    def __getitem__(self, item):
        return getattr(self, item)
