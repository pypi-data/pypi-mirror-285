import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout,
    QHBoxLayout, QLabel, QSpinBox, QComboBox, QFrame, QDialogButtonBox, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class InterpolationIntervalWidget(QFrame):
    def __init__(self, parent=None, max_frame=10000):
        super().__init__(parent)

        self.start_frame_spinbox = QSpinBox()
        self.start_frame_spinbox.setRange(0, max_frame - 1)  # Set realistic frame range

        self.end_frame_spinbox = QSpinBox()
        self.end_frame_spinbox.setRange(1, max_frame)  # Set realistic frame range

        self.end_frame_spinbox.valueChanged.connect(self.update_start_frame_max)

        self.interpolation_combo = QComboBox()
        self.interpolation_combo.addItems(["2x", "4x", "8x", "16x"])

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_interval)

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Start Frame:"))
        layout.addWidget(self.start_frame_spinbox)
        layout.addWidget(QLabel("End Frame:"))
        layout.addWidget(self.end_frame_spinbox)
        layout.addWidget(QLabel("Interpolation:"))
        layout.addWidget(self.interpolation_combo)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

        self.set_max_frame(max_frame)

    def remove_interval(self):
        self.setParent(None)

    def set_max_frame(self, max_frame):
        if max_frame == 0:
            self.start_frame_spinbox.setDisabled(True)
            self.end_frame_spinbox.setDisabled(True)
        else:
            self.start_frame_spinbox.setDisabled(False)
            self.end_frame_spinbox.setDisabled(False)
            self.start_frame_spinbox.setMaximum(max_frame - 1)
            self.end_frame_spinbox.setMaximum(max_frame)
            self.update_start_frame_max()
            if self.end_frame_spinbox.value() > max_frame:
                self.end_frame_spinbox.setValue(max_frame)

    def update_start_frame_max(self):
        self.start_frame_spinbox.setMaximum(self.end_frame_spinbox.value() - 1)

    def get_interval_data(self):
        return {
            "start": self.start_frame_spinbox.value(),
            "stop": self.end_frame_spinbox.value(),
            "interp": int(self.interpolation_combo.currentText().replace("x", ""))
        }

class InterpolationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select Interpolation Intervals")

        self.layout = QVBoxLayout()

        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["Channel 1", "Channel 2", "Channel 3"])  # Example channels
        self.channel_combo.currentIndexChanged.connect(self.update_max_frame)

        self.layout.addWidget(QLabel("Channel to Interpolate:"))
        self.layout.addWidget(self.channel_combo)

        self.add_interval_button = QPushButton("Add Interval")
        self.add_interval_button.clicked.connect(self.add_interval)

        self.dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        self.dialog_buttons.accepted.connect(self.check_intervals)
        self.dialog_buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.add_interval_button)
        self.layout.addWidget(self.dialog_buttons)

        self.setLayout(self.layout)

        self.intervals = []
        self.update_max_frame()

    def add_interval(self):
        max_frame = self.get_max_frame()
        interval_widget = InterpolationIntervalWidget(max_frame=max_frame)
        self.intervals.append(interval_widget)
        self.layout.insertWidget(self.layout.count() - 3, interval_widget)

    def update_max_frame(self):
        max_frame = self.get_max_frame()
        if max_frame == 0:
            self.remove_all_intervals()
            self.add_interval_button.setDisabled(True)
            QMessageBox.information(self, "No Frames", "Only one image is present in the selected time series. Interpolation is not possible.").exec_()
        else:
            self.add_interval_button.setDisabled(False)
            for interval_widget in self.intervals:
                interval_widget.set_max_frame(max_frame)

    def remove_all_intervals(self):
        for interval_widget in self.intervals:
            interval_widget.setParent(None)
        self.intervals.clear()

    def get_max_frame(self):
        # Simulated logic for determining max frame based on selected channel
        channel = self.channel_combo.currentText()
        if channel == "Channel 1":
            return 1000
        elif channel == "Channel 2":
            return 2000
        elif channel == "Channel 3":
            return 3000
        return 0  # Edge case: only one image in the series

    def check_intervals(self):
        for interval_widget in self.intervals:
            start_frame = interval_widget.start_frame_spinbox.value()
            end_frame = interval_widget.end_frame_spinbox.value()
            max_frame = self.get_max_frame()

            if start_frame < 0 or start_frame >= max_frame:
                QMessageBox.warning(self, "Invalid Interval", f"Start frame {start_frame} is out of bounds.").exec_()
                return
            if end_frame <= start_frame or end_frame > max_frame:
                QMessageBox.warning(self, "Invalid Interval", f"End frame {end_frame} must be greater than start frame {start_frame} and within bounds.").exec_()
                return

        self.accept()

    def get_data(self):
        channel = self.channel_combo.currentText()
        intervals = [interval_widget.get_interval_data() for interval_widget in self.intervals]
        return channel, intervals

class IntervalViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        self.plot_widget.setLabel('left', 'Interpolation')
        self.plot_widget.setLabel('bottom', 'Frame')

        self.plot_widget.showGrid(x=True, y=True)

    def plot_intervals(self, max_frame, intervals):
        self.plot_widget.clear()

        for interval in intervals:
            start = interval['start']
            stop = interval['stop']
            interp = interval['interp']
            color = pg.mkColor(255, 0, 0)  # Red color for interpolation

            self.plot_widget.plot([start, stop], [interp, interp], pen=color, fillLevel=0, fillBrush=color)

        self.plot_widget.setXRange(0, max_frame)
        self.plot_widget.setYRange(0, 16)  # Assuming the maximum interpolation level is 16x

class IntervalViewerWindow(QMainWindow):
    def __init__(self, max_frame, intervals, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interpolation Intervals Viewer")
        self.setGeometry(100, 100, 800, 600)  # Set a fixed size for the viewer window

        self.viewer = IntervalViewer()
        self.setCentralWidget(self.viewer)
        self.viewer.plot_intervals(max_frame, intervals)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Movie Frame Interpolation")

        self.interpolation_button = QPushButton("Interpolate Frames")
        self.interpolation_button.clicked.connect(self.open_interpolation_dialog)

        self.viewer_button = QPushButton("View Interpolated Intervals")
        self.viewer_button.clicked.connect(self.open_interval_viewer)

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        central_layout.addWidget(self.interpolation_button)
        central_layout.addWidget(self.viewer_button)

        self.setCentralWidget(central_widget)

        self.channel = None
        self.intervals = []

    def open_interpolation_dialog(self):
        dialog = InterpolationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.channel, self.intervals = dialog.get_data()
            print("Channel to Interpolate:", self.channel)
            print("Selected Intervals for Interpolation:", self.intervals)
            # Here you would call your interpolation algorithm with the selected intervals

    def open_interval_viewer(self):
        if not self.intervals:
            QMessageBox.information(self, "No Intervals", "No intervals to display. Please add intervals first.").exec_()
            return

        max_frame = 3000 if not self.channel else self.get_max_frame_for_channel(self.channel)
        viewer_window = IntervalViewerWindow(max_frame, self.intervals, self)
        viewer_window.show()

    def get_max_frame_for_channel(self, channel):
        # Simulated logic for determining max frame based on selected channel
        if channel == "Channel 1":
            return 1000
        elif channel == "Channel 2":
            return 2000
        elif channel == "Channel 3":
            return 3000
        return 0

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
