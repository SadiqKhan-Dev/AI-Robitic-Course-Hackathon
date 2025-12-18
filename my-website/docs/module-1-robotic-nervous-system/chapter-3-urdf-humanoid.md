---
sidebar_position: 4
---

# Chapter 3: Humanoid Description with URDF

## Learning Objectives

After completing this chapter, you will be able to:
- Explain the concepts of links, joints, and coordinate frames in URDF
- Understand the hierarchical structure of humanoid robot descriptions
- Recognize the connection between AI logic and robot control through URDF

## URDF: Unified Robot Description Format

URDF (Unified Robot Description Format) is an XML-based format used to describe robotic systems in ROS. It defines the physical and kinematic properties of robots, including their structure, appearance, and dynamics. For humanoid robots, URDF provides a standardized way to represent the complex arrangement of links and joints that make up the robot's body.

## Links: The Rigid Bodies

In URDF, links represent the rigid parts of a robot. A humanoid robot typically has links for:
- Torso/upper body
- Head
- Arms (upper arm, lower arm, hand)
- Legs (thigh, shank, foot)
- Spine segments (if articulated)

Each link contains information about:
- Visual properties (for rendering)
- Collision properties (for simulation and collision detection)
- Inertial properties (for dynamics simulation)

## Joints: The Connections

Joints define how links connect and move relative to each other. The most common joint types in humanoid robots are:

- **Revolute joints**: Rotational joints with a defined range of motion (e.g., elbow, knee)
- **Continuous joints**: Revolute joints without limits (e.g., shoulder, hip)
- **Prismatic joints**: Linear sliding joints (less common in humanoids)
- **Fixed joints**: Static connections (e.g., sensor mounting)

Joint definitions include:
- Parent and child links
- Joint type
- Position and orientation relative to the parent
- Axis of rotation/translation
- Limits (for revolute and prismatic joints)

## Coordinate Frames

Each link in a URDF has its own coordinate frame, defined by:
- An origin (position and orientation) relative to the parent link
- Three perpendicular axes (typically X, Y, Z)

These frames establish a kinematic chain that allows the robot's pose to be calculated relative to a base frame. This is crucial for tasks like forward and inverse kinematics.

## Humanoid Joint Hierarchy Example

Here's a simplified URDF snippet showing the joint hierarchy in a humanoid robot:

```xml
<robot name="humanoid_robot">
  <!-- Base link -->
  <link name="base_link" />

  <!-- Torso -->
  <joint name="torso_joint" type="fixed">
    <parent link="base_link" />
    <child link="torso" />
  </joint>
  <link name="torso" />

  <!-- Head -->
  <joint name="neck_joint" type="revolute">
    <parent link="torso" />
    <child link="head" />
    <axis xyz="0 0 1" />
    <limit lower="-1.0" upper="1.0" effort="100" velocity="1"/>
  </joint>
  <link name="head" />

  <!-- Left Arm -->
  <joint name="left_shoulder_joint" type="continuous">
    <parent link="torso" />
    <child link="left_upper_arm" />
    <axis xyz="0 1 0" />
  </joint>
  <link name="left_upper_arm" />
  
  <joint name="left_elbow_joint" type="revolute">
    <parent link="left_upper_arm" />
    <child link="left_lower_arm" />
    <axis xyz="0 1 0" />
    <limit lower="0" upper="2.3" effort="100" velocity="1"/>
  </joint>
  <link name="left_lower_arm" />
</robot>
```

This example demonstrates the hierarchical, tree-like structure of URDF, where each link (except the root) has exactly one parent and potentially multiple children.

## Connecting AI Logic to Robot Control

URDF serves as a bridge between AI algorithms and physical robot control:

- **Perception**: AI algorithms use URDF to understand sensor positions relative to robot links
- **Planning**: Path planning algorithms use URDF kinematics to determine feasible movements
- **Control**: Joint controllers use URDF joint definitions to command appropriate actuators

For AI agents working with humanoid robots, URDF provides the spatial context necessary to:
- Interpret sensor data in the robot's frame of reference
- Plan movements that respect the robot's kinematic constraints
- Predict the outcomes of motor commands

## rclpy and URDF Integration

Python AI agents using rclpy can interact with URDF models through:

- The `robot_state_publisher` node, which publishes link transformations
- TF (Transform) libraries to work with coordinate frames
- Joint state information to understand current robot configuration

This integration allows AI agents to operate with a complete understanding of the robot's physical structure and current state.

## Summary

URDF provides a standardized way to describe the structure of humanoid robots, defining links, joints, and their hierarchical relationships. This description is essential for AI agents to understand and interact with robot systems effectively, providing the spatial and kinematic context needed for perception, planning, and control tasks. The hierarchical joint structure enables complex movements while maintaining the physical constraints of the robot's design.