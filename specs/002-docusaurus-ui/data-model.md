# Data Model: Docusaurus UI for AI/Robotics Book

## Content Entities

### Chapter Content
- **id**: Unique identifier for the chapter
- **title**: Display title of the chapter
- **slug**: URL-friendly identifier
- **module**: Reference to the parent module
- **content**: Markdown content of the chapter
- **frontmatter**: Metadata about the chapter (author, date, tags, etc.)
- **position**: Order within the module
- **prerequisites**: Other chapters that should be read first

### Module Structure
- **id**: Unique identifier for the module
- **title**: Display title of the module
- **slug**: URL-friendly identifier
- **description**: Brief overview of the module content
- **chapters**: Ordered list of chapter references
- **position**: Order within the overall course

### Navigation Hierarchy
- **id**: Unique identifier for navigation item
- **type**: 'module', 'chapter', or 'external-link'
- **label**: Display text for the navigation item
- **href**: Target URL for navigation
- **children**: Nested navigation items
- **position**: Order in navigation hierarchy

### UI Theme
- **id**: Unique identifier for theme configuration
- **name**: 'light' or 'dark'
- **primaryColor**: Main color for the theme
- **secondaryColor**: Secondary color for the theme
- **textColor**: Default text color
- **backgroundColor**: Default background color
- **codeBlockStyle**: Syntax highlighting configuration
- **userPreference**: Whether user prefers this theme

## State Models

### User Preference
- **userId**: Unique identifier for the user (optional for anonymous)
- **theme**: Current theme preference ('light' or 'dark')
- **fontSize**: Preferred font size setting
- **lastVisited**: Last chapter visited
- **bookmarks**: List of bookmarked chapters

## Relationships

### Module to Chapter
- One Module contains many Chapters
- Each Chapter belongs to exactly one Module
- Navigation hierarchy is determined by position fields

### Chapter to Navigation
- Each Chapter has one Navigation entry
- Navigation entries can have parent/child relationships
- Navigation hierarchy reflects Module → Chapter structure