#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_prefix, get_package_share_directory, get_package_share_path

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.conditions import LaunchConfigurationEquals
from launch.conditions import IfCondition
from launch.actions.append_environment_variable import AppendEnvironmentVariable

# Enum for world types
class WorldType:
    RMUC = 'RMUC'
    RMUL = 'RMUL'

def get_world_config(world_type):
    world_configs = {
        WorldType.RMUC: {
            'x': '6.35',
            'y': '7.6',
            'z': '0.2',
            'yaw': '0.0',
            'world_path': 'RMUC2024_world/RMUC2024_world.world'
        },
        WorldType.RMUL: {
            'x': '4.3',
            'y': '3.35',
            'z': '1.16',
            'yaw': '0.0',
            'world_path': 'RMUL2024_world/RMUL2024_world.world'
            # 'world_path': 'RMUL2024_world/RMUL2024_world_dynamic_obstacles.world'
        }
    }
    return world_configs.get(world_type, None)

def generate_launch_description():
    # Get the launch directory
    bringup_dir = get_package_share_directory('venom_mid360_simulation')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Specify xacro path
    default_robot_description = Command(['xacro ', os.path.join(
    get_package_share_directory('venom_mid360_simulation'), 'urdf', 'simulation_waking_robot.xacro')])

    # Create the launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('rviz', default='false')
    robot_description = LaunchConfiguration('robot_description')

    # Gazebo plugins: obstacle + Livox MID-360 ray plugin
    append_obstacle_plugin_path = AppendEnvironmentVariable(
        'GAZEBO_PLUGIN_PATH',
        os.path.join(
            get_package_share_directory('venom_mid360_simulation'),
            'meshes',
            'obstacles',
            'obstacle_plugin',
            'lib',
        ),
    )
    append_livox_plugin_path = AppendEnvironmentVariable(
        'GAZEBO_PLUGIN_PATH',
        os.path.join(get_package_prefix('ros2_livox_simulation'), 'lib'),
    )
    # mid360.xacro uses model://mid360.stl
    append_gazebo_model_path = AppendEnvironmentVariable(
        'GAZEBO_MODEL_PATH',
        os.path.join(get_package_share_directory('venom_mid360_simulation'), 'meshes'),
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='True',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_world_cmd = DeclareLaunchArgument(
        'world',
        default_value=WorldType.RMUC,
        description='Choose <RMUC> or <RMUL>'
    )

    declare_rviz_config_file_cmd = DeclareLaunchArgument(
        'rviz_config_file',
        default_value=os.path.join(bringup_dir, 'rviz', 'rviz2.rviz'),
        description='Full path to the RVIZ config file to use'
    )

    declare_robot_description_cmd = DeclareLaunchArgument(
        'robot_description',
        default_value=default_robot_description,
        description='Robot description'
    )

    # Specify the actions
    gazebo_client_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')),
    )

    robot_description_param = ParameterValue(robot_description, value_type=str)

    start_joint_state_publisher_cmd = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description_param
        }],
        output='screen'
    )

    start_robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description_param
        }],
        output='screen'
    )

    start_rviz_cmd = Node(
        condition=IfCondition(use_rviz),
        package='rviz2',
        namespace='',
        executable='rviz2',
        arguments=['-d' + os.path.join(bringup_dir, 'rviz', 'rviz2.rviz')]
    )

    def create_gazebo_launch_group(world_type):
        world_config = get_world_config(world_type)
        if world_config is None:
            return None

        return GroupAction(
            condition=LaunchConfigurationEquals('world', world_type),
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
                    launch_arguments={'world': os.path.join(bringup_dir, 'world', world_config['world_path'])}.items(),
                ),
                # Wait for gzserver before spawning; Livox plugin load is heavy
                TimerAction(
                    period=3.0,
                    actions=[
                        Node(
                            package='gazebo_ros',
                            executable='spawn_entity.py',
                            arguments=[
                                '-entity', 'robot',
                                '-topic', 'robot_description',
                                '-timeout', '180.0',
                                '-x', world_config['x'],
                                '-y', world_config['y'],
                                '-z', world_config['z'],
                                '-Y', world_config['yaw']
                            ],
                            output='screen',
                        ),
                    ],
                ),
            ]
        )

    bringup_RMUC_cmd_group = create_gazebo_launch_group(WorldType.RMUC)
    bringup_RMUL_cmd_group = create_gazebo_launch_group(WorldType.RMUL)

    # Create the launch description and populate
    ld = LaunchDescription()

    # Set environment variables
    ld.add_action(append_obstacle_plugin_path)
    ld.add_action(append_livox_plugin_path)
    ld.add_action(append_gazebo_model_path)

    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_world_cmd)
    ld.add_action(declare_rviz_config_file_cmd)
    ld.add_action(declare_robot_description_cmd)
    ld.add_action(gazebo_client_launch)
    ld.add_action(start_joint_state_publisher_cmd)
    ld.add_action(start_robot_state_publisher_cmd)
    ld.add_action(bringup_RMUL_cmd_group) # type: ignore
    ld.add_action(bringup_RMUC_cmd_group) # type: ignore

    # Uncomment this line if you want to start RViz
    ld.add_action(start_rviz_cmd)

    return ld
