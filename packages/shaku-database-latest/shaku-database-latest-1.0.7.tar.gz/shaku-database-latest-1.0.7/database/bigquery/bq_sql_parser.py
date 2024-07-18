import re

from typing import NamedTuple, Dict, List


class TableInfo(NamedTuple):
    unique_keys: List
    date_time_col: str
    cast_col_map: Dict[str, str] = {}


def __create_cast_col_sql(column_name, cast_type):
    result = f"CAST({column_name} as {cast_type})"
    return result


def replace_table_names(sql, replacement, table_info_dict, selected_columns_str="*", partition_sql=""):
    def __replace_sql(match, table_info_dict, parse_head, replacement_tmp):
        table_name = match.group(1)
        only_table_name = table_name.split(".")[-1]
        if only_table_name in table_info_dict:
            table_info = table_info_dict[only_table_name]
            unique_keys = table_info.unique_keys
            cast_col_map = table_info.cast_col_map
            unique_keys = [__create_cast_col_sql(uk, cast_col_map[uk]) if uk in cast_col_map else uk
                           for uk in unique_keys]
            # 根据字典进行替换
            return parse_head.format(replacement_tmp.format(unique_keys=",".join(unique_keys),
                                                            date_time_col=table_info.date_time_col,
                                                            table=table_name, selected_columns=selected_columns_str,
                                                            partition_sql=partition_sql))
        else:
            parse_head = parse_head.replace("({0})", "{0}")
            return parse_head.format(table_name)

    from_pattern = r"(?i)\bFROM\s+([^\s()]+)"
    join_pattern = r"(?i)\bJOIN\s+([^\s()]+)"
    replacement_tmp = replacement
    for parse_name, pattern in zip(["FROM", 'JOIN'], [from_pattern, join_pattern]):
        parse_head = r"{0} ".format(parse_name) + "({0})"
        sql = re.sub(pattern,
                     lambda match: __replace_sql(match, table_info_dict, parse_head, replacement_tmp), sql)
    return sql


def generate_sql_for_bq(sql, table_info: Dict[str, TableInfo], selected_columns: List[str] = None,
                        partition_col=None, partition_start=None, partition_end=None):
    # TODO : fix partition col and select columns, have to use partition by table
    format_sql = """
    SELECT * FROM (
          SELECT
              {selected_columns},
              ROW_NUMBER()
                  OVER (PARTITION BY {unique_keys} order by {date_time_col} desc)
                  as row_number
          FROM {table}
          {partition_sql}
        )
        WHERE row_number = 1
    """
    selected_columns_str = "*"
    partition_sql = ""
    if selected_columns:
        selected_columns_str = ",".join(selected_columns)
    if partition_col and partition_end and partition_start:
        partition_sql = f"{partition_col} between {partition_start} and {partition_end}"

    result_sql = replace_table_names(sql, format_sql, table_info, selected_columns_str, partition_sql)
    return result_sql
