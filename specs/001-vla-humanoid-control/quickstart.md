# Quickstart: VLA Humanoid Control Module

## Prerequisites

- Node.js 18+ for Docusaurus
- Python 3.11+ for ROS 2 integration
- ROS 2 (Humble Hawksbill or later) installed
- OpenAI Whisper for speech recognition
- Access to a humanoid robot compatible with ROS 2 (or simulation)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-robotic-book
```

### 2. Install Docusaurus Dependencies
```bash
cd my-website
npm install
```

### 3. Set up ROS 2 Environment
```bash
# Source ROS 2 installation
source /opt/ros/humble/setup.bash  # or your ROS 2 distribution

# Create a workspace for the project
mkdir -p ~/vla_ws/src
cd ~/vla_ws
colcon build
source install/setup.bash
```

### 4. Install Python Dependencies
```bash
pip install openai-whisper
pip install ros2
pip install your-llm-library
```

## Building the Documentation

```bash
cd my-website
npm run build
```

## Running the Documentation Site Locally

```bash
cd my-website
npm start
```

The documentation site will be available at http://localhost:3000

## Adding the VLA Module

The Vision Language Action (VLA) module consists of three chapters:

1. **Voice to Action Pipelines** - Covers speech-to-text and command interpretation
2. **Cognitive Planning with LLMs** - Details how LLMs translate natural language to action sequences
3. **Capstone: The Autonomous Humanoid** - Complete integration of all components

### File Structure
```
docs/
└── ai-robotics/
    ├── vla-pipelines.md
    ├── cognitive-planning.md
    └── autonomous-humanoid-capstone.md
```

## Integrating with Docusaurus Sidebar

Update `my-website/sidebars.js` to include the new module as the final section:

```javascript
module.exports = {
  docs: [
    {
      type: 'category',
      label: 'AI Robotics',
      items: [
        'intro',
        'ai-robotics/vla-pipelines',
        'ai-robotics/cognitive-planning',
        'ai-robotics/autonomous-humanoid-capstone',
      ],
    },
  ],
};
```

## Testing Your Changes

### Documentation Tests
```bash
npm run test
```

### Build Verification
```bash
npm run build
```

## Contributing

1. Make changes to the appropriate markdown files in the `docs/ai-robotics/` directory
2. Verify the changes by running `npm start`
3. Submit a pull request with your changes

## Troubleshooting

### Common Issues:

- **Page not loading**: Ensure all dependencies are installed and run `npm install` again
- **ROS 2 not found**: Make sure to source your ROS 2 installation in each new terminal session
- **Speech recognition failing**: Verify Whisper is properly installed and accessible