from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    remappings = [("/tf", "tf"), ("/tf_static", "tf_static")]

    args = [
        DeclareLaunchArgument("num_threads", default_value="4"),
        DeclareLaunchArgument("num_neighbors", default_value="10"),
        DeclareLaunchArgument("global_leaf_size", default_value="0.25"),
        DeclareLaunchArgument("registered_leaf_size", default_value="0.25"),
        DeclareLaunchArgument("max_dist_sq", default_value="1.0"),
        DeclareLaunchArgument(
            "init_pose",
            default_value="[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]",
            description="Initial pose [x, y, z, roll, pitch, yaw]"
        ),
        DeclareLaunchArgument(
            "prior_pcd_file",
            default_value=PathJoinSubstitution([
                EnvironmentVariable("HOME"),
                "venom_ws/src/venom_vnv/lio/Point-LIO/PCD/scans.pcd"
            ]),
        ),
    ]

    relocalization_node = Node(
        package="small_gicp_relocalization",
        executable="small_gicp_relocalization_node",
        output="screen",
        remappings=remappings,
        parameters=[{
            "num_threads": LaunchConfiguration("num_threads"),
            "num_neighbors": LaunchConfiguration("num_neighbors"),
            "global_leaf_size": LaunchConfiguration("global_leaf_size"),
            "registered_leaf_size": LaunchConfiguration("registered_leaf_size"),
            "max_dist_sq": LaunchConfiguration("max_dist_sq"),
            "map_frame": "map",
            "odom_frame": "odom",
            "laser_frame": "laser_link",
            "init_pose": LaunchConfiguration("init_pose"),
            "prior_pcd_file": LaunchConfiguration("prior_pcd_file"),
            "input_cloud_topic": "cloud_registered",
        }],
    )

    return LaunchDescription(args + [relocalization_node])
