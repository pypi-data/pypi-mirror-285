import copy
import time
import shutil
import pathlib
import hashlib
import subprocess

from urllib.parse import urlparse
from undetected_chromedriver \
    import Chrome as _Chrome
from selenium.webdriver.remote.webelement \
    import WebElement as _WebElement
from selenium.common.exceptions \
    import WebDriverException
from selenium.webdriver.common.by import By

from .options import (
    ChromeOptions,
    UndetectedOptions
)
from .extensions import (
    DEFAULT_MANIFEST,
    DEFAULT_BACKGROUND_JS_PROXY,
    DEFAULT_BACKGROUND_AUTO_AUTH
)
from .exceptions import (
    ChromeAlreadyRunningError,
    UserDataDirExistsError,
    UserDataDirBuildError
)

__all__ = ['WebElement', 'Chrome', 'Shellium']


class WebElement(_WebElement):
    """
    RU: Класс ShellElement - это обертка над WebElement, которая добавляет дополнительные функции для удобства работы.
    EN: The ShellElement class is a wrapper over WebElement that adds additional functions for convenience.
    """

    def __init__(self, parent, _id):
        """
        RU: Инициализирует объект ShellElement.
        EN: Initializes the ShellElement object.
        """
        super().__init__(parent, _id)

    def find_element(
            self,
            by=By.ID,
            value: str = None
    ) -> 'WebElement':
        """
        RU: Находит элемент на странице и возвращает его как объект ShellElement.
        EN: Finds an element on the page and returns it as a ShellElement object.
        """
        item = super().find_element(by, value)
        return WebElement(item.parent, item.id)

    def find_elements(
            self,
            by=By.ID,
            value: str = None
    ) -> list['WebElement']:
        """
        RU: Находит элементы на странице и возвращает их как список объектов ShellElement.
        EN: Finds elements on the page and returns them as a list of ShellElement objects.
        """
        items = super().find_elements(by, value)
        return [WebElement(item.parent, item.id) for item in items]

    def click(
            self,
            timeout=0.0,
            interval=0.1,
            ignore_errors=False
    ):
        """
        RU: Кликает по элементу, повторяя попытку в течение заданного времени, если произошла ошибка WebDriverException.
        EN: Clicks on the element, retrying for a given time if a WebDriverException error occurs.
        """
        start = time.time()
        current_exception = WebDriverException
        while time.time() - start <= timeout:
            try:
                return super().click()
            except WebDriverException as exception:
                current_exception = exception
                time.sleep(interval)
        if ignore_errors:
            return None
        raise current_exception

    def check_element(
            self,
            by=By.ID,
            value: str = None,
            interval=0.1,
            timeout=0.0
    ):
        """
        RU: Проверяет наличие элемента на странице в течение заданного времени.
        EN: Checks for the presence of an element on the page for a given time.
        """
        start = time.time()
        while time.time() - start <= timeout:
            try:
                return self.find_element(by, value)
            except WebDriverException:
                time.sleep(interval)
        return None

    def check_elements(
            self,
            by=By.ID,
            value: str = None,
            interval=0.1,
            timeout=0.0
    ):
        """
        RU: Проверяет наличие элементов на странице в течение заданного времени.
        EN: Checks for the presence of elements on the page for a given time.
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            items = self.find_elements(by, value)
            if items:
                return items
            time.sleep(interval)
        return None

    def send_keys(
            self,
            values: str,
            timeout=0.25):
        """
        RU: Отправляет последовательность клавиш элементу, делая паузу между каждым символом.
        EN: Sends a sequence of keys to the element, pausing between each character.
        """
        interval = timeout / len(values)
        for value in values:
            super().send_keys(value)
            time.sleep(interval)

    def exists(self):
        """
        RU: Проверяет, существует ли элемент на странице.
        EN: Checks if the element exists on the page.
        """
        try:
            return self.is_displayed()
        except WebDriverException:
            return False


class Chrome(_Chrome):
    """
    RU: Класс Chrome - это обертка над undetected_chromedriver.Chrome, которая добавляет
        дополнительные функции для удобства работы.
    EN: The Chrome class is a wrapper over undetected_chromedriver.Chrome
        that adds additional functions for convenience.
    """

    def __init__(self, **kwargs):
        """
        RU: Инициализирует объект Chrome.
        EN: Initializes the Chrome object.
        """
        proxy_server = kwargs.pop('proxy_server')
        if proxy_server is None:
            super().__init__(**kwargs)
            return

        result = urlparse(proxy_server)
        scheme = result.scheme
        port = result.port
        username = result.username
        password = result.password
        hostname = result.hostname

        BACKGROUND_JS = DEFAULT_BACKGROUND_JS_PROXY % (
            scheme, hostname, port
        )
        if username and password:
            BACKGROUND_JS += DEFAULT_BACKGROUND_AUTO_AUTH % (
                username, password
            )

        user_data_dir = kwargs.pop(
            'user_data_dir',
            pathlib.Path.home() / 'AppData/Local/Google/Chrome/User Data'
        )
        extension_name = \
            hashlib.sha256(proxy_server.encode()).hexdigest()
        temp_data_dir = pathlib.Path(user_data_dir, 'Temp')
        extension_dir = temp_data_dir / extension_name
        extension_dir.mkdir(parents=True, exist_ok=True)
        with open(extension_dir / "manifest.json", "w+") as f:
            f.write(DEFAULT_MANIFEST)
        with open(extension_dir / "background.js", "w+") as f:
            f.write(BACKGROUND_JS)

        options = kwargs.pop(
            'options',
            ChromeOptions()
        )
        options.add_argument(f'--proxy-server={scheme}://{hostname}:{port}')
        options.add_argument(f'--load-extension={extension_dir}')
        super().__init__(
            options=options,
            user_data_dir=user_data_dir,
            **kwargs
        )
        shutil.rmtree(extension_dir)

    def _wrap_value(self, value):
        """
        RU: Оборачивает значение в словарь, если оно является экземпляром ShellElement.
        EN: Wraps the value in a dictionary if it is an instance of ShellElement.
        """
        if isinstance(value, WebElement):
            return {"element-6066-11e4-a52e-4f735466cecf": value.id}
        return super()._wrap_value(value)

    def _unwrap_value(self, value):
        """
        RU: Распаковывает значение из словаря, если оно является экземпляром ShellElement.
        EN: Unwraps the value from a dictionary if it is an instance of ShellElement.
        """
        if isinstance(value, dict) and "element-6066-11e4-a52e-4f735466cecf" in value:
            return WebElement(self, (value["element-6066-11e4-a52e-4f735466cecf"]))
        return super()._unwrap_value(value)

    def find_element(
            self,
            by=By.ID,
            value=None
    ) -> WebElement:
        """
        RU: Находит элемент на странице и возвращает его как объект ShellElement.
        EN: Finds an element on the page and returns it as a ShellElement object.
        """
        item = super().find_element(by, value)
        return WebElement(item.parent, item.id)

    def find_elements(
            self,
            by=By.ID,
            value=None
    ) -> list[WebElement]:
        """
        RU: Находит элементы на странице и возвращает их как список объектов ShellElement.
        EN: Finds elements on the page and returns them as a list of ShellElement objects.
        """
        items = super().find_elements(by, value)
        return [WebElement(item.parent, item.id) for item in items]

    def check_element(
            self,
            by=By.ID,
            value=None,
            interval=0.1,
            timeout=0.0
    ):
        """
        RU: Проверяет наличие элемента на странице в течение заданного времени.
        EN: Checks for the presence of an element on the page for a given time.
        """
        start = time.time()
        while time.time() - start <= timeout:
            try:
                return self.find_element(by, value)
            except WebDriverException:
                time.sleep(interval)
        return None

    def check_elements(
            self,
            by=By.ID,
            value=None,
            interval=0.1,
            timeout=0.0
    ):
        """
        RU: Проверяет наличие элементов на странице в течение заданного времени.
        EN: Checks for the presence of elements on the page for a given time.
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            items = self.find_elements(by, value)
            if items:
                return items
            time.sleep(interval)
        return None

    def scroll_into_view(self, item):
        """
        RU: Прокручивает страницу до элемента.
        EN: Scrolls the page to the element.
        """
        if not isinstance(item, WebElement):
            raise TypeError('Item Must be a ShellElement.')
        script = 'arguments[0].scrollIntoView({block: "center"});'
        return self.execute_script(script, item)

    def exists(self):
        try:
            return len(self.window_handles) != 0
        except WebDriverException:
            return False


class Shellium:
    """
    RU: Класс Shellium предназначен для управления драйвером ShellDriver и его настройками.
    EN: The Shellium class is designed to manage the ShellDriver and its settings.
    """

    def __init__(self, **kwargs):
        """
        RU: Инициализирует объект Shellium.
        EN: Initializes the Shellium object.
        """
        # Setup options and service
        self._driver = None
        self._options = kwargs.pop(
            'options',
            ChromeOptions()
        )
        self._undetected_options = \
            UndetectedOptions(**kwargs)

    @property
    def driver(self) -> Chrome | None:
        """
        RU: Возвращает текущий экземпляр драйвера.
        EN: Returns the current driver instance.
        """
        return self._driver

    @property
    def undetected_options(self):
        """
        RU: Возвращает текущие настройки драйвера.
        EN: Returns the current driver settings.
        """
        return self._undetected_options

    @property
    def options(self) -> ChromeOptions:
        return self._options

    def run(self) -> Chrome:
        """
        RU: Запускает драйвер, если он еще не запущен.
        EN: Runs the driver if it is not already running.
        """
        if self.driver is not None:
            raise ChromeAlreadyRunningError(
                f'The Chrome is already running: {self.driver}.'
            )
        self._driver = Chrome(
            options=copy.deepcopy(self.options),
            **dict(self.undetected_options)
        )
        return self.driver

    def terminate(self):
        """
        RU: Завершает работу драйвера, если он запущен.
        EN: Terminates the driver if it is running.
        """
        if self.driver is None:
            return None
        del self._driver
        self._driver = None

    def build(self):
        """
        RU: Создает новый каталог пользовательских данных, если он еще не существует.
        EN: Creates a new user data directory if it does not already exist.
        """
        if pathlib.Path(self.undetected_options.user_data_dir).exists():
            raise UserDataDirExistsError(
                f'{self.undetected_options.user_data_dir} already exists.'
            )
        command = [
            self.undetected_options.browser_executable_path,
            '--no-startup-window',
            f'--user-data-dir={self.undetected_options.user_data_dir}'
        ]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE
        )
        _, error = process.communicate()
        if process.returncode != 0:
            raise UserDataDirBuildError(
                'Failed to build a User Data Dir.'
            )

    def destroy(self):
        """
        RU: Удаляет каталог пользовательских данных и завершает работу драйвера.
        EN: Deletes the user data directory and terminates the driver.
        """
        self.terminate()
        shutil.rmtree(
            self.undetected_options.user_data_dir,
            ignore_errors=True
        )
