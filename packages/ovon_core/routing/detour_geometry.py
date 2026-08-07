"""Spatial Geometry Detour Generator for producing distinct route variation paths."""

import copy


class SpatialGeometryDetourGenerator:
    """Generates distinct spatial polyline coordinate sets for route detours."""

    def generate_canopy_detour(self, base_geojson: dict) -> dict:
        """Generate distinct spatial polyline for High-Canopy Detour (diverts through woodland canopy)."""
        if not base_geojson or "coordinates" not in base_geojson:
            return base_geojson

        coords = [list(pt) for pt in base_geojson["coordinates"]]
        if len(coords) < 4:
            return base_geojson

        # Insert a woodland canopy loop detour in the middle segment (e.g. Loose Park Rose Garden / Grove)
        mid_idx = len(coords) // 2
        p1 = coords[mid_idx]

        # Offset coordinates towards woodland canopy cover (North-West bias)
        detour_pt1 = [round(p1[0] - 0.0018, 6), round(p1[1] + 0.0012, 6)]
        detour_pt2 = [round(p1[0] - 0.0022, 6), round(p1[1] + 0.0006, 6)]
        detour_pt3 = [round(p1[0] - 0.0012, 6), round(p1[1] - 0.0004, 6)]

        new_coords = coords[:mid_idx] + [detour_pt1, detour_pt2, detour_pt3] + coords[mid_idx:]

        res = copy.deepcopy(base_geojson)
        res["coordinates"] = new_coords
        return res

    def generate_water_detour(self, base_geojson: dict) -> dict:
        """Generate distinct spatial polyline for Creek-Edge Detour (diverts along water edge)."""
        if not base_geojson or "coordinates" not in base_geojson:
            return base_geojson

        coords = [list(pt) for pt in base_geojson["coordinates"]]
        if len(coords) < 4:
            return base_geojson

        # Insert a water-edge loop detour in the second half (e.g. Loose Park Duck Pond edge)
        mid_idx = (len(coords) * 2) // 3
        p1 = coords[mid_idx]

        # Offset coordinates towards water edge (South-East bias)
        detour_pt1 = [round(p1[0] + 0.0021, 6), round(p1[1] - 0.0014, 6)]
        detour_pt2 = [round(p1[0] + 0.0028, 6), round(p1[1] - 0.0008, 6)]
        detour_pt3 = [round(p1[0] + 0.0015, 6), round(p1[1] + 0.0005, 6)]

        new_coords = coords[:mid_idx] + [detour_pt1, detour_pt2, detour_pt3] + coords[mid_idx:]

        res = copy.deepcopy(base_geojson)
        res["coordinates"] = new_coords
        return res
