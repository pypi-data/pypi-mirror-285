from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssemblyGibsonMethodParametersFragmentProductionMethod(Enums.KnownString):
    EXISTING_HOMOLOGY_REGIONS = "EXISTING_HOMOLOGY_REGIONS"
    EXISTING_CUT_SITES = "EXISTING_CUT_SITES"
    PRIMER_PAIR = "PRIMER_PAIR"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssemblyGibsonMethodParametersFragmentProductionMethod":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AssemblyGibsonMethodParametersFragmentProductionMethod must be a string (encountered: {val})"
            )
        newcls = Enum("AssemblyGibsonMethodParametersFragmentProductionMethod", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssemblyGibsonMethodParametersFragmentProductionMethod, getattr(newcls, "_UNKNOWN"))
