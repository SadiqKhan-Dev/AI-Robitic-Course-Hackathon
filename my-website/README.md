# Physical AI & Humanoid Robotics Course

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator. It hosts educational content for a course on Physical AI & Humanoid Robotics, with a focus on NVIDIA Isaac technologies for simulation, perception, and navigation.

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Course Modules

This course is organized into multiple modules covering different aspects of humanoid robotics:

- **Module 1**: The Robotic Nervous System (ROS 2)
- **Module 2**: Digital Twin Humanoid Robots
- **Module 3**: NVIDIA Isaac Robotic Brain (Simulation, Perception & Navigation)

Module 3 specifically focuses on NVIDIA Isaac technologies including Isaac Sim for synthetic data generation, Isaac ROS for hardware-accelerated perception, and Nav2 for humanoid navigation.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
