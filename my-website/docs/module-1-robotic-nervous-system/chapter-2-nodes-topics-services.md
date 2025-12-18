---
sidebar_position: 3
---

# Chapter 2: Nodes, Topics, and Services with rclpy

## Learning Objectives

After completing this chapter, you will be able to:
- Explain the concepts of nodes, topics, and services
- Understand how data flows from sensors to actuators
- Distinguish between topic and service usage scenarios
- Use minimal Python rclpy snippets for illustration

## Nodes: The Building Blocks

In ROS 2, nodes are the fundamental building blocks of a distributed robotic system. Each node is typically responsible for a specific function such as sensor data processing, path planning, or actuator control. Nodes are designed to be modular and reusable, allowing complex robotic behaviors to be built from simpler components.

A node can be thought of as an individual organism in a larger robotic ecosystem. Just as organs in a biological system have specialized functions, nodes in a ROS 2 system handle specific aspects of robotic operation.

## Topics: Publish-Subscribe Communication

Topics provide a publish-subscribe communication mechanism in ROS 2. This is an asynchronous communication pattern where:

- Publishers send messages to topics without knowing which subscribers exist
- Subscribers receive messages from topics without knowing which publishers exist
- Multiple publishers and subscribers can interact on the same topic

This pattern is ideal for sensor data, where many components might need to receive the same information simultaneously, such as camera images, laser scans, or IMU readings.

### Example Data Flow

Consider a humanoid robot walking scenario:
- Sensor nodes publish joint position, IMU, and camera data to their respective topics
- Perception nodes subscribe to sensor topics and publish processed information
- Planning nodes subscribe to perception data and publish desired movements
- Control nodes subscribe to desired movements and send commands to actuators

## Services: Request-Response Communication

Services provide a synchronous request-response communication pattern in ROS 2. This is suitable for operations that require immediate responses, such as:

- Parameter configuration
- Transform lookups
- Service calls to specific capabilities (e.g., "find an object" or "plan a path")

Unlike topics, services establish a direct connection between the client and server for each request, making them appropriate for on-demand operations.

## Python rclpy Examples

For Python-based nodes, rclpy provides the ROS 2 client library:

```python
import rclpy
from rclpy.node import Node

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World'
        self.publisher.publish(msg)
```

For subscribers:

```python
class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)
```

## Communication Patterns

The choice between topics and services depends on the use case:

- Use **topics** for continuous data streams (sensors, robot state)
- Use **services** for on-demand operations (configuration, specific tasks)
- Use **actions** for long-running tasks with feedback (navigation, manipulation)

## Topic vs Service Usage Scenarios

### Topic Scenarios
- Sensor data broadcasting (camera feeds, laser scans)
- Robot state publication (joint positions, battery level)
- Event notifications (obstacle detected, goal reached)

### Service Scenarios
- Requesting specific information (current location, map)
- Triggering specific behaviors (take photo, calibrate sensor)
- Configuration changes (change parameters, switch modes)

## Communication Loops in Humanoid Robots

In humanoid robots, communication loops typically involve:

1. Sensor nodes continuously publishing data via topics
2. Perception nodes subscribing to sensor data and publishing processed information
3. Decision-making nodes receiving processed data and publishing commands
4. Control nodes receiving commands and publishing to actuator interfaces

This creates a continuous flow of information from sensing through action, enabling the robot to respond to its environment in real-time.

## Summary

Nodes, topics, and services form the fundamental communication architecture of ROS 2. Understanding these concepts is essential for developing distributed robotic applications where multiple software components must coordinate effectively. The publish-subscribe model of topics works well for continuous data streams, while the request-response model of services is appropriate for on-demand operations.