# Impeller

Impeller is a package for spatial transcriptomics imputation using path-based graph neural networks.

## Installation

You can install the package using pip:

```bash
pip install Impeller
```

## Usage
### Download Example Data
from Impeller import download_example_data
download_example_data()

### Load and Process Data
from Impeller import load_and_process_example_data
data, val_mask, test_mask, x, original_x = load_and_process_example_data()

### Train Model
from Impeller import create_args, train
args = create_args()
test_l1_distance, test_cosine_sim, test_rmse = train(args, data, val_mask, test_mask, x, original_x)
