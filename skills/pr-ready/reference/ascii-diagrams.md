# ASCII Diagram Patterns

Quick reference for creating effective ASCII diagrams in PR descriptions.

## Character Reference

### Box Drawing

```
Single line:          Double line:
┌───┬───┐            ╔═══╦═══╗
│   │   │            ║   ║   ║
├───┼───┤            ╠═══╬═══╣
│   │   │            ║   ║   ║
└───┴───┘            ╚═══╩═══╝

Rounded corners:
╭───────╮
│       │
╰───────╯
```

### Arrows

```
Directional:  → ← ↑ ↓ ↗ ↘ ↙ ↖
Filled:       ▶ ◀ ▲ ▼
Line arrows:  ─> <─
              │
              v
```

### Connectors

```
T-junctions:  ├ ┤ ┬ ┴
Cross:        ┼
Corner:       ┌ ┐ └ ┘
```

## Common Patterns

### 1. Service Architecture

```
┌─────────────────────────────────────────────────┐
│                   API Gateway                    │
└──────────┬──────────────┬──────────────┬────────┘
           │              │              │
           ▼              ▼              ▼
      ┌────────┐    ┌────────┐    ┌────────┐
      │  Auth  │    │  User  │    │ Order  │
      │Service │    │Service │    │Service │
      └───┬────┘    └───┬────┘    └───┬────┘
          │             │             │
          └─────────────┼─────────────┘
                        │
                   ┌────┴────┐
                   │ Message │
                   │  Queue  │
                   └─────────┘
```

### 2. Request/Response Flow

```
┌────────┐      ┌────────┐      ┌────────┐      ┌────────┐
│ Client │─────>│  Load  │─────>│  App   │─────>│   DB   │
│        │      │Balancer│      │ Server │      │        │
└────────┘      └────────┘      └────────┘      └────────┘
    ▲                               │
    │                               │
    └───────────── Response ────────┘
```

### 3. State Machine

```
                         ┌──────────┐
              ┌─────────>│  DRAFT   │<──────────┐
              │          └────┬─────┘           │
              │               │                 │
           cancel          submit            reject
              │               │                 │
              │               ▼                 │
         ┌────┴────┐    ┌──────────┐    ┌──────┴───┐
         │CANCELLED│    │ PENDING  │───>│ REJECTED │
         └─────────┘    └────┬─────┘    └──────────┘
                             │
                          approve
                             │
                             ▼
                       ┌──────────┐
                       │ APPROVED │
                       └──────────┘
```

### 4. Data Pipeline

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Extract │───>│Transform│───>│Validate │───>│  Load   │
│  (API)  │    │ (Parse) │    │ (Rules) │    │  (DB)   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
  raw.json      parsed.json   valid.json    records
```

### 5. Sequence Diagram

```
Client           Server          Database         Cache
   │                │                │              │
   │── GET /user ──>│                │              │
   │                │── Check ──────────────────────>│
   │                │<─ HIT ─────────────────────────│
   │<─── 200 OK ────│                │              │
   │                │                │              │
   │── GET /order ─>│                │              │
   │                │── Check ──────────────────────>│
   │                │<─ MISS ────────────────────────│
   │                │── SELECT ─────>│              │
   │                │<─ Result ──────│              │
   │                │── Set ───────────────────────>│
   │<─── 200 OK ────│                │              │
```

### 6. Layer Diagram

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│  (React Components, Views, Templates)   │
├─────────────────────────────────────────┤
│            Application Layer            │
│     (Services, Use Cases, Commands)     │
├─────────────────────────────────────────┤
│             Domain Layer                │
│   (Entities, Value Objects, Rules)      │
├─────────────────────────────────────────┤
│          Infrastructure Layer           │
│  (Database, External APIs, Framework)   │
└─────────────────────────────────────────┘
```

### 7. Tree Structure

```
src/
├── components/
│   ├── common/
│   │   ├── Button.tsx
│   │   └── Input.tsx
│   └── features/
│       ├── auth/
│       │   ├── LoginForm.tsx
│       │   └── RegisterForm.tsx
│       └── orders/
│           └── OrderList.tsx
├── services/
│   ├── api.ts
│   └── auth.ts
└── utils/
    └── helpers.ts
```

### 8. Before/After Comparison

```
BEFORE                              AFTER
────────────────────               ────────────────────
┌────────────────┐                 ┌────────────────┐
│   Controller   │                 │   Controller   │
│  (1200 lines)  │                 │   (200 lines)  │
│                │                 └───────┬────────┘
│  - validation  │                         │
│  - business    │                 ┌───────┼───────┐
│  - persistence │                 │       │       │
│  - response    │                 ▼       ▼       ▼
└────────────────┘            ┌──────┐ ┌──────┐ ┌──────┐
                              │Valid.│ │Serv. │ │Repo. │
                              │(200) │ │(400) │ │(300) │
                              └──────┘ └──────┘ └──────┘
```

### 9. Decision Flow

```
                    ┌─────────────┐
                    │   Request   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Authenticated?│
                    └──────┬───────┘
                          / \
                        /     \
                      YES      NO
                      /          \
                     ▼            ▼
              ┌──────────┐  ┌──────────┐
              │Authorized?│  │  401     │
              └─────┬────┘  │Unauthorized│
                   / \      └──────────┘
                 /     \
               YES      NO
               /          \
              ▼            ▼
         ┌────────┐   ┌────────┐
         │ Process│   │  403   │
         │Request │   │Forbidden│
         └────────┘   └────────┘
```

### 10. Class/Object Relationships

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │     Order       │
├─────────────────┤       ├─────────────────┤
│ - id: UUID      │       │ - id: UUID      │
│ - email: String │       │ - status: Enum  │
│ - name: String  │──────<│ - user_id: UUID │
├─────────────────┤  1:N  ├─────────────────┤
│ + getOrders()   │       │ + getUser()     │
│ + updateEmail() │       │ + addItem()     │
└─────────────────┘       └─────────────────┘
                                   │
                                   │ 1:N
                                   ▼
                          ┌─────────────────┐
                          │   OrderItem     │
                          ├─────────────────┤
                          │ - product_id    │
                          │ - quantity      │
                          │ - price         │
                          └─────────────────┘
```

### 11. Timeline

```
──●──────●──────●──────●──────●──────●──────>
  │      │      │      │      │      │
  │      │      │      │      │      └─ v2.0 Release
  │      │      │      │      └─ Beta Testing
  │      │      │      └─ Feature Complete
  │      │      └─ Alpha Release
  │      └─ Development Start
  └─ Planning Complete
```

### 12. Network Topology

```
                    ┌──────────┐
                    │ Internet │
                    └────┬─────┘
                         │
                    ┌────┴─────┐
                    │ Firewall │
                    └────┬─────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
      ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
      │  Web 1  │   │  Web 2  │   │  Web 3  │
      └────┬────┘   └────┬────┘   └────┬────┘
           │             │             │
           └─────────────┼─────────────┘
                         │
                    ┌────┴────┐
                    │   DB    │
                    │ Primary │
                    └────┬────┘
                         │
                    ┌────┴────┐
                    │   DB    │
                    │ Replica │
                    └─────────┘
```

## Tips for Effective Diagrams

### Do

- Keep it simple - fewer boxes is better
- Use consistent spacing
- Label relationships/arrows
- Include a legend if symbols aren't obvious
- Test rendering in the target platform (GitHub, GitLab, etc.)

### Don't

- Overcrowd with details
- Use colors (won't render in plain text)
- Make boxes too small for labels
- Create diagrams wider than 80 characters
- Forget to explain the diagram in text

### Width Guidelines

```
Optimal:  60-80 characters wide
Maximum:  100 characters (may wrap on some displays)
Mobile:   Keep critical info in first 40 characters
```

### When NOT to Use Diagrams

- Change is straightforward (single function fix)
- Text explanation is clearer
- Diagram would be trivially simple (2 boxes, 1 arrow)
- Time spent drawing > value added

## Quick Copy Templates

### Minimal Box

```
┌────────┐
│  Name  │
└────────┘
```

### Flow Arrow

```
A ───> B
```

### Vertical Flow

```
    ┌───┐
    │ A │
    └─┬─┘
      │
      ▼
    ┌───┐
    │ B │
    └───┘
```

### Branch/Merge

```
         ┌─ Yes ─> B
    A ──<
         └─ No ──> C
```
