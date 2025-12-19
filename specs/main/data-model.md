# Data Model: Modern Docusaurus UI for AI/Robotics Book

## Overview
This document defines the data models relevant to the UI customization of the Docusaurus-based AI/Robotics book. The primary entities are existing Docusaurus constructs that will be customized to implement the new UI.

## Key Entities

### Chapter Content
- **Entity Name**: Chapter Content
- **Fields**:
  - id (string): Unique identifier for the chapter
  - title (string): Display title of the chapter
  - content (string): The actual Markdown content
  - module_id (string): Reference to the parent module
  - position (integer): Order within the module
  - is_visible (boolean): Whether the chapter is visible in navigation
  - frontmatter (object): Metadata associated with the chapter
- **Relationships**: Belongs to one Module, contains many CodeBlocks
- **Validation Rules**: Title must not be empty, content must be valid Markdown
- **State Transitions**: None (content is static once published)

### Module Structure
- **Entity Name**: Module Structure
- **Fields**:
  - id (string): Unique identifier for the module
  - title (string): Display title of the module
  - description (string): Brief description of the module content
  - position (integer): Order in the course sequence
  - is_visible (boolean): Whether the module is visible in navigation
  - chapter_ids (array[string]): List of chapter IDs belonging to this module
- **Relationships**: Has many Chapters, belongs to the Course
- **Validation Rules**: Title must not be empty, must have at least one chapter
- **State Transitions**: None (structure is static once published)

### UI Theme
- **Entity Name**: UI Theme
- **Fields**:
  - id (string): Unique identifier for the theme configuration
  - name (string): Display name of the theme (e.g., "Light", "Dark")
  - primary_color (string): Hex code for primary brand color
  - secondary_color (string): Hex code for secondary color
  - neutral_colors (object): Object containing various shades of gray/neutral tones
  - font_family (string): Primary font family for the theme
  - code_font_family (string): Monospace font family for code snippets
  - is_default (boolean): Whether this is the default theme
- **Relationships**: Applied to the entire site
- **Validation Rules**: All color values must be valid hex codes or CSS color names
- **State Transitions**: Active/Inactive based on user selection

### Navigation Hierarchy
- **Entity Name**: Navigation Hierarchy
- **Fields**:
  - item_id (string): Unique identifier for the navigation item
  - title (string): Display text for the navigation item
  - type (string): Enum ("module", "chapter", "external_link", "divider")
  - path (string): URL path for internal links
  - external_url (string): URL for external links (if applicable)
  - parent_id (string): Reference to parent navigation item (null for top level)
  - children_ids (array[string]): List of child navigation item IDs
  - position (integer): Order within siblings
  - icon (string): Optional icon identifier for the item
- **Relationships**: Forms a hierarchical tree structure
- **Validation Rules**: Either path or external_url must be defined (but not both)
- **State Transitions**: Expanded/Collapsed for interactive navigation

## Data Relationships Diagram

```
Course (1) ←→ (Many) Module
Module (1) ←→ (Many) Chapter
Chapter (1) ←→ (Many) CodeBlock
Theme (1) ←→ (Many) UI Element
Navigation Item (1) ←→ (Many) Child Navigation Items
```

## UI-Specific Data Structures

### Module Card Component
- **Entity Name**: Module Card Display Properties
- **Fields**:
  - module_id (string): Reference to the module entity
  - card_title (string): Title displayed on the card
  - card_description (string): Short description shown on the card
  - thumbnail_image (string): Path or URL to the card's thumbnail image
  - stats (object): Object containing counts like total chapters, estimated reading time
  - tags (array[string]): Array of topic tags associated with the module
  - cta_text (string): Call-to-action text on the card
  - cta_link (string): Link for the call-to-action button
- **Validation Rules**: Card title and description must be defined
- **State Transitions**: Hover/Active states for interactivity

### Homepage Section
- **Entity Name**: Homepage Section Configuration
- **Fields**:
  - section_id (string): Unique identifier for the section
  - title (string): Section header title
  - subtitle (string): Optional subtitle for the section
  - layout_type (string): Enum ("hero", "features", "modules", "cta")
  - content_items (array[object]): Array of content items specific to the section type
  - display_order (integer): Order of the section on the homepage
  - visibility_settings (object): Settings for responsive visibility
- **Validation Rules**: Layout type must be a valid enum value
- **State Transitions**: Visible/Hidden based on responsive breakpoints

## Validation Rules Summary

- All displayed text must be non-empty strings
- Color values must follow valid CSS format (hex, rgb, rgba, named colors)
- Navigation paths must be valid relative URLs or the site will throw broken link errors
- Module and chapter IDs must be unique across the site
- Position values must be positive integers
- Relationships must reference existing entities