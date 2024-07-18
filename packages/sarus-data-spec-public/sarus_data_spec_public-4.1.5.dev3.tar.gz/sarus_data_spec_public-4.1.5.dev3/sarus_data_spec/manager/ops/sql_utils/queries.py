from collections import defaultdict
import logging
import typing as t


try:
    # sarus sql is used only for ast_utils and translator
    from sarus_sql import ast_utils, translator
except ModuleNotFoundError:
    logger = logging.getLogger(__name__)
    logger.info("sarus_sql not available. Can't translate SQL queries")

import sarus_data_spec.type as sdt
import sarus_data_spec.typing as st


logger = logging.getLogger(__name__)


def flatten_queries_dict(
    queries: st.NestedQueryDict,
) -> t.Dict[t.Tuple[str, ...], str]:
    """Transform nested dict in linear dict where each
    key is the tuple of the nesting path"""

    final_dict: t.Dict[t.Tuple[str, ...], str] = {}

    def update_dict(
        curr_path: t.List[str],
        dict_to_update: t.Dict[t.Tuple[str, ...], t.Any],
        query_or_dict: t.Union[t.Dict[str, t.Any], t.Any],
    ) -> None:
        if isinstance(query_or_dict, dict):
            for name, sub_query in query_or_dict.items():
                update_dict(
                    curr_path=[*curr_path, name],
                    dict_to_update=dict_to_update,
                    query_or_dict=sub_query,
                )
        else:
            dict_to_update[tuple(curr_path)] = t.cast(str, query_or_dict)
        return

    for name, query_or_dict in queries.items():
        update_dict(
            query_or_dict=query_or_dict,
            curr_path=[name],
            dict_to_update=final_dict,
        )
    return final_dict


def nest_queries(
    queries: t.Dict[t.Tuple[str, ...], str],
) -> st.NestedQueryDict:
    """It transform the dict of queries according to the tuple keys:
    if queries = {
            ('a','b'):'q',
            ('a','c'):'q'
    }
    the results woulf be: {a: {b: 'q', c: 'q'}

    if queries = {
            ('a','b'):'q',
            ('e','c'):'q'
    }
    the results woulf be: {a: {b: 'q'}, e: {c: 'q'}}
    """
    intermediate: t.Dict[str, t.Dict[t.Tuple[str, ...], t.Any]] = defaultdict(
        dict
    )
    final: st.NestedQueryDict = {}
    for query_path, query in queries.items():
        if len(query_path) == 0:
            final[""] = query
        elif len(query_path) == 1:
            final[query_path[0]] = query
        else:
            intermediate[query_path[0]][query_path[1:]] = query

    for name, subdict in intermediate.items():
        final[name] = nest_queries(subdict)

    return final


def nested_dict_of_types(
    types: t.Dict[t.Tuple[str, ...], st.Type],
) -> st.NestedTypeDict:
    """Similar to nest_queries but values are sarus types instead of strings"""
    intermediate: t.Dict[str, t.Dict[t.Tuple[str, ...], t.Any]] = defaultdict(
        dict
    )
    final: st.NestedTypeDict = {}
    for type_path, type in types.items():
        if len(type_path) == 1:
            final[type_path[0]] = type
        else:
            intermediate[type_path[0]][type_path[1:]] = type

    for name, subdict in intermediate.items():
        final[name] = nested_dict_of_types(subdict)

    return final


def nested_unions_from_nested_dict_of_types(
    nested_types: st.NestedTypeDict,
) -> t.Dict[str, st.Type]:
    """create unions out of nested_types"""
    fields: t.Dict[str, st.Type] = {}
    for path_string, type_or_dict in nested_types.items():
        if isinstance(type_or_dict, dict):
            fields[path_string] = sdt.Union(
                nested_unions_from_nested_dict_of_types(type_or_dict)
            )
        else:
            fields[path_string] = t.cast(st.Type, type_or_dict)
    return fields


def translate_query_to_postgres(
    query: str, input_dialect: st.SQLDialect
) -> str:
    """It translate the query to postgres if the input the input dialect is not postgres"""

    if input_dialect != st.SQLDialect.POSTGRES:
        query = str(
            translator.translate_to_postgres(
                ast_utils.parse_query(query),
                input_dialect,
            )
        )
    return query


def translate_query_to_dialect(
    query: str, output_dialect: st.SQLDialect
) -> str:
    """It translate the query to the output dialect if is not postgres"""
    # use qrlew to
    if output_dialect != st.SQLDialect.POSTGRES:
        query = str(
            translator.translate_to_dialect(
                ast_utils.parse_query(query),
                output_dialect,
            )
        )
    return query


def translate_queries_to_postgres(
    queries: t.Dict[t.Tuple[str, ...], str], input_dialect: st.SQLDialect
) -> t.Dict[t.Tuple[str, ...], str]:
    return {
        _: translate_query_to_postgres(query, input_dialect)
        for (_, query) in queries.items()
    }
