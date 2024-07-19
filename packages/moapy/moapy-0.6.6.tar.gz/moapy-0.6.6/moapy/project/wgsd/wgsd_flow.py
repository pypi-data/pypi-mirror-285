from typing import Optional
from scipy.spatial import ConvexHull
from shapely import Polygon
from pydantic import Field as dataclass_field
from moapy.auto_convert import auto_schema, MBaseModel
from abc import ABC, abstractmethod

from concreteproperties.pre import add_bar
from concreteproperties.concrete_section import ConcreteSection
from concreteproperties.prestressed_section import PrestressedSection
from concreteproperties.material import Concrete, SteelBar, SteelStrand

import sectionproperties.pre.geometry as geometry
import sectionproperties.pre.pre as pre
import concreteproperties.stress_strain_profile as ssp
import concreteproperties.utils as utils
import concreteproperties.results
import numpy as np
import trimesh
import pandas as pd

# ==== Unit & Design Code ====
class Force(MBaseModel):
    """
    Force class
    """
    Nz: float = dataclass_field(default=0.0, description="Axial force")
    Mx: float = dataclass_field(default=0.0, description="Moment about x-axis")
    My: float = dataclass_field(default=0.0, description="Moment about y-axis")

    class Config(MBaseModel.Config):
        title = "Force"

class Mesh3DPM(MBaseModel):
    """
    3D P-M onion mesh result class
    """
    mesh3dpm : list[Force] = dataclass_field(default=[], description="onion mesh result")

    class Config(MBaseModel.Config):
        title = "3DPM onion mesh result"

class Lcom(MBaseModel):
    """
    Lcom result class
    """
    name: str = dataclass_field(default="lcom", description="load combination name")
    f: Force = dataclass_field(default=Force(), description="load combination force")

    class Config(MBaseModel.Config):
        title = "Lcom Result"

class Lcoms(MBaseModel):
    """
    Strength result class
    """
    lcoms: list[Lcom] = dataclass_field(default=[Lcom(name="uls1", f=Force(Nz=100.0, Mx=10.0, My=50.0))], description="load combination result")

    class Config(MBaseModel.Config):
        title = "Strength Result"

class Result3DPM(MBaseModel):
    """
    GSD 3DPM result class
    """
    meshes: Mesh3DPM = dataclass_field(default=Mesh3DPM(), description="3DPM onion result")
    strength: list[Lcom] = dataclass_field(default=[], description="Strength result")

    class Config(MBaseModel.Config):
        title = "GSD 3DPM Result"
        widget = "3DPM_Widget"

class Unit(MBaseModel):
    """
    GSD global unit class
    """
    force: str = dataclass_field(
        default="kN", description="Force unit")
    length: str = dataclass_field(
        default="m", description="Length unit")
    section_dimension: str = dataclass_field(
        default="mm", description="Section dimension unit")
    pressure: str = dataclass_field(
        default="MPa", description="Pressure unit")
    strain: str = dataclass_field(
        default="%", description="Strain unit")

    class Config(MBaseModel.Config):
        title = "GSD Unit"

class DesignCode(MBaseModel):
    design_code: str = dataclass_field(default="ACI 318-19", max_length=30)
    sub_code: str = dataclass_field(default="SI")

    class Config(MBaseModel.Config):
        title = "GSD Design Code"


# ==== Stress Strain Curve ====
class Stress_Strain_Component(MBaseModel):
    stress: float = dataclass_field(default=0.0, description="Stress")
    strain: float = dataclass_field(default=0.0, description="Strain")

    class Config(MBaseModel.Config):
        title = "Stress Strain Component"

# ==== Concrete Material ====
class ConcreteGrade(MBaseModel):
    """
    GSD concrete class
    """
    design_code: str = dataclass_field(
        default="ACI318M-19", description="Design code")
    grade: str = dataclass_field(
        default="C12", description="Grade of the concrete")

    class Config(MBaseModel.Config):
        title = "GSD Concrete Grade"

class Concrete_General_Properties(MBaseModel):
    """
    GSD concrete general properties for calculation
    """
    strength: int = dataclass_field(
        gt=0, default=12, description="Grade of the concrete")
    elastic_modulus: float = dataclass_field(
        gt=0, default=30000, description="Elastic modulus of the concrete")
    density: float = dataclass_field(
        gt=0, default=2400, description="Density of the concrete")
    thermal_expansion_coefficient: float = dataclass_field(
        gt=0, default=0.00001, description="Thermal expansion coefficient of the concrete")
    poisson_ratio: float = dataclass_field(
        gt=0, default=0.2, description="Poisson ratio of the concrete")

    class Config(MBaseModel.Config):
        title = "GSD Concrete General Properties"

class Concrete_Stress_ULS_Options_ACI(MBaseModel):
    """
    GSD concrete stress options for ULS
    """
    material_model: str = dataclass_field(
        default="Rectangle", description="Material model for ULS")
    factor_b1: float = dataclass_field(
        default=0.85, description="Plastic strain limit for ULS")
    compressive_failure_strain: float = dataclass_field(
        default=0.003, description="Failure strain limit for ULS")

    class Config(MBaseModel.Config):
        title = "GSD Concrete Stress Options for ULS"

class Concrete_Stress_ULS_Options_Eurocode(MBaseModel):
    """
    GSD concrete stress options for ULS
    """
    material_model: str = dataclass_field(
        default="Rectangle", description="Material model for ULS")
    partial_factor_case: float = dataclass_field(
        default=1.0, description="Partial factor case for ULS")
    partial_factor: float = dataclass_field(
        default=1.5, description="Partial factor for ULS")
    compressive_failure_strain: float = dataclass_field(
        default=0.003, description="Failure strain limit for ULS")

    class Config(MBaseModel.Config):
        title = "GSD Concrete Stress Options for ULS"

class Concrete_SLS_Options(MBaseModel):
    """
    GSD concrete stress options for SLS
    """
    material_model: str = dataclass_field(
        default="Linear", description="Material model for SLS")
    plastic_strain_limit: float = dataclass_field(
        default=0.002, description="Plastic strain limit for SLS")
    failure_compression_limit: float = dataclass_field(
        default=0.003, description="Failure compression limit for SLS")
    material_model_tension: str = dataclass_field(
        default="interpolated", description="Material model for SLS tension")
    failure_tension_limit: float = dataclass_field(
        default=0.003, description="Failure tension limit for SLS")

    class Config(MBaseModel.Config):
        title = "GSD Concrete Stress Options for SLS"

# ==== Rebar & Tendon Materials ====
class RebarGrade(MBaseModel):
    """
    GSD rebar grade class
    """
    design_code: str = dataclass_field(
        default="ACI318M-19", description="Design code")
    grade: str = dataclass_field(
        default="Grade 420", description="Grade of the rebar")

    class Config(MBaseModel.Config):
        title = "GSD Rebar Grade"

class TendonGrade(MBaseModel):
    """
    GSD Tendon grade class
    """
    design_code: str = dataclass_field(
        default="ACI318M-19", description="Design code")
    grade: str = dataclass_field(default="Grade 420", description="Grade of the tendon")

    class Config(MBaseModel.Config):
        title = "GSD Tendon Grade"

class RebarProp(MBaseModel):
    """
    GSD rebar prop
    """
    area: float = dataclass_field(default=287.0, description="Area of the rebar")
    material: RebarGrade = dataclass_field(default=RebarGrade(), description="Material of the rebar")

    class Config(MBaseModel.Config):
        title = "GSD Rebar Properties"

class TendonProp(MBaseModel):
    """
    GSD Tendon prop
    """
    area: float = dataclass_field(default=287.0, description="Area of the tendon")
    material: TendonGrade = dataclass_field(default=TendonGrade(), description="Material of the tendon")
    prestress: float = dataclass_field(default=0.0, description="Prestress of the tendon")

    class Config(MBaseModel.Config):
        title = "GSD Tendon Properties"

class Rebar_General_Properties(MBaseModel):
    """
    GSD rebar general properties for calculation
    """
    strength: int = dataclass_field(
        default=420, description="Grade of the rebar")
    elastic_modulus: float = dataclass_field(
        default=200000, description="Elastic modulus of the rebar")
    density: float = dataclass_field(
        default=7850, description="Density of the rebar")
    thermal_expansion_coefficient: float = dataclass_field(
        default=0.00001, description="Thermal expansion coefficient of the rebar")
    poisson_ratio: float = dataclass_field(
        default=0.3, description="Poisson ratio of the rebar")

    class Config(MBaseModel.Config):
        title = "GSD Rebar General Properties"

class Rebar_Stress_ULS_Options_ACI(MBaseModel):
    """
    GSD rebar stress options for ULS
    """
    material_model: str = dataclass_field(
        default="Elastic-Plastic", description="Material model for ULS")
    failure_strain: float = dataclass_field(
        default=0.7, description="Failure strain limit for ULS")

    class Config(MBaseModel.Config):
        title = "GSD Rebar Stress Options for ULS"

class Rebar_Stress_SLS_Options(MBaseModel):
    """
    GSD rebar stress options for SLS
    """
    material_model: str = dataclass_field(
        default="Elastic-Plastic", description="Material model for SLS")
    failure_strain: float = dataclass_field(
        default=0.7, metadata={"default" : 0.7, "description": "Failure strain limit for SLS"})

    class Config(MBaseModel.Config):
        title = "GSD Rebar Stress Options for SLS"

class MaterialRebar(MBaseModel):
    """
    GSD rebar class
    """
    grade: RebarGrade = dataclass_field(
        default=RebarGrade(), description="Grade of the rebar")
    curve_uls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.0025, stress=500.0), Stress_Strain_Component(strain=0.05, stress=500.0)], description="Stress strain curve")
    curve_sls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.0025, stress=500.0), Stress_Strain_Component(strain=0.05, stress=500.0)], description="Stress strain curve")

    class Config(MBaseModel.Config):
        title = "GSD Material Rebar"

class MaterialTendon(MBaseModel):
    """
    GSD tendon class
    """
    grade: TendonGrade = dataclass_field(default=TendonGrade(), description="Grade of the tendon")
    curve_uls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.00725, stress=1450.0), Stress_Strain_Component(strain=0.05, stress=1750.0)], description="Stress strain curve")
    curve_sls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.00725, stress=1450.0), Stress_Strain_Component(strain=0.05, stress=1750.0)], description="Stress strain curve")

    class Config(MBaseModel.Config):
        title = "GSD Material Tendon"

class MaterialConcrete(MBaseModel):
    """
    GSD material for Concrete class
    """
    grade: ConcreteGrade = dataclass_field(
        default=ConcreteGrade(), description="Grade of the concrete")
    curve_uls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.0006, stress=0.0), Stress_Strain_Component(strain=0.0006, stress=34.0), Stress_Strain_Component(strain=0.003, stress=34.0)], description="Stress strain curve concrete ULS")
    curve_sls: list[Stress_Strain_Component] = dataclass_field(default=[Stress_Strain_Component(strain=0.0, stress=0.0), Stress_Strain_Component(strain=0.001, stress=32.8)], description="Stress strain curve")

    class Config(MBaseModel.Config):
        title = "GSD Material Concrete"

class Material(MBaseModel):
    """
    GSD concrete class
    """
    concrete: MaterialConcrete = dataclass_field(
        default=MaterialConcrete(), description="Concrete properties")
    rebar: Optional[MaterialRebar] = dataclass_field(
        default=MaterialRebar(), description="Rebar properties")
    tendon: Optional[MaterialTendon] = dataclass_field(
        default=MaterialTendon(), description="Tendon properties")

    class Config(MBaseModel.Config):
        title = "GSD Material"

# ==== Geometry ====
class Point(MBaseModel):
    """
    Point class
    """
    x: float
    y: float

    class Config(MBaseModel.Config):
        title = "Point"

class Points(MBaseModel):
    """
    GSD Points class
    """
    points: list[Point] = dataclass_field(default=[Point(x=0.0, y=0.0), Point(x=400.0, y=0.0), Point(x=400.0, y=600.0), Point(x=0.0, y=600.0)], description="Points")

    class Config(MBaseModel.Config):
        title = "GSD Points"

class ConcreteGeometry(MBaseModel):
    """
    GSD concrete geometry class
    """
    outerPolygon: Points = dataclass_field(default=Points(points=[Point(x=0.0, y=0.0), Point(x=400.0, y=0.0), Point(x=400.0, y=600.0), Point(x=0.0, y=600.0)]), description="Outer polygon of the concrete")
    innerPolygon: Points = dataclass_field(default=None, description="Inner polygon of the concrete")
    material: ConcreteGrade = dataclass_field(default=ConcreteGrade(), description="Material of the concrete")

    class Config(MBaseModel.Config):
        title = "GSD Concrete Geometry"

class RebarGeometry(MBaseModel):
    """
    GSD rebar geometry class
    """
    points: list[Point] = dataclass_field(default=[Point(x=40.0, y=40.0), Point(x=360.0, y=40.0), Point(x=360.0, y=560.0), Point(x=40.0, y=560.0)], description="Rebar Points")
    prop: RebarProp = dataclass_field(default=RebarProp(), description="properties of the rebar")

    class Config(MBaseModel.Config):
        title = "GSD Rebar Geometry"

class TendonGeometry(MBaseModel):
    """
    GSD tender geometry class
    """
    points: list[Point] = dataclass_field(default=[Point(x=200.0, y=100.0)], description="Tendon Points")
    prop: TendonProp = dataclass_field(default=TendonProp(), description="properties of the tender")

    class Config(MBaseModel.Config):
        title = "GSD Tender Geometry"

class Geometry(MBaseModel):
    """
    GSD geometry class
    """
    concrete: ConcreteGeometry = dataclass_field(default=ConcreteGeometry(), description="Concrete geometry")
    rebar: Optional[RebarGeometry] = dataclass_field(default=RebarGeometry(), description="Rebar geometry")
    tendon: Optional[TendonGeometry] = dataclass_field(default=TendonGeometry(), description="Tender geometry")

    class Config(MBaseModel.Config):
        title = "GSD Geometry"

class Lcb(MBaseModel):
    """
    GSD load combination class
    """
    uls: Lcoms = dataclass_field(default=Lcoms(), description="uls load combination")

    class Config(MBaseModel.Config):
        title = "GSD Load Combination"

# ==== options ====
class PMOptions(MBaseModel):
    """
    GSD options class
    """
    dgncode: str = dataclass_field(default="ACI318M-19", description="Design code")
    by_ecc_pu: str = dataclass_field(default="ecc", description="ecc or P-U")

    class Config(MBaseModel.Config):
        title = "GSD Options"


# ==== functions ====
@auto_schema
def conc_properties_design(
    general: Concrete_General_Properties,
    uls: Concrete_Stress_ULS_Options_ACI,
    sls: Concrete_SLS_Options
) -> MaterialConcrete:
    """
    Return the concrete material properties based on the design code

    Args:
        general: general concrete properties
        uls: concrete stress options for ULS
        sls: concrete stress options for SLS

    return:
        MaterialConcrete: material properties of selected data
    """
    if general is None:
        general = Concrete_General_Properties()
    if uls is None:
        uls = Concrete_Stress_ULS_Options_ACI()
    if sls is None:
        sls = Concrete_SLS_Options()

    if uls.material_model == 'Rectangle':
        _uls_strains = [
            0,
            uls.compressive_failure_strain * (1 - uls.factor_b1),
            uls.compressive_failure_strain * (1 - uls.factor_b1),
            uls.compressive_failure_strain,
        ]
        _uls_stress = [
            0,
            0,
            uls.factor_b1 * general.strength,
            uls.factor_b1 * general.strength,
        ]

    if sls.material_model == 'Linear':
        _sls_strains = [
            0,
            sls.failure_compression_limit,
        ]
        _sls_stress = [
            0,
            general.strength,
        ]

    ss_uls_components = [Stress_Strain_Component(stress=_uls_stress[i], strain=_uls_strains[i]) for i in range(len(_uls_strains))]
    ss_sls_components = [Stress_Strain_Component(stress=_sls_stress[i], strain=_sls_strains[i]) for i in range(len(_sls_strains))]
    return MaterialConcrete(curve_uls=ss_uls_components, curve_sls=ss_sls_components)

@auto_schema
def rebar_properties_design(
    general: Rebar_General_Properties,
    uls: Rebar_Stress_ULS_Options_ACI,
    sls: Rebar_Stress_SLS_Options
) -> MaterialRebar:
    """
    Return the material properties based on the design code

    Args:
        general: general rebar properties
        uls: rebar stress options for ULS
        sls: rebar stress options for SLS

    return:
        MaterialRebar: material properties of selected data
    """
    yield_strain = general.strength / general.elastic_modulus

    _sls_strains = [
        0,
        yield_strain,
        sls.failure_strain
    ]
    _sls_stress = [
        0,
        general.strength,
        general.strength,
    ]

    _uls_strains = [
        0,
        yield_strain,
        uls.failure_strain
    ]
    _uls_stress = [
        0,
        general.strength,
        general.strength
    ]

    ss_uls_components = [Stress_Strain_Component(stress=_uls_stress[i], strain=_uls_strains[i]) for i in range(len(_uls_strains))]
    ss_sls_components = [Stress_Strain_Component(stress=_sls_stress[i], strain=_sls_strains[i]) for i in range(len(_sls_strains))]

    return MaterialRebar(curve_uls=ss_uls_components, curve_sls=ss_sls_components)

class PM3DCurve:
    """
    Class for PM3D Curve Calculation
    """
    def __init__(self, matl=Material, geom=Geometry, lcb=Lcb, opt=PMOptions):
        if hasattr(matl, "concrete"):
            self.conc = matl.concrete
            if self.conc is not None:
                self.concrete_material_uls = self.conc.curve_uls
                self.concrete_material_sls = self.conc.curve_sls

        if hasattr(matl, "rebar"):
            self.rebar = matl.rebar
            if self.rebar is not None:
                self.rebar_material_uls = self.rebar.curve_uls
                self.rebar_material_sls = self.rebar.curve_sls

        if hasattr(matl, "tendon"):
            self.tendon = matl.tendon
            if self.tendon is not None:
                self.tendon_material_uls = self.tendon.curve_uls
                self.tendon_material_sls = self.tendon.curve_sls

        self.geom = geom
        if self.geom is not None:
            self.concrete_geom = self.geom.concrete
            if hasattr(self.geom, "rebar"):
                self.rebar_geom = self.geom.rebar

            if hasattr(self.geom, "tendon"):
                self.tendon_geom = self.geom.tendon

        self.lcom = lcb
        if self.lcom is not None:
            self.lcom_uls = self.lcom.uls

        self.option = opt

    def get_concrete_material_curve(self, type_):
        if type_ == "uls":
            curve_data = self.concrete_material_uls
        elif type_ == "sls":
            curve_data = self.concrete_material_sls

        return [component.stress for component in curve_data], [component.strain for component in curve_data]

    def get_rebar_material_curve(self, type_):
        if type_ == "uls":
            curve_data = self.rebar_material_uls
        elif type_ == "sls":
            curve_data = self.rebar_material_sls

        return [component.stress for component in curve_data], [component.strain for component in curve_data]

    def get_tendon_material_curve(self, type_):
        if type_ == "uls":
            curve_data = self.tendon_material_uls
        elif type_ == "sls":
            curve_data = self.tendon_material_sls

        return [component.stress for component in curve_data], [component.strain for component in curve_data]

    def get_max_strain_with_zero_stress(self, data):
        df = pd.DataFrame(data["DATA"]).transpose()
        df.columns = data["HEAD"]

        zero_stress_strains = df[df["Stress"] == 0.0]["Strain"]

        max_strain = zero_stress_strains.max()
        return max_strain

    def get_concrete_geom(self):
        return self.concrete_geom

    def get_rebar_geom(self):
        if hasattr(self, 'rebar_geom'):
            return self.rebar_geom
        return None

    def get_tendon_geom(self):
        if hasattr(self, 'tendon_geom'):
            return self.tendon_geom
        return None

    def get_lcom_uls_data(self):
        return self.lcom_uls.DATA

    def get_lcom_sls_data(self):
        return self.lcom_sls.DATA

    def get_option_by_ecc_pu(self):
        return self.option.by_ecc_pu

    def compound_section(
        self,
        concrete: list[dict],
        rebar: list[dict],
        tendon: list[dict],
        conc_mat: pre.Material = pre.DEFAULT_MATERIAL,
        steel_mat: pre.Material = pre.DEFAULT_MATERIAL,
        tendon_mat: pre.Material = pre.DEFAULT_MATERIAL
    ) -> geometry.CompoundGeometry:
        conc_polygon = concrete.outerPolygon

        def convert_points_to_list(points):
            return [[point.x, point.y] for point in points]

        polygon = Polygon(convert_points_to_list(conc_polygon.points))
        concrete_geometry = geometry.Geometry(geom=polygon, material=conc_mat)

        # cnosider rebar
        if rebar is not None:
            area = rebar.prop.area
            posi = rebar.points
            trans_pos = convert_points_to_list(posi)

            for x, y in trans_pos:
                concrete_geometry = add_bar(
                    geometry=concrete_geometry,
                    area=area,
                    material=steel_mat,
                    x=x,
                    y=y,
                    n=4
                )

        # consider tendon
        if tendon is not None:
            t_area = tendon.prop.area
            t_posi = tendon.points
            t_trans_pos = convert_points_to_list(t_posi)

            for x, y in t_trans_pos:
                concrete_geometry = add_bar(
                    geometry=concrete_geometry,
                    area=t_area,
                    material=tendon_mat,
                    x=x,
                    y=y,
                )

        if isinstance(concrete_geometry, geometry.CompoundGeometry):
            return concrete_geometry
        else:
            raise ValueError("Concrete section generation failed.")

    # TODO Tendon 만 있을 경우 Cb값에 대해 처리해줘야되나?
    def get_Cb(self, sect, theta_rad, ecu, esu):
        d_ext, _ = sect.extreme_bar(theta=theta_rad)
        return (ecu / (ecu + esu)) * d_ext

    def make_3dpm_data(self):
        if self.conc is None or self.rebar is None or self.geom is None or self.lcom is None:
            return "Data is not enough."

        # TODO 이 변수들 지걸로 맞춰줘야되!!
        beta1 = 0.8
        ecu = 0.003
        esu = 0.05
        fck = 30.0

        ss_uls = self.get_concrete_material_curve("uls")
        ss_sls = self.get_concrete_material_curve("sls")
        ss_conc_uls = ssp.ConcreteUltimateProfile(stresses=ss_uls[0], strains=ss_uls[1], compressive_strength=fck)
        ss_conc_ser = ssp.ConcreteServiceProfile(stresses=ss_sls[0], strains=ss_sls[1], ultimate_strain=ecu)

        # ss_rebar_uls = ssp.StressStrainProfile(self.get_rebar_material_curve("uls")["Strain"], self.get_rebar_material_curve("uls")["Stress"])
        # ss_rebar_sls = ssp.StressStrainProfile(self.get_rebar_material_curve("sls")["Strain"], self.get_rebar_material_curve("sls")["Stress"])

        concrete_matl = Concrete(
            name=self.conc.grade.grade,
            density=2.4e-6,
            stress_strain_profile=ss_conc_ser,
            ultimate_stress_strain_profile=ss_conc_uls,
            flexural_tensile_strength=0.6 * np.sqrt(40),
            colour="lightgrey",
        )

        if hasattr(self, 'rebar'):
            steel_matl = SteelBar(
                name=self.rebar.grade.grade,
                density=7.85e-6,
                stress_strain_profile=ssp.SteelElasticPlastic(
                    yield_strength=500,
                    elastic_modulus=200e3,
                    fracture_strain=esu,
                ),
                colour="grey",
            )
        else:
            steel_matl = None

        if hasattr(self, 'tendon_geom'):
            tendon_matl = SteelStrand(
                name="1830 MPa Strand",
                density=7.85e-6,
                stress_strain_profile=ssp.StrandHardening(
                    yield_strength=1500,
                    elastic_modulus=200e3,
                    fracture_strain=0.035,
                    breaking_strength=1830,
                ),
                colour="slategrey",
                prestress_stress=self.tendon_geom.prop.prestress,
            )
        else:
            tendon_matl = None

        # reference geometry
        hasRebar = True if self.get_rebar_geom() is not None else False
        compound_sect = self.compound_section(self.get_concrete_geom(), self.get_rebar_geom(), self.get_tendon_geom(), concrete_matl, steel_matl, tendon_matl)
        if self.get_tendon_geom() is not None:
            ref_sec = PrestressedSection(compound_sect)
        else:
            ref_sec = ConcreteSection(compound_sect)

        results = []
        theta_range = np.arange(0.0, 361.0, 15.0).tolist()

        for theta in theta_range:
            theta_rad = np.radians(theta)
            x11_max, x11_min, y22_max, y22_min = utils.calculate_local_extents( 
                geometry=ref_sec.compound_geometry,
                cx=ref_sec.gross_properties.cx,
                cy=ref_sec.gross_properties.cy,
                theta=theta_rad
            )

            C_Max = abs(y22_max - y22_min) / beta1
            d_n_range = np.linspace(0.01, C_Max * 1.1, 10).tolist()  # numpy 배열을 float 리스트로 변환

            if hasRebar is True:
                Cb = self.get_Cb(ref_sec, theta_rad, ecu, esu)
                d_n_range.append(Cb)

            for d_n in d_n_range:
                res = concreteproperties.results.UltimateBendingResults(theta_rad)
                res = ref_sec.calculate_ultimate_section_actions(d_n, res)
                results.append(res)

        return results

class DgnCode(ABC):
    """
    Class for Design Code
    """
    def __init__(self) -> None:
        pass

    @abstractmethod
    def make_3dpm_data(self, material: Material, geometry: Geometry, lcb: Lcb, opt: PMOptions):
        pm = PM3DCurve(material, geometry, lcb, opt)
        return pm.make_3dpm_data()

    def get_option_by_ecc_pu(self, opt: PMOptions):
        return opt.by_ecc_pu

class DgnCodeUS(DgnCode):
    """
    Class for Design Code US
    """
    def __init__(self) -> None:
        super().__init__()

    def make_3dpm_data(self, material: Material, geometry: Geometry, lcb: Lcb, opt: PMOptions):
        res = super().make_3dpm_data(material, geometry, lcb, opt)
        # 원래 데이터를 갖고 있는게 좋을지는 기획 내용에 따라 다를 수 있음
        pnmax = max(res, key=lambda x: x.n).n
        pnmax *= 0.8
        for result in res:
            _et = 0.003 * (result.k_u**-1 - 1.0)
            _phi_tens = 0.85
            _phi_comp = 0.65
            _e_tens = 0.005
            _e_comp = 0.002
            if _et >= _e_tens:
                phi = _phi_tens
            elif _et <= _e_comp:
                phi = _phi_comp
            else:
                phi = _phi_comp + (_phi_tens - _phi_comp) * (_e_tens - _e_comp) / (_e_tens - _e_comp)

            _tmp = result.n * phi
            result.n = min(_tmp, pnmax)
            result.m_x *= phi
            result.m_y *= phi
            result.m_xy *= phi

        return res

class DgnCodeEU(DgnCode):
    """
    Class for Design Code EU
    """
    def __init__(self) -> None:
        super().__init__()

    def make_3dpm_data(self, material: Material, geometry: Geometry, lcb: Lcb, opt: PMOptions):
        return super().make_3dpm_data(material, geometry, lcb, opt)

@auto_schema
def calc_3dpm(material: Material, geometry: Geometry, lcb: Lcb, opt: PMOptions) -> Result3DPM:
    """
    Return the 3D PM Curve & norminal strength points

    Args:
        material: Material
        geometry: Geometry
        lcb: Lcb
        opt: PMOptions

    return:
        Result3DPM: 3DPM curve & norminal strength points about lcom
    """
    if opt.dgncode == "ACI318M-19":
        pm = DgnCodeUS()
    else:
        pm = DgnCodeEU()

    results = pm.make_3dpm_data(material, geometry, lcb, opt)

    d_n_values = [result.n for result in results]
    m_x_values = [result.m_x for result in results]
    m_y_values = [result.m_y for result in results]

    points = np.column_stack((m_x_values, m_y_values, d_n_values))
    hull = ConvexHull(points)
    mesh1 = trimesh.Trimesh(vertices=hull.points, faces=hull.simplices)
    ray = trimesh.ray.ray_pyembree.RayMeshIntersector(mesh1)

    result_lcom_uls = []
    for lcom in lcb.uls.lcoms:
        lcom_name = lcom.name
        lcom_point = [lcom.f.Mx, lcom.f.My, lcom.f.Nz]

        if pm.get_option_by_ecc_pu(opt) == "ecc":
            origin = np.array([0, 0, 0])
        else:
            origin = np.array([0, 0, lcom_point[2]])

        direction = lcom_point - origin
        direction = direction / np.linalg.norm(direction)

        locations, index_ray, index_tri = ray.intersects_location(
            ray_origins=np.array([origin]),
            ray_directions=np.array([direction])
        )

        result_lcom_uls.append(Lcom(name=lcom_name, f=Force(Nz=locations[0, 2], Mx=locations[0, 0], My=locations[0, 1])))

    meshres = []
    for i in range(len(hull.points)):
        meshres.append(Force(Mx=hull.points[i][0], My=hull.points[i][1], Nz=hull.points[i][2]))

    meshData = Mesh3DPM(mesh3dpm=meshres)
    return Result3DPM(meshes=meshData, strength=result_lcom_uls)

# dummy functions
@auto_schema
def concrete_geometry(Polygon: Points, matl: ConcreteGrade) -> ConcreteGeometry:
    return ConcreteGeometry(outerPolygon=Polygon, material=matl)

@auto_schema
def rebar_geometry(position: Points, prop: RebarProp) -> RebarGeometry:
    return RebarGeometry(position=position.points, prop=prop)

@auto_schema
def tendon_geometry(position: Points, prop: TendonProp) -> TendonGeometry:
    return TendonGeometry(position=position.points, prop=prop)

@auto_schema
def geometry_design(concrete: ConcreteGeometry, rebar: RebarGeometry) -> Geometry:
    return Geometry(concrete=concrete, rebar=rebar)

@auto_schema
def material_properties_design(conc: MaterialConcrete, rebar: MaterialRebar) -> Material:
    return Material(concrete=conc, rebar=rebar)

@auto_schema
def lcom_design(uls: Lcoms) -> Lcb:
    return Lcb(uls=uls)

@auto_schema
def options_design(opt: PMOptions) -> PMOptions:
    return PMOptions(dgncode=opt.dgncode, by_ecc_pu=opt.by_ecc_pu)

# res = rebar_geometry(**{
#   "position": {
#     "points": [
#       {
#         "x": 0,
#         "y": 0
#       },
#       {
#         "x": 400,
#         "y": 0
#       },
#       {
#         "x": 400,
#         "y": 600
#       },
#       {
#         "x": 0,
#         "y": 600
#       }
#     ]
#   },
#   "prop": {
#     "area": 287,
#     "material": {
#       "design_code": "ACI318M-19",
#       "grade": "Grade 420"
#     }
#   }
# })

# print(res)

# _material = Material()
# _geometry = Geometry()
# _lcb = Lcb()
# _opt = PMOptions()
# res=calc_3dpm(_material, _geometry, _lcb, _opt)
# print(res)

# from dataclasses import dataclass, asdict
# res = MaterialRebar()
# data_dict = [component.__dict__ for component in res.curve_uls]
# print(data_dict)



















