# Glossary: Isaac Technology Concepts

## Simulation Terms

**Isaac Sim**: NVIDIA's robotics simulator providing high-fidelity physics simulation and photorealistic rendering capabilities built on the Omniverse platform.

**Photorealistic Simulation**: Simulation that accurately replicates visual properties of the real world including lighting, materials, and environmental conditions.

**Synthetic Data**: Artificially generated sensor data that statistically matches real-world sensor outputs for perception model training.

**Universal Scene Description (USD)**: Extensible framework for 3D scenes and workflows developed by Pixar, forming the foundation of Isaac Sim's scene representation.

**Domain Randomization**: Technique of randomizing non-essential elements in synthetic environments to increase the robustness of models trained on synthetic data.

## Perception & SLAM Terms

**Isaac ROS**: Collection of packages that enable hardware-accelerated perception and navigation on NVIDIA platforms using the Robot Operating System (ROS).

**Visual SLAM (VSLAM)**: Visual Simultaneous Localization and Mapping, a technique that uses visual sensors to simultaneously map an environment and localize the camera within it.

**CUDA**: Parallel computing platform and programming model developed by NVIDIA for general-purpose computing on GPUs.

**TensorRT**: SDK for high-performance deep learning inference on NVIDIA GPUs.

**Apriltag**: Fiducial marker system that provides accurate pose estimation for robotics applications.

**Hardware Acceleration**: Using specialized hardware (like GPUs) to accelerate computations, particularly for perception and neural network inference.

## Navigation Terms

**Nav2 (Navigation2)**: The standard navigation framework for ROS 2, providing a complete system for navigation in mobile robots.

**Path Planning**: Process of determining a route from a start position to a goal while avoiding obstacles.

**Kinematic Constraints**: Physical limitations on robot movement based on its mechanical structure and joint configurations.

**Bipedal Movement**: Two-legged locomotion similar to human walking, with specific stability and balance requirements.

**Zero Moment Point (ZMP)**: Point where the sum of moments of the ground reaction forces equals zero, critical for humanoid stability.

**Capture Point**: Point where a humanoid robot must step to come to a stop without falling.

**Footstep Planning**: Planning algorithm that determines where and when to place feet for stable locomotion in humanoid robots.

## NVIDIA-Specific Terms

**Omniverse**: NVIDIA's simulation and collaboration platform that enables real-time, physically-accurate 3D design workflows.

**RTX**: NVIDIA's real-time ray tracing and AI platform that enhances graphics performance and rendering quality.

**Jetson Platform**: NVIDIA's embedded computing platform designed for AI and robotics applications at the edge.

**Tensor Cores**: Specialized processing units in NVIDIA GPUs designed to accelerate deep learning workloads.

**Isaac ROS Managed Services**: Containerized ROS 2 nodes optimized for NVIDIA Jetson and GPU-enabled platforms.