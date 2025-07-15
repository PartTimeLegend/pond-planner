# Pond Planner 🐟

A comprehensive pond planning application that helps you calculate optimal pond dimensions, fish stocking levels, and equipment requirements for your backyard pond project.

## Features

- **Pond Volume Calculation**: Supports 13 different pond shapes with accurate volume calculations
- **Fish Stocking Analysis**: Database of 100+ fish species with space and bioload requirements
- **Equipment Sizing**: Calculates pump, filter, and UV sterilizer requirements
- **Comprehensive Reports**: Generates detailed planning reports with recommendations
- **ACID Compliance**: Transaction-safe operations with rollback capabilities
- **Extensible Design**: SOLID principles with dependency injection for easy customization

## Supported Pond Shapes

### Geometric Shapes

- Rectangular
- Circular
- Oval
- Triangular
- Hexagonal
- Octagonal

### Organic Shapes

- Kidney
- Teardrop
- Crescent
- Irregular

### Complex Shapes

- L-Shaped
- Figure-8
- Star

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/PartTimeLegend/pond-planner.git
   cd pond-planner
   ```

2. **Create a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Command Line Interface

Run the interactive pond planner:

```bash
python main.py
```

The application will guide you through:

1. Setting pond dimensions and shape
2. Selecting fish types and quantities
3. Generating a comprehensive planning report

### Programmatic Usage

```python
from PondPlanner import PondPlanner

# Create a pond planner instance
planner = PondPlanner()

# Set pond dimensions (length, width, depth in meters, shape)
planner.set_dimensions(5.0, 3.0, 1.5, "rectangular")

# Add fish to the pond
planner.add_fish("goldfish", 10)
planner.add_fish("koi", 3)

# Or add multiple fish types at once (atomic operation)
fish_batch = {"goldfish": 10, "koi": 3, "shubunkin": 5}
planner.add_fish_batch(fish_batch)

# Calculate pond volume
volume = planner.calculate_volume_liters()
print(f"Pond volume: {volume:,.0f} liters")

# Check if pond is adequately sized
required_volume = planner.calculate_required_volume()
bioload = planner.calculate_bioload()

# Get equipment recommendations
pump_lph, pump_category = planner.calculate_pump_size()
filter_specs = planner.calculate_filter_size()

# Get stocking recommendations
recommendations = planner.get_stocking_recommendations()

# Generate comprehensive report
report = planner.generate_report()
print(report)
```

## Architecture

The application follows SOLID principles and clean architecture patterns:

### Core Components

- **PondPlanner**: Main facade class coordinating all operations
- **VolumeCalculator**: Shape-specific volume calculations using YAML configuration
- **StockingCalculator**: Fish capacity and bioload calculations
- **EquipmentCalculator**: Pump and filter sizing calculations
- **ReportGenerator**: Comprehensive report generation

### Services

- **PondStockManager**: Fish inventory management with transaction support
- **PondValidationService**: Input validation using configurable rules
- **PondTransactionManager**: ACID-compliant transaction management

### Repositories

- **YamlFishRepository**: Fish database management from YAML files
- **YamlShapeRepository**: Pond shape configuration from YAML files

### Key Features

- **Dependency Injection**: All components use interface-based dependency injection
- **Transaction Support**: ACID properties with rollback capabilities
- **Extensible Configuration**: Fish and shape data loaded from YAML files
- **Comprehensive Validation**: Multi-layer validation with detailed error messages

## Configuration

### Adding New Fish Species

Edit `fish_database.yaml`:

```yaml
fish_species:
  your_fish_key:
    name: "Your Fish Name"
    adult_length_cm: 25
    bioload_factor: 1.2
    min_liters_per_fish: 150
```

### Adding New Pond Shapes

Edit `pond_shapes.yaml`:

```yaml
pond_shapes:
  your_shape:
    name: "Your Shape"
    description: "Description of your shape"
    formula_type: "simple"  # or circular, elliptical, etc.
    area_formula: "length * width"
    multiplier: 1.0
    uses_length: true
    uses_width: true
```

## Sample Output

```text
POND PLANNING REPORT
====================

Pond Specifications:
- Dimensions: 5.0m x 3.0m x 1.5m
- Shape: Rectangular
- Total Volume: 22,500 liters

Current Fish Stock:
- Goldfish: 10 fish
- Koi: 3 fish

Stocking Analysis:
- Required Volume: 3,600 liters
- Available Volume: 22,500 liters
- Status: ✓ Adequate
- Total Bioload: 17.5

Equipment Recommendations:
- Pump Size: 12,375 LPH (Medium bioload)
- 2,475 liters filter media
- UV Sterilizer: 79 watts
- Mechanical Filter: Pre-filter with 50-100 micron capability

Maximum Stocking Recommendations:
- Goldfish: up to 300 fish
- Koi: up to 23 fish
- Shubunkin: up to 118 fish
...
```

## API Reference

### Main Classes

#### PondPlanner

The main facade class for pond planning operations.

**Methods:**

- `set_dimensions(length, width, depth, shape)`: Set pond dimensions
- `add_fish(fish_type, quantity)`: Add fish to stock
- `remove_fish(fish_type, quantity)`: Remove fish from stock
- `add_fish_batch(fish_dict)`: Add multiple fish types atomically
- `calculate_volume_liters()`: Calculate pond volume
- `calculate_required_volume()`: Calculate volume needed for current stock
- `calculate_bioload()`: Calculate total bioload
- `get_stocking_recommendations()`: Get maximum stocking levels
- `calculate_pump_size()`: Get pump requirements
- `calculate_filter_size()`: Get filtration requirements
- `generate_report()`: Generate comprehensive report

**Properties:**

- `fish_stock`: Current fish inventory (read-only)
- `fish_database`: Fish species database (read-only)

### Validation

All input validation provides detailed error messages:

```python
try:
    planner.set_dimensions(-1, 5, 2, "rectangular")
except ValueError as e:
    print(e)  # "Invalid dimensions: Length must be at least 0.1 meters"
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

For coverage report:

```bash
python -m pytest --cov=. tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow SOLID principles
- Add comprehensive tests for new features
- Update documentation for API changes
- Ensure YAML validation for configuration changes
- Use type hints for all new code

## Requirements

- Python 3.8+
- PyYAML 6.0+

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Fish database compiled from aquaculture and pond management resources
- Pond shape calculations based on geometric formulas and industry standards
- Equipment sizing based on aquarium and pond filtration best practices

## Support

For questions, issues, or feature requests, please open an issue on GitHub.
