# Pond Planner 🐟

A comprehensive pond planning application that helps you calculate optimal pond dimensions, fish stocking levels, and equipment requirements for your backyard pond project.

## Features

- **Pond Volume Calculation**: Supports 13 different pond shapes with accurate volume calculations
- **Fish Stocking Analysis**: Database of 100+ fish species with space and bioload requirements
- **Equipment Sizing**: Calculates pump, filter, and UV sterilizer requirements
- **Comprehensive Reports**: Generates detailed planning reports with recommendations
- **ACID Compliance**: Transaction-safe operations with rollback capabilities
- **Extensible Design**: SOLID principles with dependency injection for easy customization

## Quick Start

### Using Docker (Recommended)

```bash
# Pull and run the latest version
docker pull ghcr.io/parttimelegend/pond-planner:latest
docker run -it ghcr.io/parttimelegend/pond-planner:latest
```

### Local Installation

```bash
# Clone the repository
git clone https://github.com/parttimelegend/pond-planner.git
cd pond-planner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Supported Pond Shapes

The application supports 13 different pond shapes across three categories:

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

## Fish Database

The application includes a comprehensive database of 100+ fish species with:

- Common and scientific names
- Adult size specifications
- Bioload factors for filtration calculations
- Minimum space requirements per fish
- Compatibility information

## Equipment Calculations

Automatic sizing for:

- **Pumps**: Flow rate based on pond volume and bioload
- **Biological Filters**: Media volume requirements
- **UV Sterilizers**: Wattage specifications
- **Mechanical Filters**: Micron rating recommendations

## Example Usage

```python
from PondPlanner import PondPlanner

# Create planner instance
planner = PondPlanner()

# Set pond dimensions
planner.set_dimensions(5.0, 3.0, 1.5, "rectangular")

# Add fish
planner.add_fish("goldfish", 10)
planner.add_fish("koi", 3)

# Generate report
report = planner.generate_report()
print(report)
```

## Architecture

The application follows SOLID principles with:

- **Dependency Injection**: Configurable components
- **Repository Pattern**: Pluggable data sources
- **Transaction Management**: ACID-compliant operations
- **Validation Services**: Multi-layer input validation
- **Service Layer**: Business logic separation

## License

This project is licensed under the MIT License - see the [LICENSE](about/license.md) file for details.

## Support

For questions, issues, or feature requests, please open an issue on [GitHub](https://github.com/parttimelegend/pond-planner/issues).
