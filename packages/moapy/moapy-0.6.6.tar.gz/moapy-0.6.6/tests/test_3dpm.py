from scipy.spatial import ConvexHull
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import pytest
import moapy.project.wgsd.wgsd_flow as wgsd_flow

def test_3dpm_conc_rebar_EU():
    material = wgsd_flow.Material()
    material.concrete = wgsd_flow.MaterialConcrete()
    material.concrete.grade = wgsd_flow.ConcreteGrade()
    conc_uls_ss = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.0006, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.0006, stress=34.0), wgsd_flow.Stress_Strain_Component(strain=0.003, stress=34.0)]
    material.concrete.curve_uls = conc_uls_ss
    material.concrete.curve_sls = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.001, stress=32.8)]
    material.rebar = wgsd_flow.MaterialRebar()
    material.rebar.grade = wgsd_flow.RebarGrade()
    material.rebar.curve_uls = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.0025, stress=500.0), wgsd_flow.Stress_Strain_Component(strain=0.05, stress=500.0)]
    material.rebar.curve_sls = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.0025, stress=500.0), wgsd_flow.Stress_Strain_Component(strain=0.05, stress=500.0)]

    geom = wgsd_flow.Geometry
    geom.concrete = wgsd_flow.ConcreteGeometry()
    geom.concrete.outerPolygon = wgsd_flow.Points(points=[wgsd_flow.Point(x=0.0, y=0.0), wgsd_flow.Point(x=400.0, y=0.0), wgsd_flow.Point(x=400.0, y=600.0), wgsd_flow.Point(x=0.0, y=600.0)])
    geom.concrete.material = wgsd_flow.ConcreteGrade()

    reb = wgsd_flow.RebarGeometry
    reb.prop = wgsd_flow.RebarProp()
    reb.prop.area = 287.0
    reb.prop.material = wgsd_flow.RebarGrade()
    reb.prop.material.grade = "Grade 420"
    reb.points = [wgsd_flow.Point(x=40.0, y=40.0), wgsd_flow.Point(x=360.0, y=40.0), wgsd_flow.Point(x=360.0, y=560.0), wgsd_flow.Point(x=40.0, y=560.0)]
    geom.rebar = reb

    ten = wgsd_flow.TendonGeometry
    ten.prop = wgsd_flow.TendonProp()
    ten.prop.area = 287.0
    ten.prop.material = wgsd_flow.TendonGrade()
    ten.prop.material.grade = "Grade 420"
    ten.points = [wgsd_flow.Point(x=200.0, y=100.0)]
    geom.tendon = ten

    lcb = wgsd_flow.Lcb
    lcb.uls = wgsd_flow.Lcoms(lcoms=[wgsd_flow.Lcom(name="uls1", f=wgsd_flow.Force(Nz=100.0, Mx=10.0, My=50.0)), wgsd_flow.Lcom(name="uls2", f=wgsd_flow.Force(Nz=100.0, Mx=15.0, My=50.0)), wgsd_flow.Lcom(name="uls3", f=wgsd_flow.Force(Nz=100.0, Mx=0.0, My=0.0)), wgsd_flow.Lcom(name="uls4", f=wgsd_flow.Force(Nz=-100.0, Mx=0.0, My=0.0)) ])
    opt = wgsd_flow.PMOptions()
    opt.dgncode = "EN1992:2004"
    res = wgsd_flow.calc_3dpm(material, geom, lcb, opt)
    assert pytest.approx(res.strength[0].name) == 'uls1'
    # assert pytest.approx(res.strength[0].f.Mx) == 852061.208548877
    # assert pytest.approx(res.strength[0].f.My) == 4260306.042744385
    # assert pytest.approx(res.strength[0].f.Nz) == 8520612.08548877
    # assert pytest.approx(res.strength[1].name) == 'uls2'
    # assert pytest.approx(res.strength[1].f.Mx) == 1278091.8128233156
    # assert pytest.approx(res.strength[1].f.My) == 4260306.042744385
    # assert pytest.approx(res.strength[1].f.Nz) == 8520612.08548877
    # assert pytest.approx(res.strength[2].name) == 'uls3'
    # assert pytest.approx(res.strength[2].f.Mx) == 0.0
    # assert pytest.approx(res.strength[2].f.My) == 0.0
    # assert pytest.approx(res.strength[2].f.Nz) == 8541922.118669573
    # assert pytest.approx(res.strength[3].name) == 'uls4'
    # assert pytest.approx(res.strength[3].f.Mx) == 0.0
    # assert pytest.approx(res.strength[3].f.My) == 0.0
    # assert pytest.approx(res.strength[3].f.Nz) == -574000.0434647535
    fig = []
    for data in res.meshes.mesh3dpm:
        fig.append((data.Mx, data.My, data.Nz))
    return fig

def test_3dpm():
    material = wgsd_flow.Material()
    geom = wgsd_flow.Geometry()
    lcb = wgsd_flow.Lcb()
    opt = wgsd_flow.PMOptions()
    res = wgsd_flow.calc_3dpm(material, geom, lcb, opt)
    assert pytest.approx(res.strength[0].name) == 'uls1'
    # assert pytest.approx(res.strength[0].f.Mx) == 852061.208548877
    # assert pytest.approx(res.strength[0].f.My) == 4260306.042744385
    # assert pytest.approx(res.strength[0].f.Nz) == 8520612.08548877
    # assert pytest.approx(res.strength[1].name) == 'uls2'
    # assert pytest.approx(res.strength[1].f.Mx) == 1278091.8128233156
    # assert pytest.approx(res.strength[1].f.My) == 4260306.042744385
    # assert pytest.approx(res.strength[1].f.Nz) == 8520612.08548877
    # assert pytest.approx(res.strength[2].name) == 'uls3'
    # assert pytest.approx(res.strength[2].f.Mx) == 0.0
    # assert pytest.approx(res.strength[2].f.My) == 0.0
    # assert pytest.approx(res.strength[2].f.Nz) == 8541922.118669573
    # assert pytest.approx(res.strength[3].name) == 'uls4'
    # assert pytest.approx(res.strength[3].f.Mx) == 0.0
    # assert pytest.approx(res.strength[3].f.My) == 0.0
    # assert pytest.approx(res.strength[3].f.Nz) == -574000.0434647535
    fig = []
    for data in res.meshes.mesh3dpm:
        fig.append((data.Mx, data.My, data.Nz))
    return fig

def test_3dpm_conc_rebar_US():
    material = wgsd_flow.Material()
    material.concrete = wgsd_flow.MaterialConcrete()
    material.concrete.grade = wgsd_flow.ConcreteGrade()
    conc_uls_ss = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.0006, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.0006, stress=34.0), wgsd_flow.Stress_Strain_Component(strain=0.003, stress=34.0)]
    material.concrete.curve_uls = conc_uls_ss
    material.concrete.curve_sls = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.001, stress=32.8)]
    material.rebar = wgsd_flow.MaterialRebar()
    material.rebar.grade = wgsd_flow.RebarGrade()
    material.rebar.curve_uls = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.0025, stress=500.0), wgsd_flow.Stress_Strain_Component(strain=0.05, stress=500.0)]
    material.rebar.curve_sls = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.0025, stress=500.0), wgsd_flow.Stress_Strain_Component(strain=0.05, stress=500.0)]

    geom = wgsd_flow.Geometry
    geom.concrete = wgsd_flow.ConcreteGeometry()
    geom.concrete.outerPolygon = wgsd_flow.Points(points=[wgsd_flow.Point(x=0.0, y=0.0), wgsd_flow.Point(x=400.0, y=0.0), wgsd_flow.Point(x=400.0, y=600.0), wgsd_flow.Point(x=0.0, y=600.0)])
    geom.concrete.material = wgsd_flow.ConcreteGrade()

    reb = wgsd_flow.RebarGeometry
    reb.prop = wgsd_flow.RebarProp()
    reb.prop.area = 287.0
    reb.prop.material = wgsd_flow.RebarGrade()
    reb.prop.material.grade = "Grade 420"
    reb.points = [wgsd_flow.Point(x=40.0, y=40.0), wgsd_flow.Point(x=360.0, y=40.0), wgsd_flow.Point(x=360.0, y=560.0), wgsd_flow.Point(x=40.0, y=560.0)]
    geom.rebar = reb

    lcb = wgsd_flow.Lcb
    lcb.uls = wgsd_flow.Lcoms(lcoms=[wgsd_flow.Lcom(name="uls1", f=wgsd_flow.Force(Nz=100.0, Mx=10.0, My=50.0)), wgsd_flow.Lcom(name="uls2", f=wgsd_flow.Force(Nz=100.0, Mx=15.0, My=50.0)), wgsd_flow.Lcom(name="uls3", f=wgsd_flow.Force(Nz=100.0, Mx=0.0, My=0.0)), wgsd_flow.Lcom(name="uls4", f=wgsd_flow.Force(Nz=-100.0, Mx=0.0, My=0.0)) ])
    opt = wgsd_flow.PMOptions()
    opt.dgncode = "ACI318M-19"
    res = wgsd_flow.calc_3dpm(material, geom, lcb, opt)
    fig = []
    for data in res.meshes.mesh3dpm:
        fig.append((data.Mx, data.My, data.Nz))
    return fig
    # assert pytest.approx(res.strength.lcoms[0].name) == 'uls1'
    # assert pytest.approx(res.strength.lcoms[0].f.Mx) == 852061.208548877
    # assert pytest.approx(res.strength.lcoms[0].f.My) == 4260306.042744385
    # assert pytest.approx(res.strength.lcoms[0].f.Nz) == 8520612.08548877
    # assert pytest.approx(res.strength.lcoms[1].name) == 'uls2'
    # assert pytest.approx(res.strength.lcoms[1].f.Mx) == 1278091.8128233156
    # assert pytest.approx(res.strength.lcoms[1].f.My) == 4260306.042744385
    # assert pytest.approx(res.strength.lcoms[1].f.Nz) == 8520612.08548877
    # assert pytest.approx(res.strength.lcoms[2].name) == 'uls3'
    # assert pytest.approx(res.strength.lcoms[2].f.Mx) == 0.0
    # assert pytest.approx(res.strength.lcoms[2].f.My) == 0.0
    # assert pytest.approx(res.strength.lcoms[2].f.Nz) == 8541922.118669573
    # assert pytest.approx(res.strength.lcoms[3].name) == 'uls4'
    # assert pytest.approx(res.strength.lcoms[3].f.Mx) == 0.0
    # assert pytest.approx(res.strength.lcoms[3].f.My) == 0.0
    # assert pytest.approx(res.strength.lcoms[3].f.Nz) == -574000.0434647535

def test_3dpm_conc_tendon(prestressing):
    material = wgsd_flow.Material()
    material.concrete = wgsd_flow.MaterialConcrete()
    material.concrete.grade = wgsd_flow.ConcreteGrade()
    conc_uls_ss = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.0006, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.0006, stress=34.0), wgsd_flow.Stress_Strain_Component(strain=0.003, stress=34.0)]
    material.concrete.curve_uls = conc_uls_ss
    material.concrete.curve_sls = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.001, stress=32.8)]
    material.tendon = wgsd_flow.MaterialTendon()
    material.tendon.grade = wgsd_flow.TendonGrade()
    material.tendon.curve_uls = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.00725, stress=1450.0), wgsd_flow.Stress_Strain_Component(strain=0.05, stress=1750.0), wgsd_flow.Stress_Strain_Component(strain=0.1, stress=1750.0)]
    material.tendon.curve_sls = [wgsd_flow.Stress_Strain_Component(strain=0.0, stress=0.0), wgsd_flow.Stress_Strain_Component(strain=0.00725, stress=1450.0), wgsd_flow.Stress_Strain_Component(strain=0.05, stress=1750.0), wgsd_flow.Stress_Strain_Component(strain=0.1, stress=1750.0)]

    geom = wgsd_flow.Geometry
    geom.concrete = wgsd_flow.ConcreteGeometry()
    geom.concrete.outerPolygon = wgsd_flow.Points(points=[wgsd_flow.Point(x=0.0, y=0.0), wgsd_flow.Point(x=400.0, y=0.0), wgsd_flow.Point(x=400.0, y=600.0), wgsd_flow.Point(x=0.0, y=600.0)])
    geom.concrete.material = wgsd_flow.ConcreteGrade()

    tendon = wgsd_flow.TendonGeometry
    tendon.prop = wgsd_flow.TendonProp()
    tendon.prop.area = 2000.0
    tendon.prop.material = wgsd_flow.TendonGrade()
    tendon.prop.material.grade = "Grade 420"
    tendon.prop.prestress = prestressing
    tendon.points = [wgsd_flow.Point(x=200.0, y=150.0)]
    geom.tendon = tendon

    lcb = wgsd_flow.Lcb
    lcb.uls = wgsd_flow.Lcoms(lcoms=[wgsd_flow.Lcom(name="uls1", f=wgsd_flow.Force(Nz=100.0, Mx=10.0, My=50.0)), wgsd_flow.Lcom(name="uls2", f=wgsd_flow.Force(Nz=100.0, Mx=15.0, My=50.0))])
    opt = wgsd_flow.PMOptions()
    res = wgsd_flow.calc_3dpm(material, geom, lcb, opt)
    fig = []
    for data in res.meshes.mesh3dpm:
        fig.append((data.Mx, data.My, data.Nz))
    return fig

def test_3dpm_conc_rebar_default_US():
    material = wgsd_flow.Material()
    geom = wgsd_flow.Geometry()
    lcb = wgsd_flow.Lcb()
    opt = wgsd_flow.PMOptions()
    res = wgsd_flow.calc_3dpm(material, geom, lcb, opt)
    fig = []
    for data in res.meshes.mesh3dpm:
        fig.append((data.Mx, data.My, data.Nz))
    return fig

res = test_3dpm()
# # test_3dpm_conc_rebar_US()
# test_3dpm_conc_rebar_EU()
# res = test_3dpm_conc_rebar_US()
m_x_values = [item[0] for item in res]
m_y_values = [item[1] for item in res]
d_n_values = [item[2] for item in res]

# Combine m_x and m_y into a single array of points
points = np.column_stack((m_x_values, m_y_values, d_n_values))

hull = ConvexHull(points)

# Create the 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the convex hull
vertices = [points[simplex] for simplex in hull.simplices]
poly3d = Poly3DCollection(vertices, color='cyan', alpha=0.8)
ax.add_collection3d(poly3d)

# 새로운 데이터 셋의 Convex Hull 플롯

# Plot the original points
ax.scatter(m_x_values, m_y_values, d_n_values, color='green', label='Dataset 2')

# Set labels
ax.set_xlabel('m_x')
ax.set_ylabel('m_y')
ax.set_zlabel('d_n')
ax.set_title('3D PM Interacetion')

# Show the plot
plt.show()