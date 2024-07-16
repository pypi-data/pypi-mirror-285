from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.assembly_concatenation_method_parameters_polymer_type import (
    AssemblyConcatenationMethodParametersPolymerType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssemblyConcatenationMethodParameters")


@attr.s(auto_attribs=True, repr=False)
class AssemblyConcatenationMethodParameters:
    """  """

    _polymer_type: Union[Unset, AssemblyConcatenationMethodParametersPolymerType] = UNSET

    def __repr__(self):
        fields = []
        fields.append("polymer_type={}".format(repr(self._polymer_type)))
        return "AssemblyConcatenationMethodParameters({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        polymer_type: Union[Unset, int] = UNSET
        if not isinstance(self._polymer_type, Unset):
            polymer_type = self._polymer_type.value

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if polymer_type is not UNSET:
            field_dict["polymerType"] = polymer_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_polymer_type() -> Union[Unset, AssemblyConcatenationMethodParametersPolymerType]:
            polymer_type = UNSET
            _polymer_type = d.pop("polymerType")
            if _polymer_type is not None and _polymer_type is not UNSET:
                try:
                    polymer_type = AssemblyConcatenationMethodParametersPolymerType(_polymer_type)
                except ValueError:
                    polymer_type = AssemblyConcatenationMethodParametersPolymerType.of_unknown(_polymer_type)

            return polymer_type

        try:
            polymer_type = get_polymer_type()
        except KeyError:
            if strict:
                raise
            polymer_type = cast(Union[Unset, AssemblyConcatenationMethodParametersPolymerType], UNSET)

        assembly_concatenation_method_parameters = cls(
            polymer_type=polymer_type,
        )

        return assembly_concatenation_method_parameters

    @property
    def polymer_type(self) -> AssemblyConcatenationMethodParametersPolymerType:
        if isinstance(self._polymer_type, Unset):
            raise NotPresentError(self, "polymer_type")
        return self._polymer_type

    @polymer_type.setter
    def polymer_type(self, value: AssemblyConcatenationMethodParametersPolymerType) -> None:
        self._polymer_type = value

    @polymer_type.deleter
    def polymer_type(self) -> None:
        self._polymer_type = UNSET
