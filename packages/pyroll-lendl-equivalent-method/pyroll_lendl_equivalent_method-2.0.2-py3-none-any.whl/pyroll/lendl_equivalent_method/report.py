from matplotlib import pyplot as plt
from pyroll.report import hookimpl
from pyroll.core import RollPass, ThreeRollPass, Unit
from shapely import LineString, Polygon
from shapely.affinity import rotate
from typing import List


@hookimpl
def unit_plot(unit: Unit):
    """Plot roll pass contour and its profiles"""
    if isinstance(unit, RollPass):

        contour_line_oriented = orient_geometry_to_technology(unit.contour_lines, unit)
        in_lendl_section_oriented = orient_geometry_to_technology(unit.in_profile.lendl_section, unit)
        out_lendl_section_oriented = orient_geometry_to_technology(unit.out_profile.lendl_section, unit)

        fig: plt.Figure = plt.figure(constrained_layout=True, figsize=(4, 4))
        ax: plt.Axes = fig.subplots()

        ax.set_aspect("equal", "datalim")
        ax.grid(lw=0.5)
        plt.title("Lendl Areas and Boundaries")

        ax.fill(*in_lendl_section_oriented.boundary.xy, color="red", alpha=0.5)
        ax.fill(*out_lendl_section_oriented.boundary.xy, color="blue", alpha=0.5)
        for cl in contour_line_oriented:
            ax.plot(*cl.xy, color="k")

        return fig


def orient_geometry_to_technology(geom: List[LineString], unit: RollPass):
    orientation = unit.orientation

    if isinstance(orientation, str):
        if orientation.lower() in ["horizontal", "h", "y"]:
            orientation = 0
        elif orientation.lower() in ["vertical", "v"]:
            orientation = 90
        elif orientation.lower() in ["antiy", "ay"]:
            orientation = 60

    if orientation != 0:
        if isinstance(geom, List):
            return [rotate(cl, angle=orientation, origin=(0, 0)) for cl in geom]
        else:
            return rotate(geom, angle=orientation, origin=(0, 0))
    return geom
