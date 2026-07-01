# Phase 60 — Student Dashboard Active Elections Redesign

UI-only refresh of the **Active Elections** section on the student dashboard. No backend or voting logic changes.

## Components

| File | Role |
|------|------|
| `StudentActiveElectionList.vue` | Section grid (1 col mobile, 2 col desktop), empty state |
| `StudentActiveElectionCard.vue` | Premium election card with status, countdown, CTA |
| `studentActiveElectionDisplay.js` | Card labels, actions, countdown formatting |
| `FaIcon.vue` | Font Awesome 6 wrapper |

## Card contents

- Header: ballot icon, title, election type, status badge (OPEN / PAUSED / …)
- Body: closing date, position preview (+N more)
- Countdown pill: “Voting ends in …”
- Student status chip: Not Yet Started, Ready to Vote, Ballot In Progress, Vote Submitted
- Single dynamic CTA: Vote Now / Continue Ballot / View Confirmation
- Footer: eligibility, channels (Web · USSD heuristic), SVT protection
- Last updated relative time

## Data source

Existing `useStudentVotePortal` + `dashboardApi.getStudentElectionDetail` — enriched card model only on the frontend.

Dashboard uses `portalElectionCards` (all eligible active elections, including submitted ballots).

## Icons

Font Awesome 6 loaded via CDN in `index.html`.
