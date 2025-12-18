from clinic_agent.clinic_server import get_doctors, get_doctor_availability

def test_doctor_lookup_by_day_and_area():
    res = get_doctors("ent", area="dankuni", day="wednesday")
    assert isinstance(res, list)
    assert any(d['doctor_id']=='d4' for d in res)

def test_doctor_availability_by_date():
    r = get_doctor_availability("d3", "2025-11-27")  # adjust date to a known weekday
    assert 'available' in r
