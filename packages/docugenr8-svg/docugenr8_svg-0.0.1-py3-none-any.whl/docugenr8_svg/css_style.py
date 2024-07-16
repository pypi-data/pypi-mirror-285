from docugenr8_svg.selector_functions import get_specificity


class CssStyle:
    def __init__(
        self,
        selector: str,
        attr: str,
        value: str,
    ) -> None:
        self.selector = selector
        self.attr = attr
        self.value = value
        self.specificity = get_specificity(selector)
