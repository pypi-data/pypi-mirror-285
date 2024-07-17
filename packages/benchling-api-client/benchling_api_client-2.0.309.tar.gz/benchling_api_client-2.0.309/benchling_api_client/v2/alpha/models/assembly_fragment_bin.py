from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.assembly_fragment_bin_bin_type import AssemblyFragmentBinBinType
from ..models.assembly_fragment_bin_fragment_production_method import (
    AssemblyFragmentBinFragmentProductionMethod,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssemblyFragmentBin")


@attr.s(auto_attribs=True, repr=False)
class AssemblyFragmentBin:
    """  """

    _bin_type: Union[Unset, AssemblyFragmentBinBinType] = UNSET
    _fragment_production_method: Union[Unset, AssemblyFragmentBinFragmentProductionMethod] = UNSET
    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("bin_type={}".format(repr(self._bin_type)))
        fields.append("fragment_production_method={}".format(repr(self._fragment_production_method)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        return "AssemblyFragmentBin({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        bin_type: Union[Unset, int] = UNSET
        if not isinstance(self._bin_type, Unset):
            bin_type = self._bin_type.value

        fragment_production_method: Union[Unset, int] = UNSET
        if not isinstance(self._fragment_production_method, Unset):
            fragment_production_method = self._fragment_production_method.value

        id = self._id
        name = self._name

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if bin_type is not UNSET:
            field_dict["binType"] = bin_type
        if fragment_production_method is not UNSET:
            field_dict["fragmentProductionMethod"] = fragment_production_method
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_bin_type() -> Union[Unset, AssemblyFragmentBinBinType]:
            bin_type = UNSET
            _bin_type = d.pop("binType")
            if _bin_type is not None and _bin_type is not UNSET:
                try:
                    bin_type = AssemblyFragmentBinBinType(_bin_type)
                except ValueError:
                    bin_type = AssemblyFragmentBinBinType.of_unknown(_bin_type)

            return bin_type

        try:
            bin_type = get_bin_type()
        except KeyError:
            if strict:
                raise
            bin_type = cast(Union[Unset, AssemblyFragmentBinBinType], UNSET)

        def get_fragment_production_method() -> Union[Unset, AssemblyFragmentBinFragmentProductionMethod]:
            fragment_production_method = UNSET
            _fragment_production_method = d.pop("fragmentProductionMethod")
            if _fragment_production_method is not None and _fragment_production_method is not UNSET:
                try:
                    fragment_production_method = AssemblyFragmentBinFragmentProductionMethod(
                        _fragment_production_method
                    )
                except ValueError:
                    fragment_production_method = AssemblyFragmentBinFragmentProductionMethod.of_unknown(
                        _fragment_production_method
                    )

            return fragment_production_method

        try:
            fragment_production_method = get_fragment_production_method()
        except KeyError:
            if strict:
                raise
            fragment_production_method = cast(
                Union[Unset, AssemblyFragmentBinFragmentProductionMethod], UNSET
            )

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        try:
            id = get_id()
        except KeyError:
            if strict:
                raise
            id = cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        try:
            name = get_name()
        except KeyError:
            if strict:
                raise
            name = cast(Union[Unset, str], UNSET)

        assembly_fragment_bin = cls(
            bin_type=bin_type,
            fragment_production_method=fragment_production_method,
            id=id,
            name=name,
        )

        return assembly_fragment_bin

    @property
    def bin_type(self) -> AssemblyFragmentBinBinType:
        if isinstance(self._bin_type, Unset):
            raise NotPresentError(self, "bin_type")
        return self._bin_type

    @bin_type.setter
    def bin_type(self, value: AssemblyFragmentBinBinType) -> None:
        self._bin_type = value

    @bin_type.deleter
    def bin_type(self) -> None:
        self._bin_type = UNSET

    @property
    def fragment_production_method(self) -> AssemblyFragmentBinFragmentProductionMethod:
        if isinstance(self._fragment_production_method, Unset):
            raise NotPresentError(self, "fragment_production_method")
        return self._fragment_production_method

    @fragment_production_method.setter
    def fragment_production_method(self, value: AssemblyFragmentBinFragmentProductionMethod) -> None:
        self._fragment_production_method = value

    @fragment_production_method.deleter
    def fragment_production_method(self) -> None:
        self._fragment_production_method = UNSET

    @property
    def id(self) -> str:
        """ Unique identifier for the bin. """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET
