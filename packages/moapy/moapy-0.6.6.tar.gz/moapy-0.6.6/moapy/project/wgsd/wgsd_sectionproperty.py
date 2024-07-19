from pydantic import BaseModel, Field as dataclass_field
from sectionproperties.analysis.section import Section
from sectionproperties.pre.geometry import Polygon, Geometry
from moapy.auto_convert import auto_schema
from moapy.project.wgsd.wgsd_flow import Point, Points
from moapy.mdreporter import ReportUtil, enUnit
from typing import List, Tuple

class SectionProperty(BaseModel):
    """
    Section Property
    """
    Area: float = dataclass_field(default=0.0, description="Area")
    Asy: float = dataclass_field(default=0.0, description="Asy")
    Asz: float = dataclass_field(default=0.0, description="Asz")
    Ixx: float = dataclass_field(default=0.0, description="Ixx")
    Iyy: float = dataclass_field(default=0.0, description="Iyy")
    Izz: float = dataclass_field(default=0.0, description="Izz")
    Cy: float = dataclass_field(default=0.0, description="Cy")
    Cz: float = dataclass_field(default=0.0, description="Cz")
    Syp: float = dataclass_field(default=0.0, description="Syp")
    Sym: float = dataclass_field(default=0.0, description="Sym")
    Szp: float = dataclass_field(default=0.0, description="Szp")
    Szm: float = dataclass_field(default=0.0, description="Szm")
    Ipyy: float = dataclass_field(default=0.0, description="Ipyy")
    Ipzz: float = dataclass_field(default=0.0, description="Ipzz")
    Zy: float = dataclass_field(default=0.0, description="Zy")
    Zz: float = dataclass_field(default=0.0, description="Zz")
    ry: float = dataclass_field(default=0.0, description="ry")
    rz: float = dataclass_field(default=0.0, description="rz")

    class Config:
        title = "Section Property"

class MPolygon(BaseModel):
    """
    Polygon
    """
    outerPolygon: Points = dataclass_field(default=Points(), description="Outer polygon")

    class Config:
        title = "Polygon"

@auto_schema
def input_polygon(points: Points) -> MPolygon:
    return MPolygon(outerPolygon=points)

def convert_points_to_tuple(points: List[Point]) -> Tuple[Tuple[float, float], ...]:
    return tuple((point.x, point.y) for point in points)

@auto_schema
def calc_sectprop(polygon: MPolygon) -> SectionProperty:
    geom = Geometry(Polygon(convert_points_to_tuple(polygon.outerPolygon.points)))
    geom.create_mesh(mesh_sizes=100.0)

    section = Section(geom)
    section.calculate_geometric_properties()
    section.calculate_warping_properties()
    section.calculate_plastic_properties()
    return SectionProperty(Area=section.get_area(), Asy=section.get_as()[0], Asz=section.get_as()[1], Ixx=section.get_j(), Iyy=section.get_ic()[0], Izz=section.get_ic()[1],
                           Cy=section.get_c()[0], Cz=section.get_c()[1], Syp=section.get_z()[0], Sym=section.get_z()[1], Szp=section.get_z()[2], Szm=section.get_z()[3],
                           Ipyy=section.get_ip()[0], Ipzz=section.get_ip()[1], Zy=section.get_s()[0], Zz=section.get_s()[1], ry=section.get_rc()[0], rz=section.get_rc()[1]
                           )

@auto_schema
def report_sectprop(sectprop: SectionProperty) -> str:
    rpt = ReportUtil("sectprop.md", "*Section Properties*")
    rpt.add_line_fvu("A_{rea}", sectprop.Area, enUnit.AREA)
    rpt.add_line_fvu("A_{sy}", sectprop.Asy, enUnit.AREA)
    rpt.add_line_fvu("A_{sz}", sectprop.Asz, enUnit.AREA)
    rpt.add_line_fvu("I_{xx}", sectprop.Ixx, enUnit.INERTIA)
    rpt.add_line_fvu("I_{yy}", sectprop.Iyy, enUnit.INERTIA)
    rpt.add_line_fvu("I_{zz}", sectprop.Izz, enUnit.INERTIA)
    rpt.add_line_fvu("C_y", sectprop.Cy, enUnit.LENGTH)
    rpt.add_line_fvu("C_z", sectprop.Cz, enUnit.LENGTH)
    rpt.add_line_fvu("S_{yp}", sectprop.Syp, enUnit.VOLUME)
    rpt.add_line_fvu("S_{ym}", sectprop.Sym, enUnit.VOLUME)
    rpt.add_line_fvu("S_{zp}", sectprop.Szp, enUnit.VOLUME)
    rpt.add_line_fvu("S_{zm}", sectprop.Szm, enUnit.VOLUME)
    rpt.add_line_fvu("I_{pyy}", sectprop.Ipyy, enUnit.INERTIA)
    rpt.add_line_fvu("I_{pzz}", sectprop.Ipzz, enUnit.INERTIA)
    rpt.add_line_fvu("Z_y", sectprop.Zy, enUnit.VOLUME)
    rpt.add_line_fvu("Z_z", sectprop.Zz, enUnit.VOLUME)
    rpt.add_line_fvu("r_y", sectprop.ry, enUnit.LENGTH)
    rpt.add_line_fvu("r_z", sectprop.rz, enUnit.LENGTH)
    return rpt.get_md_text()
