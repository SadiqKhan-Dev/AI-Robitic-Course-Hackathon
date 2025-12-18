# Quickstart: Modern Docusaurus UI for AI/Robotics Book

## Prerequisites

- Node.js v18+ installed
- npm, yarn, or pnpm package manager
- Git for version control
- A text editor or IDE

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-robotic-book
```

### 2. Navigate to the Website Directory
```bash
cd my-website
```

### 3. Install Dependencies
```bash
npm install
# or
yarn install
# or
pnpm install
```

### 4. Start the Development Server
```bash
npm start
# or
yarn start
# or
pnpm start
```

The documentation site will be available at http://localhost:3000

## Configuration

### Docusaurus Configuration
The main configuration is located in `docusaurus.config.ts`:

```typescript
// Example configuration elements
module.exports = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Embodied Intelligence in the Physical World',
  url: 'https://your-docusaurus-site.example.com',
  baseUrl: '/',
  // Theme configuration
  themes: [
    '@docusaurus/theme-classic',
    '@docusaurus/theme-search-algolia',
  ],
  // Plugin configuration
  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        sidebarPath: require.resolve('./sidebars.js'),
      },
    ],
  ],
};
```

### Sidebar Navigation
The sidebar navigation is defined in `sidebars.ts` and follows this structure:

```typescript
module.exports = {
  tutorialSidebar: [
    'intro',  // Home page
    {
      type: 'category',  // Module
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [  // Chapters within the module
        'module-1-robotic-nervous-system/intro',
        'module-1-robotic-nervous-system/chapter-1-ros2-nervous-system',
        // ... more chapters
      ],
    },
    // ... more modules
  ],
};
```

## Adding New Content

### Creating a New Chapter
1. Create a new `.md` or `.mdx` file in the appropriate module directory
2. Add frontmatter metadata:
   ```markdown
   ---
   title: Chapter Title
   sidebar_label: Short Label
   ---
   ```
3. Add the new chapter to the appropriate module in `sidebars.ts`

### Creating a New Module
1. Create a new directory in the `docs` folder
2. Add the module to the sidebar configuration in `sidebars.ts`

## Theme Customization

### CSS Customization
Custom CSS can be added in `src/css/custom.css`:
- Override default styles
- Add custom UI elements
- Adjust spacing and typography

### Theme Configuration
Colors and theme options can be configured in `docusaurus.config.ts`:
- Primary and secondary colors
- Dark/light mode settings
- Code block styling

## Building for Production

```bash
npm run build
# or
yarn build
# or
pnpm build
```

The built static files will be in the `build` directory and can be served by any static hosting service.

## Deploying

### GitHub Pages
The site can be deployed to GitHub Pages using GitHub Actions or manually.

### Other Platforms
The generated static files can be deployed to any static hosting platform:
- Netlify
- Vercel
- AWS S3
- Custom web server

## Troubleshooting

### Common Issues:

- **Page not loading**: Ensure all dependencies are installed with `npm install`
- **Sidebar not showing new content**: Update `sidebars.ts` to include the new content
- **Images not displaying**: Place images in the `static/img` directory and reference with `/img/path/to/image`
- **Search not working**: Ensure the Algolia search plugin is configured properly

### Development:
- Check browser console for JavaScript errors
- Verify that all referenced files exist
- Use `npm run serve` to test the production build locally