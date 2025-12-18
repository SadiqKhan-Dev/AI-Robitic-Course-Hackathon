---
sidebar_position: 4
---

# Chapter 3: Nav2 for Humanoid Navigation

## Learning Objectives

After completing this chapter, you will be able to:
- Understand path planning concepts for humanoid robots
- Identify constraints of bipedal movement in navigation
- Configure Nav2 for humanoid robots with specialized parameters
- Explain kinematic constraints for humanoid navigation
- Apply Nav2 parameter adjustments for bipedal movement

## Path Planning Concepts for Humanoid Robots

Navigation in humanoid robots presents unique challenges compared to wheeled or tracked platforms due to the complexities of bipedal locomotion. Unlike wheeled robots that can move smoothly in any direction within their kinematic constraints, humanoid robots must maintain balance while navigating, requiring special consideration in path planning algorithms.

### Differences from Traditional Mobile Robot Navigation

Humanoid navigation planning must account for:
- **Balance preservation**: Continuous maintenance of center of mass within support polygon
- **Dynamic stability**: Ability to maintain balance during motion
- **Footstep planning**: Discrete placement of feet rather than continuous motion
- **Multi-body dynamics**: Coordination of multiple limbs for locomotion
- **Energy efficiency**: Biologically-inspired gait patterns to minimize energy consumption

### Nav2 Architecture Overview

Navigation2 (Nav2) is the standard navigation framework for ROS 2, providing a complete system for navigation in mobile robots. For humanoid robots, Nav2 requires specific adaptations to account for bipedal locomotion constraints.

The Nav2 system architecture includes:
- **Navigation Server**: Coordinates the complete navigation lifecycle
- **Action Clients**: Interfaces for navigation goals and feedback
- **Planners**: Global and local planners for trajectory generation
- **Controllers**: Motion controllers for executing trajectories
- **Recovery Behaviors**: Mechanisms for escaping navigation failures

## Constraints of Bipedal Movement in Navigation

Bipedal locomotion introduces several kinematic and dynamic constraints that must be properly accounted for in navigation planning:

### Kinematic Constraints

Humanoid robots have specific movement limitations:
- **Limited turning radius**: Cannot rotate in place like differential drive robots
- **Forward-only primary motion**: Predominantly forward movement with lateral steps limited
- **Discrete step placement**: Feet must be placed at specific locations for stability
- **Ankle mobility limits**: Limited orientation adjustment during stepping

### Dynamic Constraints

Motion stability considerations:
- **Zero Moment Point (ZMP)**: The point where the sum of moments of the ground reaction forces equals zero
- **Capture Point**: The point where a humanoid must step to come to a stop without falling
- **Centroidal Momentum**: Linear and angular momentum about the center of mass that must be controlled
- **Gyroscopic effects**: From rotating limbs that affect whole-body stability

### Environmental Constraints

Humanoids require specific environmental characteristics:
- **Flat surfaces**: Navigable terrain within foot geometry tolerances
- **Step height limits**: Obstacles must be under maximum traversable step height
- **Clearances**: Adequate space for arm swing during walking
- **Support areas**: Sufficient space for step placement during turns

## Nav2 Configuration for Humanoid Robots

Configuring Nav2 for humanoid robots requires adjusting several parameters to account for bipedal constraints:

### Global Planner Adjustments

The global planner in Nav2 needs modifications for humanoid navigation:

```yaml
bt_navigator:
  ros__parameters:
    global_frame: odom
    robot_base_frame: base_link
    # Humanoid-specific path smoothing
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/footprint
    
    # Behavior tree configuration
    default_bt_xml_filename: "navigate_w_replanning_and_recovery.xml"
    
    # Humanoid-specific recovery behaviors
    enable_groot_monitoring: True
    enable_action_monitoring: True
    interrupt_on_shutdown: False
```

### Local Planner Parameters

The local planner is critical for humanoid navigation:

```yaml
# Controller server parameters
controller_server:
  ros__parameters:
    controller_frequency: 20.0  # Lower frequency for humanoid stability
    min_x_velocity_threshold: 0.05
    min_y_velocity_threshold: 0.025  # Lower threshold for careful stepping
    min_theta_velocity_threshold: 0.01
    
    # Humanoid-specific controllers
    progress_checker_plugin: "progress_checker"
    goal_checker_plugin: "goal_checker"
    controller_plugins: ["FollowPath"]
    
    FollowPath:
      plugin: "nav2_mppi_controller::MPPICtrl"
      # Specialized for humanoid dynamics
      model_dt: 0.05  # Increased for stability
      model_horizon: 0.5  # Shorter horizon for real-time adjustment
      model_input_clipping: [1.0, 1.0, 1.0]  # Reduced for stability
      reference_scale: 1.0
      rate_limits: [2.0, 5.0, 5.0]  # Conservative limits for bipedal motion
      error_feedback_terms: [1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
      model_name: "kinematic"  # Specify kinematic model
      cmd_out_scale: [0.8, 0.5, 0.5]  # Reduced for stability
```

### Costmap Considerations

Humanoid robots require specialized costmap configurations:

```yaml
local_costmap:
  ros__parameters:
    update_frequency: 5.0  # Lower update frequency for processing time
    publish_frequency: 2.0
    global_frame: odom
    robot_base_frame: base_link
    use_rollout_diagnostics: true
    
    # Humanoid-specific inflation
    footprint: [[-0.3, -0.2], [-0.3, 0.2], [0.5, 0.2], [0.5, -0.2]]  # Larger footprint for stability
    footprint_padding: 0.05
    
    # Additional layers for humanoid constraints
    plugins: ["static_layer", "obstacle_layer", "inflation_layer", "voxel_layer"]
    
    inflation_layer:
      plugin: "nav2_costmap_2d::InflationLayer"
      cost_scaling_factor: 2.0  # Higher cost scaling for conservative navigation
      inflation_radius: 0.8  # Increased for humanoid step planning
      inflate_unknown: false
      inflate_around_unknown: false

    voxel_layer:
      plugin: "nav2_costmap_2d::VoxelLayer"
      enabled: true  # Enable for 3D obstacle detection
      voxel_size: 0.05
      max_voxels: 10000
      origin_z: 0.0
      z_resolution: 0.05
      z_voxels: 10
      unknown_threshold: 1
      mark_threshold: 0
      observation_sources: point_cloud_sensor
      point_cloud_sensor: # 3D sensors for height detection
        topic: /humanoid/lidar/points
        max_obstacle_height: 2.0
        clearing: true
        marking: true
        data_type: "PointCloud2"
        raytrace_max_range: 6.0
        raytrace_min_range: 0.0
        obstacle_max_range: 4.0
        obstacle_min_range: 0.0
```

## Kinematic Constraints for Humanoid Navigation

Humanoid robots have complex kinematic chains that require special consideration in navigation:

### Whole-Body Motion Planning

Unlike simpler robots, humanoid motion planning must consider:
- **Center of Mass (CoM) trajectory**: Maintaining CoM within support polygon
- **Zero Moment Point (ZMP) trajectory**: Ensuring ZMP remains within support area
- **Joint space constraints**: Maintaining valid configurations during motion
- **Kinematic redundancy**: Optimizing redundant degrees of freedom for stability

### Footstep Planning

Critical for humanoid navigation:

```yaml
# Example footstep planner configuration
footstep_planner:
  ros__parameters:
    max_step_length: 0.3  # Maximum forward step length
    max_step_width: 0.25  # Maximum lateral step distance
    max_step_height: 0.15  # Maximum step-over height
    min_step_length: 0.1  # Minimum step length
    min_step_width: 0.05  # Minimum step width
    nominal_step_time: 0.8  # Time per step
    max_yaw_rate: 0.2  # Maximum turning rate
    
    # Footprint for step validity
    foothold_min_clearance: 0.02
    foothold_max_roughness: 0.05
    foothold_max_gap_width: 0.15
```

### Gait Pattern Considerations

Navigation must account for specific gait patterns:
- **Walk stability**: Maintaining dynamic balance during gait cycles
- **Transition phases**: Smooth transitions between walking and standing
- **Gait adaptation**: Adjusting to terrain and obstacle conditions
- **Energy optimization**: Efficient locomotion patterns

## Practical Examples of Nav2 Parameter Adjustments for Bipedal Movement

### Configuring for Stability vs Speed Trade-offs

Humanoid robots often require more conservative navigation parameters:

```yaml
# Conservative velocity limits for stability
velocity_smoother_server:
  ros__parameters:
    smoothing_frequency: 20.0
    scale_velocities: false
    velocity_scaling_tolerance: 0.1
    feedback_type: 0  # 0: ODOMETRY, 1: COMMAND_VEL
    max_velocity: [0.4, 0.0, 0.3]  # Reduced linear and angular velocities
    min_velocity: [-0.2, 0.0, -0.2]  # Limited reverse and turning velocities
    # Acceleration limits for smooth motion
    acc_lim: [0.5, 0.0, 0.5]  # Conservative acceleration limits
```

### Terrain Adaptation Strategies

Humanoid robots may need to adjust navigation based on terrain characteristics:

```yaml
# Adaptive navigation parameters for different terrains
terrain_adaptation:
  ros__parameters:
    # Parameters for flat surfaces
    flat_surface_params:
      max_linear_speed: 0.3
      max_angular_speed: 0.2
      min_turn_radius: 0.4

    # Parameters for uneven terrain
    uneven_terrain_params:
      max_linear_speed: 0.15
      max_angular_speed: 0.1
      min_turn_radius: 0.6  # Larger turn radius for stability
      step_adjustment_enabled: true
```

## Practical Implementation Examples

### Example 1: Humanoid Robot in Indoor Environment

Consider a humanoid robot with a leg separation of 0.3 meters and a center of mass height of 0.8 meters navigating through an office environment:

```yaml
# Global planner configuration for humanoid robot
global_planner:
  ros__parameters:
    planner_frequency: 1.0  # Lower frequency for careful planning
    plan_to_goal_max_retries: 5  # Increase retries for complex paths
    goal_checker.reset_after_costmap_update: false
    # Humanoid-specific path smoothing parameters
    potential_scale: 3.0
    alignment_scale: 1.0
    granularity: 0.5  # More granular for narrow passages

# Local planner configuration for humanoid stability
local_planner:
  ros__parameters:
    controller_frequency: 10.0  # Adjust for humanoid balance
    max_linear_velocity: 0.3  # Conservative for stability
    min_linear_velocity: 0.1  # Prevent stopping on slopes
    max_angular_velocity: 0.3
    min_angular_velocity: 0.1
    # Humanoid-specific path following parameters
    xy_goal_tolerance: 0.15  # Accommodate foot placement accuracy
    yaw_goal_tolerance: 0.15  # Allow some orientation tolerance
    stateful: true
    # Acceleration limits for stable movement
    max_acceleration: 0.25
    max_deceleration: 0.3
```

### Example 2: Footstep Planning Configuration

For robots that require explicit footstep planning:

```yaml
# Footstep planner parameters
footstep_planner_server:
  ros__parameters:
    # Kinematic constraints for the humanoid
    leg_separation: 0.3
    com_height: 0.8
    max_step_length: 0.3  # Max forward step
    max_step_width: 0.25  # Max lateral step
    max_step_height: 0.1  # Max step over obstacle
    min_step_length: 0.05  # Min step for fine adjustments
    # Balance constraints
    com_margin: 0.05  # Center of mass safety margin
    zmp_margin: 0.08  # ZMP safety margin
    # Timing parameters
    step_duration: 1.2  # Time per step
    double_support_ratio: 0.1  # Time in double support
    # Swing foot trajectory
    swing_trajectory_height: 0.05  # Height of foot during swing
    swing_trajectory_shape: "cubic"  # Cubic polynomial trajectory
```

### Example 3: Collision Avoidance for Bipedal Robots

Special considerations for collision avoidance with bipedal locomotion:

```yaml
# Costmap configuration for humanoid robots
costmap_config:
  local_costmap:
    ros__parameters:
      # Larger footprint to account for bipedal balance
      footprint: [[-0.4, -0.25], [-0.4, 0.25], [0.6, 0.25], [0.6, -0.25]]
      footprint_padding: 0.05

      # Specialized obstacle handling for humanoid navigation
      plugins:
        - {name: obstacles, type: 'nav2_costmap_2d::ObstacleLayer'}
        - {name: inflation, type: 'nav2_costmap_2d::InflationLayer'}
        - {name: voxel, type: 'nav2_costmap_2d::VoxelLayer'}

      inflation_layer:
        inflation_radius: 1.0  # Larger inflation for safer paths
        cost_scaling_factor: 3.0  # Higher scaling for conservative planning
        inflation_remember_time: 0.5  # Short time for dynamic obstacle handling

      voxel_layer:
        enabled: true
        max_obstacle_height: 2.0  # Account for humanoid torso height
        origin_z: 0.0
        z_resolution: 0.05
        z_voxels: 20
        unknown_threshold: 15
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /humanoid/laser_scan
          max_obstacle_height: 2.0
          clearing: true
          marking: true
          data_type: "LaserScan"
          raytrace_max_range: 10.0
          raytrace_min_range: 0.0
          obstacle_max_range: 8.0
          obstacle_min_range: 0.1
```

## Visualization of Humanoid Navigation Concepts

To better understand the unique aspects of humanoid navigation, here are some key conceptual visualizations:

### Figure 1: Support Polygon vs Wheeled Platforms

```
Humanoid Robot:
  O    O      (feet positions)
  |\\  //|    (center of mass must stay within triangle formed by feet)
  | \\// |
  |  V   |
  ========    (support polygon for stability)

Wheeled Robot:
  O------O    (continuous contact with ground)
  |      |
  |======|    (larger support area, less balance constraint)
```

The support polygon for a humanoid robot is significantly smaller than for a wheeled platform, requiring more careful path planning.

### Figure 2: Navigation Pipeline for Humanoid Robots

```mermaid
graph LR
    A[Navigation Goal] --> B{Path Planning with Bipedal Constraints}
    B --> C[Global Path with Kinematic Feasibility}
    C --> D[Local Planner with Balance Constraints]
    D --> E[Step Generator]
    E --> F[Stable Locomotion Controller]
    F --> G[Humanoid Robot Movement]
    G --> H[Position Feedback]
    H --> D
```

### Figure 3: ZMP and Capture Point in Humanoid Navigation

For dynamic stability during locomotion:

```
Ground Contact Points (feet):
  O----------------O
  |                |
  |    ZMP (Red)   | <-- Zero Moment Point
  |    CoM (Blue)  | <-- Center of Mass
  |                |
  |  Capture Point | <-- Location for next footstep to maintain balance
  ==================
```

The ZMP (Zero Moment Point) must remain within the support polygon (area between feet) for stable walking, and the Capture Point indicates where the robot should step to come to a stop.

## Implementation Considerations

When implementing Nav2 for humanoid robots, consider these practical aspects:

1. **Testing and Validation**: Thoroughly test on both simulation and real-world scenarios
2. **Tuning Process**: Start conservative and gradually increase performance parameters
3. **Safety Margins**: Always maintain safety margins for balance and obstacle clearance
4. **Monitoring**: Implement monitoring to detect navigation failures and stability issues
5. **Fallback Behaviors**: Plan for graceful degradation when navigation fails

## Summary

Nav2 for humanoid navigation requires significant adaptations to account for the unique kinematic and dynamic constraints of bipedal locomotion. Proper configuration of global and local planners, costmaps, and controller parameters is essential for achieving stable and efficient navigation with humanoid robots.

The integration of footstep planning, balance preservation, and gait pattern optimization into the Nav2 framework enables humanoid robots to navigate complex environments while maintaining dynamic stability. Success in humanoid navigation depends on properly tuning the navigation parameters to match the specific kinematic constraints and balance requirements of the robot platform.

## Related Chapters

- [Chapter 1: NVIDIA Isaac Sim & Synthetic Data](./chapter-1-nvidia-isaac-sim.md) - Learn about simulation and synthetic data generation foundations
- [Chapter 2: Isaac ROS: Accelerated Perception & VSLAM](./chapter-2-isaac-ros-perception.md) - Explore perception and SLAM fundamentals

Understanding these constraints and configuration approaches allows robotics developers to effectively deploy Nav2 for humanoid navigation applications while ensuring safe and stable robot locomotion.