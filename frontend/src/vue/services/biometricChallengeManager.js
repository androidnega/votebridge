/** Liveness challenge rules — verification is blink-only (v1.0). */

export const VERIFY_CHALLENGE_TYPES = ["blink_once", "blink_twice"];

const LEGACY_TURN_CHALLENGES = new Set([
  "turn_left",
  "turn_right",
  "turn_left_then_right",
  "blink_then_left",
  "blink_then_right",
]);

export function isValidVerifyChallenge(challenge) {
  return Boolean(
    challenge?.challenge_id && VERIFY_CHALLENGE_TYPES.includes(challenge.challenge_type)
  );
}

/** Map legacy turn challenges to blink-only for verification UX. */
export function normalizeVerifyChallengeType(type) {
  if (type === "blink_twice") return "blink_twice";
  if (LEGACY_TURN_CHALLENGES.has(type) || type === "blink_once") return "blink_once";
  return "blink_once";
}

export function verifyChallengeLabel(type) {
  return normalizeVerifyChallengeType(type) === "blink_twice" ? "Blink twice" : "Blink once";
}

export function verifyChallengeInstruction(type) {
  return normalizeVerifyChallengeType(type) === "blink_twice"
    ? "Blink twice to continue"
    : "Blink once to continue";
}

export function challengeNeeds(type, action, mode = "verify") {
  if (mode === "enrollment" && type === "enrollment_sequence") {
    if (action === "blink") return true;
    if (action === "turn_left") return true;
    if (action === "turn_right") return true;
    return false;
  }

  if (mode === "verify" && action === "blink") {
    const normalized = normalizeVerifyChallengeType(type);
    return normalized === "blink_once" || normalized === "blink_twice";
  }

  if (mode === "verify") return false;

  if (action === "blink") return type.includes("blink");
  if (action === "turn_left") return type.includes("turn_left");
  if (action === "turn_right") return type.includes("turn_right");
  return false;
}

export function getRequiredSteps(type, mode = "verify") {
  const steps = ["face"];

  if (mode === "enrollment" && type === "enrollment_sequence") {
    return [...steps, "blink", "turn_left", "turn_right"];
  }

  if (challengeNeeds(type, "blink", mode)) steps.push("blink");
  if (normalizeVerifyChallengeType(type) === "blink_twice") steps.push("blink2");

  return steps;
}

export function nextActionHint(type, completedSteps, warning, mode = "verify") {
  if (warning) return warning;

  if (challengeNeeds(type, "blink", mode) && !completedSteps.has("blink")) {
    return "Blink now";
  }
  if (normalizeVerifyChallengeType(type) === "blink_twice" && completedSteps.has("blink") && !completedSteps.has("blink2")) {
    return "Blink once more";
  }
  if (mode === "enrollment") {
    if (challengeNeeds(type, "turn_left", mode) && !completedSteps.has("turn_left")) {
      return "Turn head left";
    }
    if (challengeNeeds(type, "turn_right", mode) && !completedSteps.has("turn_right")) {
      return "Turn head right";
    }
  }

  const required = getRequiredSteps(type, mode);
  if (required.every((s) => completedSteps.has(s))) {
    return mode === "verify" ? "Hold still — capturing verification frames" : "Hold still — capture frames";
  }
  if (!completedSteps.has("face")) return "Position your face in the frame";
  return "Hold steady";
}

export function isChallengeComplete(type, completedSteps, mode = "verify") {
  return getRequiredSteps(type, mode).every((s) => completedSteps.has(s));
}
