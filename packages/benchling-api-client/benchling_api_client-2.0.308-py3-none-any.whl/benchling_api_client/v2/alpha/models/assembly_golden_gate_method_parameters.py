from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.assembly_golden_gate_method_parameters_fragment_production_method import (
    AssemblyGoldenGateMethodParametersFragmentProductionMethod,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssemblyGoldenGateMethodParameters")


@attr.s(auto_attribs=True, repr=False)
class AssemblyGoldenGateMethodParameters:
    """  """

    _fragment_production_method: Union[
        Unset, AssemblyGoldenGateMethodParametersFragmentProductionMethod
    ] = UNSET
    _maximum_primer_pair_melting_temperature_difference: Union[Unset, float] = UNSET
    _minimum_binding_region_length: Union[Unset, float] = UNSET
    _minimum_binding_region_melting_temperature: Union[Unset, float] = UNSET
    _pre_recognition_site_bases: Union[Unset, str] = UNSET
    _pre_recognition_site_length: Union[Unset, float] = UNSET
    _type2_s_restriction_enzyme_id: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("fragment_production_method={}".format(repr(self._fragment_production_method)))
        fields.append(
            "maximum_primer_pair_melting_temperature_difference={}".format(
                repr(self._maximum_primer_pair_melting_temperature_difference)
            )
        )
        fields.append("minimum_binding_region_length={}".format(repr(self._minimum_binding_region_length)))
        fields.append(
            "minimum_binding_region_melting_temperature={}".format(
                repr(self._minimum_binding_region_melting_temperature)
            )
        )
        fields.append("pre_recognition_site_bases={}".format(repr(self._pre_recognition_site_bases)))
        fields.append("pre_recognition_site_length={}".format(repr(self._pre_recognition_site_length)))
        fields.append("type2_s_restriction_enzyme_id={}".format(repr(self._type2_s_restriction_enzyme_id)))
        return "AssemblyGoldenGateMethodParameters({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        fragment_production_method: Union[Unset, int] = UNSET
        if not isinstance(self._fragment_production_method, Unset):
            fragment_production_method = self._fragment_production_method.value

        maximum_primer_pair_melting_temperature_difference = (
            self._maximum_primer_pair_melting_temperature_difference
        )
        minimum_binding_region_length = self._minimum_binding_region_length
        minimum_binding_region_melting_temperature = self._minimum_binding_region_melting_temperature
        pre_recognition_site_bases = self._pre_recognition_site_bases
        pre_recognition_site_length = self._pre_recognition_site_length
        type2_s_restriction_enzyme_id = self._type2_s_restriction_enzyme_id

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if fragment_production_method is not UNSET:
            field_dict["fragmentProductionMethod"] = fragment_production_method
        if maximum_primer_pair_melting_temperature_difference is not UNSET:
            field_dict[
                "maximumPrimerPairMeltingTemperatureDifference"
            ] = maximum_primer_pair_melting_temperature_difference
        if minimum_binding_region_length is not UNSET:
            field_dict["minimumBindingRegionLength"] = minimum_binding_region_length
        if minimum_binding_region_melting_temperature is not UNSET:
            field_dict["minimumBindingRegionMeltingTemperature"] = minimum_binding_region_melting_temperature
        if pre_recognition_site_bases is not UNSET:
            field_dict["preRecognitionSiteBases"] = pre_recognition_site_bases
        if pre_recognition_site_length is not UNSET:
            field_dict["preRecognitionSiteLength"] = pre_recognition_site_length
        if type2_s_restriction_enzyme_id is not UNSET:
            field_dict["type2SRestrictionEnzymeId"] = type2_s_restriction_enzyme_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_fragment_production_method() -> Union[
            Unset, AssemblyGoldenGateMethodParametersFragmentProductionMethod
        ]:
            fragment_production_method = UNSET
            _fragment_production_method = d.pop("fragmentProductionMethod")
            if _fragment_production_method is not None and _fragment_production_method is not UNSET:
                try:
                    fragment_production_method = AssemblyGoldenGateMethodParametersFragmentProductionMethod(
                        _fragment_production_method
                    )
                except ValueError:
                    fragment_production_method = (
                        AssemblyGoldenGateMethodParametersFragmentProductionMethod.of_unknown(
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
                Union[Unset, AssemblyGoldenGateMethodParametersFragmentProductionMethod], UNSET
            )

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

        def get_minimum_binding_region_length() -> Union[Unset, float]:
            minimum_binding_region_length = d.pop("minimumBindingRegionLength")
            return minimum_binding_region_length

        try:
            minimum_binding_region_length = get_minimum_binding_region_length()
        except KeyError:
            if strict:
                raise
            minimum_binding_region_length = cast(Union[Unset, float], UNSET)

        def get_minimum_binding_region_melting_temperature() -> Union[Unset, float]:
            minimum_binding_region_melting_temperature = d.pop("minimumBindingRegionMeltingTemperature")
            return minimum_binding_region_melting_temperature

        try:
            minimum_binding_region_melting_temperature = get_minimum_binding_region_melting_temperature()
        except KeyError:
            if strict:
                raise
            minimum_binding_region_melting_temperature = cast(Union[Unset, float], UNSET)

        def get_pre_recognition_site_bases() -> Union[Unset, str]:
            pre_recognition_site_bases = d.pop("preRecognitionSiteBases")
            return pre_recognition_site_bases

        try:
            pre_recognition_site_bases = get_pre_recognition_site_bases()
        except KeyError:
            if strict:
                raise
            pre_recognition_site_bases = cast(Union[Unset, str], UNSET)

        def get_pre_recognition_site_length() -> Union[Unset, float]:
            pre_recognition_site_length = d.pop("preRecognitionSiteLength")
            return pre_recognition_site_length

        try:
            pre_recognition_site_length = get_pre_recognition_site_length()
        except KeyError:
            if strict:
                raise
            pre_recognition_site_length = cast(Union[Unset, float], UNSET)

        def get_type2_s_restriction_enzyme_id() -> Union[Unset, str]:
            type2_s_restriction_enzyme_id = d.pop("type2SRestrictionEnzymeId")
            return type2_s_restriction_enzyme_id

        try:
            type2_s_restriction_enzyme_id = get_type2_s_restriction_enzyme_id()
        except KeyError:
            if strict:
                raise
            type2_s_restriction_enzyme_id = cast(Union[Unset, str], UNSET)

        assembly_golden_gate_method_parameters = cls(
            fragment_production_method=fragment_production_method,
            maximum_primer_pair_melting_temperature_difference=maximum_primer_pair_melting_temperature_difference,
            minimum_binding_region_length=minimum_binding_region_length,
            minimum_binding_region_melting_temperature=minimum_binding_region_melting_temperature,
            pre_recognition_site_bases=pre_recognition_site_bases,
            pre_recognition_site_length=pre_recognition_site_length,
            type2_s_restriction_enzyme_id=type2_s_restriction_enzyme_id,
        )

        return assembly_golden_gate_method_parameters

    @property
    def fragment_production_method(self) -> AssemblyGoldenGateMethodParametersFragmentProductionMethod:
        if isinstance(self._fragment_production_method, Unset):
            raise NotPresentError(self, "fragment_production_method")
        return self._fragment_production_method

    @fragment_production_method.setter
    def fragment_production_method(
        self, value: AssemblyGoldenGateMethodParametersFragmentProductionMethod
    ) -> None:
        self._fragment_production_method = value

    @fragment_production_method.deleter
    def fragment_production_method(self) -> None:
        self._fragment_production_method = UNSET

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
    def minimum_binding_region_length(self) -> float:
        """ Minimum length of the primer binding region. """
        if isinstance(self._minimum_binding_region_length, Unset):
            raise NotPresentError(self, "minimum_binding_region_length")
        return self._minimum_binding_region_length

    @minimum_binding_region_length.setter
    def minimum_binding_region_length(self, value: float) -> None:
        self._minimum_binding_region_length = value

    @minimum_binding_region_length.deleter
    def minimum_binding_region_length(self) -> None:
        self._minimum_binding_region_length = UNSET

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
    def pre_recognition_site_bases(self) -> str:
        """ Specific base pairs to insert before the type IIS enzyme recognition site. """
        if isinstance(self._pre_recognition_site_bases, Unset):
            raise NotPresentError(self, "pre_recognition_site_bases")
        return self._pre_recognition_site_bases

    @pre_recognition_site_bases.setter
    def pre_recognition_site_bases(self, value: str) -> None:
        self._pre_recognition_site_bases = value

    @pre_recognition_site_bases.deleter
    def pre_recognition_site_bases(self) -> None:
        self._pre_recognition_site_bases = UNSET

    @property
    def pre_recognition_site_length(self) -> float:
        """ Number of base pairs to insert before the type IIS enzyme recognition site. """
        if isinstance(self._pre_recognition_site_length, Unset):
            raise NotPresentError(self, "pre_recognition_site_length")
        return self._pre_recognition_site_length

    @pre_recognition_site_length.setter
    def pre_recognition_site_length(self, value: float) -> None:
        self._pre_recognition_site_length = value

    @pre_recognition_site_length.deleter
    def pre_recognition_site_length(self) -> None:
        self._pre_recognition_site_length = UNSET

    @property
    def type2_s_restriction_enzyme_id(self) -> str:
        if isinstance(self._type2_s_restriction_enzyme_id, Unset):
            raise NotPresentError(self, "type2_s_restriction_enzyme_id")
        return self._type2_s_restriction_enzyme_id

    @type2_s_restriction_enzyme_id.setter
    def type2_s_restriction_enzyme_id(self, value: str) -> None:
        self._type2_s_restriction_enzyme_id = value

    @type2_s_restriction_enzyme_id.deleter
    def type2_s_restriction_enzyme_id(self) -> None:
        self._type2_s_restriction_enzyme_id = UNSET
