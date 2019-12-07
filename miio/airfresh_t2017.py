import enum
import logging
from collections import defaultdict
from typing import Any, Dict

import click

from .click_common import EnumType, command, format_output
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_AIRFRESH_T2017 = "dmaker.airfresh.t2017"

AVAILABLE_PROPERTIES = {
    MODEL_AIRFRESH_T2017: [
        "power",
        "mode",
        "pm25",
        "co2",
        "temperature_outside",
        "favourite_speed",
        "control_speed",
        "filter_intermediate",
        "filter_inter_day",
        "filter_efficient",
        "filter_effi_day",
        "ptc_on",
        "ptc_level",
        "ptc_status",
        "child_lock",
        "sound",
        "display",
        "screen_direction",
    ]
}


class AirFreshException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Off = "off"
    Auto = "auto"
    Sleep = "sleep"
    Favorite = "favourite"


class PtcLevel(enum.Enum):
    Off = "off"
    Low = "low"
    Medium = "medium"
    High = "high"


class ScreenOrientation(enum.Enum):
    Portrait = "forward"
    LandscapeLeft = "left"
    LandscapeRight = "right"


class AirFreshStatus:
    """Container for status reports from the air fresh t2017."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Air Airfresh T2017 (dmaker.airfresh.t2017):

        {
            'power': true,
            'mode': "favourite",
            'pm25': 1,
            'co2': 550,
            'temperature_outside': 24,
            'favourite_speed': 241,
            'control_speed': 241,
            'filter_intermediate': 100,
            'filter_inter_day': 90,
            'filter_efficient': 100,
            'filter_effi_day': 180,
            'ptc_on': false,
            'ptc_level': "low",
            'ptc_status': false,
            'child_lock': false,
            'sound': true,
            'display': false,
            'screen_direction': "forward",
        }
        """

        self.data = data

    @property
    def power(self) -> str:
        """Power state."""
        return "on" if self.data["power"] else "off"

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.data["power"]

    @property
    def mode(self) -> OperationMode:
        """Current operation mode."""
        return OperationMode(self.data["mode"])

    @property
    def pm25(self) -> int:
        """Fine particulate patter (PM2.5)."""
        return self.data["pm25"]

    @property
    def co2(self) -> int:
        """Carbon dioxide."""
        return self.data["co2"]

    @property
    def temperature(self) -> int:
        """Current temperature, if available."""
        return self.data["temperature_outside"]

    @property
    def favorite_speed(self) -> int:
        """Favorite speed."""
        return self.data["favourite_speed"]

    @property
    def control_speed(self) -> int:
        """Control speed."""
        return self.data["control_speed"]

    @property
    def dust_filter_life_remaining(self) -> int:
        """Remaining dust filter life in percent."""
        return self.data["filter_intermediate"]

    @property
    def dust_filter_days_used(self) -> int:
        """How long the dust filter has been in use in days."""
        return self.data["filter_inter_day"]

    @property
    def upper_filter_life_remaining(self) -> int:
        """Remaining upper filter life in percent."""
        return self.data["filter_efficient"]

    @property
    def upper_filter_days_used(self) -> int:
        """How long the upper filter has been in use in days."""
        return self.data["filter_effi_day"]

    @property
    def ptc(self) -> bool:
        """Return True if PTC is on."""
        return self.data["ptc_on"]

    @property
    def ptc_level(self) -> int:
        """PTC level."""
        return PtcLevel(self.data["ptc_level"])

    @property
    def ptc_status(self) -> bool:
        """Return true if PTC status is on."""
        return self.data["ptc_status"]

    @property
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"]

    @property
    def buzzer(self) -> bool:
        """Return True if sound is on."""
        return self.data["sound"]

    @property
    def display(self) -> bool:
        """Return True if the display is on."""
        return self.data["display"]

    @property
    def screen_orientation(self) -> int:
        """Screen orientation."""
        return ScreenOrientation(self.data["screen_direction"])

    def __repr__(self) -> str:
        s = (
            "<AirFreshStatus power=%s, "
            "mode=%s, "
            "pm25=%s, "
            "co2=%s, "
            "temperature=%s °C, "
            "favorite_speed=%s, "
            "control_speed=%s, "
            "dust_filter_life_remaining=%s, "
            "dust_filter_days_used=%s, "
            "upper_filter_life_remaining=%s, "
            "upper_filter_days_used=%s, "
            "ptc=%s, "
            "ptc_level=%s, "
            "ptc_status=%s, "
            "child_lock=%s, "
            "buzzer=%s, "
            "display=%s, "
            "screen_orientation=%s>"
            % (
                self.power,
                self.mode,
                self.pm25,
                self.co2,
                self.temperature,
                self.favorite_speed,
                self.control_speed,
                self.dust_filter_life_remaining,
                self.dust_filter_days_used,
                self.upper_filter_life_remaining,
                self.upper_filter_days_used,
                self.ptc,
                self.ptc_level,
                self.ptc_status,
                self.child_lock,
                self.buzzer,
                self.display,
                self.screen_orientation,
            )
        )
        return s

    def __json__(self):
        return self.data


class AirFreshT2017(Device):
    """Main class representing the air fresh t2017."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_AIRFRESH_T2017,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_AIRFRESH_T2017

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Mode: {result.mode}\n"
            "PM2.5: {result.pm25}\n"
            "CO2: {result.co2}\n"
            "Temperature: {result.temperature}\n"
            "Favorite speed: {result.favorite_speed}\n"
            "Control speed: {result.control_speed}\n"
            "Dust filter life remaining: {result.dust_filter_life_remaining}\n"
            "Dust filter days used: {result.dust_filter_days_used}\n"
            "Upper filter life remaining: {result.upper_filter_life_remaining}\n"
            "Upper filter days used: {result.upper_filter_days_used}\n"
            "PTC: {result.ptc}\n"
            "PTC level: {result.ptc_level}\n"
            "PTC status: {result.ptc_status}\n"
            "Child lock: {result.child_lock}\n"
            "Buzzer: {result.buzzer}\n"
            "Display: {result.display}\n"
            "Screen orientation: {result.screen_orientation}\n",
        )
    )
    def status(self) -> AirFreshStatus:
        """Retrieve properties."""

        properties = AVAILABLE_PROPERTIES[self.model]

        # A single request is limited to 16 properties. Therefore the
        # properties are divided into multiple requests
        _props = properties.copy()
        values = []
        while _props:
            values.extend(self.send("get_prop", _props[:15]))
            _props[:] = _props[15:]

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count,
                values_count,
            )

        return AirFreshStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("mode", type=EnumType(OperationMode, False)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set mode."""
        return self.send("set_mode", [mode.value])

    @command(
        click.argument("display", type=bool),
        default_output=format_output(
            lambda led: "Turning on display" if led else "Turning off display"
        ),
    )
    def set_display(self, display: bool):
        """Turn led on/off."""
        if display:
            return self.send("set_display", ["on"])
        else:
            return self.send("set_display", ["off"])

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set sound on/off."""
        if buzzer:
            return self.send("set_sound", ["on"])
        else:
            return self.send("set_sound", ["off"])

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        if lock:
            return self.send("set_child_lock", ["on"])
        else:
            return self.send("set_child_lock", ["off"])

    @command(default_output=format_output("Resetting upper filter"))
    def reset_upper_filter(self):
        """Resets filter days used and remaining life of the upper filter."""
        return self.send("set_filter_reset", ["efficient"])

    @command(default_output=format_output("Resetting dust filter"))
    def reset_dust_filter(self):
        """Resets filter days used and remaining life of the dust filter."""
        return self.send("set_filter_reset", ["intermediate"])
