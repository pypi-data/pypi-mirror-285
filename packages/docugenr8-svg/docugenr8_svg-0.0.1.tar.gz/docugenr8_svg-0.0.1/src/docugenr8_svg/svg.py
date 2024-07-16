from __future__ import annotations

import copy
import xml.etree.ElementTree as ET  # noqa: N817
from xml.etree.ElementTree import Element as XmlElement

from docugenr8_svg.css_style import CssStyle
from docugenr8_svg.global_styles import GlobalStyles
from docugenr8_svg.selector_functions import is_id_selector
from docugenr8_svg.specificity import Specificity
from docugenr8_svg.svg_attr import SvgAttr
from docugenr8_svg.svg_element import SvgElement


class Svg:
    def __init__(self, file_path: str) -> None:
        xml_root = ET.parse(file_path).getroot()
        self.styles: GlobalStyles = GlobalStyles()
        self.ids: dict[str, SvgElement] = {}
        self.root: SvgElement = self.extract_xml_elements(xml_root, None)
        self.styles.apply_styles(self.root)

    def extract_xml_elements(
        self,
        xml_element: XmlElement,
        parent: SvgElement | None,
    ) -> None:
        svg_element = SvgElement(xml_element.tag, parent)
        if parent is None and self.styles.root is None:
            self.styles.add_root(svg_element)
        svg_element.attributes = convert_svg_attributes(xml_element.attrib)
        if "style" in svg_element.attributes:
            formattings = extract_formatting(svg_element.attributes["style"].value)
            for formatting in formattings:
                formatting_type = formatting[0]
                formatting_value = formatting[1]
                formatting_specificity = Specificity(1, 0, 0, 0)
                svg_element.attributes[formatting_type] = SvgAttr(formatting_value, formatting_specificity)
            del svg_element.attributes["style"]
        if "id" in svg_element.attributes:
            element_id = svg_element.attributes["id"]
            self.ids[element_id.value] = svg_element
        svg_element.text = xml_element.text
        if svg_element.tag_name.endswith("use"):
            svg_element = self.convert_element_with_use(svg_element)
        for xml_child in xml_element:
            if xml_child.tag.endswith("style"):
                self.styles.add_styles(extract_css(xml_child.text))
            else:
                svg_child = self.extract_xml_elements(xml_child, svg_element)
                svg_element.children.append(svg_child)
        return svg_element

    def convert_element_with_use(self, svg_element: SvgElement) -> SvgElement:
        xlink_attrs = [value for key, value in svg_element.attributes.items() if "xlink" in key and "href" in key]
        if len(xlink_attrs) != 1:
            raise ValueError("Missing xlink:href attribute.")
        element_id = xlink_attrs[0].value
        if not is_id_selector(element_id):
            raise ValueError("The value for id is not valid.")
        element_id = element_id[1:]
        if element_id not in self.ids:
            raise ValueError(f"The element for the given id: {element_id} is not found.")
        new_element = copy.deepcopy(self.ids[element_id])
        del new_element.attributes["id"]
        new_element.parent = svg_element.parent
        for key in svg_element.attributes:
            if key.endswith("href"):
                continue
            new_element.attributes[key] = svg_element.attributes[key]
        return new_element


def convert_svg_attributes(xml_attributes: dict[str, str]) -> dict[str, SvgAttr]:
    svg_attributes: dict[str, SvgAttr] = {}
    for xml_attr_key in xml_attributes:
        svg_attributes[xml_attr_key] = SvgAttr(xml_attributes[xml_attr_key], Specificity(1, 0, 0, 0))
    return svg_attributes


def extract_css(css_string: str) -> list[CssStyle]:
    result: list[CssStyle] = []
    i = 0
    start_selector = 0
    start_format = 0
    while i < len(css_string):
        while i < len(css_string) and css_string[i] != "{":
            i += 1
        selectors = extract_selectors(css_string[start_selector:i].strip())
        start_format = i + 1
        while i < len(css_string) and css_string[i] != "}":
            i += 1
        formattings = extract_formatting(css_string[start_format:i].strip())
        for selector in selectors:
            for formatting in formattings:
                if selector != "" and formatting != "":
                    result.append(CssStyle(selector, formatting[0], formatting[1]))  # noqa: PERF401
        start_selector = i + 1
    return result


def extract_selectors(selector: str) -> list[str]:
    return [value.strip() for value in selector.split(",")]


def extract_formatting(formatting: str) -> list[tuple[str, str]]:
    lines = [value.strip() for value in formatting.split(";")]
    result = []
    for line in lines:
        if line != "" and (line.find(":") > 0):
            seperated_values = tuple(value.strip() for value in line.split(":"))
            result.append(seperated_values)
    return result
