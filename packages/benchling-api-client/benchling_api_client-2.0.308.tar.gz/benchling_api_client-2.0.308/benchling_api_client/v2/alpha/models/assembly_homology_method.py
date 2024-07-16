from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.assembly_homology_method_parameters import AssemblyHomologyMethodParameters
from ..models.assembly_homology_method_type import AssemblyHomologyMethodType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssemblyHomologyMethod")


@attr.s(auto_attribs=True, repr=False)
class AssemblyHomologyMethod:
    """  """

    _parameters: Union[Unset, AssemblyHomologyMethodParameters] = UNSET
    _type: Union[Unset, AssemblyHomologyMethodType] = UNSET

    def __repr__(self):
        fields = []
        fields.append("parameters={}".format(repr(self._parameters)))
        fields.append("type={}".format(repr(self._type)))
        return "AssemblyHomologyMethod({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        parameters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._parameters, Unset):
            parameters = self._parameters.to_dict()

        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_parameters() -> Union[Unset, AssemblyHomologyMethodParameters]:
            parameters: Union[Unset, Union[Unset, AssemblyHomologyMethodParameters]] = UNSET
            _parameters = d.pop("parameters")

            if not isinstance(_parameters, Unset):
                parameters = AssemblyHomologyMethodParameters.from_dict(_parameters)

            return parameters

        try:
            parameters = get_parameters()
        except KeyError:
            if strict:
                raise
            parameters = cast(Union[Unset, AssemblyHomologyMethodParameters], UNSET)

        def get_type() -> Union[Unset, AssemblyHomologyMethodType]:
            type = UNSET
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = AssemblyHomologyMethodType(_type)
                except ValueError:
                    type = AssemblyHomologyMethodType.of_unknown(_type)

            return type

        try:
            type = get_type()
        except KeyError:
            if strict:
                raise
            type = cast(Union[Unset, AssemblyHomologyMethodType], UNSET)

        assembly_homology_method = cls(
            parameters=parameters,
            type=type,
        )

        return assembly_homology_method

    @property
    def parameters(self) -> AssemblyHomologyMethodParameters:
        if isinstance(self._parameters, Unset):
            raise NotPresentError(self, "parameters")
        return self._parameters

    @parameters.setter
    def parameters(self, value: AssemblyHomologyMethodParameters) -> None:
        self._parameters = value

    @parameters.deleter
    def parameters(self) -> None:
        self._parameters = UNSET

    @property
    def type(self) -> AssemblyHomologyMethodType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: AssemblyHomologyMethodType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET
