from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.assembly_gibson_method_parameters_fragment_production_method import (
    AssemblyGibsonMethodParametersFragmentProductionMethod,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssemblyGibsonMethodParameters")


@attr.s(auto_attribs=True, repr=False)
class AssemblyGibsonMethodParameters:
    """  """

    _fragment_production_method: Union[Unset, AssemblyGibsonMethodParametersFragmentProductionMethod] = UNSET
    _maximum_homology_and_binding_region_length: Union[Unset, float] = UNSET
    _maximum_primer_pair_melting_temperature_difference: Union[Unset, float] = UNSET
    _minimum_binding_region_melting_temperature: Union[Unset, float] = UNSET
    _minimum_homology_and_binding_region_length: Union[Unset, float] = UNSET
    _minimum_primer_melting_temperature: Union[Unset, float] = UNSET

    def __repr__(self):
        fields = []
        fields.append("fragment_production_method={}".format(repr(self._fragment_production_method)))
        fields.append(
            "maximum_homology_and_binding_region_length={}".format(
                repr(self._maximum_homology_and_binding_region_length)
            )
        )
        fields.append(
            "maximum_primer_pair_melting_temperature_difference={}".format(
                repr(self._maximum_primer_pair_melting_temperature_difference)
            )
        )
        fields.append(
            "minimum_binding_region_melting_temperature={}".format(
                repr(self._minimum_binding_region_melting_temperature)
            )
        )
        fields.append(
            "minimum_homology_and_binding_region_length={}".format(
                repr(self._minimum_homology_and_binding_region_length)
            )
        )
        fields.append(
            "minimum_primer_melting_temperature={}".format(repr(self._minimum_primer_melting_temperature))
        )
        return "AssemblyGibsonMethodParameters({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        fragment_production_method: Union[Unset, int] = UNSET
        if not isinstance(self._fragment_production_method, Unset):
            fragment_production_method = self._fragment_production_method.value

        maximum_homology_and_binding_region_length = self._maximum_homology_and_binding_region_length
        maximum_primer_pair_melting_temperature_difference = (
            self._maximum_primer_pair_melting_temperature_difference
        )
        minimum_binding_region_melting_temperature = self._minimum_binding_region_melting_temperature
        minimum_homology_and_binding_region_length = self._minimum_homology_and_binding_region_length
        minimum_primer_melting_temperature = self._minimum_primer_melting_temperature

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if fragment_production_method is not UNSET:
            field_dict["fragmentProductionMethod"] = fragment_production_method
        if maximum_homology_and_binding_region_length is not UNSET:
            field_dict["maximumHomologyAndBindingRegionLength"] = maximum_homology_and_binding_region_length
        if maximum_primer_pair_melting_temperature_difference is not UNSET:
            field_dict[
                "maximumPrimerPairMeltingTemperatureDifference"
            ] = maximum_primer_pair_melting_temperature_difference
        if minimum_binding_region_melting_temperature is not UNSET:
            field_dict["minimumBindingRegionMeltingTemperature"] = minimum_binding_region_melting_temperature
        if minimum_homology_and_binding_region_length is not UNSET:
            field_dict["minimumHomologyAndBindingRegionLength"] = minimum_homology_and_binding_region_length
        if minimum_primer_melting_temperature is not UNSET:
            field_dict["minimumPrimerMeltingTemperature"] = minimum_primer_melting_temperature

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_fragment_production_method() -> Union[
            Unset, AssemblyGibsonMethodParametersFragmentProductionMethod
        ]:
            fragment_production_method = UNSET
            _fragment_production_method = d.pop("fragmentProductionMethod")
            if _fragment_production_method is not None and _fragment_production_method is not UNSET:
                try:
                    fragment_production_method = AssemblyGibsonMethodParametersFragmentProductionMethod(
                        _fragment_production_method
                    )
                except ValueError:
                    fragment_production_method = (
                        AssemblyGibsonMethodParametersFragmentProductionMethod.of_unknown(
                            _fragment_production_method
                        )
                    )

            return fragment_production_method

        try:
            fragment_production_method = get_fragment_production_method()
        except KeyError:
            if strict:
                raise
            fragment_production_method = cast(
                Union[Unset, AssemblyGibsonMethodParametersFragmentProductionMethod], UNSET
            )

        def get_maximum_homology_and_binding_region_length() -> Union[Unset, float]:
            maximum_homology_and_binding_region_length = d.pop("maximumHomologyAndBindingRegionLength")
            return maximum_homology_and_binding_region_length

        try:
            maximum_homology_and_binding_region_length = get_maximum_homology_and_binding_region_length()
        except KeyError:
            if strict:
                raise
            maximum_homology_and_binding_region_length = cast(Union[Unset, float], UNSET)

        def get_maximum_primer_pair_melting_temperature_difference() -> Union[Unset, float]:
            maximum_primer_pair_melting_temperature_difference = d.pop(
                "maximumPrimerPairMeltingTemperatureDifference"
            )
            return maximum_primer_pair_melting_temperature_difference

        try:
            maximum_primer_pair_melting_temperature_difference = (
                get_maximum_primer_pair_melting_temperature_difference()
            )
        except KeyError:
            if strict:
                raise
            maximum_primer_pair_melting_temperature_difference = cast(Union[Unset, float], UNSET)

        def get_minimum_binding_region_melting_temperature() -> Union[Unset, float]:
            minimum_binding_region_melting_temperature = d.pop("minimumBindingRegionMeltingTemperature")
            return minimum_binding_region_melting_temperature

        try:
            minimum_binding_region_melting_temperature = get_minimum_binding_region_melting_temperature()
        except KeyError:
            if strict:
                raise
            minimum_binding_region_melting_temperature = cast(Union[Unset, float], UNSET)

        def get_minimum_homology_and_binding_region_length() -> Union[Unset, float]:
            minimum_homology_and_binding_region_length = d.pop("minimumHomologyAndBindingRegionLength")
            return minimum_homology_and_binding_region_length

        try:
            minimum_homology_and_binding_region_length = get_minimum_homology_and_binding_region_length()
        except KeyError:
            if strict:
                raise
            minimum_homology_and_binding_region_length = cast(Union[Unset, float], UNSET)

        def get_minimum_primer_melting_temperature() -> Union[Unset, float]:
            minimum_primer_melting_temperature = d.pop("minimumPrimerMeltingTemperature")
            return minimum_primer_melting_temperature

        try:
            minimum_primer_melting_temperature = get_minimum_primer_melting_temperature()
        except KeyError:
            if strict:
                raise
            minimum_primer_melting_temperature = cast(Union[Unset, float], UNSET)

        assembly_gibson_method_parameters = cls(
            fragment_production_method=fragment_production_method,
            maximum_homology_and_binding_region_length=maximum_homology_and_binding_region_length,
            maximum_primer_pair_melting_temperature_difference=maximum_primer_pair_melting_temperature_difference,
            minimum_binding_region_melting_temperature=minimum_binding_region_melting_temperature,
            minimum_homology_and_binding_region_length=minimum_homology_and_binding_region_length,
            minimum_primer_melting_temperature=minimum_primer_melting_temperature,
        )

        return assembly_gibson_method_parameters

    @property
    def fragment_production_method(self) -> AssemblyGibsonMethodParametersFragmentProductionMethod:
        if isinstance(self._fragment_production_method, Unset):
            raise NotPresentError(self, "fragment_production_method")
        return self._fragment_production_method

    @fragment_production_method.setter
    def fragment_production_method(
        self, value: AssemblyGibsonMethodParametersFragmentProductionMethod
    ) -> None:
        self._fragment_production_method = value

    @fragment_production_method.deleter
    def fragment_production_method(self) -> None:
        self._fragment_production_method = UNSET

    @property
    def maximum_homology_and_binding_region_length(self) -> float:
        """ Maximum length, in base pairs, of the primer's binding/homology regions. """
        if isinstance(self._maximum_homology_and_binding_region_length, Unset):
            raise NotPresentError(self, "maximum_homology_and_binding_region_length")
        return self._maximum_homology_and_binding_region_length

    @maximum_homology_and_binding_region_length.setter
    def maximum_homology_and_binding_region_length(self, value: float) -> None:
        self._maximum_homology_and_binding_region_length = value

    @maximum_homology_and_binding_region_length.deleter
    def maximum_homology_and_binding_region_length(self) -> None:
        self._maximum_homology_and_binding_region_length = UNSET

    @property
    def maximum_primer_pair_melting_temperature_difference(self) -> float:
        """ Maximum difference of melting temperature between both primers in a pair. """
        if isinstance(self._maximum_primer_pair_melting_temperature_difference, Unset):
            raise NotPresentError(self, "maximum_primer_pair_melting_temperature_difference")
        return self._maximum_primer_pair_melting_temperature_difference

    @maximum_primer_pair_melting_temperature_difference.setter
    def maximum_primer_pair_melting_temperature_difference(self, value: float) -> None:
        self._maximum_primer_pair_melting_temperature_difference = value

    @maximum_primer_pair_melting_temperature_difference.deleter
    def maximum_primer_pair_melting_temperature_difference(self) -> None:
        self._maximum_primer_pair_melting_temperature_difference = UNSET

    @property
    def minimum_binding_region_melting_temperature(self) -> float:
        """ Minimum melting temperature of the primer binding region. """
        if isinstance(self._minimum_binding_region_melting_temperature, Unset):
            raise NotPresentError(self, "minimum_binding_region_melting_temperature")
        return self._minimum_binding_region_melting_temperature

    @minimum_binding_region_melting_temperature.setter
    def minimum_binding_region_melting_temperature(self, value: float) -> None:
        self._minimum_binding_region_melting_temperature = value

    @minimum_binding_region_melting_temperature.deleter
    def minimum_binding_region_melting_temperature(self) -> None:
        self._minimum_binding_region_melting_temperature = UNSET

    @property
    def minimum_homology_and_binding_region_length(self) -> float:
        """ Minimum length, in base pairs, of the primer's binding/homology regions. """
        if isinstance(self._minimum_homology_and_binding_region_length, Unset):
            raise NotPresentError(self, "minimum_homology_and_binding_region_length")
        return self._minimum_homology_and_binding_region_length

    @minimum_homology_and_binding_region_length.setter
    def minimum_homology_and_binding_region_length(self, value: float) -> None:
        self._minimum_homology_and_binding_region_length = value

    @minimum_homology_and_binding_region_length.deleter
    def minimum_homology_and_binding_region_length(self) -> None:
        self._minimum_homology_and_binding_region_length = UNSET

    @property
    def minimum_primer_melting_temperature(self) -> float:
        """ Minimum melting temperature of the whole primer. """
        if isinstance(self._minimum_primer_melting_temperature, Unset):
            raise NotPresentError(self, "minimum_primer_melting_temperature")
        return self._minimum_primer_melting_temperature

    @minimum_primer_melting_temperature.setter
    def minimum_primer_melting_temperature(self, value: float) -> None:
        self._minimum_primer_melting_temperature = value

    @minimum_primer_melting_temperature.deleter
    def minimum_primer_melting_temperature(self) -> None:
        self._minimum_primer_melting_temperature = UNSET
