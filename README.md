# Pond Planner 🐟

[![Build and Publish Docker Image](https://github.com/PartTimeLegend/pond-planner/actions/workflows/docker-build.yml/badge.svg)](https://github.com/PartTimeLegend/pond-planner/actions/workflows/docker-build.yml)

A comprehensive pond planning application that helps you calculate optimal pond dimensions, fish stocking levels, and equipment requirements for your backyard pond project.

## Features

- **Pond Volume Calculation**: Supports 13 different pond shapes with accurate volume calculations
- **Fish Stocking Analysis**: Database of 267 fish species with space and bioload requirements
- **Save/Load Pond Configurations**: Persistent storage of pond designs with metadata
- **Equipment Sizing**: Calculates pump, filter, and UV sterilizer requirements
- **Interactive CLI Interface**: User-friendly menu-driven interface for pond planning
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

### Option 1: Docker (Recommended)

The easiest way to run Pond Planner is using Docker:

```bash
# Pull the latest image from GitHub Container Registry
docker pull ghcr.io/parttimelegend/pond-planner:latest

# Run the application interactively
docker run -it ghcr.io/parttimelegend/pond-planner:latest

# Or run with docker-compose
git clone https://github.com/parttimelegend/pond-planner.git
cd pond-planner
docker-compose up pond-planner
```

### Option 2: Local Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/parttimelegend/pond-planner.git
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

4. **Verify installation**:

   ```bash
   python verify_setup.py
   ```

   This script will check that all dependencies are installed and the application is working correctly.

## Quick Start

### Docker Usage

```bash
# Interactive mode
docker run -it ghcr.io/parttimelegend/pond-planner:latest

# With persistent storage for saved ponds
docker run -it -v $(pwd)/data:/app/data ghcr.io/parttimelegend/pond-planner:latest

# With docker-compose for development (includes persistent storage)
docker-compose up pond-planner-dev

# Build locally
docker build -t pond-planner .
docker run -it pond-planner
```

**Note**: The docker-compose configuration automatically handles persistent storage for saved pond configurations.

### Command Line Interface

Run the interactive pond planner:

```bash
python main.py
```

The application provides a user-friendly menu interface with options to:

1. **Create new pond plan** - Design a new pond with custom dimensions and fish selection
2. **Load saved pond plan** - Restore a previously saved pond configuration
3. **List saved pond plans** - View all saved pond designs with metadata
4. **Delete saved pond plan** - Remove unwanted saved configurations
5. **Exit** - Close the application

#### Interactive Features

- **Enhanced fish selection**: Use the `list` command to browse all 267 available fish species
- **Intelligent filtering**: Fish are categorized by type (freshwater, saltwater, tropical, etc.)
- **Save with descriptions**: Add custom descriptions to your pond designs
- **Metadata tracking**: Automatic creation dates and fish counts for saved ponds

The application will guide you through:

1. Setting pond dimensions and shape
2. Selecting fish types and quantities from 267 species
3. Saving your pond configuration with a custom name and description
4. Loading and modifying existing pond designs
5. Generating comprehensive planning reports

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

# Save pond configuration with description
filename = planner.save_pond("My Garden Pond", "Beautiful koi pond for the backyard")
print(f"Saved as: {filename}")

# List all saved ponds
saved_ponds = planner.list_saved_ponds()
for pond in saved_ponds:
    print(f"- {pond['name']}: {pond['shape']} pond with {pond['fish_count']} fish")

# Load a saved pond configuration
planner_2 = PondPlanner()
planner_2.load_pond("My Garden Pond")
print(f"Loaded pond volume: {planner_2.calculate_volume_liters():,.0f} liters")
print(f"Fish stock: {planner_2.get_fish_stock()}")

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
- **PondPersistenceService**: Save/load pond configurations with JSON serialization

### Repositories

- **YamlFishRepository**: Fish database management from YAML files
- **YamlShapeRepository**: Pond shape configuration from YAML files

### Key Features

- **Dependency Injection**: All components use interface-based dependency injection
- **Transaction Support**: ACID properties with rollback capabilities
- **Extensible Configuration**: Fish and shape data loaded from YAML files
- **Comprehensive Validation**: Multi-layer validation with detailed error messages

## Configuration

### Data Persistence

Pond configurations are automatically saved to the `data/saved_ponds/` directory as JSON files. Each saved pond includes:

- Pond dimensions and shape
- Complete fish stock inventory
- Creation timestamp and description
- Metadata for easy browsing and management

The persistence system is designed to be:

- **Portable**: JSON files can be easily shared or backed up
- **Human-readable**: Files can be manually inspected or edited
- **Versioned**: Compatible with future application updates

### Fish Database

The application includes a comprehensive database of **267 fish species** covering:

- **Freshwater Species**: Goldfish, Koi, Shubunkin, Catfish varieties
- **Tropical Fish**: Angelfish, Tetras, Gouramis, Cichlids
- **Specialty Fish**: Arowanas, Discus, Exotic varieties
- **Regional Varieties**: Asian, European, American species

Each fish species includes detailed information:

- Adult length and bioload requirements
- Minimum space requirements per fish
- Compatibility and care notes

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
    formula_type: "simple" # or circular, elliptical, etc.
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
- `save_pond(name, description)`: Save current pond configuration to file
- `load_pond(filename)`: Load pond configuration from file
- `list_saved_ponds()`: List all saved pond configurations with metadata
- `delete_saved_pond(filename)`: Delete a saved pond configuration
- `pond_exists(filename)`: Check if a saved pond configuration exists
- `get_fish_stock()`: Get current fish inventory
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

## Troubleshooting

### Common Issues

#### ModuleNotFoundError: No module named 'yaml'

This occurs when PyYAML is not installed. Make sure you've followed the installation steps:

```bash
# Activate your virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install PyYAML directly
pip install PyYAML>=6.0
```

#### File permissions issues with saved ponds

Ensure the application has write permissions to create the `data/` directory:

```bash
# Create the directory if it doesn't exist
mkdir -p data/saved_ponds

# Check permissions
ls -la data/
```

#### Docker container doesn't persist saved ponds

Use volume mounting to persist data:

```bash
# Mount local data directory
docker run -it -v $(pwd)/data:/app/data ghcr.io/parttimelegend/pond-planner:latest

# Or use docker-compose (recommended)
docker-compose up pond-planner
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

## Docker Images

The application is available as Docker images with multiple tags:

- `latest` - Latest stable release from main branch
- `main` - Latest build from main branch
- `develop` - Latest build from develop branch
- `v1.0.0` - Specific version tags
- `YYYY-MM-DD` - Daily builds from main branch

### Image Variants

- **Production**: Multi-stage optimized image (~100MB)
- **Development**: Includes development tools and dependencies

## CI/CD

The project uses GitHub Actions for:

- ✅ **Automated Testing** - Python 3.9, 3.11, and 3.12
- ✅ **Code Quality** - Linting with ruff, formatting with black
- ✅ **Security Scanning** - bandit, safety, and Trivy
- ✅ **Docker Building** - Multi-platform (amd64, arm64)
- ✅ **Container Registry** - GitHub Container Registry
- ✅ **Documentation** - GitHub Pages deployment
- ✅ **Release Management** - Automated releases on tags
