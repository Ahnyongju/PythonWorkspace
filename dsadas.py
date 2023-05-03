import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QLabel, QFileDialog, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRectF

def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def calculate_area_from_drone_image(image_path, scale_factor, roi_points):
    if len(roi_points) != 4:
        return 0

    side_a = distance(roi_points[0], roi_points[1])
    side_b = distance(roi_points[1], roi_points[2])

    area = side_a * side_b * scale_factor * 2
    return area

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image_path = None
        self.image_label = QLabel(self)
        self.graphics_view = QGraphicsView(self)
        self.setCentralWidget(self.graphics_view)
        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)

        self.setWindowTitle("Drone Area Calculator")
        self.setGeometry(100, 100, 800, 600)

        self.roi_points = []
        self.scale_factor = 0.1
        self.drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.image_path is not None:
            pos = event.pos() - QPoint(8, 30)  # Adjusting for window header
            self.start_point = pos
            self.end_point = pos

            if len(self.roi_points) < 4:
                self.roi_points.append((pos.x(), pos.y()))

            if len(self.roi_points) == 4:
                area = calculate_area_from_drone_image(self.image_path, self.scale_factor, self.roi_points)
                QMessageBox.information(self, "영역 면적 결과", "영역의 면적: {:.2f}㎡".format(area))
                self.roi_points = []

        self.update()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.image_path is not None:
            self.end_point = event.pos() - QPoint(8, 30)  # Adjusting for window header
            self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_O:
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            self.image_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)", options=options)

            if self.image_path:
                img = cv2.imread(self.image_path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, ch = img.shape
                bytes_per_line = ch * w

                img_qt = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(img_qt)
                self.scene.clear()
                self.scene.addPixmap(pixmap)
                self.graphics_view.setSceneRect(QRectF(0, 0, w, h))
                self.graphics_view.fitInView(self.graphics_view.sceneRect(), Qt.KeepAspectRatio)
                self.graphics_view.adjustSize()

                self.roi_points = []



if  __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())