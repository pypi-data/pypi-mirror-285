from docugenr8_svg.specificity import Specificity


class SvgAttr:
    def __init__(
        self,
        value: str,
        specificity: Specificity,
    ) -> None:
        self.__value = value
        self.__specificity = specificity
        self.__history: list[SvgAttr] = []

    def __str__(self) -> str:
        text = f"{self.__value}"
        text += " "
        text += str(self.specificity)
        return text

    def __repr__(self):
        repr_text = str(self) + f" at {hex(id(self))}"
        return repr_text

    @property
    def value(self):
        return self.__value

    @property
    def specificity(self):
        return self.__specificity

    @property
    def history(self):
        return self.__history

    def apply_value(
        self,
        new_value: str,
        new_specificity: Specificity,
    ) -> None:
        if self.__specificity < new_specificity:
            self.__history.append(
                SvgAttr(
                    self.__value,
                    Specificity(
                        self.__specificity.inline_weight,
                        self.__specificity.id_weight,
                        self.__specificity.class_weight,
                        self.__specificity.type_weight,
                    ),
                )
            )
            self.__value = new_value
            self.__specificity = new_specificity
        else:
            self.__history.append(SvgAttr(new_value, new_specificity))
