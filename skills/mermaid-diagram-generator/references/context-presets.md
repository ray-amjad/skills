# Context Presets

Pre-configured theme and styling presets for different diagram contexts. These presets are applied based on the user's response during the adaptive interview (Step 0).

## How Presets Work

When the user selects a context during the interview, the corresponding preset is applied to:
1. **Mermaid `themeVariables`** - Controls diagram colors, fonts, and spacing
2. **CSS overrides** - Controls the HTML page styling around the diagram
3. **Font stack** - Controls typography throughout the output

The preset values should be merged into the HTML template's `mermaid.initialize()` call and `<style>` block.

---

## Academic / Scientific Preset

Best for: research papers, theses, journal figures, technical reports, dissertation diagrams.

### Design Principles
- Clean, minimal decoration
- High-contrast for print reproduction
- Grayscale-friendly colors (still readable in B&W)
- Serif typography for traditional academic feel
- Generous whitespace for clarity

### Mermaid Configuration

```javascript
mermaid.initialize({
    startOnLoad: true,
    theme: 'neutral',
    themeVariables: {
        primaryColor: '#1e3a5f',
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#152d4a',
        lineColor: '#374151',
        secondaryColor: '#4b5563',
        secondaryTextColor: '#ffffff',
        secondaryBorderColor: '#374151',
        tertiaryColor: '#64748b',
        tertiaryTextColor: '#ffffff',
        tertiaryBorderColor: '#475569',
        noteBkgColor: '#f8fafc',
        noteTextColor: '#1e293b',
        noteBorderColor: '#cbd5e1',
        fontSize: '15px',
        fontFamily: 'Georgia, "Times New Roman", Times, serif'
    },
    sequence: {
        actorFontFamily: 'Georgia, "Times New Roman", Times, serif',
        noteFontFamily: 'Georgia, "Times New Roman", Times, serif',
        messageFontFamily: 'Georgia, "Times New Roman", Times, serif',
        actorFontSize: 14,
        noteFontSize: 13,
        messageFontSize: 13,
        mirrorActors: true
    },
    flowchart: {
        useMaxWidth: true,
        htmlLabels: false,
        curve: 'basis',
        nodeSpacing: 60,
        rankSpacing: 60
    }
});
```

### CSS Overrides

```css
/* Academic Preset Overrides */
body.preset-academic {
    font-family: Georgia, 'Times New Roman', Times, serif;
    background: #ffffff;
    color: #1a1a1a;
    line-height: 1.7;
}

body.preset-academic h1 {
    font-family: Georgia, 'Times New Roman', Times, serif;
    font-weight: normal;
    font-size: 1.8rem;
    color: #1a1a1a;
    border-bottom: 1px solid #d1d5db;
    padding-bottom: 8px;
}

body.preset-academic .subtitle {
    font-style: italic;
    color: #4b5563;
    font-size: 14px;
}

body.preset-academic .diagram-container {
    background: #ffffff;
    border: 1px solid #d1d5db;
    box-shadow: none;
    border-radius: 4px;
}

body.preset-academic .key-points {
    background: #ffffff;
    border: 1px solid #d1d5db;
    box-shadow: none;
    border-radius: 4px;
}

body.preset-academic .key-points h2 {
    font-family: Georgia, 'Times New Roman', Times, serif;
    font-weight: normal;
    font-size: 1.4rem;
    border-bottom: 1px solid #d1d5db;
}

body.preset-academic .key-points h3 {
    font-family: Georgia, 'Times New Roman', Times, serif;
    font-weight: bold;
    font-size: 1.1rem;
}

/* Print optimization for academic */
@media print {
    body.preset-academic {
        background: white;
        padding: 0;
        max-width: 100%;
    }

    body.preset-academic .diagram-container,
    body.preset-academic .key-points {
        border: 1px solid #999;
        page-break-inside: avoid;
    }

    body.preset-academic .editor-sidebar {
        display: none !important;
    }
}
```

### Sans-Serif Variant

If the user prefers sans-serif during the interview, replace the font stack:

```javascript
// Replace in themeVariables:
fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif'

// Replace in sequence config:
actorFontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif'
noteFontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif'
messageFontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif'
```

```css
/* Replace in CSS overrides: */
body.preset-academic {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

body.preset-academic h1,
body.preset-academic .key-points h2,
body.preset-academic .key-points h3 {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
```

---

## Presentation Preset

Best for: slide decks, talks, stakeholder demos, team meetings, conference presentations.

### Design Principles
- Bold, high-contrast colors for projector visibility
- Larger fonts and node sizes for readability at distance
- System sans-serif for clean modern look
- Vibrant but professional color palette
- Generous spacing between elements

### Mermaid Configuration

```javascript
mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    themeVariables: {
        primaryColor: '#2563eb',
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#1d4ed8',
        lineColor: '#1e293b',
        secondaryColor: '#dc2626',
        secondaryTextColor: '#ffffff',
        secondaryBorderColor: '#b91c1c',
        tertiaryColor: '#059669',
        tertiaryTextColor: '#ffffff',
        tertiaryBorderColor: '#047857',
        noteBkgColor: '#fef3c7',
        noteTextColor: '#92400e',
        noteBorderColor: '#f59e0b',
        fontSize: '18px',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    sequence: {
        actorFontSize: 18,
        noteFontSize: 16,
        messageFontSize: 16,
        actorMargin: 100,
        width: 240,
        height: 75,
        messageMargin: 45,
        mirrorActors: true
    },
    flowchart: {
        useMaxWidth: true,
        htmlLabels: false,
        curve: 'basis',
        nodeSpacing: 70,
        rankSpacing: 70,
        padding: 20
    }
});
```

### CSS Overrides

```css
/* Presentation Preset Overrides */
body.preset-presentation {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f172a;
    color: #f1f5f9;
    line-height: 1.5;
}

body.preset-presentation h1 {
    font-size: 2.4rem;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
    letter-spacing: -0.02em;
}

body.preset-presentation .subtitle {
    color: #94a3b8;
    font-size: 16px;
    text-align: center;
}

body.preset-presentation .diagram-container {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

body.preset-presentation .key-points {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 30px 40px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

body.preset-presentation .key-points h2 {
    color: #ffffff;
    font-size: 1.6rem;
    font-weight: 700;
    border-bottom: 2px solid #334155;
}

body.preset-presentation .key-points h3 {
    color: #e2e8f0;
    font-size: 1.3rem;
    font-weight: 600;
}

body.preset-presentation .key-points ul,
body.preset-presentation .key-points ol {
    color: #cbd5e1;
    font-size: 16px;
}

body.preset-presentation .key-points strong {
    color: #ffffff;
}

body.preset-presentation .key-points code {
    background: #334155;
    color: #e2e8f0;
    padding: 2px 8px;
    border-radius: 4px;
}

/* Callout overrides for presentation */
body.preset-presentation .phase {
    background: #1e3a5f;
    border-left-color: #3b82f6;
}

body.preset-presentation .phase-title {
    color: #60a5fa;
}

body.preset-presentation .warning {
    background: #451a03;
    border-left-color: #f59e0b;
}

body.preset-presentation .success {
    background: #052e16;
    border-left-color: #10b981;
}

body.preset-presentation .error {
    background: #450a0a;
    border-left-color: #ef4444;
}
```

---

## Applying Presets

When generating the HTML file, apply the preset as follows:

### 1. Set Body Class

Add the preset class to `<body>`:

```html
<!-- For Academic -->
<body class="preset-academic">

<!-- For Presentation -->
<body class="preset-presentation">

<!-- For no preset (default/custom) -->
<body>
```

### 2. Merge Mermaid Config

Use the preset's `mermaid.initialize()` config as the base. If the user also selected the interactive editor, the sidebar controls will override these values dynamically.

### 3. Include CSS Overrides

Include the preset's CSS overrides in the `<style>` block, after the base styles and before the interactive editor styles (if applicable).

### 4. Preset Defaults for Interactive Editor

When the interactive editor sidebar is enabled alongside a preset, initialize the sidebar controls with the preset's values:

| Control | Academic Default | Presentation Default |
|---------|-----------------|---------------------|
| Theme | Neutral | Default |
| Primary Color | `#1e3a5f` | `#2563eb` |
| Secondary Color | `#4b5563` | `#dc2626` |
| Accent Color | `#64748b` | `#059669` |
| Font Family | Serif | Sans-serif |
| Font Size | 15px | 18px |

---

## Documentation Preset (Default)

When the user selects "Documentation" or doesn't specify a context, use the skill's existing default styling (from the base template in SKILL.md). No preset class is added to the body, and the standard Mermaid `'default'` theme is used.

## Quick Sketch Mode

When the user selects "Quick Sketch", use the default documentation preset but skip the interactive editor sidebar. Generate a clean, simple static HTML file using the existing template from SKILL.md.
