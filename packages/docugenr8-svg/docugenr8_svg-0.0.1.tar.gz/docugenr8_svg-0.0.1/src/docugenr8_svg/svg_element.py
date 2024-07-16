from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from docugenr8_svg.svg_attr import SvgAttr
    from docugenr8_svg.svg_element import SvgElement


class SvgElement:
    def __init__(
        self,
        tag_name: str,
        parent: SvgElement | None = None,
    ) -> None:
        self.parent: SvgElement = parent
        self.tag_name = tag_name
        self.text: str | None = None
        self.attributes: dict[str, SvgAttr] = {}
        self.children: list[SvgElement] = []
