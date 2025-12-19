import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'module-1-robotic-nervous-system/intro',
        'module-1-robotic-nervous-system/chapter-1-ros2-nervous-system',
        'module-1-robotic-nervous-system/chapter-2-nodes-topics-services',
        'module-1-robotic-nervous-system/chapter-3-urdf-humanoid',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Digital Twin Humanoid Robots',
      items: [
        'module-2-digital-twin-humanoid/index',
        'module-2-digital-twin-humanoid/chapter-1-physics-simulation-gazebo',
        'module-2-digital-twin-humanoid/chapter-2-high-fidelity-unity',
        'module-2-digital-twin-humanoid/chapter-3-sensor-simulation',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: NVIDIA Isaac Robotic Brain',
      items: [
        'module-3-nvidia-isaac-brain/index',
        'module-3-nvidia-isaac-brain/chapter-1-nvidia-isaac-sim',
        'module-3-nvidia-isaac-brain/chapter-2-isaac-ros-perception',
        'module-3-nvidia-isaac-brain/chapter-3-nav2-humanoid-navigation',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision Language Action (VLA) Humanoid Control',
      items: [
        'ai-robotics/vla-pipelines',
        'ai-robotics/cognitive-planning',
        'ai-robotics/autonomous-humanoid-capstone',
      ],
    },
  ],

  // But you can create a sidebar manually
  /*
  tutorialSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
   */
};

export default sidebars;
