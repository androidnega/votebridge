# VoteBridge — Flowcharts

Visual step-by-step flows for the main processes in VoteBridge. Render Mermaid diagrams in GitHub or VS Code.

**Reading guide:**
- **§1–6** — Core prototype flows (login, voting, election lifecycle, results)
- **§7** — USSD channel (optional alternate path)
- **§8–9** — Advanced governance and realtime internals

---

## 1. User login flow

```mermaid
flowchart TD
    A[User opens VoteBridge] --> B{Already logged in?}
    B -->|Yes| C[Go to dashboard]
    B -->|No| D[Enter your index number]
    D --> E{API resolves account}
    E -->|Student/Candidate| F[Send OTP]
    E -->|Privileged| G[Staff access → email/username + password]
    G --> H[Send OTP]
    F --> K[Enter OTP]
    H --> K
    K --> L{OTP valid?}
    L -->|No| D
    L -->|Yes| M{Biometric required?}
    M -->|Staff + policy| N[Face verification]
    M -->|No| C
    N --> C
```

**Layman summary:** Everyone uses the **same sign-in page** with student-first copy (“Enter your index number”). Staff use a subtle **Staff access** link, then email/username and password, then OTP.

---

## 2. Student web voting flow (full)

```mermaid
flowchart TD
    A[Student logs in] --> B[Student Dashboard]
    B --> C[Clicks Vote Now on election]
    C --> D[System checks eligibility]
    D -->|Not eligible| E[Show error]
    D -->|Eligible| F{SVT already issued?}
    F -->|No| G[Send voting code via SMS]
    F -->|Yes| H[Go to verify screen]
    G --> H
    H --> I[Student enters SVT code]
    I --> J{Code valid?}
    J -->|No| H
    J -->|Yes| K[Ballot session created]
    K --> L[Presence Capture page]
    L --> M[Camera detects face]
    M --> N[Student takes photo]
    N --> O[Photo saved to server]
    O --> P[Open official ballot]
    P --> Q[Vote position by position]
    Q --> R[Review ballot]
    R --> S[Submit ballot]
    S --> T[Votes recorded + SVT consumed]
    T --> U[Strongroom seal created]
    U --> V[Show confirmation receipt]
```

**Layman summary:** Get code on phone → enter code → quick selfie for integrity → pick candidates → submit → get receipt.

---

## 3. SVT (Secure Voting Token) lifecycle

```mermaid
stateDiagram-v2
    [*] --> Issued: SMS sent to student
    Issued --> Validated: Student enters correct code
    Issued --> Expired: Time limit reached
    Issued --> Revoked: Admin revokes
    Validated --> Used: Ballot submitted
    Validated --> Expired: Session timeout
    Used --> [*]
    Expired --> [*]
    Revoked --> [*]
```

| Status | Meaning |
|--------|---------|
| **Issued** | Code sent; not yet entered |
| **Validated** | Code accepted; ballot session active |
| **Used** | Student finished voting |
| **Expired** | Code or session timed out |
| **Revoked** | Admin cancelled the token |

---

## 4. Election lifecycle (admin view)

```mermaid
flowchart LR
    A[Draft] --> B[Scheduled]
    B --> C[Open]
    C --> D[Paused]
    D --> C
    C --> E[Closed]
    E --> F[Results generated]
    F --> G[Certified]
    G --> H[Published]
    H --> I[Archived]
```

```mermaid
flowchart TD
    subgraph Setup
        S1[Create election]
        S2[Add positions]
        S3[Add candidates]
        S4[Import eligibility]
        S5[Readiness check]
    end

    subgraph Voting
        V1[Open election]
        V2[Students vote via Web/USSD]
        V3[Monitor election + live trend]
    end

    subgraph Results
        R1[Close election]
        R2[Auto-generate results]
        R3[Super Admin certifies]
        R4[Strongroom seal]
        R5[Publish to students]
        R6[Archive]
    end

    S1 --> S2 --> S3 --> S4 --> S5 --> V1
    V1 --> V2 --> V3 --> R1
    R1 --> R2 --> R3 --> R4 --> R5 --> R6
```

---

## 5. Ballot submission (technical)

```mermaid
flowchart TD
    A[Student clicks Submit] --> B[Frontend sends selections + SVT]
    B --> C[Django API receives request]
    C --> D[VoteService validates session]
    D --> E{Presence captured?}
    E -->|Web + missing| F[Reject: presence_required]
    E -->|OK| G[For each position selection]
    G --> H[Create Vote row with hash]
    H --> I[Log vote_cast audit]
    I --> J[Consume SVT - mark used]
    J --> K[Create BallotSeal]
    K --> L[Broadcast WebSocket event]
    L --> M[Return confirmation reference]
```

---

## 6. Results publication flow

```mermaid
flowchart TD
    A[Election closed] --> B[System aggregates votes]
    B --> C[Build standings JSON]
    C --> D[Run integrity checks]
    D --> E{Integrity OK?}
    E -->|Issues| F[Flag for review]
    E -->|OK| G[Status: pending certification]
    G --> H[Super Admin reviews]
    H --> I[Certify results]
    I --> J[Create ElectionSeal]
    J --> K[Publish results]
    K --> L[Students see winners]
    L --> M[Archive when done]
```

**While election is OPEN:** steps K and L do **not** happen for live rankings — students never see interim winners.

---

## 7. USSD voting flow (simplified)

```mermaid
flowchart TD
    A[Student dials USSD code] --> B[Arkesel sends request to VoteBridge]
    B --> C[USSD session created]
    C --> D[Student enters PIN]
    D --> E[Select election / position]
    E --> F[Select candidate by number]
    F --> G[Confirm vote]
    G --> H[Vote recorded same as web]
    H --> I[SMS confirmation optional]
```

**Note:** USSD does **not** use the web presence photo step.

---

## 8. Strongroom vault access (advanced governance)

Not part of the primary prototype navigation. Committee nomination UI is demoted; vault access is Super Admin governance.

```mermaid
flowchart TD
    A[Admin nominates committee] --> B[Super Admin approves]
    B --> C[Vault access request]
    C --> D[Super Admin reviews]
    D --> E[Vault session opened]
    E --> F[Custodians authenticate]
    F --> G{Biometric step-up?}
    G -->|Yes| H[Face verify]
    G -->|No| I[Access vault terminal]
    H --> I
    I --> J[View seals / evidence]
    J --> K[Session closed]
```

---

## 9. Real-time update flow

```mermaid
sequenceDiagram
    participant Student
    participant Vue as Vue Frontend
    participant API as Django API
    participant PG as PostgreSQL
    participant Redis
    participant WS as WebSocket
    participant Admin as Admin Dashboard

    Student->>Vue: Submit ballot
    Vue->>API: POST /voting/.../submit/
    API->>PG: Save votes (transaction)
    API->>Redis: Publish event
    Redis->>WS: Push to groups
    WS->>Admin: ballot.submitted (sanitized)
    Note over WS,Admin: Strong Room / Operations feeds are Super Admin only
    API->>Vue: Confirmation response
```

---

## Related documents

- [ELECTION-LIFECYCLE.md](./ELECTION-LIFECYCLE.md) — narrative walkthrough
- [PRIVILEGES-AND-ROLES.md](./PRIVILEGES-AND-ROLES.md) — who can run each step
- [SYSTEM-ARCHITECTURE.md](./SYSTEM-ARCHITECTURE.md) — technical architecture
