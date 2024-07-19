from typing import Dict, List, Tuple


from geoformat.conf.error_messages import import_matplotlib_error, import_numpy_error

from geoformat.conversion.coordinates_conversion import force_rhr_polygon_coordinates
from geoformat.conversion.geometry_conversion import geometry_to_bbox
from geoformat.geoprocessing.merge_geometries import merge_geometries

try:
    import numpy as np

    import_numpy_success = True
except ImportError:
    import_numpy_success = False

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path

    import_matplotlib_success = True

except ImportError:
    import_matplotlib_success = False


if import_matplotlib_success is True and import_numpy_success is True:
    class DrawGeometry:

        def __init__(self, geometry: Dict) -> None:
            """
            Initializes the DrawGeometry class with geometry data and optional styling.

            :param geometry: A dictionary representing the geometric data to plot.
            """
            self.geometry = geometry
            self.bbox = geometry.get("bbox") or geometry_to_bbox(geometry=self.geometry)
            self.fig, self.ax = plt.subplots()

        def create_codes(self, num_points: int) -> List[int]:
            """
            Creates a list of Path codes for constructing a geometry path.

            :param num_points: The number of points in the geometry.
            :return: A list of Matplotlib Path codes.
            """
            return [Path.MOVETO] + [Path.LINETO] * (num_points - 1)

        def validate_coordinates(self, coordinates: List[List[float]]) -> bool:
            """
            Validates the provided coordinates to ensure they are non-empty and plotable.

            :param coordinates: The coordinates to validate.
            :return: True if the coordinates are valid, False otherwise.
            """
            if coordinates:
                if isinstance(coordinates[0], (list, tuple)):
                    return any(coords for coords in coordinates)
                return True
            return False

        def plot_point(self, coordinates: List[float]) -> None:
            """
            Plots a single point on the ax object.

            :param coordinates: A list containing the x and y coordinates of the point.
            """
            matplolib_point_style = {
                "marker": 'o',
                "markersize": 5,
                "markeredgecolor": 'black',
                "markerfacecolor": 'red',
                "markeredgewidth": 1,
                "linestyle": None,
                "linewidth": None,
                "zorder": 2,
                "alpha": 1,
                "antialiased": True,
            }

            self.ax.plot(coordinates[0], coordinates[1], **matplolib_point_style)

        def plot_line_string(self, coordinates: List[List[float]]) -> None:
            """
            Plots a single LineString geometry.

            :param coordinates: A list of [x, y] pairs representing the LineString's vertices.
            """
            matplotlib_linestring_style = {
                "edgecolor": 'black',
                "facecolor": "none",
                "linewidth": 1,
                "linestyle": '-',
                "zorder": 1,
                "alpha": 1,
                "antialiased": True,
            }
            verts = np.array(coordinates)
            path = Path(verts)
            patch = PathPatch(path, **matplotlib_linestring_style)
            self.ax.add_patch(patch)

        def plot_polygon(self, coordinates: List[List[List[float]]]) -> None:
            """
            Processes and plots polygon geometry with the given coordinates.

            :param coordinates: A nested list representing the polygon's outer boundary and any inner holes.
            """
            matplotlib_polygon_style = {
                "edgecolor": 'black',
                "facecolor": "#d8e0ea",
                "linewidth": 1,
                "linestyle": '-',
                "zorder": 0,
                "alpha": 1,
                "antialiased": True,
            }
            coordinates = force_rhr_polygon_coordinates(coordinates=coordinates)
            verts = None
            codes = []

            for ring in coordinates:
                ring_verts = np.array(ring)
                if verts is None:
                    verts = ring_verts
                else:
                    verts = np.concatenate([verts, ring_verts])
                codes += self.create_codes(len(ring))

            path = Path(verts, codes)
            patch = PathPatch(path, **matplotlib_polygon_style)
            self.ax.add_patch(patch)

        def plot_multi_point(self, coordinates: List[List[float]]) -> None:
            """Plots a MultiPoint geometry."""
            for pt in coordinates:
                if pt:
                    self.plot_point(pt)

        def plot_multi_line_string(self, coordinates: List[List[List[float]]]) -> None:
            """Plots a MultiLineString geometry."""
            for ls in coordinates:
                if ls:
                    self.plot_line_string(ls)

        def plot_multi_polygon(self, coordinates: List[List[List[List[float]]]]) -> None:
            """Plots a MultiPolygon geometry."""
            for poly in coordinates:
                if poly:
                    self.plot_polygon(poly)

        def plot_geometry(self, geometry: Dict) -> None:
            """
            Plots the provided geometry based on its type.

            :param geometry: The geometry dictionary to plot.
            """
            geometry_type = geometry['type']
            geometry_handlers = {
                'Point': self.plot_point,
                'MultiPoint': self.plot_multi_point,
                'LineString': self.plot_line_string,
                'MultiLineString': self.plot_multi_line_string,
                'Polygon': self.plot_polygon,
                'MultiPolygon': self.plot_multi_polygon
            }

            if geometry_type in geometry_handlers:
                handler = geometry_handlers[geometry_type]
                coordinates = geometry.get('coordinates', [])
                if self.validate_coordinates(coordinates=coordinates) is True:
                    handler(coordinates=coordinates)

        def expand_bbox(self) -> Tuple[float, float, float, float]:
            """
            Expands the bounding box by a margin.

            :return: An expanded bounding box.
            """
            if self.bbox:
                x_diff = self.bbox[2] - self.bbox[0]
                y_diff = self.bbox[3] - self.bbox[1]

                x_margin = x_diff * 0.1 or 1
                y_margin = y_diff * 0.1 or 1
                expand_bbox = self.bbox[0] - x_margin, self.bbox[1] - y_margin, self.bbox[2] + x_margin, self.bbox[
                    3] + y_margin
            else:
                expand_bbox = (-1, -1, 1, 1)

            return expand_bbox

        def plot(self, graticule=False) -> None:
            """
            Main method to plot the provided geometry and apply custom style if provided.
            """
            # plot geometry and apply style
            if self.geometry['type'] == 'GeometryCollection':
                for geometry in self.geometry['geometries']:
                    self.plot_geometry(geometry)
            else:
                self.plot_geometry(self.geometry)

            # add margin
            margin = self.expand_bbox()
            self.ax.set_xlim(margin[0], margin[2])
            self.ax.set_ylim(margin[1], margin[3])

            # add grid
            if graticule is True:
                self.ax.minorticks_on()
                self.ax.grid(which='major', color='black', linestyle='-', linewidth=0.5, alpha=0.5)
                self.ax.grid(which='minor', color='gray', linestyle=':', linewidth=0.2, alpha=0.5)

            plt.gca().set_aspect('equal', adjustable='box')
            plt.show()



def draw_geometry(geometry: Dict, graticule=False) -> None:
    """
    Plots a given geometry using the DrawGeometry class.

    :param geometry: A dictionary representing the geometric data to plot.
    :param graticule: add graticule for better geometry location
    """
    if import_matplotlib_success is True and import_numpy_success is True:
        DrawGeometry(geometry=geometry).plot(graticule=graticule)
    else:
        if import_matplotlib_success is False:
            raise Exception(import_matplotlib_error)
        if import_numpy_success is False:
            raise Exception(import_numpy_error)

def draw_feature(feature: Dict, graticule=False) -> None:
    """
    Draws the geometry of a given feature using the DrawGeometry class.

    This function extracts the "geometry" key from the provided feature dictionary and
    plots it.

    :param feature: A dictionary representing a geographic feature, which must include a
                    "geometry" key containing geometric data to plot.
    :param graticule: add graticule for better geometry location
    """
    if import_matplotlib_success is True and import_numpy_success is True:
        feature_geometry = feature.get("geometry")
        if feature_geometry:
            draw_geometry(geometry=feature_geometry, graticule=graticule)
    else:
        if import_matplotlib_success is False:
            raise Exception(import_matplotlib_error)
        if import_numpy_success is False:
            raise Exception(import_numpy_error)


def draw_geolayer(geolayer: Dict, graticule=False) -> None:
    """
    Iterates over features in a geolayer, merges their geometries, and plots the combined geometry.

    Each feature's geometry within the geolayer is merged into a single geometry, which is then plotted.

    :param geolayer: A Geolayer dict
    :param graticule: add graticule for better geometry location
    """
    if import_matplotlib_success is True and import_numpy_success is True:
        geolayer_geometry = None
        for i_feat, feature in geolayer["features"].items():
            feature_geometry = feature.get('geometry')
            if feature_geometry:
                if geolayer_geometry is None:
                    geolayer_geometry = feature_geometry
                else:
                    geolayer_geometry = merge_geometries(geolayer_geometry, feature_geometry)

        draw_geometry(geometry=geolayer_geometry, graticule=graticule)
    else:
        if import_matplotlib_success is False:
            raise Exception(import_matplotlib_error)
        if import_numpy_success is False:
            raise Exception(import_numpy_error)
