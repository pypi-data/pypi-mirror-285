"""
Include all the documentation pages here
"""
from typing import Callable

import reflex as rx
# Import the pages
from docs.components import sidebar_section
from docs import styles  # ! DELETE ME


@sidebar_section(
    page_title="Introduction :: PyMath Docs",
    route="/docs",
    sidebar_title="Introduction"
)
def introduction() -> rx.Component:
    """Define the introduction to the package"""
    with open("docs/content/introduction.md", encoding="utf-8") as md_file:
        content = md_file.read()
    return rx.markdown(
        content,
        component_map=styles.markdown_style,
        align="center",
        margin_top="2em",
        margin_right="2em",
        margin_bottom="2em"
    )


@sidebar_section(
    page_title="Basic Usage :: PyMath Docs",
    route="/docs/basic_usage",
    sidebar_title="Basic Usage"
)
def basic_usage() -> rx.Component:
    """Define the introduction to the package"""
    with open("docs/content/basic_usage.md", encoding="utf-8") as md_file:
        content = md_file.read()
    return rx.markdown(
        content,
        component_map=styles.markdown_style,
        align="center",
        margin_top="2em",
        margin_right="2em",
        margin_bottom="2em"
    )

# Define the function that would allow us to automatize the documentation process #


def documentation_pages() -> list[Callable[..., rx.Component]]:
    """Import and return all the documentation pages"""
    # In the folder docs/content, read all the .md files available
    return [
        introduction,
        basic_usage
    ]
