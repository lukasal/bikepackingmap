def centroid(polylines):
    x, y = [], []
    for polyline in polylines:
        for coord in polyline:
            x.append(coord[0])
            y.append(coord[1])
    return [(min(x) + max(x)) / 2, (min(y) + max(y)) / 2]


def bounding_box(polylines, margin=0.3):
    x, y = [], []
    for polyline in polylines:
        for coord in polyline:
            x.append(coord[0])
            y.append(coord[1])
    return [[min(x) - margin, min(y) - margin], [max(x) + margin, max(y) + margin]]
