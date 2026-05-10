# Interactive HTML Template

Complete reference template for generating interactive, editable Mermaid diagrams. Use this template when the user opts for the interactive editor during the adaptive interview (Step 0).

## When to Use This Template

Use the interactive template when:
- User explicitly requests editability, customization, or interactive features
- User selects "Yes" when asked about the interactive editor during the interview
- User mentions wanting to change colors, fonts, or export the diagram

For quick sketches or simple documentation, use the standard static template from SKILL.md instead.

---

## Architecture Overview

The interactive template uses a **mutable Mermaid source** pattern:

- `ORIGINAL_MERMAID_CODE` — Immutable original, never modified
- `currentMermaidCode` — Mutable working copy modified by shape/edge/text changes
- `rebuildMermaidCode()` — Replays all stored overrides against the original to produce the working copy
- `reRenderDiagram()` — Renders `currentMermaidCode` with Mermaid, then applies SVG post-processing (colors, scale)

**Two types of changes:**
- **Structural changes** (shape, text, edges) → modify the Mermaid source string, re-render
- **Cosmetic changes** (fill color, stroke color, scale) → SVG post-processing after render

**State is split into:**
- `pageTheme` — Controls page/container background (Light, Dark)
- `diagramStyle` — Controls Mermaid's internal theme for node colors (Default, Dark, Neutral, Forest)

---

## Key Features

### Sidebar Controls
- **Page Theme** — Light/Dark page background (does NOT change diagram node colors)
- **Diagram Style** — Mermaid theme for node coloring (Default, Dark, Neutral, Forest)
- **Global Colors** — Primary, secondary, accent color pickers
- **Typography** — Font family (sans-serif, serif, monospace) and font size slider
- **Zoom** — Scale slider (50-200%) with scrollable container
- **Export** — PNG and SVG export buttons
- **Reset** — Clear all customizations

### Node Interactions
- **Click** — Opens popover with fill color, border color, and shape selector
- **Double-click** — Inline text editing
- **Shift+click** — Cycle node emphasis (80%, 100%, 120%, 150%)
- **Shape selector** — Rectangle, Rounded, Diamond, Circle, Stadium

### Edge/Arrow Interactions
- **Click an arrow** — Opens edge editor with style, label, source/target controls
- **Double-click an arrow label** — Inline label text editing
- **Edge styles** — Solid (`-->`), Dotted (`-.->`), Thick (`==>`)
- **Re-routing** — Change source and target nodes via dropdowns

### Zoom Scrollability
- The diagram container uses `overflow: auto` with `max-height: 80vh`
- When zoomed, explicit width/height is set on the wrapper so scrollbars appear
- Users can scroll to see all parts of a zoomed diagram

### PNG Export
- Uses the "expand-then-capture" approach: temporarily removes overflow/zoom constraints
- `html2canvas` captures the full, properly-styled diagram as the browser renders it
- All constraints restored after capture
- Renders at 2x resolution for retina quality

---

## Complete Interactive HTML Template

The following is the full HTML template. Replace the placeholder comments with actual content. The template below uses `test-interactive-diagram.html` as the validated reference implementation.

**For the complete, tested HTML source**, refer to the `test-interactive-diagram.html` file in the repository root. When generating a diagram, follow this structure:

### HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><!-- DIAGRAM_TITLE --></title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
    <style>
        /* See CSS sections below */
    </style>
</head>
<body class="page-light">
    <!-- Sidebar toggle (visible on mobile) -->
    <button class="sidebar-toggle" onclick="toggleSidebar()">&#9776;</button>

    <!-- Editor Sidebar -->
    <aside class="editor-sidebar" id="editorSidebar">
        <div class="sidebar-header">
            <h2>Diagram Editor</h2>
            <button class="sidebar-close" onclick="toggleSidebar()">&times;</button>
        </div>

        <!-- Page Theme (controls page background, NOT node colors) -->
        <div class="sidebar-section">
            <h3>Page Theme</h3>
            <select id="pageThemeSelect" onchange="onPageThemeChange(this.value)">
                <option value="light">Light</option>
                <option value="dark">Dark</option>
            </select>
        </div>

        <!-- Diagram Style (controls Mermaid node coloring) -->
        <div class="sidebar-section">
            <h3>Diagram Style</h3>
            <select id="diagramStyleSelect" onchange="onDiagramStyleChange(this.value)">
                <option value="default">Default</option>
                <option value="dark">Dark</option>
                <option value="neutral">Neutral</option>
                <option value="forest">Forest</option>
            </select>
        </div>

        <!-- Global Colors -->
        <div class="sidebar-section">
            <h3>Colors</h3>
            <div class="color-row"><span>Primary</span><input type="color" id="colorPrimary" onchange="onColorChange()"></div>
            <div class="color-row"><span>Secondary</span><input type="color" id="colorSecondary" onchange="onColorChange()"></div>
            <div class="color-row"><span>Accent</span><input type="color" id="colorAccent" onchange="onColorChange()"></div>
        </div>

        <!-- Typography -->
        <div class="sidebar-section">
            <h3>Typography</h3>
            <label>Font Family <select id="fontSelect" onchange="onFontChange()">
                <option value="sans-serif">Sans-serif</option>
                <option value="serif">Serif</option>
                <option value="monospace">Monospace</option>
            </select></label>
            <label>Font Size <span class="range-value" id="fontSizeValue">14px</span></label>
            <input type="range" id="fontSizeSlider" min="10" max="24" value="14" oninput="onFontSizeChange(this.value)">
        </div>

        <!-- Zoom -->
        <div class="sidebar-section">
            <h3>Zoom</h3>
            <label>Scale <span class="range-value" id="zoomValue">100%</span></label>
            <input type="range" id="zoomSlider" min="50" max="200" value="100" step="10" oninput="onZoomChange(this.value)">
        </div>

        <!-- Export & Reset -->
        <div class="sidebar-section">
            <h3>Export</h3>
            <button class="export-btn" onclick="exportPNG()">Export as PNG</button>
            <button class="export-btn" onclick="exportSVG()">Export as SVG</button>
        </div>
        <div class="sidebar-section">
            <button class="export-btn reset" onclick="resetToDefaults()">Reset to Defaults</button>
        </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
        <h1><!-- DIAGRAM_TITLE --></h1>
        <p class="subtitle"><!-- DIAGRAM_SUBTITLE --></p>
        <div class="diagram-container" id="diagramContainer">
            <div class="diagram-wrapper" id="diagramWrapper">
                <div class="diagram-loading" id="diagramLoading"></div>
                <div id="diagramOutput"></div>
            </div>
        </div>
        <div class="key-points">
            <h2>Key Points</h2>
            <!-- KEY_POINTS_CONTENT -->
        </div>
    </main>

    <!-- Node Editor Popover (color + shape) -->
    <div class="node-color-picker" id="nodeColorPicker">
        <button class="picker-close" onclick="closeNodePicker()">&times;</button>
        <h4>Node Editor</h4>
        <div class="picker-row"><span>Fill</span><input type="color" id="nodeFillColor" onchange="onNodeFillChange(this.value)"></div>
        <div class="picker-row"><span>Border</span><input type="color" id="nodeStrokeColor" onchange="onNodeStrokeChange(this.value)"></div>
        <div class="picker-row" style="margin-top:8px"><span>Shape</span></div>
        <select id="nodeShapeSelect" onchange="onNodeShapeChange(this.value)">
            <option value="rectangle">Rectangle</option>
            <option value="rounded">Rounded</option>
            <option value="diamond">Diamond</option>
            <option value="circle">Circle</option>
            <option value="stadium">Stadium</option>
        </select>
    </div>

    <!-- Edge Editor Popover -->
    <div class="edge-editor" id="edgeEditor">
        <button class="picker-close" onclick="closeEdgeEditor()">&times;</button>
        <h4>Arrow Editor</h4>
        <label>Style <select id="edgeStyleSelect">
            <option value="-->">Solid Arrow</option>
            <option value="-.->">Dotted Arrow</option>
            <option value="==>">Thick Arrow</option>
        </select></label>
        <label>Label <input type="text" id="edgeLabelInput" placeholder="Arrow label text"></label>
        <label>From <select id="edgeSourceSelect"></select></label>
        <label>To <select id="edgeTargetSelect"></select></label>
        <button class="apply-btn" onclick="applyEdgeChanges()">Apply Changes</button>
    </div>

    <!-- Inline Text Editor -->
    <div class="text-edit-overlay" id="textEditOverlay">
        <input type="text" id="textEditInput" onkeydown="onTextEditKeydown(event)" onblur="commitTextEdit()">
    </div>

    <script>
        /* See JavaScript sections below */
    </script>
</body>
</html>
```

### Critical CSS Sections

The full CSS includes these sections (see `test-interactive-diagram.html` for complete styles):

1. **Base styles** — Flexbox layout, body, system fonts
2. **Page Theme: Dark** — `body.page-dark` styles for all containers, sidebar, popovers
3. **Editor Sidebar** — 280px sticky sidebar with sections
4. **Sidebar Toggle** — Mobile hamburger button (hidden on desktop)
5. **Main Content** — Title, diagram container (`overflow: auto`, `max-height: 80vh`), key points
6. **Node Color Picker** — Absolute-positioned popover with color inputs + shape dropdown
7. **Edge Editor** — Absolute-positioned popover with style, label, source/target controls
8. **Text Edit Overlay** — Positioned input for inline editing
9. **Interactive Highlights** — Hover/selected states for nodes and edges
10. **Responsive** — Sidebar collapses on mobile (< 768px)
11. **Print** — Hides sidebar, popovers, and editor elements
12. **Accessibility** — Focus states, high contrast, reduced motion

### Critical JavaScript Architecture

```javascript
// Immutable original
const ORIGINAL_MERMAID_CODE = `<!-- MERMAID_CODE -->`;
// Mutable working copy
let currentMermaidCode = ORIGINAL_MERMAID_CODE;

let diagramState = {
    pageTheme: 'light',       // 'light' | 'dark' (page background)
    diagramStyle: 'default',  // 'default' | 'dark' | 'neutral' | 'forest' (Mermaid theme)
    colors: { primary: '#0284c7', secondary: '#f59e0b', accent: '#10b981' },
    fontFamily: 'sans-serif',
    fontSize: 14,
    zoom: 100,
    sidebarOpen: true,
    nodeOverrides: {},  // { nodeId: { fill, stroke, shape, textContent, scaleX, scaleY } }
    edgeOverrides: {}   // { edgeIndex: { arrow, label, source, target } }
};
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `rebuildMermaidCode()` | Replays all node shape/text + edge overrides against ORIGINAL to rebuild currentMermaidCode |
| `reRenderDiagram()` | Renders currentMermaidCode with Mermaid, then applies color overrides + click handlers |
| `applyNodeColorOverrides()` | SVG post-processing for fill, stroke, scale on nodes |
| `setupClickHandlers()` | Attaches click/dblclick on nodes, edges, edge labels |
| `parseMermaidSource()` / `parseNodes()` / `parseEdges()` | Parses flowchart code into structured node/edge data |
| `applyShapeOverride()` | Modifies Mermaid source to change a node's bracket syntax |
| `applyEdgeOverride()` | Modifies Mermaid source to change an edge's style/label/routing |
| `exportPNG()` | Expand-then-capture: removes overflow/zoom constraints, html2canvas captures full diagram, restores |
| `exportSVG()` | Serializes SVG element to downloadable file |
| `saveState()` / `loadState()` | localStorage persistence with v1→v2 migration |
| `onPageThemeChange()` | Toggles body class `page-light` / `page-dark` |
| `onDiagramStyleChange()` | Changes Mermaid theme, triggers re-render |

---

## Template Placeholders

When generating the HTML file, replace these placeholders:

| Placeholder | Replace With |
|-------------|-------------|
| `<!-- DIAGRAM_TITLE -->` | Descriptive title (used in `<title>` and `<h1>`) |
| `<!-- DIAGRAM_SUBTITLE -->` | Optional subtitle or description |
| `<!-- MERMAID_CODE -->` | The Mermaid diagram syntax (escaped for JS template literal) |
| `<!-- KEY_POINTS_CONTENT -->` | HTML content for the Key Points section |

### Important: Escaping Mermaid Code

Since the Mermaid code is embedded in a JavaScript template literal, escape backticks and `${` sequences:

```javascript
// Replace ` with \`
// Replace ${ with \${
const ORIGINAL_MERMAID_CODE = `flowchart TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Action]
    B -->|No| D[Other]`;
```

---

## Applying Context Presets

When a preset is selected during the interview:

1. **Add preset class to `<body>`**: e.g., `<body class="page-light preset-academic">`
2. **Include preset CSS** from `context-presets.md` in the `<style>` block
3. **Update default state values** in the JavaScript:

```javascript
// For Academic preset:
let diagramState = {
    pageTheme: 'light',
    diagramStyle: 'neutral',
    colors: { primary: '#1e3a5f', secondary: '#4b5563', accent: '#64748b' },
    fontFamily: 'serif',
    fontSize: 15,
    // ...
};
```

4. **Update sidebar control defaults**: Set initial `<select>` and `<input>` values to match

---

## Interaction Guide for Users

Include this brief guide in generated HTML files (as a collapsible `<details>` section):

```html
<details>
    <summary><strong>How to Use the Interactive Editor</strong></summary>
    <ul>
        <li><strong>Page Theme</strong> - Switch between light and dark page backgrounds</li>
        <li><strong>Diagram Style</strong> - Change the Mermaid diagram color scheme</li>
        <li><strong>Click a node</strong> - Change its fill color, border color, or shape</li>
        <li><strong>Double-click a node</strong> - Edit its text label</li>
        <li><strong>Shift+click a node</strong> - Cycle through size options (80%, 100%, 120%, 150%)</li>
        <li><strong>Click an arrow</strong> - Change its style, edit its label, or re-route it</li>
        <li><strong>Double-click an arrow label</strong> - Quickly edit the label text</li>
        <li><strong>Zoom</strong> - Scale the diagram; scroll within the container to see all parts</li>
        <li><strong>Export</strong> - Save as PNG or SVG (full diagram captured)</li>
        <li><strong>Auto-save</strong> - All customizations persist automatically</li>
        <li><strong>Reset</strong> - Click "Reset to Defaults" to clear everything</li>
    </ul>
</details>
```

---

## Diagram Type Compatibility

| Feature | Flowchart | Sequence | ER | State | Class | Gantt | Git | Mindmap |
|---------|-----------|----------|-----|-------|-------|-------|-----|---------|
| Page theme | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Diagram style | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Global colors | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Font/size | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Zoom + scroll | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Click node colors | Yes | Actors | Entities | States | Classes | No | No | No |
| Node shape change | Yes | No | No | No | No | No | No | No |
| Text editing | Yes | Actors | Entities | States | Classes | No | No | No |
| Node resize | Yes | No | No | Yes | Yes | No | No | No |
| Edge editing | Yes | No | No | No | No | No | No | No |
| Edge re-routing | Yes | No | No | No | No | No | No | No |
| PNG export | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| SVG export | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

---

## State Schema (v2)

```javascript
{
    version: 2,
    lastModified: "ISO-8601",
    pageTheme: "light",          // "light" | "dark"
    diagramStyle: "default",     // "default" | "dark" | "neutral" | "forest"
    colors: {
        primary: "#0284c7",
        secondary: "#f59e0b",
        accent: "#10b981"
    },
    fontFamily: "sans-serif",    // "sans-serif" | "serif" | "monospace"
    fontSize: 14,
    zoom: 100,                   // 50-200
    sidebarOpen: true,
    nodeOverrides: {
        "NodeId": {
            fill: "#hex",        // optional
            stroke: "#hex",      // optional
            shape: "rectangle",  // optional: rectangle|rounded|diamond|circle|stadium
            textContent: "text", // optional
            scaleX: 1.0,         // optional
            scaleY: 1.0          // optional
        }
    },
    edgeOverrides: {
        "0": {                   // keyed by edge index (order in source)
            arrow: "-->",        // optional: --> | -.-> | ==>
            label: "text",       // optional
            source: "NodeA",     // optional
            target: "NodeB"      // optional
        }
    }
}
```

localStorage key: `mermaid-diagram-state-{title-slug}`

Includes v1 → v2 migration: old `theme` field is split into `pageTheme` + `diagramStyle`, and `edgeOverrides` is added.
