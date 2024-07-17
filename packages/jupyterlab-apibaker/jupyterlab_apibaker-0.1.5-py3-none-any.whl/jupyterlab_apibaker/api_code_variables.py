app_code = """\
import argparse

from loguru import logger
from main import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    <parser_argument>
    args = parser.parse_args()

    <variables_setup>

    <logger>

    <main_call>
"""
