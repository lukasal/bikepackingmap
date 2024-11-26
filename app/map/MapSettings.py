import seaborn as sns
import matplotlib.colors as mcolors


class MapSettings:
    def __init__(self, activities):
        activity_types = activities["type"].unique()
        line_colors = [
            mcolors.rgb2hex(color)
            for color in sns.color_palette("dark", len(activity_types), desat=0.8)
        ]
        self.color = {
            activity: color for activity, color in zip(activity_types, line_colors)
        }

        self.line_thickness = 5
        self.stage_labels_active = True
        self.stage_start_icon = "house"
        self.stage_icon_shape = "circle"
        self.stage_icon_size = 22
        self.stage_icon_inner_size = 10
        self.stage_border_transparent = False
        self.stage_border_color = "#000000"
        self.stage_background_transparent = False
        self.stage_background_color = "#FFFFFF"
        self.stage_symbol_color = "#007799"
        self.rest_day = True
        self.rest_day_symbol = "house"
        self.rest_day_color = "yellow"
        self.end_symbol = "flag"
        self.end_color = None

        self.spec_resolution = 75
        self.spec_width = 6
        self.spec_height = 6.5
        self.map_width = "100%"
        self.map_height = "60%"

        self.tiles = tiles = {
            "stadia_terrain": "https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png?api_key=18eb0b62-6b8d-4784-9997-f9b5a9ac39fd",
            "google_hybrid": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}&apistyle=s.t%3A2|s.e%3Al|p.v%3Aoff",
            "google_satellit": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&apistyle=s.t%3A2|s.e%3Al|p.v%3Aoff",
        }
        self.popup_name = True
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
