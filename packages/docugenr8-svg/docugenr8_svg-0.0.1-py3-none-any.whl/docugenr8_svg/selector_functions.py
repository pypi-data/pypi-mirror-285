import re

from docugenr8_svg.specificity import Specificity
from docugenr8_svg.svg_attr import SvgAttr
from docugenr8_svg.svg_element import SvgElement


# Selector Functions
def get_specificity(complex_selector: str) -> Specificity:
    sum_specificity = Specificity(0, 0, 0, 0)
    composite_selectors_with_combinators = get_composite_selectors_with_combinators(complex_selector)
    composite_selectors = [
        element for index, element in enumerate(composite_selectors_with_combinators) if index % 2 == 0
    ]
    for composite_selector in composite_selectors:
        simple_selectors = get_simple_selectors(composite_selector)
        for simple_selector in simple_selectors:
            type_selector = get_type_selector(simple_selector)
            match type_selector:
                case "type":
                    sum_specificity.add(Specificity(0, 0, 0, 1))
                case "class":
                    sum_specificity.add(Specificity(0, 0, 1, 0))
                case "id":
                    sum_specificity.add(Specificity(0, 1, 0, 0))
                case "attr":
                    sum_specificity.add(Specificity(0, 0, 1, 0))
                case "pseudo-class":
                    sum_specificity.add(Specificity(0, 0, 1, 0))
                case "pseudo-element":
                    # no pseudo-elements are allowed
                    raise ValueError("Pseudo-elements not allowed.")
    return sum_specificity


def match_complex_selector_with_element(
    complex_selector: str,
    svg_element: SvgElement,
) -> bool:
    composite_selectors_with_combinators = get_composite_selectors_with_combinators(complex_selector)
    composite_selectors_with_combinators.reverse()
    first_composite_selector = composite_selectors_with_combinators.pop(0)
    if not match_composite_selector_with_element(first_composite_selector, svg_element):
        return False
    current_element = svg_element
    while len(composite_selectors_with_combinators) > 0:
        combinator = composite_selectors_with_combinators.pop(0)
        composite_selector = composite_selectors_with_combinators.pop(0)
        current_element = match_composite_selector_and_combinator_with_element(
            composite_selector,
            combinator,
            current_element,
        )
        if current_element is None:
            return False
    return True


def match_composite_selector_and_combinator_with_element(
    composite_selector: list[str],
    combinator: str,
    svg_element: SvgElement,
) -> SvgElement | None:
    # Decendant combinator
    if combinator == " ":
        current_element = svg_element.parent
        while current_element is not None:
            if not match_composite_selector_with_element(composite_selector, current_element):
                current_element = current_element.parent
            else:
                return current_element
        return None

    # Child combinator
    if combinator == ">":
        if svg_element.parent is None:
            return None
        if match_composite_selector_with_element(composite_selector, svg_element.parent):
            return svg_element.parent
        else:
            return None

    # Next-sibling combinator
    if combinator == "+":
        if svg_element.parent is None:
            return None
        if len(svg_element.parent.children) < 2:
            return None
        index = svg_element.parent.children.index(svg_element)
        if index - 1 > 0:
            sibling_element = svg_element.parent.children[index - 1]
            if match_composite_selector_with_element(composite_selector, sibling_element):
                return sibling_element
        return None

    # Subsequent-sibling combinator
    if combinator == "~":
        if svg_element.parent is None:
            return None
        if len(svg_element.parent.children) < 2:
            return None
        if index - 1 == 0:
            return None
        index = svg_element.parent.children.index(svg_element)
        for i in range(index, -1, -1):
            sibling_element = svg_element.parent.children[i]
            if match_composite_selector_with_element(composite_selector, sibling_element):
                return sibling_element
        return None


def match_composite_selector_with_element(
    composite_selector: str,
    svg_element: SvgElement,
) -> bool:
    for simple_selector in get_simple_selectors(composite_selector):
        if not match_simple_selector_with_element(simple_selector, svg_element):
            return False
    return True


def get_composite_selectors_with_combinators(complex_selector: str) -> list[str]:
    tokens: list[str] = []
    current_token = ""
    i = 0
    norm_selector = re.sub(r"\s+", " ", complex_selector).strip()

    while i < len(norm_selector):
        char = norm_selector[i]
        if char in (" ", ">", "+", "~"):
            if current_token:
                tokens.append(current_token)
                current_token = ""
            if char == " " and (i + 1) < len(norm_selector):
                if norm_selector[i + 1] in {">", "+", "~"}:
                    char = norm_selector[i + 1]
                    i += 1
            if (i + 1) < len(norm_selector):
                if norm_selector[i + 1] == " ":
                    i += 1
            tokens.append(char)
        else:
            current_token += char
        i += 1

    if current_token:
        tokens.append(current_token.strip())

    return tokens


def get_simple_selectors(composite_selector: str) -> list[str]:
    tokens: list[str] = []
    current_token = ""
    i = 0
    while i < len(composite_selector):
        char = composite_selector[i]

        if char in {".", "#", "[", "*"}:
            if current_token:
                tokens.append(current_token)
                current_token = ""
            current_token += char
        elif char in {":"}:
            if current_token:
                tokens.append(current_token)
                current_token = ""
            current_token += char
            if i + 1 < len(composite_selector):
                if composite_selector[i + 1] == ":":
                    current_token += composite_selector[i + 1]
                    i += 1
        else:
            current_token += char
        i += 1

    if current_token:
        tokens.append(current_token)

    return tokens


def match_simple_selector_with_element(
    simple_selector: str,
    element: SvgElement,
) -> bool:
    type_selector = get_type_selector(simple_selector)
    match type_selector:
        case "type":
            return element.tag_name.endswith(simple_selector)
        case "class":
            if "class" in element.attributes:
                return simple_selector[1:] == element.attributes["class"].value
            else:
                return False
        case "id":
            if "id" in element.attributes:
                return simple_selector[1:] == element.attributes["id"].value
            else:
                return False
        case "attr":
            return match_attr_selector_with_element(simple_selector, element.attributes)
        case "pseudo-class":
            return match_pseudo_class_selector_with_element(simple_selector, element)
        case "pseudo-element":
            # no pseudo-elements are allowed
            return False


def get_type_selector(simple_selector: str) -> str:
    if is_type_selector(simple_selector):
        return "type"
    if is_class_selector(simple_selector):
        return "class"
    if is_id_selector(simple_selector):
        return "id"
    if is_attribute_selector(simple_selector):
        return "attr"
    if is_pseudo_class_selector(simple_selector):
        return "pseudo-class"
    if is_pseudo_element_selector(simple_selector):
        return "pseudo-element"
    raise TypeError("CSS Selector not valid.")


def match_attr_selector_with_element(attr_selector: str, elem_attrs: dict[str, SvgAttr]) -> bool:
    attr_tokens = tokenize_attr_selector(attr_selector)
    if not len(attr_tokens) == 1 and not len(attr_tokens) == 3:
        raise ValueError(f"Attribute Selector is not valid: {attr_selector}")
    if len(attr_tokens) == 1:
        return attr_tokens[0] in elem_attrs
    if len(attr_tokens) == 3:
        attr = attr_tokens[0]
        operator = attr_tokens[1]
        value = remove_quotes(attr_tokens[2])
        if attr not in elem_attrs:
            return False
    match operator:
        case "=":
            return value == elem_attrs[attr].value
        case "*=":
            return value in elem_attrs[attr].value
        case "^=":
            return elem_attrs[attr].value.startswith(value)
        case "$=":
            return elem_attrs[attr].value.endswith(value)
        case "~=":
            attr_words = elem_attrs[attr].value.split()
            return value in attr_words
        case "|=":
            return elem_attrs[attr].value == value or elem_attrs[attr].value.startswith(value + "-")
        case _:
            raise ValueError(f"Operator in Attribute Selector is not valid: {operator}")


def match_pseudo_class_selector_with_element(
    selector: str,
    element: SvgElement,
) -> bool:
    tokens = tokenize_pseudo_class_selector(selector)
    if len(tokens) not in {1, 4}:
        raise ValueError(f"Pseudo Class Selector is not valid: {selector}")
    if len(tokens) == 4 and not (tokens[1] == "(" or tokens[3] == ")"):
        raise ValueError(f"Pseudo Class Selector is not valid: {selector}")
    if len(tokens) == 1:
        match tokens[0]:
            case "first-child":
                return element.parent.children.index(element) == 0
            case "last-child":
                return element.parent.children.index(element) == len(element.parent.children) - 1
            case "first-of-type":
                index = element.parent.children.index(element)
                for i in range(index):
                    if element.parent.children[i].tag_name == element.tag_name:
                        return False
                return True
            case "last-of-type":
                start = element.parent.children.index(element) + 1
                stop = len(element.parent.children)
                for i in range(start, stop):
                    if element.parent.children[i].tag_name == element.tag_name:
                        return False
                return True
            case "only-child":
                return len(element.parent.children) == 1
            case "only-of-type":
                num_children = len(element.parent.children)
                num_of_type = 0
                for i in range(num_children):
                    if element.parent.children[i].tag_name == element.tag_name:
                        num_of_type += 1
                return num_of_type == 1
            case "empty":
                return len(element.children) == 0
    else:
        tokens[2] = tokens[2].replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")
        equation = extract_pseudo_class_functional_notation(tokens[2])
        match tokens[0]:
            case "nth-child":
                list_of_elements: list[SvgElement] = list.copy(element.parent.children)
                index = list_of_elements.index(element) + 1
                i = 0
                iterator = calculate_functional_notation(i, equation)
                while iterator <= len(element.parent.children) and iterator >= 0:
                    if index == iterator:
                        return True
                    i += 1
                    iterator = calculate_functional_notation(i, equation)
                return False
            case "nth-last-child":
                list_of_elements: list[SvgElement] = list.copy(element.parent.children)
                list_of_elements.reverse()
                index = list_of_elements.index(element) + 1
                i = 0
                iterator = calculate_functional_notation(i, equation)
                while iterator <= len(element.parent.children) and iterator >= 0:
                    if index == iterator:
                        return True
                    i += 1
                    iterator = calculate_functional_notation(i, equation)
                return False
            case "nth-of-type":
                list_of_elements: list[SvgElement] = []
                if element.parent is None:
                    return False
                if len(element.parent.children) == 0:
                    return False
                for sibling in element.parent.children:
                    if element.tag_name == sibling.tag_name:
                        list_of_elements.append(sibling)  # noqa: PERF401
                index = list_of_elements.index(element) + 1
                i = 0
                iterator = calculate_functional_notation(i, equation)
                while iterator <= len(list_of_elements) and iterator >= 0:
                    if index == iterator:
                        return True
                    i += 1
                    iterator = calculate_functional_notation(i, equation)
                return False
            case "nth-last-of-type":
                list_of_elements: list[SvgElement] = []
                for sibling in element.parent.children:
                    if element.tag_name == sibling.tag_name:
                        list_of_elements.append(sibling)  # noqa: PERF401
                list_of_elements.reverse()
                list_of_elements.index(element)
                index = list_of_elements.index(element) + 1
                i = 0
                iterator = calculate_functional_notation(i, equation)
                while iterator <= len(list_of_elements) and iterator >= 0:
                    if index == iterator:
                        return True
                    i += 1
                    iterator = calculate_functional_notation(i, equation)
                return False
            case "not":
                raise NotImplementedError(f'Selector: "{tokens[0]}" is not implemented yet.')


def calculate_functional_notation(
    iterator: int,
    equation: tuple[int, int, str, int],
) -> int:
    if equation[2] == "+":
        return (equation[0] * equation[1]) * iterator + equation[3]
    if equation[2] == "-":
        return (equation[0] * equation[1]) * iterator - equation[3]


def extract_pseudo_class_functional_notation(
    expression: str,
) -> tuple[int, int, str, int]:
    if expression == "even":
        return (1, 2, "+", 0)
    if expression == "odd":
        return (1, 2, "+", 1)

    # prefix * a * n (operator) b
    prefix: int | None = None
    a: int | None = None
    n: bool | None = None
    operator: str | None = None
    b: int | None = None
    i = 0
    adder = ""
    while i < len(expression):
        char = expression[i]

        if prefix is None:
            if char == "+":
                prefix = 1
                i += 1
                continue
            elif char == "-":
                prefix = -1
                i += 1
                continue
            else:
                prefix = 1
        if a is None:
            if char.isdigit():
                adder += char
                i += 1
                continue
            elif adder:
                a = int(adder)
                adder = ""
            else:
                a = 1
        if n is None:
            if char == "n":
                n = True
                i += 1
                continue
            else:
                n = True
        if operator is None:
            if char == "+" or char == "-":
                operator = char
                i += 1
                continue
            else:
                raise ValueError(f"Functional notation {expression} not valid.")
        if b is None:
            if char.isdigit():
                adder += char
                i += 1
                continue
            else:
                raise ValueError(f"Functional notation {expression} not valid.")

    if a is None and adder:
        a = int(adder)
        adder = ""
    if b is None and adder:
        b = int(adder)
        adder = ""

    if operator is None:
        operator = "+"
        b = 0

    return (prefix, a, operator, b)


def remove_quotes(s: str) -> str:
    if len(s) >= 2 and ((s[0] == "'" and s[-1] == "'") or (s[0] == '"' and s[-1] == '"')):
        return s[1:-1]
    else:
        return s


def tokenize_pseudo_class_selector(selector: str) -> list[str]:
    tokens: list[str] = []
    current_token = ""
    i = 0
    selector = selector[1:]
    while i < len(selector):
        char = selector[i]
        if char in {"(", ")"}:
            if current_token:
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)
        else:
            current_token += char
        i += 1
    if current_token:
        tokens.append(current_token)

    return tokens


def tokenize_attr_selector(attr_selector: str) -> list[str]:
    tokens: list[str] = []
    current_token = ""
    i = 0
    attr_selector = attr_selector[1:-1]
    while i < len(attr_selector):
        char = attr_selector[i]

        if char == "=":
            if current_token:
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)
        elif char in {"*", "^", "$", "~", "|"}:
            if current_token:
                tokens.append(current_token)
                current_token = ""
            if attr_selector[i + 1] == "=":
                tokens.append(attr_selector[i : i + 2])
                i += 1
            else:
                raise ValueError(f"Attribute Selector not valid: {attr_selector}")
        else:
            current_token += char
        i += 1

    if current_token:
        tokens.append(current_token)

    return tokens


def is_type_selector(simple_selector: str) -> bool:
    first_char = simple_selector[0]
    if first_char in {"#", ".", "["}:
        return False
    return is_valid_selector_name(simple_selector)


def is_class_selector(simple_selector: str) -> bool:
    if not simple_selector.startswith("."):
        return False
    return is_valid_selector_name(simple_selector[1:])


def is_id_selector(simple_selector: str) -> bool:
    if not simple_selector.startswith("#"):
        return False
    return is_valid_selector_name(simple_selector[1:])


def is_attribute_selector(simple_selector: str) -> bool:
    pattern = re.compile(
        r"^\[\s*"  # Opening bracket and optional whitespace
        r"[_a-zA-Z][_a-zA-Z0-9-]*"  # Attribute name
        r"(\s*"  # Optional whitespace and...
        r"([*^$|~]?=)"  # Optional match operator
        r"\s*"  # Optional whitespace
        r'(".*?"|\'.*?\'|[^\'"\]]+)?'  # Optional attribute value (quoted or unquoted)
        r"\s*)?"  # Optional whitespace
        r"\]$"  # Closing bracket
    )

    return bool(pattern.match(simple_selector))


def is_pseudo_class_selector(simple_selector: str) -> bool:
    pseudo_classes = {
        ":first-child",
        ":last-child",
        ":first-of-type",
        ":last-of-type",
        ":only-child",
        ":only-of-type",
        ":empty",
    }

    # Check if it's a valid basic pseudo-class
    if simple_selector in pseudo_classes:
        return True

    # Check for pseudo-classes that accept parameters
    pseudo_class_with_params = {":nth-child", ":nth-last-child", ":nth-of-type", ":nth-last-of-type", ":not"}

    for pseudo_class in pseudo_class_with_params:
        if simple_selector.startswith(pseudo_class):
            return True

    return False


def is_pseudo_element_selector(simple_selector: str) -> bool:
    return simple_selector.startswith("::")


def is_valid_selector_name(class_name):
    """Check if the given class name is a valid CSS class name.

    Args:
        class_name (str): The class name to validate.

    Returns:
        bool: True if the class name is valid, False otherwise.
    """
    # Regular expression for a valid CSS class name
    # This regex covers the rules discussed:
    # - Start with a letter, underscore, or hyphen (not followed by a digit)
    # - Followed by any number of letters, digits, hyphens, underscores, or Unicode characters
    pattern = re.compile(r"^[a-zA-Z_-][a-zA-Z0-9_-]*$")

    return bool(pattern.match(class_name))
