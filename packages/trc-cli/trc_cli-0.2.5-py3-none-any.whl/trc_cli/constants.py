from pathlib import Path

current_file_path = Path(__file__).resolve()
base_dir = current_file_path.parent

FEATURE_FLAGS = (
    "integration.technologyDiscovery",
    "technologydiscovery.factsheetsbomlink",
    "technologydiscovery.libraryinventory",
    "integration.technologyDiscovery.devFeatures"
)
WORKSPACE_READINESS_FIELD = 'lxIsSBOMAttached'

MICROSERVICES_PATH = base_dir / 'static' / 'microservices.json'
SBOMS_PATH = base_dir / 'static' / 'sboms'
TEMP_STORAGE = base_dir / 'static' / 'factsheetids.json'
