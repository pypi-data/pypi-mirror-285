from dkist_fits_specifications.utils import schema_type_hint
from dkist_fits_specifications.utils.spec_processors.expansion import expand_schema
from dkist_fits_specifications.utils.spec_processors.expansion import ExpansionIndex


def expand_naxis(naxis: int, schema: schema_type_hint) -> schema_type_hint:
    naxis_range = range(1, naxis + 1)
    n_expansion = ExpansionIndex(index="n", size=1, values=naxis_range)
    i_expansion = ExpansionIndex(index="i", size=1, values=naxis_range)
    j_expansion = ExpansionIndex(index="j", size=1, values=naxis_range)
    pp_expansion = ExpansionIndex(index="pp", size=2, values=[1, 10, 25, 75, 90, 95, 98, 99])
    expansions = [n_expansion, i_expansion, j_expansion, pp_expansion]
    return expand_schema(schema=schema, expansions=expansions)


def expand_index_d(schema: schema_type_hint, *, DNAXIS: int, **kwargs) -> schema_type_hint:
    d_expansion = ExpansionIndex(index="d", size=1, values=range(1, DNAXIS + 1))
    return expand_schema(schema=schema, expansions=[d_expansion])
