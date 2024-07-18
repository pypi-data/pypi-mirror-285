# import sys
# import numpy as np
# import matplotlib.pyplot as plt
# from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

# class HeatmapCanvas(FigureCanvas):
#     def __init__(self, intervals, max_frame, parent=None):
#         fig, self.ax = plt.subplots(figsize=(10, 4))  # Increased figure size for better layout
#         super().__init__(fig)
#         self.setParent(parent)

#         self.create_1d_heatmap(intervals, max_frame)

#     def create_1d_heatmap(self, intervals, max_frame):
#         # Create an array for the heatmap
#         heatmap = np.zeros(max_frame)

#         # Insert interpolated values into the heatmap
#         current_index = 0
#         for interval in intervals:
#             start = interval['start']
#             stop = interval['stop']
#             interp = int(interval['interp'])
#             interp_factor = 2 ** interp

#             for i in range(start, stop):
#                 heatmap[current_index] = interp
#                 current_index += 1
#                 for _ in range(1, interp_factor):
#                     if current_index < max_frame:
#                         heatmap[current_index] = int(interp)
#                         current_index += 1
#         print("Heatmap values:", heatmap)  # Debugging line to check heatmap values

#         # Create a modern-looking colormap
#         colors = [
#             (1, 1, 1, 0),       # Transparent for 0 interpolation
#             (0.8, 0.8, 1, 1),   # Light blue for 2x
#             (0.6, 0.6, 1, 1),   # Medium blue for 4x
#             (0.4, 0.4, 1, 1),   # Dark blue for 8x
#             (0.2, 0.2, 1, 1),   # Darker blue for 16x
#         ]
#         cmap = LinearSegmentedColormap.from_list("interpolation_cmap", colors)
#         norm = BoundaryNorm([0, 1, 2, 3, 4, 5], cmap.N)

#         # Create the 1D heatmap
#         heatmap_image = heatmap.reshape(1, -1)

#         im = self.ax.imshow(heatmap_image, aspect='auto', cmap=cmap, norm=norm, extent=[0, max_frame, 0, 1])

#         # Customize the plot
#         self.ax.set_yticks([])
#         self.ax.set_xlabel('Frame')
#         self.ax.set_title('Interpolation Levels')

#         # Add a custom horizontal legend below the x-axis
#         handles = [
#             plt.Line2D([0], [0], color=cmap(norm(1)), lw=4, label='2x'),
#             plt.Line2D([0], [0], color=cmap(norm(2)), lw=4, label='4x'),
#             plt.Line2D([0], [0], color=cmap(norm(3)), lw=4, label='8x'),
#             plt.Line2D([0], [0], color=cmap(norm(4)), lw=4, label='16x')
#         ]
#         legend = self.ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.2),
#                                 ncol=4, title="Interpolation Levels")

#         plt.tight_layout(pad=3.0)  # Ensure the layout fits properly
#         self.draw()


# class InterpolationHeatmapWindow(QWidget):
#     def __init__(self, intervals, max_frame):
#         super().__init__()
#         self.setWindowTitle("Interpolation Heatmap Viewer")

#         layout = QVBoxLayout(self)

#         self.heatmap_canvas = HeatmapCanvas(intervals, max_frame, self)
#         layout.addWidget(self.heatmap_canvas)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     # Example intervals
#     max_frame = 13
#     intervals = [
#         {"start": 0, "stop": 1, "interp": 1.0},
#         {"start": 1, "stop": 2, "interp": 2.0}
#     ]

#     heatmap_window = InterpolationHeatmapWindow(intervals, max_frame)
#     heatmap_window.show()

#     sys.exit(app.exec_())

import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

class HeatmapCanvas(FigureCanvas):
    def __init__(self, intervals, max_frame, parent=None):
        fig, self.ax = plt.subplots(figsize=(10, 4))  # Increased figure size for better layout
        super().__init__(fig)
        self.setParent(parent)

        self.create_1d_heatmap(intervals, max_frame)

    def create_1d_heatmap(self, intervals, max_frame):
        # Create an array for the heatmap
        heatmap = np.zeros(max_frame)

        # Insert interpolated values into the heatmap
        current_index = 0
        for interval in intervals:
            start = interval['start']
            stop = interval['stop']
            interp = int(interval['interp'])
            interp_factor = 2 ** interp

            for i in range(start, stop):
                heatmap[current_index] = 0  # No color for real frames
                current_index += 1
                for _ in range(1, interp_factor):
                    if current_index < max_frame:
                        heatmap[current_index] = interp
                        current_index += 1
            heatmap[current_index] = 0  # No color for the last real frame in the interval
            current_index += 1

        print("Heatmap values:", heatmap)  # Debugging line to check heatmap values

        # Create a modern-looking colormap
        colors = [
            (1, 1, 1, 0),       # Transparent for 0 interpolation
            (0.8, 0.8, 1, 1),   # Light blue for 2x
            (0.6, 0.6, 1, 1),   # Medium blue for 4x
            (0.4, 0.4, 1, 1),   # Dark blue for 8x
            (0.2, 0.2, 1, 1),   # Darker blue for 16x
        ]
        cmap = LinearSegmentedColormap.from_list("interpolation_cmap", colors)
        norm = BoundaryNorm([0, 1, 2, 3, 4, 5], cmap.N)

        # Create the 1D heatmap
        heatmap_image = heatmap.reshape(1, -1)

        im = self.ax.imshow(heatmap_image, aspect='auto', cmap=cmap, norm=norm, extent=[0, max_frame, 0, 1])

        # Customize the plot
        self.ax.set_yticks([])
        self.ax.set_xlabel('Frame')
        self.ax.set_title('Interpolation Levels')

        # Draw lines beneath the graph for each interval
        current_index = 0
        for interval in intervals:
            start = interval['start']
            stop = interval['stop']
            interp = int(interval['interp'])
            interp_factor = 2 ** interp

            start_index = current_index
            for i in range(start, stop):
                current_index += 1
                for _ in range(1, interp_factor):
                    if current_index < max_frame:
                        current_index += 1
            stop_index = current_index

            self.ax.hlines(-0.1, start_index, stop_index - 1, colors=cmap(norm(interp)), lw=4)
            self.ax.vlines(start_index, -0.15, -0.05, colors='black', lw=1)
            self.ax.vlines(stop_index - 1, -0.15, -0.05, colors='black', lw=1)

        # Add a custom horizontal legend below the x-axis
        handles = [
            plt.Line2D([0], [0], color=cmap(norm(1)), lw=4, label='2x'),
            plt.Line2D([0], [0], color=cmap(norm(2)), lw=4, label='4x'),
            plt.Line2D([0], [0], color=cmap(norm(3)), lw=4, label='8x'),
            plt.Line2D([0], [0], color=cmap(norm(4)), lw=4, label='16x')
        ]
        legend = self.ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.2),
                                ncol=4, title="Interpolation Levels")

        plt.tight_layout(pad=3.0)  # Ensure the layout fits properly
        self.draw()

class InterpolationHeatmapWindow(QWidget):
    def __init__(self, intervals, max_frame):
        super().__init__()
        self.setWindowTitle("Interpolation Heatmap Viewer")

        layout = QVBoxLayout(self)

        self.heatmap_canvas = HeatmapCanvas(intervals, max_frame, self)
        layout.addWidget(self.heatmap_canvas)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Example intervals
    max_frame = 13
    intervals = [
        {"start": 0, "stop": 1, "interp": 1.0},
        {"start": 1, "stop": 2, "interp": 2.0}
    ]

    heatmap_window = InterpolationHeatmapWindow(intervals, max_frame)
    heatmap_window.show()

    sys.exit(app.exec_())
