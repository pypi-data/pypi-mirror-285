
class UnitConverter:
    """
    A class to convert units between the International System of Units (SI) and the United States Customary Units (US).
    """
    def __init__(self):
        """
        Initializes the unit conversion ratios.
        """
        # si : International System of Units
        # us : United States Customary Units
        
        # Convert Ratio - Length
        # Base unit is meter and foot
        self.length_si_ratios = {'m': 1, 'cm': 1e+2, 'mm': 1e+3 }
        self.length_us_ratios = {'ft': 1, 'in': 12 }

        # Convert Ratio - Area
        # Base unit is square meter and square foot
        self.area_si_ratios = {'m': 1, 'cm': 1e+4, 'mm': 1e+6}
        self.area_us_ratios = {'ft': 1, 'in': 144 }

        # Volume units
        # Base unit is cubic meter and cubic foot
        self.volume_si_ratios = {'m': 1, 'cm': 1e+6, 'mm': 1e+9}
        self.volume_us_ratios = {'ft': 1, 'in': 1728}
        
        # Convert Ratio - Force
        # Base unit is newton and lbf
        self.force_si_ratios = {'N': 1, 'kN': 1e-3, 'MN': 1e-6}
        self.force_us_ratios = {'lbf': 1, 'kip': 1e-3}
        
        # Convert Ratio - Stress
        # Base unit is pascale and pound per square inch (psi)
        self.stress_si_ratios = {'Pa': 1, 'kPa': 1e-3, 'MPa': 1e-6}
        self.stress_us_ratios = {'psi': 1, 'ksi': 1e-3}
        
        # Convert Ratio - Strain (Unitless)
        # Base unit is pure number
        self.strain_ratios = {'strain': 1, 'percent': 1e-2, 'permil': 1e-3}
        
        # Convert Ratio - Mass
        # Base unit is kilogram and pound
        self.mass_si_ratios = {'kg': 1, 'ton': 1e-3}
        self.mass_us_ratios = {'lb': 1}
        
    def length(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    )-> float:
        """
        Converts length units between SI and US systems.
        
        Parameters:
        - value: The value to convert.
        - from_unit: The unit to convert from.
        - to_unit: The unit to convert to.
        
        Returns:
        - The converted value.
        """
        # https://www.nist.gov/pml/us-surveyfoot/revised-unit-conversion-factors
        
        # SI to SI conversion
        if from_unit in self.length_si_ratios and to_unit in self.length_si_ratios:
            return value * self.length_si_ratios[to_unit] / self.length_si_ratios[from_unit]
        
        # US to US conversion
        elif from_unit in self.length_us_ratios and to_unit in self.length_us_ratios:
            return value * self.length_us_ratios[to_unit] / self.length_us_ratios[from_unit]
        
        # SI to US conversion
        elif from_unit in self.length_si_ratios and to_unit in self.length_us_ratios:
            # First convert to inches and then to the target unit
            value_in_meters = value / self.length_si_ratios[from_unit]
            # 1 foot is 0.3048 meters
            value_in_foots = value_in_meters / 0.3048
            return value_in_foots * self.length_us_ratios[to_unit]
        
        # US to SI conversion
        elif from_unit in self.length_us_ratios and to_unit in self.length_si_ratios:
            # First convert to inches and then to the target unit
            value_in_foots = value / self.length_us_ratios[from_unit]
            # 1 foot is 0.3048 meters
            value_in_meters = value_in_foots * 0.3048
            return value_in_meters * self.length_si_ratios[to_unit]
        
        else:
            raise ValueError("Invalid unit conversion")

    def area(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    )-> float:
        """
        Converts area units between SI and US systems.
        
        Parameters:
        - value: The value to convert.
        - from_unit: The unit to convert from.
        - to_unit: The unit to convert to.
        
        Returns:
        - The converted value.
        """
        # SI to SI conversion
        if from_unit in self.area_si_ratios and to_unit in self.area_si_ratios:
            return value * self.area_si_ratios[to_unit] / self.area_si_ratios[from_unit]
        
        # US to US conversion
        elif from_unit in self.area_us_ratios and to_unit in self.area_us_ratios:
            return value * self.area_us_ratios[to_unit] / self.area_us_ratios[from_unit]
        
        # SI to US conversion
        elif from_unit in self.area_si_ratios and to_unit in self.area_us_ratios:
            # First convert to inches and then to the target unit
            value_in_meters = value / self.area_si_ratios[from_unit]
            # 1 foot is 0.3048 meters
            value_in_foots = value_in_meters / (0.3048**2)
            return value_in_foots * self.area_us_ratios[to_unit]
        
        # US to SI conversion
        elif from_unit in self.area_us_ratios and to_unit in self.area_si_ratios:
            # First convert to inches and then to the target unit
            value_in_foots = value / self.area_us_ratios[from_unit]
            # 1 foot is 0.3048 meters
            value_in_meters = value_in_foots * (0.3048**2)
            return value_in_meters * self.area_si_ratios[to_unit]
        
        else:
            raise ValueError("Invalid unit conversion")

    def volume(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    )-> float:
        """
        Converts volume units between SI and US systems.
        
        Parameters:
        - value: The value to convert.
        - from_unit: The unit to convert from.
        - to_unit: The unit to convert to.
        
        Returns:
        - The converted value.
        """
        # SI to SI conversion
        if from_unit in self.volume_si_ratios and to_unit in self.volume_si_ratios:
            return value * self.volume_si_ratios[to_unit] / self.volume_si_ratios[from_unit]
        
        # US to US conversion
        elif from_unit in self.volume_us_ratios and to_unit in self.volume_us_ratios:
            return value * self.volume_us_ratios[to_unit] / self.volume_us_ratios[from_unit]
        
        # SI to US conversion
        elif from_unit in self.volume_si_ratios and to_unit in self.volume_us_ratios:
            # First convert to inches and then to the target unit
            value_in_meters = value / self.volume_si_ratios[from_unit]
            # 1 foot is 0.3048 meters
            value_in_foots = value_in_meters / (0.3048**3)
            return value_in_foots * self.volume_us_ratios[to_unit]
        
        # US to SI conversion
        elif from_unit in self.volume_us_ratios and to_unit in self.volume_si_ratios:
            # First convert to inches and then to the target unit
            value_in_foots = value / self.volume_us_ratios[from_unit]
            # 1 foot is 0.3048 meters
            value_in_meters = value_in_foots * (0.3048**3)
            return value_in_meters * self.volume_si_ratios[to_unit]
        
        else:
            raise ValueError("Invalid unit conversion")
    
    def length_exponential(
        self,
        value: float,
        exponent: int,
        from_unit: str,
        to_unit: str
    )-> float:
        """
        Converts length units between SI and US systems with exponents.
        
        Parameters:
        - value: The value to convert.
        - exponent: The exponent to apply.
        - from_unit: The unit to convert from.
        - to_unit: The unit to convert to.
        
        Returns:
        - The converted value.
        """
        # SI to SI conversion
        if from_unit in self.length_si_ratios and to_unit in self.length_si_ratios:
            return value * (self.length_si_ratios[to_unit] / self.length_si_ratios[from_unit])**exponent
        
        # US to US conversion
        elif from_unit in self.length_us_ratios and to_unit in self.length_us_ratios:
            return value * (self.length_us_ratios[to_unit] / self.length_us_ratios[from_unit])**exponent
        
        # SI to US conversion
        elif from_unit in self.length_si_ratios and to_unit in self.length_us_ratios:
            # First convert to inches and then to the target unit
            value_in_meters = value / (self.length_si_ratios[from_unit]**exponent)
            # 1 foot is 0.3048 meters
            value_in_foots = value_in_meters / (0.3048**exponent)
            return value_in_foots * (self.length_us_ratios[to_unit]**exponent)
        
        # US to SI conversion
        elif from_unit in self.length_us_ratios and to_unit in self.length_si_ratios:
            # First convert to inches and then to the target unit
            value_in_foots = value / (self.length_us_ratios[from_unit]**exponent)
            # 1 foot is 0.3048 meters
            value_in_meters = value_in_foots * (0.3048**exponent)
            return value_in_meters * (self.length_si_ratios[to_unit]**exponent)
        
        else:
            raise ValueError("Invalid unit conversion")
    
    def temperature(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    )-> float:
        """
        Converts temperature units between Kelvin, Celsius, and Fahrenheit.
        
        Parameters:
        - value: The value to convert.
        - from_unit: The unit to convert from.
        - to_unit: The unit to convert to.
        
        Returns:
        - The converted value.
        """
        
        if from_unit == 'K' and to_unit == 'C':
            return value - 273.15
        elif from_unit == 'K' and to_unit == 'F':
            return (value - 273.15) * 9/5 + 32
        elif from_unit == 'C' and to_unit == 'K':
            return value + 273.15
        elif from_unit == 'C' and to_unit == 'F':
            return value * 9/5 + 32
        elif from_unit == 'F' and to_unit == 'K':
            return (value - 32) * 5/9 + 273.15
        elif from_unit == 'F' and to_unit == 'C':
            return (value - 32) * 5/9
        else:
            raise ValueError("Invalid unit conversion")
    
    def force(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    )-> float:
        """
        Converts force units between SI and US systems.
        
        Parameters:
        - value: The value to convert.
        - from_unit: The unit to convert from.
        - to_unit: The unit to convert to.
        
        Returns:
        - The converted value.
        """
        # https://en.wikipedia.org/wiki/Standard_gravity
        # https://en.wikipedia.org/wiki/International_yard_and_pound
        # https://en.wikipedia.org/wiki/Pound_(force)
        # Standard Acceleration due to Gravity; ISO 80000 =  9.80665m/s2
        # 1 lb = 0.453 592 37 kg
        # 1 lbf = 1 lb X 0.453 592 37 kg X 9.80665 m/s2 = 4.448 221 615 260 5 N
        
        # SI to SI conversion
        if from_unit in self.force_si_ratios and to_unit in self.force_si_ratios:
            return value * self.force_si_ratios[to_unit] / self.force_si_ratios[from_unit]
        
        # US to US conversion
        elif from_unit in self.force_us_ratios and to_unit in self.force_us_ratios:
            return value * self.force_us_ratios[to_unit] / self.force_us_ratios[from_unit]
        
        # SI to US conversion
        elif from_unit in self.force_si_ratios and to_unit in self.force_us_ratios:
            # First convert to newtons and then to the target unit
            value_in_newtons = value / self.force_si_ratios[from_unit]
            # 1 lbf is 4.4482216152605 newtons
            value_in_lbf = value_in_newtons / 4.4482216152605
            return value_in_lbf * self.force_us_ratios[to_unit]
        
        # Imperial to Metric conversion
        elif from_unit in self.force_us_ratios and to_unit in self.force_si_ratios:
            # First convert to lbf and then to the target unit
            value_in_lbf = value / self.force_us_ratios[from_unit]
            # 1 lbf is 4.4482216152605 newtons
            value_in_newtons = value_in_lbf * 4.4482216152605
            return value_in_newtons * self.force_si_ratios[to_unit]
        
        else:
            raise ValueError("Invalid unit conversion")

    def stress(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    )-> float:
        """
        Converts stress units between SI and US systems.
        
        Parameters:
        - value: The value to convert.
        - from_unit: The unit to convert from.
        - to_unit: The unit to convert to.
        
        Returns:
        - The converted value.
        """
        # 1 lbf = 1 lb X 0.453 592 37 kg X 9.80665 m/s2 = 4.448 221 615 260 5 N
        # 1 in = 0.0254 m , 1 in2 = 0.0254^2 m2
        # 1 psi = 1 lbf/in2 = 4.448 221 615 260 5 N / 0.0254^2 m2 = 6894.75729316836 Pa
        
        # SI to SI conversion
        if from_unit in self.stress_si_ratios and to_unit in self.stress_si_ratios:
            return value * self.stress_si_ratios[to_unit] / self.stress_si_ratios[from_unit]
        
        # US to US conversion
        elif from_unit in self.stress_us_ratios and to_unit in self.stress_us_ratios:
            return value * self.stress_us_ratios[to_unit] / self.stress_us_ratios[from_unit]
        
        # SI to US conversion
        elif from_unit in self.stress_si_ratios and to_unit in self.stress_us_ratios:
            # First convert to pascales and then to the target unit
            value_in_pascales = value / self.stress_si_ratios[from_unit]
            # 1 psi is 6894.75729316836 pascales
            value_in_psi = value_in_pascales / 6894.75729316836
            return value_in_psi * self.stress_us_ratios[to_unit]
        
        # US to SI conversion
        elif from_unit in self.stress_us_ratios and to_unit in self.stress_si_ratios:
            # First convert to psi and then to the target unit
            value_in_psi = value / self.stress_us_ratios[from_unit]
            # 1 psi is 6894.75729316836 pascales
            value_in_pascales = value_in_psi * 6894.75729316836
            return value_in_pascales * self.stress_si_ratios[to_unit]
        
        else:
            raise ValueError("Invalid unit conversion")

    def strain(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    )-> float:
        """
        Converts strain units between unitless, percent, and permil.
        
        Parameters:
        - value: The value to convert.
        - from_unit: The unit to convert from.
        - to_unit: The unit to convert to.
        
        Returns:
        - The converted value.
        """
        # Conversion
        if from_unit in self.strain_ratios and to_unit in self.strain_ratios:
            return value * self.strain_ratios[from_unit] / self.strain_ratios[to_unit]
        else:
            raise ValueError("Invalid unit conversion")
    
    def mass(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    )-> float:
        """
        Converts mass units between SI and US systems.
        
        Parameters:
        - value: The value to convert.
        - from_unit: The unit to convert from.
        - to_unit: The unit to convert to.
        
        Returns:
        - The converted value.
        """
        # https://en.wikipedia.org/wiki/Pound_(mass)
        # 1 lb = 0.453 592 37 kg
        
        # SI to SI conversion
        if from_unit in self.mass_si_ratios and to_unit in self.mass_si_ratios:
            return value * self.mass_si_ratios[to_unit] / self.mass_si_ratios[from_unit]
        
        # US to US conversion
        elif from_unit in self.mass_us_ratios and to_unit in self.mass_us_ratios:
            return value * self.mass_us_ratios[to_unit] / self.mass_us_ratios[from_unit]
        
        # SI to US conversion
        elif from_unit in self.mass_si_ratios and to_unit in self.mass_us_ratios:
            # First convert to inches and then to the target unit
            value_in_kilograms = value / self.mass_si_ratios[from_unit]
            # 1 lb is 0.45359237 kg
            value_in_pounds = value_in_kilograms / 0.45359237
            return value_in_pounds * self.mass_us_ratios[to_unit]
        
        # US to SI conversion
        elif from_unit in self.mass_us_ratios and to_unit in self.mass_si_ratios:
            # First convert to inches and then to the target unit
            value_in_pounds = value / self.mass_us_ratios[from_unit]
            # 1 lb is 0.45359237 kg
            value_in_kilograms = value_in_pounds * 0.45359237
            return value_in_kilograms * self.mass_si_ratios[to_unit]
        
        else:
            raise ValueError("Invalid unit conversion")
    
    def density(
        self,
        value: float,
        from_mass_units: str,
        from_volumn_units: str,
        to_mass_units: str,
        to_volumn_units: str,
    )-> float:
            """
            Converts density units between SI and US systems.
            
            Parameters:
            - value: The value to convert.
            - from_volumn_units: The volumn unit to convert from.
            - from_mass_units: The mass unit to convert from.
            - to_volumn_units: The volumn unit to convert to.
            - to_mass_units: The mass unit to convert to.
            
            Returns:
            - The converted value.
            """
            
            # Convert the value to the base unit
            value_in_kilograms = self.mass(value, from_mass_units, 'kg')
            value_in_meters = self.volume(value, from_volumn_units, 'm')
            
            # Convert the value to the target unit
            value_in_target_mass_units = self.mass(value_in_kilograms, 'kg', to_mass_units)
            value_in_target_volumn_units = self.volume(value_in_meters, 'm', to_volumn_units)
            
            # Calculate the density
            return value_in_target_mass_units / value_in_target_volumn_units
        
    def moment(
        self,
        value: float,
        from_force_units: str,
        from_length_units: str,
        to_force_units: str,
        to_length_units: str
    )-> float:
        """
        Converts moment units between SI and US systems.
        
        Parameters:
        - value: The value to convert.
        - from_force_units: The force unit to convert from.
        - from_length_units: The length unit to convert from.
        - to_force_units: The force unit to convert to.
        - to_length_units: The length unit to convert to.
        
        Returns:
        - The converted value.
        """
        # Convert the value to the base unit
        value_in_newtons = self.force(value, from_force_units, 'N')
        value_in_meters = self.length(value, from_length_units, 'm')
        
        # Convert the value to the target unit
        value_in_target_force_units = self.force(value_in_newtons, 'N', to_force_units)
        value_in_target_length_units = self.length(value_in_meters, 'm', to_length_units)
        
        # Calculate the moment
        return value_in_target_force_units * value_in_target_length_units
    
import unittest

class TestUnitConverter(unittest.TestCase):
    def setUp(self):
        self.converter = UnitConverter()

    def test_length_conversion(self):
        # SI unit conversions
        self.assertAlmostEqual(self.converter.length(1, 'm', 'mm'), 1000, places=5)
        self.assertAlmostEqual(self.converter.length(1, 'm', 'cm'), 100, places=5)
        self.assertAlmostEqual(self.converter.length(1000, 'mm', 'm'), 1, places=5)
        self.assertAlmostEqual(self.converter.length(100, 'cm', 'm'), 1, places=5)
        self.assertAlmostEqual(self.converter.length(1000, 'mm', 'cm'), 100, places=5)
        self.assertAlmostEqual(self.converter.length(100, 'cm', 'mm'), 1000, places=5)

        # US Customary unit conversions
        self.assertAlmostEqual(self.converter.length(1, 'ft', 'in'), 12, places=5)
        self.assertAlmostEqual(self.converter.length(12, 'in', 'ft'), 1, places=5)

        # SI to US conversions
        self.assertAlmostEqual(self.converter.length(1, 'm', 'ft'), 3.28084, places=5)
        self.assertAlmostEqual(self.converter.length(1, 'm', 'in'), 39.37008, places=5)
        self.assertAlmostEqual(self.converter.length(100, 'cm', 'ft'), 3.28084, places=5)
        self.assertAlmostEqual(self.converter.length(1000, 'mm', 'ft'), 3.28084, places=5)
        self.assertAlmostEqual(self.converter.length(100, 'cm', 'in'), 39.37008, places=5)
        self.assertAlmostEqual(self.converter.length(1000, 'mm', 'in'), 39.37008, places=5)

        # US to SI conversions
        self.assertAlmostEqual(self.converter.length(1, 'ft', 'm'), 0.3048, places=5)
        self.assertAlmostEqual(self.converter.length(1, 'ft', 'cm'), 30.48, places=5)
        self.assertAlmostEqual(self.converter.length(1, 'ft', 'mm'), 304.8, places=5)
        self.assertAlmostEqual(self.converter.length(1, 'in', 'm'), 0.0254, places=5)
        self.assertAlmostEqual(self.converter.length(1, 'in', 'cm'), 2.54, places=5)
        self.assertAlmostEqual(self.converter.length(1, 'in', 'mm'), 25.4, places=5)

    def test_area_conversion(self):
        # SI unit conversions (metric)
        self.assertAlmostEqual(self.converter.area(1, 'm', 'mm'), 1e6, places=0)
        self.assertAlmostEqual(self.converter.area(1, 'm', 'cm'), 1e4, places=0)
        self.assertAlmostEqual(self.converter.area(1e6, 'mm', 'm'), 1, places=5)
        self.assertAlmostEqual(self.converter.area(1e4, 'cm', 'm'), 1, places=5)
        self.assertAlmostEqual(self.converter.area(1e6, 'mm', 'cm'), 1e4, places=0)
        self.assertAlmostEqual(self.converter.area(1e4, 'cm', 'mm'), 1e6, places=0)

        # US Customary unit conversions
        self.assertAlmostEqual(self.converter.area(1, 'ft', 'in'), 144, places=0)
        self.assertAlmostEqual(self.converter.area(144, 'in', 'ft'), 1, places=5)

        # SI to US conversions
        self.assertAlmostEqual(self.converter.area(1, 'm', 'ft'), 10.7639, places=4)
        self.assertAlmostEqual(self.converter.area(1, 'm', 'in'), 1550.0031, places=4)
        self.assertAlmostEqual(self.converter.area(10000, 'cm', 'ft'), 10.7639, places=4)
        self.assertAlmostEqual(self.converter.area(1000000, 'mm', 'ft'), 10.7639, places=4)
        self.assertAlmostEqual(self.converter.area(10000, 'cm', 'in'), 1550.0031, places=4)
        self.assertAlmostEqual(self.converter.area(1000000, 'mm', 'in'), 1550.0031, places=4)

        # US to SI conversions
        self.assertAlmostEqual(self.converter.area(1, 'ft', 'm'), 0.092903, places=6)
        self.assertAlmostEqual(self.converter.area(1, 'ft', 'cm'), 929.0304, places=4)
        self.assertAlmostEqual(self.converter.area(1, 'ft', 'mm'), 92903.04, places=2)
        self.assertAlmostEqual(self.converter.area(1, 'in', 'm'), 0.00064516, places=8)
        self.assertAlmostEqual(self.converter.area(1, 'in', 'cm'), 6.4516, places=4)
        self.assertAlmostEqual(self.converter.area(1, 'in', 'mm'), 645.16, places=2)

    def test_volume_conversion(self):
        # Metric unit conversions (SI)
        self.assertAlmostEqual(self.converter.volume(1, 'm', 'cm'), 1e6, places=0)
        self.assertAlmostEqual(self.converter.volume(1, 'm', 'mm'), 1e9, places=0)
        self.assertAlmostEqual(self.converter.volume(1e6, 'cm', 'm'), 1, places=5)
        self.assertAlmostEqual(self.converter.volume(1e9, 'mm', 'm'), 1, places=5)
        self.assertAlmostEqual(self.converter.volume(1e6, 'cm', 'mm'), 1e9, places=0)
        self.assertAlmostEqual(self.converter.volume(1e9, 'mm', 'cm'), 1e6, places=0)

        # US Customary unit conversions
        self.assertAlmostEqual(self.converter.volume(1, 'ft', 'in'), 1728, places=0)
        self.assertAlmostEqual(self.converter.volume(1728, 'in', 'ft'), 1, places=5)

        # SI to US conversions
        self.assertAlmostEqual(self.converter.volume(1, 'm', 'ft'), 35.3147, places=4)
        self.assertAlmostEqual(self.converter.volume(1, 'm', 'in'), 61023.7441, places=4)
        self.assertAlmostEqual(self.converter.volume(1e6, 'cm', 'ft'), 35.3147, places=4)
        self.assertAlmostEqual(self.converter.volume(1e9, 'mm', 'ft'), 35.3147, places=4)
        self.assertAlmostEqual(self.converter.volume(1e6, 'cm', 'in'), 61023.7441, places=4)
        self.assertAlmostEqual(self.converter.volume(1e9, 'mm', 'in'), 61023.7441, places=4)

        # US to SI conversions
        self.assertAlmostEqual(self.converter.volume(1, 'ft', 'm'), 0.0283168, places=7)
        self.assertAlmostEqual(self.converter.volume(1, 'ft', 'cm'), 28316.8466, places=4)
        self.assertAlmostEqual(self.converter.volume(1, 'ft', 'mm'), 28316846.6, places=1)
        self.assertAlmostEqual(self.converter.volume(1, 'in', 'm'), 0.0000163871, places=10)
        self.assertAlmostEqual(self.converter.volume(1, 'in', 'cm'), 16.3871, places=4)
        self.assertAlmostEqual(self.converter.volume(1, 'in', 'mm'), 16387.1, places=1)

    def test_length_exponential_conversion(self):
        exponent = 4

        # SI to SI conversions
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'm', 'cm'), 100**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'm', 'mm'), 1000**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'cm', 'm'), (1/100)**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'cm', 'mm'), 10**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'mm', 'm'), (1/1000)**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'mm', 'cm'), (1/10)**exponent, places=8)

        # US to US conversions
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'ft', 'in'), 12**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'in', 'ft'), (1/12)**exponent, places=8)

        # SI to US conversions
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'm', 'ft'), (1 / 0.3048)**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'm', 'in'), (1 / (0.3048 / 12))**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'cm', 'ft'), (0.01 / 0.3048)**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'cm', 'in'), (0.01 / (0.3048 / 12))**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'mm', 'ft'), (0.001 / 0.3048)**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'mm', 'in'), (0.001 / (0.3048 / 12))**exponent, places=8)

        # US to SI conversions
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'ft', 'm'), 0.3048**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'ft', 'cm'), (0.3048 * 100)**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'ft', 'mm'), (0.3048 * 1000)**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'in', 'm'), (0.0254)**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'in', 'cm'), (0.0254 * 100)**exponent, places=8)
        self.assertAlmostEqual(self.converter.length_exponential(1, exponent, 'in', 'mm'), (0.0254 * 1000)**exponent, places=8)

    def test_force_conversion(self):
        # SI to SI conversions
        self.assertAlmostEqual(self.converter.force(1, 'N', 'kN'), 0.001, places=6)
        self.assertAlmostEqual(self.converter.force(1, 'N', 'MN'), 1e-6, places=9)
        self.assertAlmostEqual(self.converter.force(1, 'kN', 'N'), 1000, places=0)
        self.assertAlmostEqual(self.converter.force(1, 'MN', 'N'), 1e6, places=0)
        self.assertAlmostEqual(self.converter.force(1, 'kN', 'MN'), 0.001, places=6)
        self.assertAlmostEqual(self.converter.force(1, 'MN', 'kN'), 1000, places=0)

        # US to US conversions
        self.assertAlmostEqual(self.converter.force(1, 'lbf', 'kip'), 0.001, places=6)
        self.assertAlmostEqual(self.converter.force(1, 'kip', 'lbf'), 1000, places=0)

        # SI to US conversions
        self.assertAlmostEqual(self.converter.force(1, 'N', 'lbf'), 0.224809, places=6)
        self.assertAlmostEqual(self.converter.force(1, 'kN', 'lbf'), 224.809, places=3)
        self.assertAlmostEqual(self.converter.force(1, 'MN', 'lbf'), 224809, places=0)
        self.assertAlmostEqual(self.converter.force(1, 'N', 'kip'), 0.000224809, places=9)
        self.assertAlmostEqual(self.converter.force(1, 'kN', 'kip'), 0.224809, places=6)
        self.assertAlmostEqual(self.converter.force(1, 'MN', 'kip'), 224.809, places=3)

        # US to SI conversions
        self.assertAlmostEqual(self.converter.force(1, 'lbf', 'N'), 4.44822, places=5)
        self.assertAlmostEqual(self.converter.force(1, 'lbf', 'kN'), 0.00444822, places=8)
        self.assertAlmostEqual(self.converter.force(1, 'lbf', 'MN'), 4.44822e-6, places=5)
        self.assertAlmostEqual(self.converter.force(1, 'kip', 'N'), 4448.22, places=2)
        self.assertAlmostEqual(self.converter.force(1, 'kip', 'kN'), 4.44822, places=5)
        self.assertAlmostEqual(self.converter.force(1, 'kip', 'MN'), 0.00444822, places=8)

    def test_stress_conversion(self):
        # SI to SI conversions
        self.assertAlmostEqual(self.converter.stress(1, 'Pa', 'kPa'), 0.001, places=6)
        self.assertAlmostEqual(self.converter.stress(1, 'Pa', 'MPa'), 1e-6, places=9)
        self.assertAlmostEqual(self.converter.stress(1, 'kPa', 'Pa'), 1000, places=0)
        self.assertAlmostEqual(self.converter.stress(1, 'MPa', 'Pa'), 1e6, places=0)
        self.assertAlmostEqual(self.converter.stress(1, 'kPa', 'MPa'), 0.001, places=6)
        self.assertAlmostEqual(self.converter.stress(1, 'MPa', 'kPa'), 1000, places=0)

        # US to US conversions
        self.assertAlmostEqual(self.converter.stress(1, 'psi', 'ksi'), 0.001, places=6)
        self.assertAlmostEqual(self.converter.stress(1, 'ksi', 'psi'), 1000, places=0)

        # SI to US conversions
        self.assertAlmostEqual(self.converter.stress(1, 'Pa', 'psi'), 0.000145038, places=9)
        self.assertAlmostEqual(self.converter.stress(1, 'kPa', 'psi'), 0.145038, places=6)
        self.assertAlmostEqual(self.converter.stress(1, 'MPa', 'psi'), 145.038, places=3)
        self.assertAlmostEqual(self.converter.stress(1, 'Pa', 'ksi'), 0.000000145038, places=12)
        self.assertAlmostEqual(self.converter.stress(1, 'kPa', 'ksi'), 0.000145038, places=9)
        self.assertAlmostEqual(self.converter.stress(1, 'MPa', 'ksi'), 0.145038, places=6)

        # US to SI conversions
        self.assertAlmostEqual(self.converter.stress(1, 'psi', 'Pa'), 6894.757, places=3)
        self.assertAlmostEqual(self.converter.stress(1, 'psi', 'kPa'), 6.894757, places=6)
        self.assertAlmostEqual(self.converter.stress(1, 'psi', 'MPa'), 0.006894757, places=9)
        self.assertAlmostEqual(self.converter.stress(1, 'ksi', 'Pa'), 6894757, places=0)
        self.assertAlmostEqual(self.converter.stress(1, 'ksi', 'kPa'), 6894.757, places=3)
        self.assertAlmostEqual(self.converter.stress(1, 'ksi', 'MPa'), 6.894757, places=6)

    def test_strain_conversion(self):
        # Unitless to percent and permil
        self.assertAlmostEqual(self.converter.strain(1, 'strain', 'percent'), 100, places=5)
        self.assertAlmostEqual(self.converter.strain(1, 'strain', 'permil'), 1000, places=5)

        # Percent to unitless and permil
        self.assertAlmostEqual(self.converter.strain(100, 'percent', 'strain'), 1, places=5)
        self.assertAlmostEqual(self.converter.strain(1, 'percent', 'permil'), 10, places=5)

        # Permil to unitless and percent
        self.assertAlmostEqual(self.converter.strain(1000, 'permil', 'strain'), 1, places=5)
        self.assertAlmostEqual(self.converter.strain(10, 'permil', 'percent'), 1, places=5)

    def test_mass_conversion(self):
        # SI to SI conversions
        self.assertAlmostEqual(self.converter.mass(1, 'kg', 'ton'), 0.001, places=6)
        self.assertAlmostEqual(self.converter.mass(1, 'ton', 'kg'), 1000, places=0)

        # SI to US conversions
        self.assertAlmostEqual(self.converter.mass(1, 'kg', 'lb'), 2.20462, places=5)
        self.assertAlmostEqual(self.converter.mass(1, 'ton', 'lb'), 2204.62, places=2)

        # US to SI conversions
        self.assertAlmostEqual(self.converter.mass(1, 'lb', 'kg'), 0.45359237, places=8)
        self.assertAlmostEqual(self.converter.mass(1, 'lb', 'ton'), 0.00045359237, places=11)
        
    def test_density_conversion(self):
        # Metric to Metric conversions
        self.assertAlmostEqual(self.converter.density(1, 'kg', 'm', 'ton', 'cm'), 1e-9, places=12)
        self.assertAlmostEqual(self.converter.density(1, 'ton', 'm', 'kg', 'cm'), 1e-3, places=0)
        self.assertAlmostEqual(self.converter.density(1, 'kg', 'cm', 'ton', 'm'), 1e+3, places=5)
        self.assertAlmostEqual(self.converter.density(1, 'kg', 'mm', 'ton', 'm'), 1e+6, places=12)

        # Imperial to Imperial conversions
        self.assertAlmostEqual(self.converter.density(1, 'lb', 'ft', 'lb', 'in'), 1/1728, places=12)
        self.assertAlmostEqual(self.converter.density(1, 'lb', 'in', 'lb', 'ft'), 1728, places=0)

        # Metric to Imperial conversions
        self.assertAlmostEqual(self.converter.density(1, 'kg', 'm', 'lb', 'ft'), 0.062428, places=6)
        self.assertAlmostEqual(self.converter.density(1, 'ton', 'm', 'lb', 'ft'), 62.42796, places=5)
        self.assertAlmostEqual(self.converter.density(1, 'kg', 'cm', 'lb', 'ft'), 62428, places=0)
        self.assertAlmostEqual(self.converter.density(1, 'kg', 'm', 'lb', 'in'), 3.61273e-5, places=10)

        # Imperial to Metric conversions
        self.assertAlmostEqual(self.converter.density(1, 'lb', 'ft', 'kg', 'm'), 16.0185, places=4)
        self.assertAlmostEqual(self.converter.density(1, 'lb', 'ft', 'ton', 'm'), 0.0160185, places=7)
        self.assertAlmostEqual(self.converter.density(1, 'lb', 'in', 'kg', 'cm'), 0.0276799, places=7)
        
if __name__ == '__main__':
    unittest.main()
