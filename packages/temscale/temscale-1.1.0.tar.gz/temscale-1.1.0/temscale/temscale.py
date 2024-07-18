from temscale import temerror


class Temscale:
    """main class that describes the temperature and functions for temperature output and conversion"""
    temperature_value = 0
    temperature_type = None
    temperature_type_name = None
    temperature_type_list = ["C", "K", "F"]

    def __init__(self, new_temperature_value: float, new_temperature_type: str) -> None:
        self.set_value(new_temperature_value)
        self.set_type(new_temperature_type)

    def __eq__(self, other) -> bool:
        """
        translates to Kelvin and checks the temperature, returns True if the temperature is equal, otherwise False.
        :type other: Temscale
        """
        self_type = self.temperature_type
        other_type = other.temperature_type

        if self.temperature_type != "K":
            self.to_kelvin()
        if other.temperature_type != "K":
            other.to_kelvin()

        result = self.temperature_value == other.temperature_value

        if self.temperature_type == "K":
            self.convert(self_type)
        if other.temperature_type == "K":
            other.convert(other_type)

        return result

    def __ne__(self, other) -> bool:
        """
        translate to Kelvin and check the temperature, returns True if the temperature is not equal, otherwise False.
        :type other: Temscale
        """
        self_type = self.temperature_type
        other_type = other.temperature_type

        if self.temperature_type != "K":
            self.to_kelvin()
        if other.temperature_type != "K":
            other.to_kelvin()

        result = self.temperature_value != other.temperature_value

        if self.temperature_type == "K":
            self.convert(self_type)
        if other.temperature_type == "K":
            other.convert(other_type)

        return result

    def __lt__(self, other) -> bool:
        """
        converts to Kelvin and checks if the temperature is less than X, returns True if the temperature is less,
        otherwise False.
        :type other: Temscale
        """
        self_type = self.temperature_type
        other_type = other.temperature_type

        if self.temperature_type != "K":
            self.to_kelvin()
        if other.temperature_type != "K":
            other.to_kelvin()

        result = self.temperature_value < other.temperature_value

        if self.temperature_type == "K":
            self.convert(self_type)
        if other.temperature_type == "K":
            other.convert(other_type)

        return result

    def __gt__(self, other) -> bool:
        """
        converts to Kelvin and checks if the temperature is greater than X, returns True if the temperature is greater,
        otherwise False.
        :type other: Temscale
        """
        self_type = self.temperature_type
        other_type = other.temperature_type

        if self.temperature_type != "K":
            self.to_kelvin()
        if other.temperature_type != "K":
            other.to_kelvin()

        result = self.temperature_value > other.temperature_value

        if self.temperature_type == "K":
            self.convert(self_type)
        if other.temperature_type == "K":
            other.convert(other_type)

        return result

    def __le__(self, other) -> bool:
        """
        converts to Kelvin and checks if the temperature is greater than or equal to X,
        returns True if the temperature is greater than or equal to X, otherwise False.
        :type other: Temscale
        """
        self_type = self.temperature_type
        other_type = other.temperature_type

        if self.temperature_type != "K":
            self.to_kelvin()
        if other.temperature_type != "K":
            other.to_kelvin()

        result = self.temperature_value <= other.temperature_value

        if self.temperature_type == "K":
            self.convert(self_type)
        if other.temperature_type == "K":
            other.convert(other_type)

        return result

    def __ge__(self, other) -> bool:
        """
        converts to Kelvin and checks if the temperature is less than or equal to X,
        returns True if the temperature is less than or equal to X, otherwise False.
        :type other: Temscale
        """
        self_type = self.temperature_type
        other_type = other.temperature_type

        if self.temperature_type != "K":
            self.to_kelvin()
        if other.temperature_type != "K":
            other.to_kelvin()

        result = self.temperature_value >= other.temperature_value

        if self.temperature_type == "K":
            self.convert(self_type)
        if other.temperature_type == "K":
            other.convert(other_type)

        return result

    def get_value(self) -> float:
        """get the temperature value"""

        return self.temperature_value

    def get_type(self) -> str:
        """get the temperature type"""

        return self.temperature_type

    def set_value(self, new_temperature_value: float) -> None:
        self.temperature_value = new_temperature_value

    def set_type(self, new_temperature_type: str) -> None:
        match new_temperature_type:
            case "C":
                self.temperature_type = new_temperature_type
                self.temperature_type_name = "Celsius"
            case "K":
                self.temperature_type = new_temperature_type
                self.temperature_type_name = "Kelvin"
            case "F":
                self.temperature_type = new_temperature_type
                self.temperature_type_name = "Fahrenheit"
            case _:
                raise (TypeError, "temperature value is not correct")

    def to_celsius(self) -> None:
        """converts temperature to Celsius"""

        match self.temperature_type:
            case "C":
                raise (temerror.TemperatureError, "The temperature's already Celsius")
            case "K":
                self.temperature_value -= 273.15
                self.set_type("C")
            case "F":
                self.temperature_value = (self.temperature_value - 32) / 1.8
                self.set_type("C")
            case _:
                raise (temerror.TemperatureError,
                       f"the value '{self.temperature_type}' is not a temperature type")

    def to_kelvin(self) -> None:
        """converts temperature to Kelvin"""

        match self.temperature_type:
            case "C":
                self.temperature_value += 273.15
                self.set_type("K")
            case "K":
                raise (temerror.TemperatureError, "The temperature's already Kelvin")
            case "F":
                self.temperature_value = (self.temperature_value + 459.67) / 1.8
                self.set_type("K")
            case _:
                raise (temerror.TemperatureError,
                       f"the value '{self.temperature_type}' is not a temperature type")

    def to_fahrenheit(self) -> None:
        """converts temperature to Fahrenheit"""

        match self.temperature_type:
            case "C":
                self.temperature_value = (self.temperature_value * 1.8) + 32
                self.set_type("F")
            case "K":
                self.temperature_value = (self.temperature_value * 1.8) - 459.67
                self.set_type("F")
            case "F":
                raise (temerror.TemperatureError, "The temperature's already Fahrenheit")
            case _:
                raise (temerror.TemperatureError,
                       f"the value '{self.temperature_type}' is not a temperature type")

    def convert(self, new_type) -> None:
        match new_type:
            case self.temperature_type:
                raise ValueError(f"the value is already '{new_type}'")
            case "C":
                self.to_celsius()
            case "K":
                self.to_kelvin()
            case "F":
                self.to_fahrenheit()
            case _:
                raise ValueError(f"The '{new_type}' is not a temperature scale type")


def to_tuple(tem: Temscale) -> tuple:
    return tem.get_value(), tem.temperature_type


def from_tuple(t: tuple) -> Temscale:
    return Temscale(*t)


def to_list(tem: Temscale) -> list:
    return [tem.get_value(), tem.temperature_type]


def from_list(ls: list) -> Temscale:
    return Temscale(*ls)


def to_dict(tem: Temscale) -> dict:
    return {"temperature_value": tem.get_value(), "temperature_type": tem.temperature_type}


def from_dict(d: dict) -> Temscale:
    return Temscale(d["temperature_value"], d["temperature_type"])


def output_format(tem: Temscale, format_temperature: str) -> str:
    """returns data in formats
    parameters "format_temperature":
    v - temperature value
    t - type of temperature scale
    For example: v = 100, t = "C", "{v}:{t}" - "100:C" """

    return format_temperature.format(v=str(tem.temperature_value), t=tem.temperature_type)


def input_format(format_temperature: str, divider: str) -> Temscale:
    """accepts data in formats
    parameters "format_temperature":
    For example: d = ":", "100:C" - v = 100, t = "C" """

    value = format_temperature.split(divider)
    return Temscale(float(value[0]), value[1])
