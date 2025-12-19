---
sidebar_position: 1
---

# Introduction to Physical AI & Humanoid Robotics

Welcome to the comprehensive course on **Physical AI & Humanoid Robotics**. This course is designed to guide you through the fundamental concepts and practical implementations needed to understand and build humanoid robots using modern AI techniques.

## Course Overview

This course is structured into multiple modules, each covering a critical aspect of humanoid robotics:

- **Module 1**: The Robotic Nervous System (ROS 2)
- **Module 2**: Digital Twin Humanoid Robots
- **Module 3**: NVIDIA Isaac Robotic Brain
- **Module 4**: Vision Language Action (VLA) Humanoid Control

## Content Creation Workflow

This documentation site is built using Docusaurus, a modern static site generator designed for documentation. If you're contributing content, follow these guidelines:

### Adding a New Chapter

1. Create a new `.md` or `.mdx` file in the appropriate module directory
2. Add frontmatter metadata at the top of the file:
   ```markdown
   ---
   title: Chapter Title
   sidebar_label: Short Label
   ---
   ```
3. Add the new chapter to the appropriate module in `sidebars.ts`

### Markdown Guidelines

- Use standard Markdown syntax for content
- Use appropriate heading levels (h1-h3) for structure
- Include code examples with proper language annotations
- Link to related content within the course

### Technical Documentation Standards

- Focus on clear, practical explanations
- Include code examples with real-world applications
- Provide visual aids where helpful
- Ensure examples are up-to-date and tested

## Getting Started

To run this documentation site locally:

1. Ensure you have Node.js version 20.0 or above installed
2. Navigate to the `my-website` directory
3. Install dependencies with `npm install`
4. Start the development server with `npm run start`
5. Visit `http://localhost:3000` in your browser

The site will automatically reload when you make changes to any of the documentation files.
