import numpy as np
from pyqtmgl.widgets.continuous_viewer import ContinuousViewer
from pyqtmgl.test.runner import run_dockable

def main():
    n_lines = 10
    n_points = 1e5
    x = np.repeat([np.arange(n_points)], n_lines, axis=0)
    d = (np.arange(n_lines) + 1) * np.pi
    y = np.sin(x / d[:, None]) * x / 1e5
    run_dockable([ContinuousViewer], points=y)

if __name__ == "__main__":
    main()