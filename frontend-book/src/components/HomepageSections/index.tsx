import React from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import ModuleCard from '@site/src/components/ModuleCard';
import styles from './styles.module.css';

interface HomepageSectionsProps {}

const HomepageSections: React.FC<HomepageSectionsProps> = () => {
  // Module data - in a real implementation, this might come from a config or API
  const modules = [
    {
      id: 'module-1',
      title: 'ROS 2 Nervous System',
      description: 'Learn how ROS 2 serves as the nervous system for robotic applications, enabling communication between different components.',
      imageUrl: '/img/modules/ros2-nervous-system.svg',
      linkUrl: '/docs/module-1-robotic-nervous-system/intro',
      color: '#3a7bd5'
    },
    {
      id: 'module-2',
      title: 'Digital Twin Humanoid Robots',
      description: 'Explore creating digital twins for humanoid robots to simulate, test, and validate robot behaviors in a virtual environment.',
      imageUrl: '/img/modules/digital-twin-humanoid.svg',
      linkUrl: '/docs/module-2-digital-twin-humanoid/',
      color: '#00d2ff'
    },
    {
      id: 'module-3',
      title: 'NVIDIA Isaac Robotic Brain',
      description: 'Implement AI capabilities for robots using NVIDIA Isaac, including perception, planning, and control systems.',
      imageUrl: '/img/modules/isaac-brain.svg',
      linkUrl: '/docs/module-3-nvidia-isaac-brain/',
      color: '#f85032'
    },
    {
      id: 'module-4',
      title: 'Vision Language Action (VLA) Humanoid Control',
      description: 'Master VLA models for controlling humanoid robots using vision, language, and action inputs.',
      imageUrl: '/img/modules/vla-control.svg',
      linkUrl: '/docs/ai-robotics/vla-pipelines',
      color: '#ff7e5f'
    },
    {
      id: 'module-5',
      title: 'Advanced AI Algorithms',
      description: 'Deep dive into machine learning and AI algorithms specifically designed for robotics applications.',
      imageUrl: '/img/modules/ai-algorithms.svg',
      linkUrl: '/docs/ai-robotics/ai-fundamentals',
      color: '#654ea3'
    },
    {
      id: 'module-6',
      title: 'Robot Ethics & Safety',
      description: 'Understand the ethical considerations and safety protocols for developing and deploying robotic systems.',
      imageUrl: '/img/modules/robot-ethics.svg',
      linkUrl: '/docs/robotics/ethics-safety',
      color: '#141e30'
    }
  ];

  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <Heading as="h2" className={styles.sectionTitle}>
              Course Modules
            </Heading>
            <p className={styles.sectionSubtitle}>
              Explore our comprehensive modules covering all aspects of AI-powered robotics
            </p>
          </div>
        </div>
        
        <div className="row">
          {modules.map((module) => (
            <ModuleCard
              key={module.id}
              title={module.title}
              description={module.description}
              imageUrl={module.imageUrl}
              linkUrl={module.linkUrl}
              color={module.color}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default HomepageSections;