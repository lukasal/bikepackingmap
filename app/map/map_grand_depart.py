import folium
from folium.plugins import BeautifyIcon


def map_grand_depart(activities, settings):

    grand_depart = folium.FeatureGroup(name="Grand depart", control=False)

    first_stage = activities[activities.index == activities.index.min()]
    # first_stage = activities[activities["start_date"] == activities["start_date"].min()]

    # Grand depart marker
    icon_ = BeautifyIcon(
        icon="play",
        icon_shape="circle",
        border_color="black",
        text_color="green",
        background_color="white",
        icon_size=[42, 42],
        icon_anchor=(21, 21),
        inner_icon_style="font-size:30px;",  # Adjust inner icon size
        id="grand_depart",
    )

    folium.Marker(
        location=first_stage["map.polyline"].iloc[0][0],
        icon=icon_,
        icon_size=10,
        zIndexOffset=1000,
        tooltip=first_stage["start_location"].iloc[0],
    ).add_to(grand_depart)

    return grand_depart
