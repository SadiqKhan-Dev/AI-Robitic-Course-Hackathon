# Quickstart Guide: ROS 2 Robotic Nervous System Module

**Feature**: ROS 2 Robotic Nervous System (Docusaurus-based course module)
**Date**: 2025-12-17
**Author**: AI Assistant

## Getting Started

This guide will help you set up the Docusaurus-based Physical AI & Humanoid Robotics course, specifically Module 1: The Robotic Nervous System (ROS 2) Context.

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn package manager
- Git
- Basic knowledge of Markdown and command line tools

## Setup Instructions

### 1. Clone or Initialize the Repository

```bash
# If starting from scratch
npx create-docusaurus@latest my-physical-ai-course classic
cd my-physical-ai-course

# If using an existing repository
git clone <repository-url>
cd <repository-name>
```

### 2. Install Dependencies

```bash
npm install
# or
yarn install
```

### 3. Create Module 1 Directory Structure

```bash
# Create the module directory
mkdir -p docs/module-1-ros2-nervous-system

# Create the three chapters
touch docs/module-1-ros2-nervous-system/index.md
touch docs/module-1-ros2-nervous-system/chapter-1-ros2-fundamentals.md
touch docs/module-1-ros2-nervous-system/chapter-2-communication-primitives.md
touch docs/module-1-ros2-nervous-system/chapter-3-python-ai-integration.md
```

### 4. Configure Docusaurus

Update `docusaurus.config.js` to include your site's metadata and theme configuration:

```javascript
// docusaurus.config.js
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Embodied Intelligence in the Physical World',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://your-username.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub Pages, this is usually /<project-name>/
  baseUrl: '/ai-robotic-book/',

  // GitHub pages deployment config.
  organizationName: 'your-username', // Usually your GitHub org/user name.
  projectName: 'ai-robotic-book', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: false, // Optional: disable the blog plugin
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'Physical AI & Robotics',
        logo: {
          alt: 'Robotics Course Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Course Modules',
          },
          {
            href: 'https://github.com/facebook/docusaurus',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Modules',
            items: [
              {
                label: 'Module 1: ROS 2 Nervous System',
                to: '/docs/module-1-ros2-nervous-system',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Stack Overflow',
                href: 'https://stackoverflow.com/questions/tagged/docusaurus',
              },
              {
                label: 'Discord',
                href: 'https://discordapp.com/invite/docusaurus',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/facebook/docusaurus',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Course. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
```

### 5. Update Sidebar Configuration

Update `sidebars.js` to include your module and its chapters:

```javascript
// sidebars.js
/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2) Context',
      items: [
        'module-1-ros2-nervous-system/index',
        'module-1-ros2-nervous-system/chapter-1-ros2-fundamentals',
        'module-1-ros2-nervous-system/chapter-2-communication-primitives',
        'module-1-ros2-nervous-system/chapter-3-python-ai-integration',
      ],
    },
  ],
};

export default sidebars;
```

### 6. Add Content to Your Chapters

Now you can start adding content to your chapter files. Here's a template for the index.md:

```markdown
---
sidebar_position: 1
---

# Module 1: The Robotic Nervous System (ROS 2) Context

Welcome to Module 1 of the Physical AI & Humanoid Robotics course. This module introduces ROS 2 as the foundational nervous system for humanoid robots, enabling communication, control, and coordination between perception, decision-making, and actuation.

## Learning Objectives

After completing this module, you will be able to:
- Explain ROS 2's role in humanoid robotics
- Understand the concepts of nodes, topics, and services
- Connect Python AI agents using rclpy
- Interpret humanoid structure using URDF
```

### 7. Start the Development Server

```bash
npm run start
# or
yarn start
```

This will start a local development server at `http://localhost:3000` where you can view and edit your documentation site in real-time.

### 8. Build for Production

When you're ready to build your site for deployment:

```bash
npm run build
# or
yarn build
```

## GitHub Pages Deployment

To deploy to GitHub Pages:

1. Ensure your `docusaurus.config.js` has the correct `organizationName` and `projectName`
2. Run the deployment command:

```bash
GIT_USER=<Your GitHub username> npm run deploy
# or
GIT_USER=<Your GitHub username> yarn deploy
```

This will build your site and push it to the `gh-pages` branch, which will automatically be published to your GitHub Pages site.

## Next Steps

- Complete the content for each chapter according to the feature specification
- Add diagrams and visual aids to enhance understanding
- Test the site thoroughly to ensure all links work correctly
- Deploy to GitHub Pages when ready for public access