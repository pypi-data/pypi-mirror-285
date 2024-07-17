import pytest
import moapy.project.wgsd.wgsd_sectionproperty as wgsd_sectionproperty

def test_sectprop_calc():
    inp = wgsd_sectionproperty.MPolygon()
    res = wgsd_sectionproperty.calc_sectprop(inp)
    res_data = res.to_dict()
    assert pytest.approx(res_data['Area']) == 240000.0
    assert pytest.approx(res_data['Asy']) == 200000.0
    assert pytest.approx(res_data['Asz']) == 200000.0
    assert pytest.approx(res_data['Ixx']) == 7517216331.957718
    assert pytest.approx(res_data['Iyy']) == 7200000000.0
    assert pytest.approx(res_data['Izz']) == 3200000000.0
    assert pytest.approx(res_data['Cy']) == 200.0
    assert pytest.approx(res_data['Cz']) == 300.0
    assert pytest.approx(res_data['Syp']) == 24000000.
    assert pytest.approx(res_data['Sym']) == 24000000.
    assert pytest.approx(res_data['Szp']) == 16000000.
    assert pytest.approx(res_data['Szm']) == 16000000.
    assert pytest.approx(res_data['Ipyy']) == 7200000000.
    assert pytest.approx(res_data['Ipzz']) == 3200000000.
    assert pytest.approx(res_data['Zy']) == 36000000.
    assert pytest.approx(res_data['Zz']) == 24000000.
    assert pytest.approx(res_data['ry']) == 173.2050807568887
    assert pytest.approx(res_data['rz']) == 115.47005383792664
