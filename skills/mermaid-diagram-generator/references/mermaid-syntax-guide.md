# Mermaid Syntax Guide

Complete reference for Mermaid.js diagram syntax.

## Sequence Diagrams

### Basic Syntax

```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob

    A->>B: Solid arrow with message
    B-->>A: Dotted return arrow
    A->B: Solid arrow without arrowhead
    B-->A: Dotted arrow without arrowhead
```

### Arrow Types

| Syntax | Description |
|--------|-------------|
| `->` | Solid line without arrow |
| `-->` | Dotted line without arrow |
| `->>` | Solid line with arrowhead |
| `-->>` | Dotted line with arrowhead |
| `-x` | Solid line with cross at end |
| `--x` | Dotted line with cross at end |
| `-)` | Solid line with open arrow |
| `--)` | Dotted line with open arrow |

### Activations

```mermaid
sequenceDiagram
    Alice->>+John: Hello John
    John-->>-Alice: Great!
```

### Notes

```mermaid
sequenceDiagram
    Note left of Alice: Text on left
    Note right of Bob: Text on right
    Note over Alice,Bob: Text spanning both
```

### Loops and Alternatives

```mermaid
sequenceDiagram
    loop Every minute
        Alice->>Bob: Ping
    end

    alt Success case
        Bob->>Alice: Success
    else Failure case
        Bob->>Alice: Error
    end

    opt Optional
        Bob->>Alice: Extra info
    end
```

### Parallel Actions

```mermaid
sequenceDiagram
    par Alice to Bob
        Alice->>Bob: Request 1
    and Alice to John
        Alice->>John: Request 2
    end

    Bob-->>Alice: Response 1
    John-->>Alice: Response 2
```

---

## Flowcharts

### Node Shapes

```mermaid
flowchart TD
    A[Rectangle]
    B(Rounded)
    C([Stadium])
    D[[Subroutine]]
    E[(Database)]
    F((Circle))
    G>Flag]
    H{Diamond}
    I{{Hexagon}}
    J[/Parallelogram/]
    K[\Parallelogram\]
    L[/Trapezoid\]
    M[\Trapezoid/]
```

### Arrow Types

```mermaid
flowchart LR
    A --> B      %% Arrow
    B --- C      %% Line
    C -.-> D     %% Dotted
    D ==> E      %% Thick
    E ~~~ F      %% Invisible
```

### Arrow with Text

```mermaid
flowchart LR
    A -->|Text| B
    B -.->|Text| C
    C ==>|Text| D
```

### Direction

```mermaid
flowchart TD   %% Top to Down
flowchart LR   %% Left to Right
flowchart BT   %% Bottom to Top
flowchart RL   %% Right to Left
```

### Subgraphs

```mermaid
flowchart TB
    subgraph Frontend
        A[React]
        B[Next.js]
    end

    subgraph Backend
        C[API]
        D[Database]
    end

    A --> C
    C --> D
```

---

## Entity Relationship Diagrams

### Relationships

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
```

### Cardinality

| Value | Description |
|-------|-------------|
| `\|o` | Zero or one |
| `\|\|` | Exactly one |
| `}o` | Zero or many |
| `}\|` | One or many |

### Relationship Types

| Syntax | Description |
|--------|-------------|
| `--` | Non-identifying |
| `..` | Identifying |

### Attributes

```mermaid
erDiagram
    USER {
        uuid id PK "Primary key"
        string email UK "Unique, not null"
        string name
        timestamp created_at
    }

    ORDER {
        uuid id PK
        uuid user_id FK "Foreign key"
        decimal total
        string status "pending, paid, shipped"
    }
```

---

## State Diagrams

### Basic States

```mermaid
stateDiagram-v2
    [*] --> State1
    State1 --> State2
    State2 --> [*]
```

### Composite States

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Running
        Running --> Paused
        Paused --> Running
        Running --> [*]
    }

    Active --> [*]
```

### Choice

```mermaid
stateDiagram-v2
    state if_state <<choice>>
    [*] --> IsPositive
    IsPositive --> if_state
    if_state --> False: if n < 0
    if_state --> True: if n >= 0
```

### Fork/Join

```mermaid
stateDiagram-v2
    state fork_state <<fork>>
    [*] --> fork_state
    fork_state --> State1
    fork_state --> State2

    state join_state <<join>>
    State1 --> join_state
    State2 --> join_state
    join_state --> [*]
```

### Notes

```mermaid
stateDiagram-v2
    State1 --> State2
    note right of State1
        Important note
        on multiple lines
    end note
```

---

## Class Diagrams

### Basic Class

```mermaid
classDiagram
    class BankAccount {
        +String owner
        +BigDecimal balance
        +deposit(amount)
        +withdrawal(amount)
    }
```

### Visibility

| Symbol | Visibility |
|--------|-----------|
| `+` | Public |
| `-` | Private |
| `#` | Protected |
| `~` | Package/Internal |

### Relationships

```mermaid
classDiagram
    classA --|> classB : Inheritance
    classC --* classD : Composition
    classE --o classF : Aggregation
    classG --> classH : Association
    classI -- classJ : Link
    classK ..> classL : Dependency
    classM ..|> classN : Realization
```

### Cardinality

```mermaid
classDiagram
    Customer "1" --> "0..*" Order
    Order "1" --> "1..*" LineItem
```

### Methods and Properties

```mermaid
classDiagram
    class User {
        +String email
        -String password
        #Date createdAt
        +authenticate() bool
        -hashPassword(String) String
    }
```

---

## Gantt Charts

### Basic Syntax

```mermaid
gantt
    title Project Schedule
    dateFormat YYYY-MM-DD

    section Planning
    Task 1           :a1, 2024-01-01, 30d
    Task 2           :after a1, 20d

    section Development
    Task 3           :2024-01-15, 45d
    Task 4           :2024-02-01, 30d
```

### Task Status

```mermaid
gantt
    dateFormat YYYY-MM-DD

    Completed task      :done, des1, 2024-01-01, 2024-01-08
    Active task         :active, des2, 2024-01-09, 3d
    Future task         :des3, after des2, 5d
    Critical task       :crit, des4, 2024-01-15, 2024-01-20
    Critical & Active   :crit, active, des5, 2024-01-18, 5d
```

---

## Git Graph

### Basic Commits

```mermaid
gitGraph
    commit
    commit
    commit
```

### Branches

```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
```

### Tags

```mermaid
gitGraph
    commit
    commit tag: "v1.0.0"
    branch develop
    commit
    checkout main
    merge develop tag: "v1.1.0"
```

---

## Pie Charts

```mermaid
pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
```

---

## Mindmaps

```mermaid
mindmap
  root((Project))
    Planning
      Requirements
      Design
    Development
      Frontend
      Backend
    Testing
      Unit Tests
      Integration Tests
```

---

## Timeline

```mermaid
timeline
    title History of Social Media
    2002 : LinkedIn
    2004 : Facebook
         : Google
    2005 : Youtube
    2006 : Twitter
```

---

## Styling

### Inline Styles

```mermaid
flowchart LR
    A[Default]
    B[Styled]

    style B fill:#f9f,stroke:#333,stroke-width:4px
```

### Style Classes

```mermaid
flowchart LR
    A[Node 1]:::someclass
    B[Node 2]:::anotherclass

    classDef someclass fill:#f96,stroke:#333
    classDef anotherclass fill:#bbf,stroke:#333
```

### Theme Configuration

```javascript
mermaid.initialize({
    theme: 'default',        // or 'dark', 'forest', 'neutral'
    themeVariables: {
        primaryColor: '#ff0000',
        primaryTextColor: '#fff',
        primaryBorderColor: '#333',
        lineColor: '#666',
        secondaryColor: '#00ff00',
        tertiaryColor: '#0000ff'
    }
});
```

---

## Comments

```mermaid
%% This is a comment
flowchart LR
    A[Node] %% Comment on same line
```

---

## Special Characters

To use special characters in text, wrap in quotes:

```mermaid
flowchart LR
    A["Text with (parentheses)"]
    B["Text with {braces}"]
    C["Text with [brackets]"]
```

---

## Line Breaks

Use `<br/>` for line breaks in node text:

```mermaid
flowchart LR
    A["First line<br/>Second line<br/>Third line"]
```

---

## Configuration Options

### Sequence Diagrams

```javascript
{
    sequence: {
        diagramMarginX: 50,
        diagramMarginY: 10,
        actorMargin: 80,
        width: 200,
        height: 65,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35,
        mirrorActors: true,
        bottomMarginAdj: 1,
        useMaxWidth: true,
        rightAngles: false,
        showSequenceNumbers: false
    }
}
```

### Flowcharts

```javascript
{
    flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis',     // or 'linear', 'step', 'stepBefore', 'stepAfter'
        diagramPadding: 8,
        nodeSpacing: 50,
        rankSpacing: 50
    }
}
```

### Gantt Charts

```javascript
{
    gantt: {
        titleTopMargin: 25,
        barHeight: 20,
        barGap: 4,
        topPadding: 50,
        leftPadding: 75,
        gridLineStartPadding: 35,
        fontSize: 11,
        numberSectionStyles: 4,
        axisFormat: '%Y-%m-%d'
    }
}
```

---

## Best Practices

1. **Keep it Simple**: Don't overcrowd diagrams
2. **Use Descriptive Labels**: Make text clear and concise
3. **Consistent Naming**: Use consistent participant/node names
4. **Add Notes**: Explain complex transitions
5. **Group Logically**: Use subgraphs and sections
6. **Test Rendering**: Some complex diagrams may need simplification
7. **Use Comments**: Document your diagram structure

---

## Common Issues

### Text Too Long
Break into multiple lines or use abbreviations:
```mermaid
flowchart LR
    A["This is a very long<br/>text that spans<br/>multiple lines"]
```

### Overlapping Connections
Adjust node positions or use invisible links:
```mermaid
flowchart LR
    A ~~~ B  %% Invisible link to position nodes
```

### Special Characters
Always quote strings with special characters:
```mermaid
flowchart LR
    A["User's Input"]
    B["Error: (404) Not Found"]
```

---

## Resources

- [Official Mermaid Documentation](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/)
- [GitHub Mermaid Support](https://github.blog/2022-02-14-include-diagrams-markdown-files-mermaid/)
