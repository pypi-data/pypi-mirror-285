import os
from typing import Any, Dict, Callable, Optional, Union, List, Tuple
from inspect import isclass
from os import path
import re
import json

import yaml
from deepmerge import always_merger, Merger
from requests import JSONDecodeError
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

FactoryType = Callable[..., Any]
ConfigurationType = Dict[str, Union[List, Dict[str, Any]]]
GetItemType = Union[str, FactoryType]

overwrite_merger = Merger(
    [(list, "override"), (dict, "merge"), (set, "override")],
    ["override"], ["override"]
)


def requests_session(retries=10, backoff=0.3, backoff_max=5):
    session = requests.Session()
    # retry 10x if we get connection errors
    retry = Retry(total=None, connect=retries, backoff_factor=backoff)
    retry.BACKOFF_MAX = backoff_max
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


def configure(config: Union[str, ConfigurationType], file_type: Optional[str] = None, ignore_missing: bool = False):
    Registry.default_registry().configure(config, file_type, ignore_missing)


def http_configure(*names: str, ignore_missing: bool = False):
    Registry.default_registry().http_configure(*names, ignore_missing=ignore_missing)


def save_http_configuration(name: str, data: Dict[str, Any]):
    Registry.default_registry().save_http_configuration(name, data)


def registry_configuration() -> Dict[str, Any]:
    return Registry.default_registry().registry_configuration()


def reconfigure():
    Registry.default_registry().reconfigure()


def get_configuration(object_name: str) -> Dict[str, Any]:
    _, kwargs = Registry.default_registry().get_object_configuration(object_name)

    return kwargs


def get_kwarg(object_name: str, key: str) -> Any:
    return Registry.default_registry().get_kwarg(object_name, key)


def get(item: GetItemType, *args: Any, **kwargs: Any) -> Any:
    return Registry.default_registry().get(item, *args, **kwargs)


def register(factory: FactoryType, name: Optional[str] = None):
    Registry.default_registry().register(factory, name)


def override_factory(item: GetItemType, factory: FactoryType):
    Registry.default_registry().override_factory(item, factory)


def default_registry() -> 'Registry':
    return Registry.default_registry()


def reset_object(object_name: str):
    Registry.default_registry().reset_object(object_name)


class Registry:
    CONFIG_META_PREFIX = '$'
    ARGS_KEY = '$args'
    TYPE_KEY = '$type'
    ENV_VAR_REGEX = re.compile(r'\${(\w+):?(.+)?}')
    _default_registry: Optional['Registry'] = None

    @staticmethod
    def reset():
        Registry._default_registry = None

    @staticmethod
    def default_registry() -> 'Registry':
        if Registry._default_registry is None:
            Registry._default_registry = Registry()

        return Registry._default_registry

    def __init__(self,
                 config_path: Optional[str] = None,
                 configuration: Optional[ConfigurationType] = None,
                 factories: Optional[Dict[str, FactoryType]] = None,
                 objects: Optional[Dict[str, Any]] = None,
                 set_default: bool = True,
                 http_timeout: Optional[float] = 2.,
                 ):
        self.config_path = config_path
        self.configuration = configuration or {}
        self.configurations = [configuration] if configuration else []
        self.factories = factories or {}
        self.factory_types = {val: key for key, val in self.factories.items()}
        self.objects = objects or {}
        self.http_timeout = http_timeout

        if set_default and Registry._default_registry is None:
            Registry._default_registry = self

        if self.config_path is not None:
            self.load_configuration()

    def reset_object(self, object_name: str):
        if object_name in self.objects:
            self.objects.pop(object_name)

    def registry_configuration(self) -> Dict[str, Any]:
        config_key = f'{self.CONFIG_META_PREFIX}registry'
        if config_key not in self.configuration:
            raise RegistryError(f'Unable to read registry configuration, "{config_key}" not found in configuration')

        _, kwargs = self.get_object_configuration(config_key)

        return kwargs

    def configure(self, config: Union[str, ConfigurationType], file_type: Optional[str] = None, ignore_missing: bool = False, append: bool = True):
        if isinstance(config, dict):
            self.merge_configuration(config)
        elif isinstance(config, str) and config.startswith(('http://', 'https://')):
            self.load_http_configuration(config, ignore_missing)
        else:
            self.load_configuration(config, file_type, ignore_missing)

        if append:
            # track configuration files used so we can reload them
            self.configurations.append(config)

    def http_configure(self, *names: str, ignore_missing: bool = True):
        registry_config = self.registry_configuration()

        if 'configuration_url' not in registry_config:
            raise RegistryError(f'Cannot use `http_configure`, "$registry.configuration_url" not available in configuration')

        for name in names:
            config_url = registry_config['configuration_url'] + '/' + name
            self.configure(config_url, ignore_missing=ignore_missing)

    def save_http_configuration(self, name: str, data: Dict[str, Any], timeout: Optional[float] = 'default'):
        """
        Saves the named configuration as a dictionary to the configuration URL
        """
        registry_config = self.registry_configuration()

        if 'configuration_url' not in registry_config:
            raise RegistryError(f'Cannot use `http_configure`, "$registry.configuration_url" not available in configuration')

        config_url = registry_config['configuration_url'] + '/' + name
        # 'default' is a sentinel value to allow the user to specify None or a value
        timeout = self.http_timeout if timeout == 'default' else timeout
        try:
            response = requests_session().put(config_url, json=data, timeout=timeout)
        except requests.ConnectionError:
            raise RegistryError(f'Cannot save parameters to "{config_url}", error connecting to server')
        except TimeoutError:
            raise RegistryError(f'Cannot save parameters to "{config_url}", timeout when communicating with server')

        if not response.ok:
            raise RegistryError(f'Cannot save parameters to "{config_url}", response status: {response.status_code}')

    def reconfigure(self):
        self.configuration = {}

        for config in self.configurations:
            self.configure(config, append=False)

    def merge_configuration(self, config: ConfigurationType):
        self.configuration = overwrite_merger.merge(self.configuration or {}, config)

    def load_configuration(self, config_path: Optional[str] = None, file_type: Optional[str] = None, ignore_missing: bool = False):
        file_path = config_path or self.config_path

        # use the file extension as the file type if none is given
        if file_type is None:
            _, config_ext = path.splitext(file_path)
            config_type = config_ext[1:]  # remove .
        else:
            config_type = file_type

        if ignore_missing and not path.exists(file_path):
            return

        with open(file_path or self.config_path) as config_file:
            if config_type == 'json':
                self.merge_configuration(json.load(config_file))
            elif config_type == 'yaml':
                self.merge_configuration(yaml.safe_load(config_file))
            else:
                raise RegistryError(f'Invalid config file format, must be "json" or "yaml": {config_type}')

    def load_http_configuration(self, config_url, ignore_missing: bool = False, timeout: Optional[float] = 'default'):
        # 'default' is a sentinel value to allow the user to specify None or a value
        timeout = self.http_timeout if timeout == 'default' else timeout
        try:
            response = requests_session().get(config_url, timeout=timeout)
        except requests.ConnectionError:
            raise RegistryError(f'Cannot read configuration from "{config_url}", error connecting to server')

        if not response.ok:
            if response.status_code == 404 and ignore_missing:
                return

            raise RegistryError(f'Cannot read configuration from "{config_url}", response status: {response.status_code}')

        try:
            config = response.json()
        except JSONDecodeError:
            raise RegistryError(f'Cannot read configuration from "{config_url}", error parsing JSON response')

        self.merge_configuration(config)

    def get_object_meta_configuration(self, object_name: str) -> Dict[str, Any]:
        if object_name not in self.configuration:
            return {}

        config = self.configuration[object_name]
        # remove any keys that don't start with @ (and aren't @args) and remove the @ from the keys
        return {k[1:]: v for k, v in config.items() if k.startswith(self.CONFIG_META_PREFIX) and k != self.ARGS_KEY}

    def find_value(self, path: List[str], config: Dict[str, Any]) -> Any:
        if path[0] not in config:
            raise RegistryError(f'Unable to find value, {path[0]} not found in config: {config}')

        value = config[path[0]]

        if len(path) == 1:
            return value

        return self.find_value(path[1:], value)

    def inject_value(self, value: Any) -> Any:
        if isinstance(value, str):
            if value.startswith('\\$'):
                return value[1:]

            if value.startswith('${'):
                env_var, default_value = self.parse_environment_variable(value)
                value = os.environ.get(env_var, default_value)

                if isinstance(value, str) and value != '':
                    return yaml.safe_load(value)

                return value

            if value.startswith('$'):
                if '.' in value:
                    return self.find_value(value[1:].split('.'), self.configuration)

                return self.get_by_name(value[1:])

        return value

    def parse_environment_variable(self, value: str) -> Tuple[str, str]:
        """ Parse an environment variable value like ${ENV_VAR:default} or ${ENV_VAR} """
        match = self.ENV_VAR_REGEX.match(value)

        if not match:
            raise RegistryInvalidEnvironmentVariableError(f'Invalid environment variable syntax: {value}')

        env_var, default_value = match.groups()

        return env_var, yaml.safe_load(default_value) if default_value else ''

    def get_object_configuration(self, object_name: Optional[str], *args: Any, **kwargs: Any) -> Tuple[List[Any], Dict[str, Any]]:
        if object_name is None or object_name not in self.configuration:
            return list(args), kwargs

        config = self.configuration[object_name]

        if isinstance(config, list):
            return [*config, *args], kwargs

        # start with the config of the factory defined by the $type key in the config, if it exists
        config_args, config_kwargs = self.get_object_configuration(config.get(self.TYPE_KEY, None))

        # merge object config, if defined
        config_args = [*config_args, *config.get(self.ARGS_KEY, [])]
        config_kwargs = {**config_kwargs, **{k: v for k, v in config.items() if not k.startswith(self.CONFIG_META_PREFIX)}}

        # merge in any additional args and kwargs
        config_args = [*config_args, *args]
        config_kwargs = {**config_kwargs, **kwargs}

        # loop through values and find instances to be injected
        config_args = [self.inject_value(arg) for arg in config_args]
        config_kwargs = {key: self.inject_value(arg) for key, arg in config_kwargs.items()}

        return config_args, config_kwargs

    def get_kwarg(self, object_name: str, key: str) -> Any:
        config_args, config_kwargs = self.get_object_configuration(object_name)

        if key not in config_kwargs:
            raise KeyError(f'Cannot get configuration value for "{object_name}", "{key}" does not exist')

        return config_kwargs[key]

    def get_object_factory(self, object_name: str) -> FactoryType:
        if object_name not in self.factories:
            if object_name not in self.configuration:
                raise RegistryFactoryNotFoundError(f'Unable to find a factory or config for object: {object_name}')

            if self.TYPE_KEY not in self.configuration[object_name]:
                raise RegistryFactoryNotFoundError(
                    f'No factory or "$type" key found in config for object: {object_name}')

            factory_name = self.configuration[object_name][self.TYPE_KEY]

            if factory_name not in self.factories:
                raise RegistryFactoryNotFoundError(
                    f'Unable to find a factory for "{object_name}" with $type: {factory_name}')

            return self.factories[factory_name]

        return self.factories[object_name]

    def register(self, factory: FactoryType, name: Optional[str] = None):
        if name is None:
            if not isclass(factory):
                raise RegistryError(f'Only classes can be registered without a name')

            name = factory.__name__

        if name in self.factories:
            raise RegistryFactoryExists(f'Factory with name "{name}" already registered')

        self.factories[name] = factory
        self.factory_types[factory] = self.factory_types.get(factory, []) + [name]

    def override_factory(self, item: GetItemType, factory: FactoryType):
        object_name = item if isinstance(item, str) else item.__name__

        if object_name not in self.factories:
            raise RegistryFactoryNotFoundError(f'Cannot override factory, existing factory not found for item: {item}')

        self.factories[object_name] = factory

    def create_object(self, object_name: str, *args: Any, **kwargs: Any):
        factory = self.get_object_factory(object_name)
        object_args, object_kwargs = self.get_object_configuration(object_name, *args, **kwargs)
        return factory(*object_args, **object_kwargs)

    def get_by_name(self, object_name: str, *args: Any, **kwargs: Any):
        if object_name in self.objects:
            return self.objects[object_name]

        self.objects[object_name] = self.create_object(object_name, *args, **kwargs)
        return self.objects[object_name]

    def get_by_type(self, factory: FactoryType, *args: Any, **kwargs: Any) -> Any:
        if factory not in self.factory_types:
            raise RegistryFactoryNotFoundError(f'Unable to find factory: {factory}')

        if not isclass(factory):
            raise RegistryFactoryIsNotClassError(f'Cannot get default object, factory must be a class: {factory}')

        object_names = self.factory_types[factory]
        object_name = factory.__name__

        if object_name not in object_names:
            raise RegistryFactoryDefaultNotFoundError(f'Unable to find a default object for factory: {factory}')

        return self.get_by_name(object_name, *args, **kwargs)

    def get(self, item: GetItemType, *args: Any, **kwargs: Any) -> Any:
        if isinstance(item, str):
            return self.get_by_name(item, *args, **kwargs)

        return self.get_by_type(item, *args, **kwargs)


class RegistryError(Exception):
    pass


class RegistryFactoryNotFoundError(RegistryError):
    pass


class RegistryFactoryDefaultNotFoundError(RegistryError):
    pass


class RegistryFactoryExists(RegistryError):
    pass


class RegistryFactoryIsNotClassError(RegistryError):
    pass


class RegistryInvalidEnvironmentVariableError(RegistryError):
    pass