# Diagram Examples

Complete templates for common diagram types using Mermaid.js.

## Sequence Diagram - API Flow

```mermaid
sequenceDiagram
    participant User
    participant Client as Client App
    participant API as API Server
    participant DB as Database
    participant External as External Service

    Note over User,External: Phase 1: Authentication

    User->>Client: Login request
    Client->>API: POST /api/auth/login
    API->>DB: Verify credentials
    DB-->>API: User found
    API-->>Client: JWT token
    Client-->>User: Redirect to dashboard

    Note over User,External: Phase 2: Data Fetch

    User->>Client: Request data
    Client->>API: GET /api/data (with JWT)
    API->>API: Validate token
    API->>DB: SELECT data
    DB-->>API: Results
    API->>External: Enrich data
    External-->>API: Additional info
    API-->>Client: Combined response
    Client-->>User: Display data
```

## Flowchart - Decision Logic

```mermaid
flowchart TD
    Start([User Purchase Request])
    CheckAuth{Authenticated?}
    CheckSub{Has Subscription?}
    CheckTeam{Team Member?}
    CheckExpired{Expired?}

    GrantAccess[Grant Access]
    DenyAccess[Deny Access]
    ShowCheckout[Show Checkout]
    ShowTeamPage[Show Team Page]

    Start --> CheckAuth
    CheckAuth -->|No| ShowCheckout
    CheckAuth -->|Yes| CheckSub

    CheckSub -->|Yes| CheckExpired
    CheckSub -->|No| CheckTeam

    CheckExpired -->|No| GrantAccess
    CheckExpired -->|Yes| ShowCheckout

    CheckTeam -->|Yes| CheckExpired
    CheckTeam -->|No| ShowCheckout

    GrantAccess --> End([Access Granted])
    ShowCheckout --> End
    ShowTeamPage --> End
    DenyAccess --> End
```

## Entity Relationship Diagram - Database Schema

```mermaid
erDiagram
    USERS ||--o{ USER_SUBSCRIPTIONS : has
    USERS ||--o{ TEAMS : owns
    USERS ||--o{ TEAM_MEMBERS : "member of"
    TEAMS ||--o{ TEAM_MEMBERS : contains
    TEAMS ||--o{ TEAM_INVITATIONS : has
    CLASSES ||--o{ USER_PROGRESS : tracks
    USERS ||--o{ USER_PROGRESS : completes

    USERS {
        uuid id PK
        string email
        string name
        timestamp created_at
    }

    USER_SUBSCRIPTIONS {
        uuid id PK
        uuid user_id FK
        timestamp expires_at
        string source
    }

    TEAMS {
        uuid id PK
        uuid owner_user_id FK
        string name
        int total_seats
        string license_type
        timestamp expires_at
    }

    TEAM_MEMBERS {
        uuid id PK
        uuid team_id FK
        uuid user_id FK
        string status
        timestamp joined_at
    }

    TEAM_INVITATIONS {
        uuid id PK
        uuid team_id FK
        string email
        string status
        timestamp expires_at
    }

    CLASSES {
        uuid id PK
        string title
        string slug
        boolean published
    }

    USER_PROGRESS {
        uuid id PK
        uuid user_id FK
        uuid video_id FK
        boolean completed
    }
```

## State Diagram - Order Status

```mermaid
stateDiagram-v2
    [*] --> Pending: Order Created

    Pending --> Processing: Payment Received
    Pending --> Cancelled: Timeout/User Cancel

    Processing --> Shipped: Items Packed
    Processing --> Failed: Payment Failed
    Processing --> Cancelled: User Cancel

    Shipped --> Delivered: Confirmed Delivery
    Shipped --> ReturnInitiated: Return Request

    Delivered --> ReturnInitiated: Return Request
    Delivered --> [*]: Complete

    Failed --> Pending: Retry Payment
    Failed --> Cancelled: Give Up

    ReturnInitiated --> ReturnProcessing: Return Received
    ReturnProcessing --> Refunded: Refund Issued
    Refunded --> [*]: Complete

    Cancelled --> [*]: Complete

    note right of Processing
        Payment gateway
        processing time
    end note

    note right of Shipped
        Tracking number
        generated
    end note
```

## Class Diagram - System Architecture

```mermaid
classDiagram
    class User {
        +UUID id
        +String email
        +String name
        +authenticate()
        +checkAccess()
    }

    class Subscription {
        +UUID id
        +UUID userId
        +Date expiresAt
        +String source
        +isActive()
        +extend()
    }

    class Team {
        +UUID id
        +String name
        +Int totalSeats
        +Date expiresAt
        +addMember()
        +removeMember()
        +availableSeats()
    }

    class TeamMember {
        +UUID id
        +UUID teamId
        +UUID userId
        +String status
        +activate()
        +remove()
    }

    class AccessControl {
        +checkSubscription()
        +checkTeamAccess()
        +grantAccess()
    }

    User "1" --> "0..*" Subscription
    User "1" --> "0..*" Team : owns
    User "0..*" --> "0..*" Team : member of
    Team "1" --> "0..*" TeamMember
    User --> AccessControl : uses
    Subscription --> AccessControl : uses
    Team --> AccessControl : uses
```

## Gantt Chart - Project Timeline

```mermaid
gantt
    title Development Roadmap Q1 2024
    dateFormat YYYY-MM-DD
    section Planning
    Requirements Gathering    :done, req1, 2024-01-01, 2024-01-15
    Technical Design          :done, des1, 2024-01-10, 2024-01-25

    section Development
    Backend API               :active, dev1, 2024-01-20, 2024-02-15
    Frontend UI               :dev2, 2024-01-25, 2024-02-20
    Database Migration        :dev3, 2024-02-10, 2024-02-18

    section Testing
    Unit Tests               :test1, 2024-02-15, 2024-02-25
    Integration Tests        :test2, 2024-02-20, 2024-03-05
    User Acceptance Testing  :test3, 2024-03-01, 2024-03-15

    section Deployment
    Staging Release          :deploy1, 2024-03-10, 2024-03-12
    Production Release       :crit, deploy2, 2024-03-20, 2024-03-22
    Monitoring & Hotfix      :monitor1, 2024-03-22, 2024-03-31
```

## Git Graph - Branch Strategy

```mermaid
gitGraph
    commit id: "Initial commit"
    branch develop
    checkout develop
    commit id: "Add user model"
    commit id: "Add authentication"

    branch feature/teams
    checkout feature/teams
    commit id: "Create teams table"
    commit id: "Add team API"
    commit id: "Add team UI"

    checkout develop
    merge feature/teams
    commit id: "Update docs"

    branch feature/billing
    checkout feature/billing
    commit id: "Integrate Stripe"
    commit id: "Add checkout flow"

    checkout develop
    merge feature/billing

    checkout main
    merge develop tag: "v1.0.0"

    checkout develop
    commit id: "Fix bug in teams"

    checkout main
    merge develop tag: "v1.0.1"
```

## Mindmap - Feature Planning

```mermaid
mindmap
  root((Team Management))
    Team Creation
      Choose License Type
        1 Year
        Lifetime
      Set Team Name
      Select Seats (min 5)
      Payment via Stripe
    Member Management
      Invite Members
        Email Input
        Bulk Import
        Invitation Expiry
      Remove Members
        Change Status
        Free Up Seat
      View Members
        Active Members
        Pending Invites
    Access Control
      Grant Subscription
        All Classes
        Team-based Access
      Check Membership
        Owner vs Member
        Active vs Removed
      Sidebar Visibility
        Hide for Members
        Show for Owners
    Team Settings
      Rename Team
      View Billing
      Check Expiration
      Manage Seats
```

## Timeline - User Journey

```mermaid
timeline
    title Team Owner Journey
    section Discovery
        Visit Landing Page : Sees team pricing
        Compare Options : Individual vs Team
    section Purchase
        Click Buy Team : Redirected to form
        Configure Team : Name, seats, license
        Checkout : Stripe payment
        Webhook Processing : Team created
    section Onboarding
        Welcome Email : Credentials sent
        First Login : Dashboard access
        Invite Members : Bulk email import
    section Management
        Monitor Usage : See active seats
        Add/Remove Members : Manage team
        Renew License : Extend expiration
```

## Tips for Each Diagram Type

### Sequence Diagrams
- Use `Note over` to mark distinct phases
- Keep participant names short but clear
- Show return messages with `-->`
- Use `alt/else/opt/loop` for conditional flows

### Flowcharts
- Use consistent shapes: `[]` for process, `{}` for decision, `()` for start/end
- Keep text in nodes brief
- Avoid crossing lines when possible
- Use subgraphs for logical grouping

### ER Diagrams
- Show cardinality clearly: `||--o{` means one-to-many
- Include key columns but not all columns
- Document constraints in column descriptions
- Group related entities visually

### State Diagrams
- Start with `[*]` for initial state
- End with `[*]` for final state
- Use notes for important state information
- Keep transition labels concise

### Class Diagrams
- Show key attributes and methods only
- Use `+` for public, `-` for private
- Show inheritance with `--|>`
- Show associations with `-->`

### Gantt Charts
- Use clear section names
- Mark critical tasks with `:crit`
- Show dependencies between tasks
- Include milestones

## Advanced Features

### Styling Individual Elements

```mermaid
flowchart TD
    A[Normal]
    B[Important]
    C[Critical]

    style B fill:#ff9,stroke:#333,stroke-width:4px
    style C fill:#f96,stroke:#333,stroke-width:4px,color:#fff
```

### Adding Links

```mermaid
flowchart LR
    A[Code Review]
    B[Merge PR]

    click A "https://github.com/repo/pulls" "View PRs"
    click B "https://github.com/repo/actions" "View Actions"
```

### Subgraphs

```mermaid
flowchart TD
    subgraph Frontend
        A[React App]
        B[Next.js Server]
    end

    subgraph Backend
        C[TRPC API]
        D[Database]
    end

    A --> B
    B --> C
    C --> D
```
