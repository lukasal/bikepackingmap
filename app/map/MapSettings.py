import seaborn as sns
import matplotlib.colors as mcolors
from app.map.InteractiveSetting import (
    BooleanSetting,
    ColorSetting,
    NumberSetting,
    TextSetting,
)
import yaml


class MapSettings:

    def __init__(self, activities, config_file=None):
        self.interactive_settings = {}
        if config_file:
            self.load_settings(config_file)

        activity_types = activities["type"].unique()
        line_colors = [
            mcolors.rgb2hex(color)
            for color in sns.color_palette("dark", len(activity_types), desat=0.8)
        ]
        for activity, color in zip(activity_types, line_colors):
            self.add_setting(
                id=f"line_color_{activity}",
                type="ColorSetting",
                group="Line",
                label=f"{activity} color",
                value=color,
            )

        self.spec_resolution = 75
        self.spec_width = 6
        self.spec_height = 6.5

        self.tiles = tiles = {
            "stadia_terrain": "https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png?api_key=18eb0b62-6b8d-4784-9997-f9b5a9ac39fd",
            "google_hybrid": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}&apistyle=s.t%3A2|s.e%3Al|p.v%3Aoff",
            "google_satellit": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&apistyle=s.t%3A2|s.e%3Al|p.v%3Aoff",
        }
        self.popup_id = True
        self.popup_date = True
        self.popup_time = True
        self.popup_type = True
        self.popup_distance = True
        self.popup_total_elevation_gain = True
        self.popup_moving_time = True
        self.popup_elapsed_time = True
        self.popup_average_speed = True
        self.popup_max_speed = True
        self.popup_power = False
        self.popup_average_heartrate = True
        self.popup_max_heartrate = True
        self.popup_average_temp = True
        self.popup_elevation_profile = True

    def get_interactive_setting(self, id):
        setting = self.interactive_settings.get(id)
        if setting:
            return setting.value
        else:
            raise KeyError(f"Setting '{id}' not found.")

    def set_interactive_setting(self, id, value):
        setting = self.interactive_settings.get(id)
        if setting:
            # Type casting based on setting type
            if isinstance(setting, NumberSetting):
                if isinstance(value, (int, float)):
                    setting.value = value
                else:
                    if "." in value:
                        setting.value = float(value)
                    else:
                        setting.value = int(value)
            elif isinstance(setting, BooleanSetting):
                if isinstance(value, bool):
                    setting.value = value
                else:
                    setting.value = value.lower() == "true"
            else:
                setting.value = value  # For other types, assign directly
        else:
            raise KeyError(f"Setting '{id}' not found.")

    def get_interactive_groups(self):
        groups = set()
        for setting in self.interactive_settings.values():
            groups.add(setting.group)
        return sorted(groups)

    def load_settings(self, config_file):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
            for id, setting in config.items():
                self.add_setting(id, **setting)

    def add_setting(self, id, **setting):
        setting_type = setting.pop("type")
        if setting_type == "BooleanSetting":
            self.interactive_settings[id] = BooleanSetting(id, **setting)
        elif setting_type == "ColorSetting":
            self.interactive_settings[id] = ColorSetting(id, **setting)
        elif setting_type == "NumberSetting":
            self.interactive_settings[id] = NumberSetting(id, **setting)
        elif setting_type == "TextSetting":
            self.interactive_settings[id] = TextSetting(id, **setting)
