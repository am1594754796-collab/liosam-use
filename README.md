# Venom 小车导航

基于 ROS 2 Humble 的无人车导航工作区：仿真、定位、底盘/雷达驱动与整机启动。

## 目录

| 目录 | 说明 |
| --- | --- |
| `simulation/venom_nav_simulation` | Gazebo + MID-360 + Fast-LIO / Nav2 仿真 |
| `localization/` | Fast-LIO、Point-LIO、rf2o、重定位 |
| `driver/` | Livox、Scout / Hunter 底盘、串口驱动 |
| `venom_robot_description/` | 小车 URDF / TF |
| `venom_bringup/` | 实车 / 整机 launch 与配置 |

## 仿真快速启动

```bash
source /opt/ros/humble/setup.bash
source simulation/venom_nav_simulation/install/setup.bash
export LD_LIBRARY_PATH=/home/$USER/.local/opt/ros/humble/lib/x86_64-linux-gnu:/home/$USER/.local/lib:$LD_LIBRARY_PATH
ros2 launch rm_nav_bringup bringup_sim.launch.py world:=RMUL mode:=nav lio:=fastlio localization:=gazebo
```
