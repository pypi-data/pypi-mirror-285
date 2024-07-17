"""Styles for the app."""
from enum import Enum
# Reflex import
import reflex as rx


class Color(Enum):
    """Include the palette of colors"""
    PRIMARY = "#D16F00"
    SECONDARY = "#CEF1E6"
    BACKGROUND = "#1E1E1E"
    BACKGROUND_CONTENT = "#F7F6F6"
    TEXT = "black"
    TEXT_SECONDARY = "white"


class TextSizes(Enum):
    """Include all the available sizes for the text"""
    HEADING_H1 = "3em"
    HEADING_H2 = "2em"
    HEADING_H3 = "1.7em"
    LINKS_TEXT = "1.2em"
    BODY_HOME_TEXT = "1.5em"
    SECTION_HEADING = "2.5em"
    CARD_HEADER = "1.2em"
    CARD_BODY = "1em"
    # This are the MOBILE sizes
    HEADING_H1_MOBILE = "2em"
    HEADING_H2_MOBILE = "1.5em"
    HEADING_H3_MOBILE = "1.3em"
    BODY_HOME_TEXT_MOBILE = "1.3em"
    BODY_HOME_LITTLE_TEXT_MOBILE = "1em"


BORDER_RADIUS = "0.375rem"
border = f"1px solid {rx.color('gray', 6)}"
text_color = rx.color("gray", 11)
accent_text_color = rx.color("accent", 10)
accent_color = rx.color("accent", 1)
hover_accent_color = {"_hover": {"color": accent_text_color}}
hover_accent_bg = {"_hover": {"background_color": accent_color}}
CONTENT_WIDTH_VW = "90vw"
SIDEBAR_WIDTH = "20em"

template_page_style = {"padding_top": "5em",
                       "padding_x": ["auto", "2em"], "flex": "1"}

heading_navbar = {
    "weight": "bold",
    "align": "center",
    "color": Color.PRIMARY.value,
    "font_size": TextSizes.HEADING_H3.value,
    "cursor": "pointer"
}

text_could_hover = {
    "font_size": TextSizes.LINKS_TEXT.value,
    "font_weight": "regular",
    "_hover": {
        "color": Color.PRIMARY.value,
        "font_weight": "bold"
    },
    "cursor": "pointer"
}

color_border = rx.color_mode_cond(
    light=Color.BACKGROUND_CONTENT.value, dark="#1F1F22")
border_spacer = f"1px solid {color_border}"

button_secondary_hover = {
    "color": rx.color_mode_cond(light="black", dark="white"),
    "_hover": {
        "font_weight": "bold",
        "color": Color.TEXT_SECONDARY.value,
        "background_color": Color.PRIMARY.value
    },
    "cursor": "pointer"
}

template_content_style = {
    "border_radius": BORDER_RADIUS,
    "padding": "1em",
    "margin_bottom": "2em",
    "min_height": "90vh",
}

link_style = {
    "color": accent_text_color,
    "text_decoration": "none",
    **hover_accent_color,
}

overlapping_button_style = {
    "background_color": "white",
    "border_radius": BORDER_RADIUS,
}

markdown_style = {
    "h1": lambda text: rx.heading(text, size=TextSizes.HEADING_H1.value),
    "code": lambda text: rx.code(text, color_scheme="gray"),
    "codeblock": lambda text, **props: rx.code_block(text, **props, margin_y="1em", margin_x="2em"),
    "a": lambda text, **props: rx.link(
        text,
        **props,
        font_weight="bold",
        text_decoration="underline",
        text_decoration_color=accent_text_color,
    ),
}
