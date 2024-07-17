"""
Sidebar component for the entire docs page
"""
from typing import Callable, Optional
# Reflex imports
import reflex as rx
# Local imports
from docs import styles

# Add a dictionary for the SECTIONS
SIDEBAR_SECTIONS: dict[str, Callable[..., rx.Component]] = {}


def sidebar(route: str) -> rx.Component:
    """The sidebar.

    Returns:
        The sidebar component.
    """
    # Get all the decorated pages and add them to the sidebar.
    return rx.box(
        rx.desktop_only(
            __sidebar_desktop_view(route),
        ),
        rx.mobile_and_tablet(
            __sidebar_mobile_and_tablet_view(route)
        ),
        display=["none", "none", "block"],
        position="sticky",
        min_width=styles.SIDEBAR_WIDTH,
        height="100%",
        top="0px",
        border_right=styles.border,
    )

# =============================================== #
#                  Sidebar Views                  #
# =============================================== #


def __sidebar_desktop_view(route: str) -> rx.Component:
    """Desktop view of the Sidebar"""
    return rx.box(
        rx.vstack(
            sidebar_header(),
            rx.vstack(
                *[
                    sidebar_item(
                        text=SIDEBAR_SECTIONS[i]["title"],
                        url=SIDEBAR_SECTIONS[i]["route"],
                        active=SIDEBAR_SECTIONS[i]["route"] == route
                    )
                    for i in sorted(SIDEBAR_SECTIONS)
                ],
                width="100%",
                overflow_y="auto",
                align_items="flex-start",
                padding="1em",
            ),
            rx.spacer(),
            sidebar_footer(),
            height="100dvh",
        ),
    )


def __sidebar_mobile_and_tablet_view(route: str) -> rx.Component:
    """Desktop view of the Sidebar"""
    return rx.vstack(
        rx.drawer.root(
            rx.hstack(
                # Add the button to display the drawer
                rx.drawer.trigger(
                    rx.button(
                        rx.icon(
                            "menu",
                            size=50
                        ),
                    ),
                    position="fixed",
                    color=styles.Color.TEXT_SECONDARY.value,
                    background=styles.Color.BACKGROUND.value,
                    margin_right="1em",
                    margin_top="1em",
                ),
                # position="fixed",
                # justify="end",
            ),
            rx.drawer.overlay(z_index="-1"),
            # Add the portal to open in this situation.
            rx.drawer.portal(
                # Add the content
                rx.drawer.content(
                    rx.vstack(
                        # Add the button to close
                        rx.spacer(),
                        rx.hstack(
                            rx.flex(
                                rx.drawer.close(
                                    rx.button(
                                        rx.icon(
                                            "x",
                                            size=50
                                        ),
                                    ),
                                    color=styles.Color.TEXT_SECONDARY.value,
                                    background="transparent",
                                    # justify="end",
                                    # right="0"
                                ),
                                # display="fixed",
                                # flex_direction="column",
                                # float="right",
                                # right="0",
                                justify="end",
                                # align="right",
                                width="100%"
                            ),
                            position="fixed",
                            top="2.5em",
                            width="100%",
                            padding="1em",
                            # display="flex",
                            # flex_direction="column",
                            # right=0,
                            # justify="end"
                        ),
                        rx.vstack(
                            # Add the sidebar
                            sidebar_header(),
                            rx.vstack(
                                *[
                                    sidebar_item(
                                        text=SIDEBAR_SECTIONS[i]["title"],
                                        url=SIDEBAR_SECTIONS[i]["route"],
                                        active=SIDEBAR_SECTIONS[i]["route"] == route
                                    )
                                    for i in sorted(SIDEBAR_SECTIONS)
                                ],
                                width="100%",
                                align_items="flex-start",
                                padding="1em",
                            ),
                            rx.spacer(),
                            sidebar_footer(),
                            background_color=styles.Color.BACKGROUND,
                            width="100%",
                            height="100%"
                        ),
                        background_color=styles.Color.BACKGROUND,
                        right="auto",
                        width="30em"
                    ),
                )
            ),
            direction="left",
        ),
        width="100%"
    )

# =============================================== #
#               Sidebar components                #
# =============================================== #


def sidebar_header() -> rx.Component:
    """Sidebar header.

    Returns:
        The sidebar header component.
    """
    return rx.hstack(
        # The logo.
        rx.image(src="/banner.png", height="3.5em", width="8em"),
        rx.spacer(),
        rx.desktop_only(
            rx.link(
                rx.button(
                    rx.icon("github"),
                    color_scheme="gray",
                    variant="soft",
                ),
                href="https://github.com/ricardoleal20/pymath_compute",
            ),
        ),
        align="center",
        width="100%",
        border_bottom=styles.border,
        padding_x="1em",
        padding_y="2em",
    )


def sidebar_footer() -> rx.Component:
    """Sidebar footer.

    Returns:
        The sidebar footer component.
    """
    return rx.hstack(
        rx.spacer(),
        rx.link(
            rx.text("Portfolio"),
            href="https://portfolio.ricardoleal20.dev",
            color_scheme="gray",
        ),
        rx.text(" :: "),
        rx.link(
            rx.text("Code"),
            href="https://github.com/ricardoleal20/pymath_compute",
            color_scheme="gray",
        ),
        width="100%",
        border_top=styles.border,
        padding="1em",
    )


def sidebar_item(
    text: str,
    url: str,
    active: bool
) -> rx.Component:
    """Sidebar item.

    Args:
        text: The text of the item.
        url: The URL of the item.

    Returns:
        rx.Component: The sidebar item component.
    """
    return rx.link(
        rx.hstack(
            rx.text(
                text,
            ),
            bg=rx.cond(
                active,
                rx.color("accent", 2),
                "transparent",
            ),
            border=rx.cond(
                active,
                f"1px solid {rx.color('accent', 6)}",
                f"1px solid {rx.color('gray', 6)}",
            ),
            color=rx.cond(
                active,
                styles.accent_text_color,
                styles.text_color,
            ),
            align="center",
            border_radius=styles.BORDER_RADIUS,
            width="100%",
            padding="1em",
        ),
        href=url,
        width="100%",
    )


# =============================================== #
#               Sidebar decorators                #
# =============================================== #
def sidebar_section(  # pylint: disable=R0913
    page_title: str,
    route: str,
    sidebar_title: Optional[str] = None,
    description: Optional[str] = None,
    meta: Optional[list[str]] = None,
    index_position: Optional[int] = None
) -> Callable[..., rx.Component]:
    """@sidebar_section decorator.
    
    It allow us to include extra information about the components, and include
    this as a section.
    
    Args:
        - page_title: Title of the page
        - route: Route of the page (should be complete)
        - sidebar_title: Title of the sidebar section
        - description (Optional): Which description we'll give for this page
        - meta (Optional): Metadata for this page
        - index_position (Optional): The position of this element in the sidebar 
    """

    def wrapper(page_cont: Callable[..., rx.Component]) -> Callable[..., rx.Component]:
        """Internal wrapper"""

        # Create the sidebar_component here
        def sidebar_page() -> rx.Component:
            return rx.hstack(
                sidebar(route),
                rx.box(
                    rx.vstack(
                        page_cont()
                    )
                ),
                align="start",
                position="relative",
            )

        sidebar_page.__doc__ = page_cont.__doc__
        sidebar_page.__name__ = page_cont.__name__
        # Add this metadata to the sidebar page
        sidebar_page.__metadata__ = {
            "title": page_title,
            "route": route,
            "description": description,
            "meta": meta if meta else [],
        }
        sidebar_page.__sb_section__ = True

        # Based on the count, get the position of this element on the sidebar
        if index_position is None:
            position = max(SIDEBAR_SECTIONS.keys(), default=0) + 1
        else:
            position = index_position
        SIDEBAR_SECTIONS[position] = {
            "title": sidebar_title if sidebar_title else page_title,
            "route": route
        }
        return sidebar_page
    # Return the wrapper
    return wrapper
