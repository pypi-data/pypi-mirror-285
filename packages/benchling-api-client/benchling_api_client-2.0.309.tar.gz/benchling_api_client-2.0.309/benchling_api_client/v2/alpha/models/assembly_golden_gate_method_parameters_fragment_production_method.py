from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssemblyGoldenGateMethodParametersFragmentProductionMethod(Enums.KnownString):
    PRIMER_PAIR = "PRIMER_PAIR"
    EXISTING_CUT_SITES = "EXISTING_CUT_SITES"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssemblyGoldenGateMethodParametersFragmentProductionMethod":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AssemblyGoldenGateMethodParametersFragmentProductionMethod must be a string (encountered: {val})"
            )
        newcls = Enum("AssemblyGoldenGateMethodParametersFragmentProductionMethod", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssemblyGoldenGateMethodParametersFragmentProductionMethod, getattr(newcls, "_UNKNOWN"))
