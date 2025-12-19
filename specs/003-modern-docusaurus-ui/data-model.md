# Data Model: Modern Docusaurus UI for AI/Robotics Book

## Overview

This document defines the data structures and relationships for the modern UI implementation of the AI/Robotics book using Docusaurus. The data model encompasses the visual and structural elements required to implement a premium UI with clear visual hierarchy and proper content organization.

## Core Entities

### Book Module
Represents a major section of the AI/Robotics book containing multiple chapters and topics.

**Fields:**
- id (string): Unique identifier for the module
- title (string): Display title of the module
- description (string): Brief description of the module content
- icon (string): Icon identifier or path for the module
- color (string): Primary color associated with the module
- position (number): Order in which the module appears
- chapters (Chapter[]): Related chapters within the module
- createdAt (DateTime): Timestamp of module creation
- updatedAt (DateTime): Timestamp of last update

**Validation rules:**
- title must be 3-100 characters
- position must be a positive integer
- color must be a valid hex color or CSS color name

### Book Chapter
Represents a subsection within a module containing educational content.

**Fields:**
- id (string): Unique identifier for the chapter
- moduleId (string): Reference to the parent module
- title (string): Display title of the chapter
- description (string): Brief description of the chapter content
- durationEstimate (string): Estimated reading time (e.g., "15 min")
- isCompleted (boolean): User completion status
- position (number): Order within the module
- metadata (Object): Additional chapter-specific data
- createdAt (DateTime): Timestamp of chapter creation
- updatedAt (DateTime): Timestamp of last update

**Validation rules:**
- title must be 3-100 characters
- moduleId must reference an existing module
- position must be a positive integer
- durationEstimate follows format "X min" or "X hr Y min"

### UI Theme
Represents the visual styling configuration supporting light and dark variations.

**Fields:**
- id (string): Unique identifier (e.g., "light", "dark")
- name (string): Display name of the theme
- primaryColor (string): Main brand color
- secondaryColor (string): Supporting brand color
- backgroundColor (string): Background color
- textColor (string): Primary text color
- textSecondaryColor (string): Secondary text color
- borderColor (string): Border color
- borderRadius (string): Radius for rounded corners
- boxShadow (string): Shadow definition
- fontFamily (string): Font family stack
- fontSizeBase (string): Base font size
- lineHeightBase (number): Base line height ratio
- spacingScale (Object): Scale for consistent spacing (e.g., {sm: "0.5rem", md: "1rem", lg: "1.5rem"})
- createdAt (DateTime): Timestamp of theme creation
- updatedAt (DateTime): Timestamp of last update

**Validation rules:**
- id must be unique
- all color values must be valid CSS color definitions
- borderRadius must be valid CSS length value
- fontFamily must be valid CSS font stack

### Homepage Section
Represents different areas of the custom homepage layout, including hero and content categorization.

**Fields:**
- id (string): Unique identifier for the section
- type (string): Type of section (e.g., "hero", "modules", "features", "testimonials", "cta")
- title (string): Section title
- subtitle (string): Section subtitle or description
- position (number): Vertical order of the section
- content (Object): Section-specific content and configuration
- isVisible (boolean): Whether the section is displayed
- themeId (string): Associated theme for this section
- createdAt (DateTime): Timestamp of section creation
- updatedAt (DateTime): Timestamp of last update

**Validation rules:**
- id must be unique
- type must be one of the allowed values
- position must be a positive integer

### Module Card
Visual representation of a book module on the homepage and other navigation areas.

**Fields:**
- id (string): Unique identifier for the card
- moduleId (string): Reference to the associated module
- title (string): Card title
- description (string): Brief description of the module
- imageUrl (string): Path to the placeholder image
- ctaText (string): Call-to-action text (e.g., "Start Learning")
- ctaLink (string): Destination URL for the CTA
- color (string): Accent color for the card
- position (number): Position in grid/list
- createdAt (DateTime): Timestamp of card creation
- updatedAt (DateTime): Timestamp of last update

**Validation rules:**
- moduleId must reference an existing module
- position must be a positive integer
- imageUrl must be a valid path
- ctaLink must be a valid URL or internal path

### Navigation Item
Represents menu items in various navigation components.

**Fields:**
- id (string): Unique identifier for the navigation item
- label (string): Display text
- url (string): Destination URL or path
- parentId (string): Reference to parent item (for dropdowns/submenus)
- position (number): Order in navigation
- icon (string): Icon identifier or path
- isActive (boolean): Whether this is the current page
- isExternal (boolean): Whether link opens in new tab
- createdAt (DateTime): Timestamp of creation
- updatedAt (DateTime): Timestamp of last update

**Validation rules:**
- label must be 1-50 characters
- position must be a positive integer
- if isExternal is true, url must be a complete URL

## Relationships

### Module-Chapter Relationship
- One Book Module contains many Book Chapters
- Relationship: Module (1) → Chapter (0..n)
- Foreign Key: Chapter.moduleId references Module.id
- Cascade delete: Deleting a module deletes its chapters

### Theme-Section Relationship
- One UI Theme applies to many Homepage Sections
- Relationship: Theme (1) → Homepage Section (0..n)
- Foreign Key: HomepageSection.themeId references Theme.id

### Module-Card Relationship
- One Book Module corresponds to one Module Card
- Relationship: Module (1) → Module Card (0..1)
- Foreign Key: ModuleCard.moduleId references Module.id

## State Transitions

### User Theme Preference
- Initial: Browser default (based on prefers-color-scheme)
- Can transition to: User selected light mode
- Can transition to: User selected dark mode
- Persistence: Stored in browser local storage

### Module Card Interactions
- Initial: Static display
- Can transition to: Hover state (with subtle animation)
- Can transition to: Active/focused state (with focus ring)
- Can transition to: Clicked state (navigation to content)

## Constraints

1. All components must be responsive and adapt to various screen sizes
2. Color contrast ratios must meet WCAG AA standards (minimum 4.5:1 for normal text)
3. Components must work in both light and dark modes without adjustment
4. Navigation structure must remain consistent across all pages
5. Module cards must maintain consistent aspect ratios regardless of content length
6. All interactive elements must have clear focus states for accessibility
7. Homepage sections must have configurable visibility for A/B testing
8. All timestamps must be stored in UTC and displayed in user's local timezone if needed