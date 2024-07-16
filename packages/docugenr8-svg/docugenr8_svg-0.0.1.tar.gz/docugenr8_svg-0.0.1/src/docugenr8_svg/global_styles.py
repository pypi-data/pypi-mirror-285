from docugenr8_svg.css_style import CssStyle
from docugenr8_svg.selector_functions import match_complex_selector_with_element
from docugenr8_svg.svg_attr import SvgAttr
from docugenr8_svg.svg_element import SvgElement


class GlobalStyles:
    def __init__(self) -> None:
        self.root: SvgElement | None = None
        self.styles: list[CssStyle] = []
        self.invalid_styles: list[CssStyle] = []

    def add_root(self, svg_root: SvgElement) -> None:
        self.root = svg_root

    def add_styles(self, css_styles: list[CssStyle]) -> None:
        self.styles.extend(css_styles)

    def apply_styles(self, svg_element: SvgElement | None = None) -> None:
        if svg_element is None:
            svg_element = self.root
        for style in self.styles:
            if match_complex_selector_with_element(style.selector, svg_element):
                if style.attr in svg_element.attributes:
                    svg_element.attributes[style.attr].apply_value(style.value, style.specificity)
                else:
                    svg_element.attributes[style.attr] = SvgAttr(style.value, style.specificity)
        for svg_child in svg_element.children:
            self.apply_styles(svg_child)
