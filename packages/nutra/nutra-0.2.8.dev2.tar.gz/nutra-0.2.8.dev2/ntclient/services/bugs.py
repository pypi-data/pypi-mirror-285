# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 09:51:48 2024

@author: shane
"""
import os
import platform
import sqlite3
import traceback
from typing import Sequence

import ntclient.services.api
from ntclient import __db_target_nt__, __db_target_usda__, __version__
from ntclient.persistence.sql.nt import sql as sql_nt
from ntclient.utils import CLI_CONFIG

# TODO: handle mocks in tests so coverage doesn't vary when bugs exist (vs. don't)


def insert(args: list, exception: Exception) -> None:
    """Insert bug report into nt.sqlite3, return True/False."""
    print("INFO: inserting bug report...")
    try:
        sql_nt(
            """
INSERT INTO bug
  (profile_id, arguments, exc_type, exc_msg, stack, client_info, app_info, user_details)
      VALUES
        (?,?,?,?,?,?,?,?)
            """,
            (
                1,
                " ".join(args) if args else None,
                exception.__class__.__name__,
                str(exception),
                os.linesep.join(traceback.format_tb(exception.__traceback__)),
                # client_info
                str(
                    {
                        "platform": platform.system(),
                        "python_version": platform.python_version(),
                        "client_interface": "cli",
                    }
                ),
                # app_info
                str(
                    {
                        "version": __version__,
                        "version_nt_db_target": __db_target_nt__,
                        "version_usda_db_target": __db_target_usda__,
                    }
                ),
                # user_details (TODO: add user details)
                None,
            ),
        )
    except sqlite3.IntegrityError as exc:
        print("WARN: %s" % repr(exc))
        dupe_bug_insertion_exc = (
            "IntegrityError('UNIQUE constraint failed: bug.arguments, bug.stack')"
        )
        if repr(exc) == dupe_bug_insertion_exc:
            print("INFO: bug report already exists")
        else:  # pragma: no cover
            raise


def _list_bugs() -> list:
    """List all bugs, with headers as dict keys."""
    rows, _, _, _ = sql_nt("SELECT * FROM bug")
    bugs = [dict(x) for x in rows]
    return bugs


def list_bugs(show_all: bool) -> tuple:
    """List all bugs, with headers.  Returns (exit_code, bugs: list[dict])."""

    bugs = _list_bugs()
    n_bugs_total = len(bugs)
    n_bugs_unsubmitted = len([x for x in bugs if not bool(x["submitted"])])

    print("You have: %s total bugs amassed in your journey." % n_bugs_total)
    print("Of these, %s require submission/reporting." % n_bugs_unsubmitted)
    print()

    for bug in bugs:
        if not show_all:
            continue
        # Skip submitted bugs by default
        if bool(bug["submitted"]) and not CLI_CONFIG.debug:
            continue
        # Print all bug properties (except noisy stacktrace)
        print(", ".join(str(x) for x in bug.values() if "\n" not in str(x)))
        print()

    if n_bugs_unsubmitted > 0:
        print("NOTE: You have bugs awaiting submission.  Please run the report command")
    return 0, bugs


def _list_bugs_unsubmitted() -> Sequence[dict]:
    """List unsubmitted bugs, with headers as dict keys."""
    rows, _, _, _ = sql_nt("SELECT * FROM bug WHERE submitted = 0")
    bugs = [dict(x) for x in rows]
    return bugs


def submit_bugs() -> int:
    """Submit bug reports to developer, return n_submitted."""
    bugs = _list_bugs_unsubmitted()

    if len(bugs) == 0:
        print("INFO: no unsubmitted bugs found")
        return 0

    api_client = ntclient.services.api.ApiClient()

    n_submitted = 0
    print("submitting %s bug reports..." % len(bugs))
    print("_" * len(bugs))

    for bug in bugs:
        _res = api_client.post_bug(bug)

        if CLI_CONFIG.debug:  # pragma: no cover
            print(_res.json())

        # Distinguish bug which are unique vs. duplicates (someone else submitted)
        if _res.status_code == 201:
            sql_nt("UPDATE bug SET submitted = 1 WHERE id = ?", (bug["id"],))
        elif _res.status_code == 204:
            sql_nt("UPDATE bug SET submitted = 2 WHERE id = ?", (bug["id"],))
        else:  # pragma: no cover
            print("WARN: unknown status [{0}]".format(_res.status_code))
            continue

        print(".", end="", flush=True)
        n_submitted += 1

    print("submitted: {0} bugs".format(n_submitted))
    return n_submitted
