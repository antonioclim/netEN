# PlantUML Diagrams - Weeks 1-14

72 diagrams optimized for PlantUML HTTP server rendering.

## Fixed Issues
- Removed `note as` syntax (causes empty rendering)
- Removed complex multi-line `note bottom/right of`
- Used `legend` for explanatory text
- Simplified syntax for HTTP API compatibility

## Generation

### Using PlantUML Server (online)
```bash
python3 generate_png_simple.py
```

### Using Local JAR (recommended)
```bash
# Download JAR once
wget https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar

# Generate all PNGs
java -jar plantuml.jar -tpng week*/*.puml
```

### A4 Format Output
```bash
pip install Pillow
python3 generate_a4.py --dpi 150 --output-dir ./png_a4
```

## Structure
- week01-14/: 5-6 diagrams per week
- Each diagram uses only working PlantUML syntax
- Colors: Material Design palette
- Font: Arial (cross-platform)
