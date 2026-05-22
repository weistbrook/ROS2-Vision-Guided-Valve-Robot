# ROS2-Vision-Guided-Valve-Robot – 视觉引导机械臂工业阀门自动化作业系统

基于 Jetson Nano 嵌入式平台，采用 ROS2 框架自主开发的一套工业阀门自动化作业系统。项目利用 YOLO11 目标检测与深度相机三维位姿解算，通过模块化 ROS2 节点协同，实现阀门自动识别、空间定位、机械臂趋近与旋拧、以及 PyQt 可视化监控的全流程闭环控制。

## 主要特性

- 🔍 **视觉感知**：YOLO11 模型实时检测阀门与旋钮，结合深度相机（RGB-D）计算三维位姿及平面法向量。
- 🤖 **机械臂控制**：自定义 `ValveCommand` 接口，封装运动队列、平面校准、旋转校正等逻辑，支持远距离趋近与精细调整。
- 🖥️ **可视化监控**：基于 PyQt5 的上位机节点，实时显示检测画面、机械臂连接状态、运动指令及系统日志。
- 📦 **模块化解耦**：各功能独立 ROS2 节点，通过自定义消息通信，便于扩展与调试。

## 功能包说明

| 包名                     | 作用                                                                                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `valve_interfaces`       | 自定义 ROS2 消息与服务接口，定义 `ValveCommand`（运动指令）、`ValveVision`（图像与深度）、`Bool` 使能信号等，统一全项目通信协议。 |
| `robot_valve_control`    | 核心控制节点（`arm_controller_node`）：订阅视觉发布的阀门位姿，解析运动类型并调用机械臂 TCP 指令，完成靠近、对齐、旋拧等动作。     |
| `valve_qt_gui`           | PyQt5 上位机节点：订阅图像/状态话题，发布手动指令与运动使能信号；提供实时视频流、按钮面板、参数调节等交互界面。                     |


## 安装与编译

### 1. 克隆仓库
git clone [https://github.com/weistbrook/ROS2_QT_valve.git](https://github.com/weistbrook/ROS2-Vision-Guided-Valve-Robot.git)

cd ROS2_QT_valve

### 2. 编译
colcon build

### 3. 环境设置
source install/setup.bash

## 使用方法
### 1. 启动视觉与机械臂控制节点

### 终端1：启动视觉检测节点（自动发布 ValveCommand）
ros2 run robot_valve_control valve_detection_node

### 终端2：启动机械臂控制节点（订阅命令并驱动真实机械臂）
ros2 run robot_valve_control arm_controller_node

### 2. 启动可视化上位机（可选）

ros2 run valve_qt_gui valve_qt_gui_node

## 🙏 Acknowledgments

- 🤖 **ROS2** - Robot operating system
- 🎯 **Ultralytics YOLO** - Object detection
- 🖥️ **PyQt** - GUI framework
- 👥 All contributors and community members

## 📫 Contact

- 👤 Project Maintainer: [weistbrook](https://github.com/weistbrook)
- 💬 For questions or suggestions, please open an issue on [GitHub Issues](https://github.com/weistbrook/ROS2_QT_valve/issues)
- 🔗 Project Link: [https://github.com/weistbrook/ROS2_QT_valve](https://github.com/weistbrook/ROS2_QT_valve)
