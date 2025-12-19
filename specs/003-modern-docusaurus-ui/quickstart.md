# Quickstart Guide: Modern Docusaurus UI Implementation

## Overview

This guide provides a step-by-step process to implement the modern, premium UI for the AI/Robotics book using Docusaurus. The implementation will focus on creating a clean, minimal design with high contrast, proper visual hierarchy, and optimized localhost development experience.

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn package manager
- Git for version control
- A code editor (VS Code recommended)

## Step 1: Clone and Set Up the Repository

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-robotic-book
   ```

2. Navigate to the frontend directory:
   ```bash
   cd frontend-book
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

## Step 2: Configure Docusaurus for Modern UI

1. Update the `docusaurus.config.ts` to enhance theme configuration:
   - Enable the v4 future flag for compatibility
   - Configure enhanced color mode options
   - Set up custom CSS file path

2. Update the CSS variables in `src/css/custom.css` with the new design system:
   - Modern color palette with improved contrast
   - Typography enhancements with better spacing
   - Component styling with consistent visual language

## Step 3: Create Custom Homepage Components

1. Create the new HomepageHero component:
   ```bash
   mkdir src/components/HomepageHero
   touch src/components/HomepageHero/index.tsx
   touch src/components/HomepageHero/styles.module.css
   ```

2. Create the ModuleCard component:
   ```bash
   mkdir src/components/ModuleCard
   touch src/components/ModuleCard/index.tsx
   touch src/components/ModuleCard/styles.module.css
   ```

3. Create the HomepageSections component:
   ```bash
   mkdir src/components/HomepageSections
   touch src/components/HomepageSections/index.tsx
   touch src/components/HomepageSections/styles.module.css
   ```

## Step 4: Implement Custom Styling

1. Replace the existing `src/css/custom.css` with enhanced styles:
   - Modern color variables with dark/light mode support
   - Improved typography scale and spacing
   - Enhanced component styles for better visual hierarchy
   - Accessibility improvements (focus states, contrast)

2. Create module-specific CSS files for new components with scoped styles

## Step 5: Update Homepage Layout

1. Modify `src/pages/index.tsx` to use new components:
   - Replace the existing header with the new HomepageHero
   - Replace HomepageFeatures with HomepageSections
   - Add module cards for each book module

2. Update `src/pages/index.module.css` for new layout requirements

## Step 6: Add Placeholder Images

1. Create placeholder images in `static/img/`:
   ```bash
   mkdir -p static/img/modules
   mkdir -p static/img/placeholders
   ```

2. Add module-specific images:
   - `static/img/modules/ros2-nervous-system.jpg`
   - `static/img/modules/digital-twin-humanoid.jpg`
   - `static/img/modules/isaac-brain.jpg`
   - And others for each module

## Step 7: Test Locally

1. Start the development server:
   ```bash
   npm run start
   ```

2. Verify the following:
   - Homepage displays with new modern design
   - Dark/light mode toggle works correctly
   - Module cards display properly with placeholder images
   - All pages maintain consistent design language
   - Responsiveness works on different screen sizes

## Step 8: Build and Deploy

1. Build the static site:
   ```bash
   npm run build
   ```

2. Test the build locally:
   ```bash
   npm run serve
   ```

## Common Customization Points

### Color Scheme
Update these variables in `src/css/custom.css` to change the color scheme:
- `--ifm-color-primary`: Main brand color
- `--ifm-color-primary-dark`: Darker variant of brand color

### Typography
Modify these variables in `src/css/custom.css` to change typography:
- `--ifm-font-family-base`: Main font stack
- `--ifm-font-size-base`: Base font size
- `--ifm-line-height-base`: Base line height

### Spacing
Adjust these variables in `src/css/custom.css` for spacing:
- `--ifm-global-spacing`: Base spacing unit
- Heading sizes: `--ifm-h1-font-size`, `--ifm-h2-font-size`, etc.

## Troubleshooting

### Component Not Rendering
- Check that import paths are correct
- Verify that the component is properly exported
- Look for TypeScript/JavaScript errors in the console

### Dark Mode Not Working
- Ensure `colorMode.respectPrefersColorScheme` is enabled in config
- Check that CSS variables are properly defined in both `:root` and `[data-theme='dark']` blocks

### Image Issues
- Verify image paths are correct in static directory
- Check that image files exist and are properly named
- Confirm that image files are in the correct format (recommended: JPEG, PNG, or WebP)

## Next Steps

1. Customize module cards with actual content from your documentation
2. Add more sections to the homepage as needed
3. Implement any additional interactive elements
4. Add analytics or other tracking if required
5. Set up deployment automation to GitHub Pages or your hosting platform