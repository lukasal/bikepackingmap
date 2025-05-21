import folium

from app.map.map_polylines import map_polylines
from app.map.map_stage_icons import map_stage_icons
from app.map.add_tiles import add_tiles
from app.map.map_grand_arrivee import map_grand_arrivee
from app.map.map_grand_depart import map_grand_depart
from app.map.helper import centroid, bounding_box


# plot all activities on map
def generate_map(
    settings,
    activities,
    out_file="mymap_terrain.html",
    tiles_name="stadia_terrain",
    zoom_margin=0.05,
    width="100%",
    height="100vh",
    final_popup=False,
    dynamic_tiles=False,
    save=True,
):
    m = folium.Map(
        location=centroid(activities["map_polyline"]),
        width=width,
        height=height,
        zoom_start=6,
        tiles=None,
        attr=".",
    )

    m = add_tiles(m, settings, tiles_name, dynamic_tiles)

    # add polylines
    if settings.get_interactive_setting("lines_active"):
        map_polylines(activities, settings).add_to(m)

    # House Markler for each stage town:
    if settings.get_interactive_setting("stage_labels_active"):
        map_stage_icons(activities, settings).add_to(m)

    # Grand depart marker
    if settings.get_interactive_setting("depart_labels_active"):
        map_grand_depart(activities, settings).add_to(m)

    # Grand arrivee marker
    if settings.get_interactive_setting("arrivee_labels_active"):
        map_grand_arrivee(activities, settings, final_popup).add_to(m)

    m.fit_bounds(bounding_box(activities["map_polyline"], margin=zoom_margin))
    if save:
        m.save(out_file)

    return m


# display(m)
