import folium
from folium.plugins import BeautifyIcon


def map_grand_depart(activities, settings):

    grand_depart = folium.FeatureGroup(name="Grand depart", control=False)

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
        location=activities[activities.index == min(activities.index)]["map.polyline"][
            0
        ][0],
        icon=icon_,
        icon_size=10,
        zIndexOffset=1000,
        tooltip=activities[activities.index == min(activities.index)]["start_location"][
            0
        ],
    ).add_to(grand_depart)

    return grand_depart
