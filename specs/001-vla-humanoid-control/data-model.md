# Data Model: VLA Humanoid Control System

## Core Entities

### VoiceCommand
- **id**: Unique identifier for the command
- **text**: Transcribed text from speech input
- **intent**: Interpreted purpose of the command
- **parameters**: Extracted parameters from the command
- **confidence**: Confidence score of the speech recognition
- **timestamp**: When the command was received

### RobotAction
- **id**: Unique identifier for the action
- **type**: Type of action (navigation, manipulation, perception)
- **parameters**: Parameters needed for the action
- **status**: Current status (pending, executing, completed, failed)
- **robot_id**: Identifier of the target robot
- **command_id**: Reference to the originating command

### IntendedActionSequence
- **id**: Unique identifier for the sequence
- **command_id**: Reference to the original command
- **actions**: Ordered list of RobotAction objects
- **context**: State information needed for execution
- **priority**: Execution priority

### RobotState
- **id**: Unique identifier for the robot
- **position**: Current 3D coordinates
- **orientation**: Current orientation in space
- **gripper_status**: Status of the gripper (open, closed, holding object)
- **battery_level**: Current battery percentage
- **sensor_readings**: Collection of current sensor data
- **timestamp**: When the state was recorded

### EnvironmentalMap
- **id**: Unique identifier for the map
- **robot_id**: Identifier of the robot associated with this map
- **obstacles**: List of detected obstacles with positions
- **navigable_areas**: Areas identified as safe for navigation
- **object_locations**: Known positions of relevant objects
- **last_updated**: Timestamp of the last update

### ObjectRecognition
- **id**: Unique identifier for the recognition
- **object_type**: Type of object (cup, ball, chair, etc.)
- **position**: 3D coordinates of the object
- **confidence**: Confidence score of the recognition
- **properties**: Additional properties (size, color, etc.)
- **timestamp**: When the object was identified

## State Transitions

### RobotAction Status Transitions:
- `pending` → `executing` when robot starts action
- `executing` → `completed` when action finishes successfully
- `executing` → `failed` when action cannot be completed
- `executing` → `interrupted` when higher priority action takes over

### VoiceCommand Status Transitions:
- `received` → `processing` when speech recognition starts
- `processing` → `interpreted` when intent is determined
- `interpreted` → `planning` when action sequence is being created
- `planning` → `executing` when robot starts performing actions