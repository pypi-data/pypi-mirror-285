"""
Home Page of the application.
"""
import reflex as rx
# Local imports
from docs import __info__ as info
from docs.components.navbar import navbar
from docs.styles import TextSizes, border_spacer


def index() -> rx.Component:
    """The home page.

    Returns:
        The UI for the home page.
    """
    return rx.box(
        # Call the navigation bar
        navbar(),
        # Call the VStack (the info inside)
        rx.vstack(
            information(),
            align="center",
            justify="center",
            # margin_x="8.5vw",
            spacing="9",
            # margin_bottom="4em",
            background="url('https://www.transparenttextures.com/patterns/asfalt-light.png')",
            animation="scroll 20s linear infinite;"
        ),
        footer(),
        width="100%",
    )

# ============================================= #
#     ADD INFORMATION TO THE HOME PAGE          #
# ============================================= #


def information():
    """Home information for the index"""
    return rx.center(
        rx.desktop_only(
            __desktop_home()
        ),
        rx.tablet_only(
            __table_home()
        ),
        rx.mobile_only(
            __mobile_home()
        ),
        min_height="80vh",
    )


def __desktop_home():
    """Desktop view for the home"""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.center(
                    rx.heading(
                        info.PROJECT_NAME,
                        font_size=TextSizes.HEADING_H1.value,
                        as_="h1",
                        line_height="1.2em",
                        justify="center",
                    ),
                    width="100%"
                ),
                rx.center(
                    rx.text(
                        info.DESCRIPTION,
                        font_size=TextSizes.BODY_HOME_TEXT.value,
                        as_="p",
                        text_align="center",
                        width="50%"
                    ),
                    width="100%"
                ),
                rx.center(
                    rx.hstack(
                        link_icons("github", info.URL_GITHUB, 35),
                        align="center"
                    ),
                    width="100%"
                )
            ),
            align="center",
            spacing="7"
        )
    )


def __table_home():
    """Table view for the home"""
    return rx.box(
        rx.vstack(
            rx.vstack(
                rx.center(
                    rx.heading(
                        info.PROJECT_NAME,
                        font_size=TextSizes.HEADING_H1.value,
                        as_="h1",
                        line_height="1.2em",
                        text_align="center"
                    ),
                    width="100%"
                ),
                rx.center(
                    rx.text(
                        info.DESCRIPTION,
                        font_size=TextSizes.BODY_HOME_TEXT.value,
                        as_="p",
                        text_align="center",
                        width="75%"
                    ),
                    width="100%"
                ),
                rx.center(
                    rx.hstack(
                        link_icons("github", info.URL_GITHUB, 35),
                        spacing="5",
                        align="center"
                    ),
                    width="100%"
                )
            ),
            align="center",
            spacing="7",
        ),
        margin_top="3em"
    )


def __mobile_home():
    """Mobile view for the home"""
    return rx.box(
        rx.vstack(
            rx.vstack(
                rx.center(
                    rx.heading(
                        info.PROJECT_NAME,
                        font_size=TextSizes.HEADING_H1_MOBILE.value,
                        as_="h1",
                        line_height="1.2em",
                        text_align="center"
                    ),
                    width="100%"
                ),
                rx.center(
                    rx.text(
                        info.DESCRIPTION,
                        font_size=TextSizes.BODY_HOME_LITTLE_TEXT_MOBILE.value,
                        as_="p",
                        text_align="center",
                        width="80%"
                    ),
                    width="100%"
                ),
                rx.center(
                    rx.hstack(
                        link_icons("github", info.URL_GITHUB, 25),
                        spacing="5",
                        justify="center",
                        align="center",
                        width="100%"
                    ),
                    width="100%"
                )
            ),
            align="center",
            spacing="7"
        ),
        margin_top="3em"
    )


def link_icons(
    icon_str: str,
    url: str,
    size: int
):
    """Link component for be inside of an Icon."""
    return rx.link(
        rx.icon(
            icon_str,
            size=size,
            color=rx.color_mode_cond(light="black", dark="white")
        ),
        href=url,
        is_external=True
    )


def footer():
    """Footer view"""
    return rx.box(
        rx.vstack(
            rx.text(
                f"Version project v{info.VERSION}",
                font_size=TextSizes.CARD_BODY.value,
                weight="bold"
            ),
            align="center"
        ),
        border_top=border_spacer,
        width="100%",
        padding_y="3em",
    )
