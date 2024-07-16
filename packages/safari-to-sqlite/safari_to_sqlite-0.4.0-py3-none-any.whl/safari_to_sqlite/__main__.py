#!/usr/bin/env python

import logging
import time
from collections.abc import Iterable
from pathlib import Path
from socket import gethostname
from sys import argv, stderr

from loguru import logger

from safari_to_sqlite.blacklist import filter_blacklist
from safari_to_sqlite.download import BATCH_SIZE, extract_bodies
from safari_to_sqlite.history import read_history
from safari_to_sqlite.more_itertools import chunked
from safari_to_sqlite.safari import get_safari_tabs
from safari_to_sqlite.turso import get_auth_creds_from_json, save_auth, turso_setup

from .datastore import Datastore, TabRow


def auth(auth_path: str) -> None:
    """Save authentication credentials to a JSON file."""
    turso_url = input(
        "Enter your Turso database URL e.g. libsql://<yours>.turso.io\n"
        "(Leave this blank to start new DB setup)\n> ",
    )
    if turso_url == "":
        (turso_url, turso_auth_token) = turso_setup()
        save_auth(auth_path, turso_url, turso_auth_token)
    elif not turso_url.startswith("libsql://"):
        logger.error("Invalid libsql URL, please try again.")
        return
    else:
        turso_auth_token = input(
            "Enter your Turso database token\n"
            "(Create this by running `turso db tokens create <your DB>`)\n> ",
        )
        save_auth(auth_path, turso_url, turso_auth_token)


def save(
    db_path: str,
    auth_json: str,
) -> Datastore:
    """Save Safari tabs to SQLite database."""
    host = gethostname()
    first_seen = int(time.time())
    logger.info(f"Loading tabs from Safari for {host}...")

    tabs = get_safari_tabs(host, first_seen)
    logger.info(f"Finished loading tabs, connecting to database: {db_path}")

    db = _insert_tabs(db_path, auth_json, tabs)
    request_missing_bodies(db, auth_json)
    return db


def _insert_tabs(db_path: str, auth_json: str, tabs: Iterable[TabRow]) -> Datastore:
    tabs = [tab for tab in tabs if filter_blacklist(tab.url)]
    logger.info(f"Found {len(tabs)} tabs")
    db = Datastore(db_path, **get_auth_creds_from_json(auth_json))
    db.insert_tabs(tabs)
    return db


def _configure_logging() -> None:
    # Ours
    logger.remove()
    logger.add(
        stderr,
        colorize=True,
        format="{time:HH:mm:ss.SS} | <level>{message}</level>",
    )
    # Turso
    replication_logger = logging.getLogger("libsql_replication")
    remote_client_logger = logging.getLogger("libsql.replication.remote_client")
    replication_logger.setLevel(logging.WARNING)
    remote_client_logger.setLevel(logging.WARNING)


def request_missing_bodies(db_path: str | Datastore, auth_json: str) -> Datastore:
    """Request body when missing and save extracted contents."""
    db: Datastore = (
        db_path
        if isinstance(db_path, Datastore)
        else Datastore(db_path, **get_auth_creds_from_json(auth_json))
    )
    needs_scraping = db.find_empty_bodies()
    logger.info(f"Found {len(needs_scraping)} URLs to scrape")
    logger.info(f"Parallelizing extraction with batch size: {BATCH_SIZE}")
    for batch in chunked(needs_scraping, BATCH_SIZE):
        successes, errors = extract_bodies(batch)
        logger.info(f"Extracted: {len(successes)}")
        if (len_errors := len(errors)) > 0:
            logger.warning(f"Errors: {len_errors}")
        db.update_bodies(successes)
        db.update_scrape_statuses(errors)
    return db


def save_history(db_path: str, auth_json: str) -> Datastore:
    """Save complete Safari history to SQLite database."""
    return _insert_tabs(db_path, auth_json, read_history())


def main() -> None:
    """Start main entry point."""
    _configure_logging()
    db_default = str(Path.home() / "Documents/tabs.db")
    auth_default = "auth.json"
    if len(argv) == 1 or argv[1].endswith(".db"):
        db_path = argv[1] if len(argv) > 1 else db_default
        auth_path = argv[2] if len(argv) > 2 else auth_default  # noqa: PLR2004
        db = save(db_path, auth_path)
    elif argv[1] == "auth":
        db = None
        auth_path = argv[1] if len(argv) > 1 else auth_default
        auth(auth_path)
    elif argv[1] == "download":
        db_path = argv[2] if len(argv) > 2 else db_default  # noqa: PLR2004
        auth_path = argv[3] if len(argv) > 3 else auth_default  # noqa: PLR2004
        db = request_missing_bodies(db_path, auth_path)
    elif argv[1] == "history":
        db_path = argv[2] if len(argv) > 2 else db_default  # noqa: PLR2004
        auth_path = argv[3] if len(argv) > 3 else auth_default  # noqa: PLR2004
        db = save_history(db_path, auth_path)
    else:
        return
    if db:
        db.close()


if __name__ == "__main__":
    main()
