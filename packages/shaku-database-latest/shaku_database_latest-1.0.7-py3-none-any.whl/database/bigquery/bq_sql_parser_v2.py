import re
from typing import NamedTuple, Dict, List


class TableInfo(NamedTuple):
    selected_columns: List[str]
    result_columns: List[str] = []
    groupby_columns: List[str] = []
    datetime_filter: str = ""
    partition_sql: str = ""

class PartitionInfo(NamedTuple):
    unique_keys: List
    date_time_col: str
    cast_col_map: Dict[str, str] = {}
    partition_col: str = ""
    partition_start: str = ""
    partition_end: str = ""
    datetime_filter: str = ""


def __create_cast_col_sql(column_name, cast_type):
    result = f"CAST({column_name} as {cast_type})"
    return result


def generate_sql_for_bq(
    sql,
    table_info_dict: Dict[str, TableInfo],
):
    # TODO : fix partition col and select columns, have to use partition by table
    format_sql = """
        SELECT * FROM (
            SELECT
                {selected_columns},
                ROW_NUMBER()
                    OVER (PARTITION BY {unique_keys} order by {date_time_col} desc)
                    as row_number
            FROM {table}
            WHERE 
                1 = 1
                {partition_sql}
            )
            WHERE row_number = 1
    """

    def __replace_sql(match, table_info_dict, parse_head, format_sql_tmp):
        table_name = match.group(1)
        only_table_name = table_name.split(".")[-1]
        if only_table_name in table_info_dict:
            table_info = table_info_dict[only_table_name]
            partition_info = PARTITION_MAPPING_INFO[only_table_name]
            unique_keys = partition_info.unique_keys
            selected_columns = table_info.selected_columns
            selected_columns_str = ",".join(selected_columns)
            partition_sql = table_info.partition_sql
            # partition_col = partition_info.partition_col
            # partition_start = partition_info.partition_start
            # partition_end = partition_info.partition_end
            # if partition_col and partition_start and partition_end:
            #     partition_sql = (
            #         f"AND {partition_col} between {partition_start} and {partition_end}"
            #     )
            # else:
            #     partition_sql = ""
            cast_col_map = partition_info.cast_col_map
            unique_keys = [
                __create_cast_col_sql(uk, cast_col_map[uk])
                if uk in cast_col_map
                else uk
                for uk in unique_keys
            ]
            # 根据字典进行替换
            return parse_head.format(
                format_sql_tmp.format(
                    unique_keys=",".join(unique_keys),
                    date_time_col=partition_info.date_time_col,
                    table=table_name,
                    selected_columns=selected_columns_str,
                    partition_sql=partition_sql
                )
            )
        else:
            parse_head = parse_head.replace("({0})", "{0}")
            return parse_head.format(table_name)

    from_pattern = r"(?i)\bFROM\s+([^\s()]+)"
    join_pattern = r"(?i)\bJOIN\s+([^\s()]+)"
    format_sql_tmp = format_sql
    for parse_name, pattern in zip(["FROM", "JOIN"], [from_pattern, join_pattern]):
        parse_head = r"{0} ".format(parse_name) + "({0})"
        sql = re.sub(
            pattern,
            lambda match: __replace_sql(
                match, table_info_dict, parse_head, format_sql_tmp
            ),
            sql,
        )
    return sql


def create_sql_from_basic_sql(sql_input: str, table_info_dict: dict) -> str:
    # Get First Table Info as main table
    table_name = list(table_info_dict.keys())[0]

    # Get table info values
    table_info = table_info_dict[table_name]

    result_columns = table_info.result_columns
    result_columns_str = ",".join(result_columns)

    groupby_columns = table_info.groupby_columns
    groupby_columns_str = ",".join(groupby_columns)
    groupby_sql = f"GROUP BY {groupby_columns_str}"

    if datetime_filter := table_info.datetime_filter:
        datetime_filter_str = f"AND {datetime_filter}"
    else:
        datetime_filter_str = ""

    # Create basic SQL
    basic_sql = sql_input.format(
        result_columns=result_columns_str,
        groupby_sql=groupby_sql,
        datetime_filter=datetime_filter_str,
    )

    # basic SQL as input for generating final SQL
    result_sql = generate_sql_for_bq(basic_sql, table_info_dict)
    return result_sql



PARTITION_MAPPING_INFO = {
    "sales_order_level": PartitionInfo(
        unique_keys=["sale_id", "merchant_id"],
        date_time_col="bq_create_time",
    ),
    "sales_prod_level": PartitionInfo(
        unique_keys=["sale_id", "sale_price", "prod_id", "shop_id"],
        date_time_col="bq_create_time",
        cast_col_map={"sale_price": "string"},
    ),
    "mapping_table": PartitionInfo(
        unique_keys=["keys"],
        date_time_col="bq_create_time",
    ),
    "payment_info": PartitionInfo(
        unique_keys=["sale_id", "payment_method", "sale_sno"],
        date_time_col="bq_create_time",
    ),
    "material_consumption_record": PartitionInfo(
        unique_keys=["merchant_id", "shop_id", "material"],
        date_time_col="order_time",
    ),
    "sales_forecast": PartitionInfo(
        unique_keys=["merchant_id", "shop_id", "prod_id"],
        date_time_col="order_time",
    )
}
