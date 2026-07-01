/**
 * Phase 58 — temporary ballot selection helpers (client session only).
 */

export function applySingleSelection(currentIds = [], candidateUuid) {
  const current = [...currentIds];
  if (current.length === 1 && current[0] === candidateUuid) {
    return [];
  }
  return [candidateUuid];
}

export function applyMultiSelection(currentIds = [], candidateUuid, maxVotes = 1) {
  const current = [...currentIds];
  const index = current.indexOf(candidateUuid);
  if (index >= 0) {
    current.splice(index, 1);
    return current;
  }
  if (current.length >= maxVotes) {
    return current;
  }
  current.push(candidateUuid);
  return current;
}

export function applySelection(position, currentIds = [], candidateUuid) {
  const max = position?.max_votes_allowed || 1;
  const isMulti = position?.choice_type === "multi" && max > 1;
  if (isMulti) {
    return applyMultiSelection(currentIds, candidateUuid, max);
  }
  return applySingleSelection(currentIds, candidateUuid);
}

export function skipPositionSelection() {
  return [];
}
