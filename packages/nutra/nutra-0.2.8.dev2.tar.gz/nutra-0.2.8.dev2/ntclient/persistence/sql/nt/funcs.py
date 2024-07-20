"""nt.sqlite3 functions module"""

from ntclient.persistence.sql.nt import sql


def sql_nt_next_index(table: str) -> int:
    """Used for previewing inserts"""
    # TODO: parameterized queries
    # noinspection SqlResolve
    query = "SELECT MAX(id) as max_id FROM %s;" % table  # nosec: B608
    rows, _, _, _ = sql(query)
    return int(rows[0]["max_id"])
