"""Logging configuration of the frontend and logger of the current page."""

import logging
import logging.config
from pathlib import Path

import streamlit as st
import yaml


def initialize_logs(name: str):
    """Initialize logging from a configuration file"""
    logs_dir = Path(__file__).resolve().parents[2] / "logs"
    logs_dir.mkdir(exist_ok=True)
    config_file = Path(__file__).resolve().parents[2] / "logging_config.yml"

    with open(config_file, encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    # The file name in the YAML is relative: make it absolute so the logs work
    # whatever the folder the application is launched from
    for handler in config.get("handlers", {}).values():
        if "filename" in handler:
            handler["filename"] = str(logs_dir / Path(handler["filename"]).name)
    logging.config.dictConfig(config)

    logging.info("-" * 50)
    logging.info(f"Launch FRONTEND : {name}")
    logging.info("-" * 50)


def get_page_logger(page_name: str):
    """
    Handles page tracking and returns a dedicated logger for the page.
    Updates session_state if the page has changed.
    """
    if "last_navigated_page" not in st.session_state:
        st.session_state.last_navigated_page = None
    if "logger" not in st.session_state:
        st.session_state.logger = logging.getLogger("root")

    if st.session_state.last_navigated_page != page_name:
        new_logger = logging.getLogger(page_name)

        new_logger.info(f"{st.session_state.last_navigated_page} -> {page_name}")

        st.session_state.last_navigated_page = page_name
        st.session_state.logger = new_logger

    return st.session_state.logger
