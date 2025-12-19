# API Contracts: Modern Docusaurus UI for AI/Robotics Book

## Overview

This document defines the API contracts for the frontend components of the modern UI implementation. Since this is a Docusaurus-based static site, the "APIs" refer to component interfaces, data structures, and event contracts.

## Component Interfaces

### 1. ThemeProvider API

#### Interface Definition
```typescript
interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: 'light' | 'dark';
  storageKey?: string;
}

interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}
```

#### Purpose
Manages the theme state across the application and provides theme-related utilities to child components.

#### Usage Example
```jsx
<ThemeProvider defaultTheme="system">
  <App />
</ThemeProvider>
```

#### Events
- `onThemeChange`: Triggered when theme changes, receives new theme value

### 2. ModuleCard API

#### Interface Definition
```typescript
interface ModuleCardProps {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
  linkUrl: string;
  color?: string;
  position?: number;
  onClick?: (event: React.MouseEvent) => void;
}

interface ModuleCardState {
  hovered: boolean;
  loaded: boolean;
}
```

#### Purpose
Displays a card representing a book module with visual elements and navigation capability.

#### Usage Example
```jsx
<ModuleCard 
  title="ROS 2 Nervous System"
  description="Learn how ROS 2 serves as the nervous system for robotic applications"
  imageUrl="/img/modules/ros2-nervous-system.jpg"
  linkUrl="/docs/module-1-robotic-nervous-system/intro"
/>
```

#### Events
- `onCardClick`: Triggered when the card is clicked
- `onImageLoad`: Triggered when the module image finishes loading

### 3. HomepageHero API

#### Interface Definition
```typescript
interface HomepageHeroProps {
  title: string;
  subtitle: string;
  ctaText: string;
  ctaUrl: string;
  backgroundImageUrl?: string;
  variant?: 'simple' | 'complex' | 'video';
}

interface HomepageHeroState {
  animationComplete: boolean;
}
```

#### Purpose
Displays the main hero section on the homepage with compelling visual elements and call to action.

#### Usage Example
```jsx
<HomepageHero 
  title="Physical AI & Humanoid Robotics"
  subtitle="Embodied Intelligence in the Physical World"
  ctaText="Start Learning"
  ctaUrl="/docs/intro"
/>
```

#### Events
- `onCtaClick`: Triggered when the call-to-action button is clicked

### 4. NavigationMenu API

#### Interface Definition
```typescript
interface NavigationMenuItem {
  id: string;
  label: string;
  url: string;
  children?: NavigationMenuItem[];
  icon?: string;
}

interface NavigationMenuProps {
  items: NavigationMenuItem[];
  orientation?: 'horizontal' | 'vertical';
  variant?: 'standard' | 'compact' | 'minimal';
  activePath?: string;
  onNavigate?: (url: string) => void;
}

interface NavigationMenuState {
  expandedItems: string[];
}
```

#### Purpose
Provides a flexible navigation menu component that can be used in headers, sidebars, or footers.

#### Usage Example
```jsx
<NavigationMenu 
  items={[
    { id: 'modules', label: 'Course Modules', url: '/docs/intro' },
    { id: 'about', label: 'About', url: '/about' }
  ]}
  activePath={location.pathname}
/>
```

#### Events
- `onNavigate`: Triggered when a navigation item is selected
- `onItemExpand`: Triggered when a submenu item is expanded (for multi-level menus)

## Data Contracts

### 1. Module Data Contract
```typescript
interface ModuleData {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  position: number;
  chapters: ChapterData[];
  createdAt: string; // ISO 8601 datetime
  updatedAt: string; // ISO 8601 datetime
}
```

### 2. Chapter Data Contract
```typescript
interface ChapterData {
  id: string;
  moduleId: string;
  title: string;
  description: string;
  durationEstimate: string;
  isCompleted: boolean;
  position: number;
  metadata: Record<string, any>;
  createdAt: string; // ISO 8601 datetime
  updatedAt: string; // ISO 8601 datetime
}
```

### 3. Theme Configuration Contract
```typescript
interface ThemeData {
  id: string; // 'light' or 'dark'
  name: string;
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
  textColor: string;
  textSecondaryColor: string;
  borderColor: string;
  borderRadius: string;
  boxShadow: string;
  fontFamily: string;
  fontSizeBase: string;
  lineHeightBase: number;
  spacingScale: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  createdAt: string; // ISO 8601 datetime
  updatedAt: string; // ISO 8601 datetime
}
```

### 4. Homepage Section Data Contract
```typescript
interface HomepageSectionData {
  id: string;
  type: 'hero' | 'modules' | 'features' | 'testimonials' | 'cta';
  title: string;
  subtitle: string;
  position: number;
  content: Record<string, any>;
  isVisible: boolean;
  themeId: string;
  createdAt: string; // ISO 8601 datetime
  updatedAt: string; // ISO 8601 datetime
}
```

## Event Contracts

### 1. Theme Change Event
```typescript
interface ThemeChangeEvent {
  type: 'THEME_CHANGED';
  payload: {
    previousTheme: 'light' | 'dark';
    newTheme: 'light' | 'dark';
    timestamp: string; // ISO 8601 datetime
  };
}
```

### 2. Module Card Interaction Event
```typescript
interface ModuleCardInteractionEvent {
  type: 'MODULE_CARD_CLICKED' | 'MODULE_CARD_HOVERED' | 'MODULE_CARD_LOADED';
  payload: {
    moduleId: string;
    elementId: string;
    interactionType: 'click' | 'hover' | 'load';
    timestamp: string; // ISO 8601 datetime
  };
}
```

### 3. Navigation Event
```typescript
interface NavigationEvent {
  type: 'NAVIGATED';
  payload: {
    fromPath: string;
    toPath: string;
    navigationMethod: 'click' | 'keyboard' | 'programmatic';
    timestamp: string; // ISO 8601 datetime
  };
}
```

## Error Handling

### 1. Image Loading Error Contract
```typescript
interface ImageLoadError {
  type: 'IMAGE_LOAD_ERROR';
  payload: {
    imageUrl: string;
    fallbackUrl: string;
    errorMessage: string;
    timestamp: string; // ISO 8601 datetime
  };
}
```

### 2. Data Fetch Error Contract (for dynamic elements)
```typescript
interface DataFetchError {
  type: 'DATA_FETCH_ERROR';
  payload: {
    requestUrl: string;
    errorType: 'NETWORK_ERROR' | 'PARSE_ERROR' | 'VALIDATION_ERROR';
    errorMessage: string;
    timestamp: string; // ISO 8601 datetime
  };
}
```

## Versioning Strategy

- Components follow semantic versioning (major.minor.patch)
- Breaking changes to props or return types trigger a major version bump
- New features trigger a minor version bump
- Bugfixes trigger a patch version bump
- Deprecation warnings are provided for at least one minor version before removal

## Backward Compatibility

- All component props are optional when possible, with sensible defaults
- Event payloads include version information for handling changes
- Previous versions of contracts are maintained during migration periods
- Clear deprecation path provided for any contract changes