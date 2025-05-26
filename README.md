# 2025-Summer-Tokyo-Studio

## Tokyo Digital Twin for Urban Risk and Regeneration

This repository supports a digital twin system for **Nihonbashi, Tokyo**, as a strategic planning platform for urban revitalization and carbon neutrality.

It connects high-frequency urban risk and low-frequency urban regeneration through simulation, analytics, and visual interfaces.

Urban digital twins are used here as an **interactive GIS-based platform** to simulate and support decisions in complex, multi-stakeholder urban systems.


### 1. Urban Risk
- Focus: High-frequency urban problems such as flooding, heat wave or earthquake events for evacuations
- Method: Agent-based evacuation models, real-time sensing

### 2. Urban Regeneration
- Focus: Low-frequency urban problems such as urban design and redevelopment
- Method: 3D design models, carbon modeling, scenario planning


## Tools and Technologies
- GIS: ArcGIS Pro, ArcGIS Online, Experience Builder
- Simulation: Rhino/Grasshopper, AnyLogic, Python (ABM, NetworkX)
- Data: 3D CityGML from PLATEAU, Street Networks from OSM, GPS Human Flows, Socioeconomic Data


## Repository Structure

```bash
2025-Summer-Tokyo-Studio/
├── data/                        # External data links + metadata
│   ├── metadata/                # Data schema, layer IDs, CRS, update logs
│   └── files/                   # Small files
│   └── README.md                # Data descriptions + download links: URLs to datasets (CityGML, OSM, e-Stat, etc.)
│
├── scripts/                     # Data analysis + visualization
│   ├── preprocess/              # Clean, merge, convert data
│   ├── analytics/               # KPI, scenario analysis
│   └── visualization/           # Charts, map layers, heatmaps
│
├── models/                      # Simulation models
│   ├── urban_risk/              # ABM for evacuation
│   ├── regeneration/            # Urban form, carbon modeling, energy simulation
│   └── README.md                # Model objectives, inputs/outputs, run instructions
│
├── dashboards/                  # Interactive platform 
│   ├── DT_links.md              # ArcGIS Dashboard + Experience Builder URLs
│
├── docs/                        # Project documentation
│   ├── use_cases.md             # Urban risk & regeneration scenarios
│   ├── architecture.md          # Digital twin system design overview
│   └── methodology.md           # Models, data integration, design logic
│
└── README.md
