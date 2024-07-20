"""Abstract base classes for conveniently associating parameters with classes"""

from typing import Callable, MutableMapping, List, Union, Dict
from abc import ABC
from copy import copy
from pydantic import create_model, BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class YAMLParam:
    def __init__(self,
                 default_value=None,
                 docstring: str = None,
                 typecast: Callable = None,
                 kwarg_alias: str = None,
                 include: bool = True,
                 allow_null_values: bool = False,
                 ):
        """
        Configuration for a YAML parameter

        :param default_value: default value for the attribute
        :param docstring: docstring
        :param typecast: typecast (if the object is not serializable)
        :param kwarg_alias: keyword argument alias. Overrides base name and useful when subclasses catch YAML
            parameters by a different name and pass them through
        :param include: whether to include this parameter output in a yaml file. Useful for when specifying this
            parameter is redundant.
        :param allow_null_values: whether to allow null values to override the default value.
        """
        # todo add a name attribute and convert to a list when retrieving values
        self.default_value = default_value
        self.docstring = docstring
        self.typecast = typecast
        self.kwarg_alias = kwarg_alias
        self.include = include
        self.allow_null_values = allow_null_values

    def __copy__(self):
        return YAMLParam(
            default_value=self.default_value,
            docstring=self.docstring,
            typecast=self.typecast,
            kwarg_alias=self.kwarg_alias,
            include=self.include,
            allow_null_values=self.allow_null_values,
        )

    def get_value(self, obj, attribute: str, **overrides):
        """
        Executes the logic to retrieve the associated parameter from the object. Also performs a typecast (if specified)

        :param obj: object to retrieve from
        :param attribute: attribute name
        :param overrides: overrides (if the attribute is in overrides, the override value is returned)
        :return: value
        """
        # return override if specified
        if attribute in overrides:
            out = overrides[attribute]
        else:
            out = getattr(obj, attribute, None)
            # check flag for whether a None value is desired over the default, if not return default value
            if out is None and self.allow_null_values is False:
                out = self.default_value

        # type cast the value
        if self.typecast is not None and out is not None:
            out = self.typecast(out)
        # otherwise return the retrieved value
        return out


class YAMLConfig(ABC):
    # name for the configuration tree
    YAML_TREE_NAME: str = None
    # docstring for the configuration tree
    YAML_TREE_DOCSTRING: str = None

    # mapping of value name to the default value, docstring (optional), and type cast (optional)
    yaml_parameters: MutableMapping[str, YAMLParam] = {}

    YAML_INDENT = '  '  # default two spaces

    # sub-configurations associated with the instance (the key should be an attribute of the instance and that instance
    #   should be a YAMLConfig instance
    sub_configurations: MutableMapping[str, 'YAMLConfig'] = {}
    # map of kwarg aliases belonging to the sub_configuration aliases
    sub_configuration_aliases: MutableMapping[str, MutableMapping[str, str]] = {}

    # attributes of the instance which are YAMLConfig instances
    #   keys should be attribute names (also init kwargs) which should accept a dictionary and pass it directly to
    #   the init of that class
    yaml_attributes: MutableMapping[str, 'YAMLConfig'] = {}

    # flag to indicate that an error should be raised when apply_parameters fails
    APPLY_PARAMETERS_RAISE: bool = True

    def __new__(cls, *args, **kwargs):
        """ensures that the YAML parameters are not shared between instances of the same class"""
        out = object.__new__(cls)
        out.yaml_parameters = {key: copy(val) for key, val in out.yaml_parameters.items()}
        return out

    def __init__(self):
        """
        A configuration ABC which enables saving kwargs (parameters) for the instance to YAML files.
        Call the __init__ of this class at the end of the subclass' init call. If there are no defined aliases,
        the init call can be skipped (but should be executed for best practices).
        """
        # sets keyword argument aliases to sub-configurations as defined
        for sub_config in self.sub_configuration_aliases:
            inst: YAMLConfig = getattr(self, sub_config, None)
            if inst is None:
                continue
            for param_name, alias in self.sub_configuration_aliases[sub_config].items():
                yaml_param: YAMLParam = inst.yaml_parameters[param_name]
                yaml_param.kwarg_alias = alias

    def _get_inst_prop_doc(self, prop_name: str) -> Union[str, None]:
        """
        Retrieves the docstring of the provided property, returning None if the prop is not a property of the instance
        or the docstring does not exist

        :param prop_name: property name of instance
        :return: docstring of property
        """
        cls_prop = getattr(self.__class__, prop_name, None)
        if cls_prop is not None and cls_prop.__doc__ is not None:
            return self._de_docstringify(cls_prop.__doc__)

    @classmethod
    def _get_cls_prop_doc(cls, prop_name: str) -> Union[str, None]:
        """
        Retrieves the docstring of the provided property from the class, returning None if the prop is not a property
        of the class or the docstring does not exist

        :param prop_name: property name of class
        :return: docstring of property
        """
        cls_prop = getattr(cls, prop_name, None)
        if cls_prop is not None and cls_prop.__doc__ is not None:
            return cls._de_docstringify(cls_prop.__doc__)

    @staticmethod
    def _de_docstringify(string: str) -> str:
        """de-formats docstring"""
        for character in ['\n', '\t']:
            string = string.replace(character, '')
        for character in ['    ']:
            string = string.replace(character, ' ')
        return string

    @classmethod
    def _indent_string_list(cls, lst: List[str]) -> List[str]:
        """indents the provided list of strings by the indent of the instance"""
        out = []
        for string in lst:
            out.append(cls.YAML_INDENT + string)
        return out

    def get_parameter_string_list(self, **overrides) -> List[str]:
        """
        Returns a list of parameter strings for the instance.

        :param overrides: optional overrides for parameter values
        """
        lines = []
        for name, params in self.yaml_parameters.items():
            if params.include is False:
                continue
            docstring = self._get_inst_prop_doc(name) or params.docstring
            if docstring is not None:
                lines.append(f'# {docstring}')
            # retrieve value from object
            value = params.get_value(self, name, **overrides)
            if value is not None:
                # if the value is a string then surround the value with " "
                value = f'"{value}"' if type(value) == str else value
            lines.append(f'{params.kwarg_alias or name}: {value if value is not None else "null"}')
            lines.append('')  # add extra line
        for sub_config in self.sub_configurations:
            instance: YAMLConfig = getattr(self, sub_config, None)
            if instance is None:
                continue
            lines.extend(instance.get_parameter_string_list(**overrides))
        if type(self.yaml_attributes) is dict:
            for attr_name, deriv_class in self.yaml_attributes.items():
                instance: YAMLConfig = getattr(self, attr_name, None)
                if instance is None:
                    continue
                lines.append(f'{attr_name}: ')
                lines.extend(
                    self._indent_string_list(instance.get_parameter_string_list())
                )
        lines.append('')  # add extra end-of-config line
        return lines

    def get_current_kwargs(self) -> dict:
        """gets the current values as a dictionary for kwarg handling"""
        out = {}
        for name, params in self.yaml_parameters.items():
            if params.include is False:
                continue
            value = getattr(self, name, None)
            if value is None and params.allow_null_values is False:
                value = params.default_value
            if params.typecast is not None and value is not None:
                value = params.typecast(value)
            out[params.kwarg_alias or name] = value
        if type(self.sub_configurations) is dict:
            for sub_config in self.sub_configurations:
                instance: YAMLConfig = getattr(self, sub_config, None)
                if instance is None:
                    continue
                out.update(**instance.get_current_kwargs())
        if type(self.yaml_attributes) is dict:
            for attr in self.yaml_attributes:
                instance: YAMLConfig = getattr(self, attr, None)
                if instance is None:
                    kwargs = {}
                else:
                    kwargs = instance.get_current_kwargs()
                out[attr] = kwargs
        return out

    def get_full_yaml_string_list(self, **overrides) -> List[str]:
        """
        Returns a list of correctly formatted strings to represent the instance.

        :param overrides: optional overrides for parameter values
        """
        lines = []
        if self.YAML_TREE_DOCSTRING is not None:
            lines.append(f'# {self.YAML_TREE_DOCSTRING}')
        lines.append(f'{self.YAML_TREE_NAME}:')
        lines.extend(
            self._indent_string_list(self.get_parameter_string_list(**overrides))
        )
        return lines

    def save_parameters_to_yaml(self,
                                file_path='di_config.yaml',
                                mode='a',
                                **overrides,
                                ):
        """
        Writes the instance parameters to file.

        :param file_path: path to destination file
        :param mode: write mode (a or w)
        :param overrides: optional overrides for parameter values
        """
        with open(file_path, mode) as f:
            f.write(
                '\n'.join(self.get_full_yaml_string_list(**overrides))
            )

    def apply_parameters(self, _raise_on_error: bool = None, **kwargs) -> MutableMapping[str, Exception]:
        """
        Applies parameters to the instance based on key values in the instance. The keywords must match exactly to the
        parameters defined in the class yaml_parameters.

        :param _raise_on_error: flag to control whether an error should be raised if an error is encountered applying
            a parameter
        :param kwargs: value updates
        :return: dict of keys which encountered errors applying
        """
        _raise_on_error = _raise_on_error if _raise_on_error is not None else self.APPLY_PARAMETERS_RAISE
        out = {}
        for name, params in self.yaml_parameters.items():
            # if value is defined and instance has this attribute, update the instance value
            if (params.kwarg_alias or name) in kwargs and hasattr(self, name):
                val = kwargs[params.kwarg_alias or name]
                # dont try to typecast None because an error will be thrown
                if val is not None and params.typecast is not None:
                    try:
                        val = params.typecast(val)
                    except (TypeError, ValueError) as e:
                        msg = f'unable to cast {params.kwarg_alias or name} value {val} using typecast {params.typecast}: {e}'
                        logger.error(msg)
                        out[name] = e
                        if _raise_on_error:
                            raise ValueError(msg)
                try:
                    setattr(self, name, val)
                except Exception as e:
                    logger.error(f'failed to set attribute {params.kwarg_alias or name} to {val}: {e}')
                    out[name] = e
                    if _raise_on_error:
                        raise e
        # pass through kwargs to sub-instances
        for sub_config in self.sub_configurations:
            instance: YAMLConfig = getattr(self, sub_config, None)
            if instance is None:
                continue
            out[sub_config] = instance.apply_parameters(_raise_on_error=_raise_on_error, **kwargs)
        # pass through kwargs to attributes
        for attr in self.yaml_attributes:
            if attr not in kwargs:
                continue
            instance: YAMLConfig = getattr(self, attr, None)
            if instance is None:
                continue
            out[attr] = instance.apply_parameters(_raise_on_error=_raise_on_error, **kwargs[attr])
        return out

    def apply_parameters_no_raise(self, **kwargs) -> MutableMapping[str, Exception]:
        """applies parameters to the instance without raising on errors"""
        return self.apply_parameters(
            _raise_on_error=False,
            **kwargs,
        )

    @classmethod
    def validate_parameters(cls, **kwargs) -> Dict:
        """
        Method for validating parameters against their type cast. Defined yaml parameters will be referenced for their
        type-cast in order to perform the validation. If there are any errors, they should be included in the output
        dictionary with an appropriate error string indicating what went wrong.

        :param kwargs: keyword arguments to validate
        :return: dictionary of any error messages and their associated parameter
        """
        out = {}
        for name, params in cls.yaml_parameters.items():
            key_name = params.kwarg_alias or name
            # if value is defined and instance has this attribute, update the instance value
            if key_name in kwargs:
                val = kwargs[key_name]
                if val is not None and params.typecast is not None:
                    try:
                        # try type casting the value
                        params.typecast(val)
                    except Exception as e:
                        # if there was an error, report that error as a string in the outgoing dictionary
                        out[key_name] = str(e)
        # pass through kwargs to sub-instances
        if type(cls.sub_configurations) is dict:
            for deriv_class in cls.sub_configurations.values():
                out.update(
                    deriv_class.validate_parameters(**kwargs)
                )
        # pass through kwargs to attributes
        if type(cls.yaml_attributes) is dict:
            for key, deriv_class in cls.yaml_attributes.items():
                if key not in kwargs:
                    continue
                out[key] = deriv_class.validate_parameters(**kwargs[key])
        return out

    @classmethod
    def get_pydantic_model(cls) -> BaseModel:
        """creates a pydantic model from the YAMLConfig instance"""
        kwargs = {}
        for name, params in cls.yaml_parameters.items():
            value = params.default_value
            if params.typecast is not None and value is not None:
                value = params.typecast(value)
            kwargs[params.kwarg_alias or name] = Field(
                value,
                title=params.kwarg_alias or name,
                description=params.docstring,
            )
        return create_model(
            f'{cls.__name__}Model',
            **kwargs,
        )

    @classmethod
    def get_pydantic_hint_model(cls) -> BaseModel:
        """
        creates a pydantic model based on the YAMLConfig which specifies None as the default value and includes the
        default value in the description string. This hint model is useful for generating JSON schema for FAST API
        type hints
        """
        kwargs = {}
        for name, params in cls.yaml_parameters.items():
            value = params.default_value
            if params.typecast is not None and value is not None:
                value = params.typecast(value)
            kwargs[params.kwarg_alias or name] = (type(value), None)

        class Config:
            """custom schema configuration"""
            schema_extra = {}

        schema_extra = Config.schema_extra
        schema_extra['properties'] = {}
        for name, params in cls.yaml_parameters.items():
            value = params.default_value
            if params.typecast is not None and value is not None:
                value = params.typecast(value)
            schema_extra['properties'][name] = {
                'title': params.kwarg_alias or name,
                'description': (cls._get_cls_prop_doc(name) or params.docstring or '') + f" (default: {value})",
            }
        # create the model
        out = create_model(
            f'{cls.__name__}Model',
            **kwargs,
            __config__=Config,
        )
        return out

    @classmethod
    def get_default_kwargs(cls) -> dict:
        """gets the default keyword arguments for the class"""
        out = {}
        for name, params in cls.yaml_parameters.items():
            value = params.default_value
            if params.typecast is not None and value is not None:
                value = params.typecast(value)
            out[params.kwarg_alias or name] = value
        if type(cls.sub_configurations) is dict:
            for attr_name, deriv_class in cls.sub_configurations.items():
                base_kwargs = deriv_class.get_default_kwargs()
                if attr_name in cls.sub_configuration_aliases:
                    for key, alias in cls.sub_configuration_aliases[attr_name].items():
                        base_kwargs[alias] = base_kwargs[key]
                        del base_kwargs[key]
                out.update(**base_kwargs)
        if type(cls.yaml_attributes) is dict:
            for attr_name, deriv_class in cls.yaml_attributes.items():
                out[attr_name] = deriv_class.get_default_kwargs()
        return out

    @classmethod
    def get_default_parameter_string_list(cls,
                                          kwarg_aliases: MutableMapping[str, str] = None,
                                          **overrides,
                                          ) -> List[str]:
        """
        Returns a list of default parameter strings for the class

        :param kwarg_aliases: kwarg aliases for subconfigurations
        :param overrides: optional overrides for parameter values
        """
        lines = []
        for name, params in cls.yaml_parameters.items():
            docstring = cls._get_cls_prop_doc(name) or params.docstring
            if docstring is not None:
                lines.append(f'# {docstring}')
            if name in overrides:
                value = overrides.get(name)
            else:
                value = params.default_value
            if value is not None:
                value = params.typecast(value) if params.typecast is not None else value
                # if the value is a string then surround the value with " "
                value = f'"{value}"' if type(value) == str else value
            if kwarg_aliases is not None and name in kwarg_aliases:
                specified_name = kwarg_aliases[name]
            elif params.kwarg_alias is not None:
                specified_name = params.kwarg_alias
            else:
                specified_name = name
            lines.append(f'{specified_name}: {value if value is not None else "null"}')
            lines.append('')  # add extra line
        if type(cls.sub_configurations) is dict:
            for attr_name, deriv_class in cls.sub_configurations.items():
                lines.extend(
                    deriv_class.get_default_parameter_string_list(
                        kwarg_aliases=cls.sub_configuration_aliases.get(attr_name, None),
                        **overrides
                    )
                )
        if type(cls.yaml_attributes) is dict:
            for attr_name, deriv_class in cls.yaml_attributes.items():
                lines.append(f'{attr_name}: ')
                lines.extend(
                    cls._indent_string_list(deriv_class.get_default_parameter_string_list())
                )
        lines.append('')  # add extra end-of-config line
        return lines

    @classmethod
    def get_class_default_yaml_string_list(cls, **overrides) -> List[str]:
        """
        Retrieves the yaml string for default values of the class

        :param overrides: optional overrides for parameter values
        """
        lines = []
        if cls.YAML_TREE_DOCSTRING is not None:
            lines.append(f'# {cls.YAML_TREE_DOCSTRING}')
        lines.append(f'{cls.YAML_TREE_NAME}:')
        lines.extend(
            cls._indent_string_list(cls.get_default_parameter_string_list(**overrides))
        )
        return lines

    @classmethod
    def save_default_parameters_to_yaml(cls,
                                        file_path='di_config.yaml',
                                        mode='a',
                                        **overrides,
                                        ):
        """
        Saves the default class configuration values to YAML

        :param file_path: path to destination file
        :param mode: write mode (a or w)
        :param overrides: optional overrides for parameter values
        """
        with open(file_path, mode) as f:
            f.write(
                '\n'.join(cls.get_class_default_yaml_string_list(**overrides))
            )
