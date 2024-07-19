import math

from pyroll.core import RollPass, Hook, ThreeRollPass
from shapely import intersection, MultiLineString, Polygon, unary_union
from shapely.affinity import rotate
from shapely.ops import clip_by_rect
import numpy as np

RollPass.lendl_width = Hook[float]()
RollPass.Profile.lendl_section = Hook[float]()


@RollPass.OutProfile.lendl_section
def out_lendl_section(self: RollPass.OutProfile):
    contour = MultiLineString(self.roll_pass.contour_lines)
    intersections = intersection(self.roll_pass.in_profile.cross_section, contour)

    return Polygon(
        np.concatenate([ls.coords for ls in intersections.geoms])
    )


@RollPass.lendl_width
def lendl_width(self: RollPass):
    return self.out_profile.lendl_section.width


@RollPass.InProfile.lendl_section
def in_lendl_section(self: RollPass.InProfile):
    half_width = self.roll_pass.lendl_width / 2
    return clip_by_rect(self.cross_section, -half_width, -math.inf, half_width, math.inf)


@ThreeRollPass.lendl_width
def lendl_width_3fold(self: RollPass):
    i = intersection(self.in_profile.cross_section, self.contour_lines[1])
    return i.width


def clip_3fold(poly: Polygon, roll_pass: ThreeRollPass):
    half_width = roll_pass.lendl_width / 2
    poly = clip_by_rect(poly, -half_width, -math.inf, half_width, 0)

    return unary_union(
        [
            rotate(poly, angle=a, origin=(0, 0))
            for a in (0, 120, 240)
        ]
    )


@ThreeRollPass.InProfile.lendl_section
def in_lendl_section_3fold(self: ThreeRollPass.InProfile):
    return clip_3fold(self.cross_section, self.roll_pass)


@ThreeRollPass.OutProfile.lendl_section
def out_lendl_section_3fold(self: ThreeRollPass.OutProfile):
    poly = Polygon(
        np.concatenate([ls.coords for ls in self.roll_pass.contour_lines])
    )
    return clip_3fold(poly, self.roll_pass)


@RollPass.Profile.equivalent_width
def equivalent_width(self: RollPass.Profile):
    return self.width


@RollPass.Profile.equivalent_height
def equivalent_height(self: RollPass.Profile):
    return self.lendl_section.area / self.roll_pass.lendl_width


@ThreeRollPass.Profile.equivalent_height
def equivalent_height(self: RollPass.Profile):
    return (self.lendl_section.area / 3 + self.roll_pass.lendl_width ** 2
            * np.sqrt(3) / 12) / self.roll_pass.lendl_width * 2
