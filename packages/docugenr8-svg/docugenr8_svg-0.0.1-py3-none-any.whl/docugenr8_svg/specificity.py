from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from docugenr8_svg.specificity import Specificity


class Specificity:
    def __init__(
        self,
        inline_weight: int,
        id_weight: int,
        class_weight: int,
        type_weight: int,
    ) -> None:
        # No value
        # The universal selector (*) and the pseudo-class :where()
        # and its parameters aren't counted when calculating the weight
        # so their value is 0-0-0, but they do match elements.
        # These selectors do not impact the specificity weight value.

        # Inline styles added to an element (e.g.,
        # style="font-weight: bold;") always overwrite
        # any normal styles in author stylesheets,
        # and therefore, can be thought of as having the highest specificity.
        # Think of inline styles as having a specificity weight of 1-0-0-0.
        # The only way to override inline styles is by using !important.
        self.inline_weight = inline_weight
        # ID column
        # Includes only ID selectors, such as #example. For each ID in
        # a matching selector, add 1-0-0 to the weight value.
        self.id_weight = id_weight
        # CLASS column
        # Includes class selectors, such as .myClass, attribute selectors
        # like [type="radio"] and [lang|="fr"], and pseudo-classes,
        # such as :hover, :nth-of-type(3n), and :required.
        # For each class, attribute selector, or pseudo-class in
        # a matching selector, add 0-1-0 to the weight value.
        self.class_weight = class_weight
        # TYPE column
        # Includes type selectors, such as p, h1, and td,
        # and pseudo-elements like ::before, ::placeholder,
        # and all other selectors with double-colon notation.
        # For each type or pseudo-element in a matching selector,
        # add 0-0-1 to the weight value.
        self.type_weight = type_weight

    def add(self, other: Specificity) -> None:
        self.type_weight += other.type_weight
        self.class_weight += other.class_weight
        self.id_weight += other.id_weight
        self.inline_weight += other.inline_weight

    def __str__(self):
        text = f"({self.inline_weight}"
        text += f"-{self.id_weight}"
        text += f"-{self.class_weight}"
        text += f"-{self.type_weight})"
        return text

    def __repr__(self) -> str:
        return str(self) + f" at {hex(id(self))}"

    def __lt__(self, other: Specificity) -> bool:
        if isinstance(other, Specificity):
            if self.inline_weight < other.inline_weight:
                return True
            if self.inline_weight > other.inline_weight:
                return False
            if self.id_weight < other.id_weight:
                return True
            if self.id_weight > other.id_weight:
                return False
            if self.class_weight < other.class_weight:
                return True
            if self.class_weight > other.class_weight:
                return False
            if self.type_weight < other.type_weight:
                return True
            if self.type_weight > other.type_weight:
                return False
            return False
        else:
            raise ValueError("The value to compare must be of a type Specificity.")
