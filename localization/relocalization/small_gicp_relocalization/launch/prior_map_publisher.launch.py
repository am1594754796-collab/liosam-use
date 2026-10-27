from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    pcd_file = LaunchConfiguration("pcd_file")

    declare_pcd_file = DeclareLaunchArgument(
        "pcd_file",
        default_value=PathJoinSubstitution([
            EnvironmentVariable("HOME"),
            "venom_ws/src/venom_vnv/lio/Point-LIO/PCD/scans.pcd"
        ]),
    )

    pcd_pub = Node(
        package="pcl_ros",
        executable="pcd_to_pointcloud",
        name="prior_map_publisher",
        output="screen",
        parameters=[{
            "file_name": pcd_file,
            "interval": 0.1,
            "tf_frame": "map",
        }],
        remappings=[("cloud_pcd", "/prior_map")],
    )

    return LaunchDescription([declare_pcd_file, pcd_pub])
