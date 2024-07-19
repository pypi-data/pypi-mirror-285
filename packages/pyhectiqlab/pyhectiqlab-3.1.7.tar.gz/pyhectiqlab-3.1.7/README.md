# Hectiq Lab

Hectiq Lab is a platform to track your machine learning experiments. 

- **⚡️ Fast and easy**: Designed with performance in mind, Hectiq Lab is fast and easy to use.
- **🖥 Full API**: Supports the full API of the Hectiq Lab package.
- **🚀 Boosted with commands**: Almost all methods are availabe from the CLI, or in python using a functional or object-oriented API.

Links to:
- [Documentation](https://docs.hectiq.ai)
- [Web app](http://lab.hectiq.ai)

## Installation

```bash
pip install pyhectiqlab
```

Then, you'll be able to use the CLI
  
```bash
hectiq-lab --help
```

Or the Python package

```python
import pyhectiqlab 
```

## Quickstart

> Usage of hectiq-lab is on invitation only. To get access, please contact us at [hectiq.ai](https://hectiq.ai).

Start by authenticating with the CLI.

```bash
hectiq-lab authenticate
```

Then, you can start tracking your experiments.

```python
from pyhectiqlab import Run
import pyhectiqlab.functional as hl

with Run(title="My first run", project="hectiq-ai/demo"): 
    hl.add_artifact("my-image.png")
```