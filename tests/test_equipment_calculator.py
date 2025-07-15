import pytest
from calculators.EquipmentCalculator import EquipmentCalculator


class TestEquipmentCalculator:
    """Test cases for EquipmentCalculator class."""

    def test_calculate_pump_size_light_bioload(self):
        """Test pump size calculation for light bioload."""
        volume = 5000.0
        bioload = 3.0

        flow_rate, category = EquipmentCalculator.calculate_pump_size(volume, bioload)

        # Base: 5000/2 = 2500, multiplier: 1 + 3/10 = 1.3, result: 2500 * 1.3 = 3250
        assert flow_rate == 3250
        assert category == "Light bioload"

    def test_calculate_pump_size_medium_bioload(self):
        """Test pump size calculation for medium bioload."""
        volume = 5000.0
        bioload = 10.0

        flow_rate, category = EquipmentCalculator.calculate_pump_size(volume, bioload)

        # Base: 2500, multiplier: 1 + 10/10 = 2.0, result: 2500 * 2.0 = 5000
        assert flow_rate == 5000
        assert category == "Medium bioload"

    def test_calculate_pump_size_heavy_bioload(self):
        """Test pump size calculation for heavy bioload."""
        volume = 5000.0
        bioload = 20.0

        flow_rate, category = EquipmentCalculator.calculate_pump_size(volume, bioload)

        # Base: 2500, multiplier: 1 + 20/10 = 3.0, result: 2500 * 3.0 = 7500
        assert flow_rate == 7500
        assert category == "Heavy bioload"

    def test_calculate_pump_size_zero_bioload(self):
        """Test pump size calculation with zero bioload."""
        volume = 4000.0
        bioload = 0.0

        flow_rate, category = EquipmentCalculator.calculate_pump_size(volume, bioload)

        # Base: 4000/2 = 2000, multiplier: 1 + 0/10 = 1.0, result: 2000
        assert flow_rate == 2000
        assert category == "Light bioload"

    def test_calculate_pump_size_invalid_volume(self):
        """Test that zero or negative volume raises ValueError."""
        with pytest.raises(ValueError, match="Pond volume must be positive"):
            EquipmentCalculator.calculate_pump_size(0.0, 5.0)

        with pytest.raises(ValueError, match="Pond volume must be positive"):
            EquipmentCalculator.calculate_pump_size(-100.0, 5.0)

    def test_calculate_pump_size_negative_bioload(self):
        """Test that negative bioload raises ValueError."""
        with pytest.raises(ValueError, match="Bioload cannot be negative"):
            EquipmentCalculator.calculate_pump_size(5000.0, -1.0)

    def test_calculate_filter_specifications_low_bioload(self):
        """Test filter specifications for low bioload."""
        volume = 10000.0
        bioload = 3.0

        specs = EquipmentCalculator.calculate_filter_specifications(volume, bioload)

        # Bio filter: min(15, 5 + 3) = 8% of 10000 = 800L
        # UV: 10000 * (1/285) ≈ 35W
        assert specs["biological_filter"] == "800 liters filter media"
        assert specs["uv_sterilizer"] == "35 watts"
        assert "50-100 micron" in specs["mechanical_filter"]

    def test_calculate_filter_specifications_high_bioload(self):
        """Test filter specifications for high bioload."""
        volume = 10000.0
        bioload = 15.0

        specs = EquipmentCalculator.calculate_filter_specifications(volume, bioload)

        # Bio filter: min(15, 5 + 15) = 15% of 10000 = 1500L
        # UV: 10000 * (1/190) ≈ 52W
        assert specs["biological_filter"] == "1500 liters filter media"
        assert specs["uv_sterilizer"] == "52 watts"
        assert "50-100 micron" in specs["mechanical_filter"]

    def test_calculate_filter_specifications_invalid_volume(self):
        """Test that invalid volume raises ValueError."""
        with pytest.raises(ValueError, match="Pond volume must be positive"):
            EquipmentCalculator.calculate_filter_specifications(0.0, 5.0)

    def test_calculate_filter_specifications_negative_bioload(self):
        """Test that negative bioload raises ValueError."""
        with pytest.raises(ValueError, match="Bioload cannot be negative"):
            EquipmentCalculator.calculate_filter_specifications(5000.0, -1.0)
