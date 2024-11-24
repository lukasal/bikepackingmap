import folium


def add_tiles(m, settings, tiles_name, dynamic_tiles):

    folium.TileLayer(
        settings.tiles[tiles_name],
        show=True,
        attr=tiles_name,
        name=tiles_name,
        id="primary_layer",
    ).add_to(m)
    if dynamic_tiles:
        for tile_name, tile_path in settings.tiles.items():
            if tile_name != tiles_name:
                folium.TileLayer(
                    tile_path, attr=tile_name, name=tile_name, show=False
                ).add_to(m)

        folium.LayerControl(overlay=True).add_to(m)

    return m
