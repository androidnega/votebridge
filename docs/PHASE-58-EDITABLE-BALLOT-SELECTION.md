# Phase 58 — Editable Ballot Selection Experience

## Summary

Students can change candidate selections freely during an active ballot session. All choices remain **temporary** (browser session storage + Pinia) until **Submit Ballot**. No votes, SVT consumption, or audit records occur until final submission.

## Selection behaviour

- Each position is a **single-selection group** (radio-style).
- Tapping another candidate **replaces** the previous choice immediately.
- Tapping the same candidate again clears the choice (optional skip).
- No page refresh required — state persists in session storage.

## Temporary state

| Storage | Key |
|---------|-----|
| Selections | `vb_ballot_selections_{electionUuid}` |
| Wizard step | `vb_ballot_step_{electionUuid}` |
| SVT session | `vb_svt_token_{electionUuid}`, `vb_svt_session_{electionUuid}` |

**Not written until submit:** Vote table, SVT consumption, audit logs.

## Navigation

- Next / Previous between positions
- Skip position (clears draft choice)
- Continue later (persists draft, returns to dashboard)
- Review → Edit any position → Submit when ready

## Final submission

`VoteService.submit_ballot()` — single transaction, consumes SVT, locks ballot.

## Files modified

### Frontend
- `utils/ballotSelection.js` — pure selection replace logic
- `utils/ballotSelection.test.js`
- `stores/voting.js` — `selectCandidate`, `skipPosition`, `continueLater`
- `components/voting/VoteCandidatePicker.vue` — radiogroup, skip, review label
- `components/voting/BallotReviewStep.vue`
- `views/elections/VotingWizardView.vue` — resume, continue later

### Backend
- `apps/security/tests/test_phase58_editable_ballot.py`

## Services reused

- `VoteService.submit_ballot()` (unchanged integrity rules)
- `SVTService` (session only until submit)
- `BallotService.get_ballot()`

## Verification checklist

| Requirement | Status |
|-------------|--------|
| Change selections multiple times | ✓ |
| One candidate per position | ✓ |
| Auto-replace previous selection | ✓ |
| No refresh required | ✓ |
| Nothing saved until submit | ✓ |
| Lock only after successful submit | ✓ |

## Tests

```bash
# Frontend
cd frontend && npm test -- ballotSelection

# Backend
cd backend && python manage.py test apps.security.tests.test_phase58_editable_ballot
```
