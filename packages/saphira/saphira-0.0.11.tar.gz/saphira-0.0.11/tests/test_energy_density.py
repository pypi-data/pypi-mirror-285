import os
os.environ['SAPHIRA_URL'] = 'http://localhost:8081'
import saphira

def test_battery_energy_density():
    # Get the required parameters
    batt_ref = int(saphira.get_param('83092519-da63-4882-a899-297e3e62b65d.json', 'BattRef-0001'))
    batt_ref_1 = int(saphira.get_param('83092519-da63-4882-a899-297e3e62b65d.json', 'BattRef-0001-1'))

    # Calculate the energy density
    energy_density = batt_ref_1 / batt_ref

    # Test if the energy density exceeds 250 Wh/kg
    assert energy_density > 250, "Battery energy density must exceed 250 Wh/kg to ensure the vehicle's efficient operation without excessive weight."

test_battery_energy_density()