import pytest
import numpy as np

from pyhectiqlab import Run


def test_push_metrics():
    run = Run(31, project="hectiq-ai/test")

    for i in range(500):
        run.add_metric("metric1", step=i, value=np.random.rand())
