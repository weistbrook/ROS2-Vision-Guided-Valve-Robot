import sys

import rclpy
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from rclpy.node import Node
from rclpy.utilities import remove_ros_args

from .valve_detect_gui import Ui_MainWindow


class Ros2GuiNode(Node):
    def __init__(self):
        super().__init__('qt_gui_node')
        self.get_logger().info('Qt GUI ROS2 node started.')


class GUINode(QMainWindow):
    def __init__(self, ros_node, parent=None):
        super().__init__(parent)
        self.ros_node = ros_node
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


def main(args=None):
    ros_args = args if args is not None else sys.argv
    rclpy.init(args=ros_args)

    qt_args = remove_ros_args(args=ros_args)
    app = QApplication(qt_args)

    ros_node = Ros2GuiNode()
    window = GUINode(ros_node=ros_node)
    window.show()

    spin_timer = QTimer()
    spin_timer.timeout.connect(lambda: rclpy.spin_once(ros_node, timeout_sec=0.0))
    spin_timer.start(10)

    exit_code = 0
    try:
        exit_code = app.exec_()
    finally:
        spin_timer.stop()
        ros_node.destroy_node()
        rclpy.shutdown()

    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
