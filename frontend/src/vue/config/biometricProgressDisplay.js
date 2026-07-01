import {
  normalizeVerifyChallengeType,
  verifyChallengeLabel,
} from "@/services/biometricChallengeManager";

/**
 * Simplified step-based progress for verification and enrollment flows.
 * Shows only completed steps plus the current active step.
 */

function livenessComplete(completedSteps, mode) {
  if (mode === "enrollment") {
    return (
      completedSteps.has("blink") &&
      completedSteps.has("turn_left") &&
      completedSteps.has("turn_right")
    );
  }
  return completedSteps.has("ready");
}

export function buildProgressSteps({
  completedSteps,
  challengeType = "",
  mode = "verify",
  framesCaptured = 0,
  framesRequired = 3,
}) {
  const steps =
    mode === "enrollment"
      ? [
          { id: "face", label: "Face detected" },
          { id: "liveness", label: "Blink & head movement" },
          { id: "capture", label: "Capturing verification frames" },
        ]
      : [
          { id: "face", label: "Face detected" },
          { id: "challenge", label: verifyChallengeLabel(challengeType) },
          { id: "capture", label: "Capturing verification frames" },
        ];

  const resolved = steps.map((step, index) => {
    let done = false;
    let active = false;

    if (step.id === "face") {
      done = completedSteps.has("face");
      active = !done;
    } else if (step.id === "liveness") {
      done = livenessComplete(completedSteps, mode);
      active = completedSteps.has("face") && !done;
    } else if (step.id === "challenge") {
      done = completedSteps.has("ready");
      active = completedSteps.has("face") && !done;
    } else if (step.id === "capture") {
      done = framesCaptured >= framesRequired;
      const prior =
        mode === "enrollment"
          ? livenessComplete(completedSteps, mode)
          : completedSteps.has("ready");
      active = prior && !done;
    }

    return {
      ...step,
      index: index + 1,
      total: steps.length,
      done,
      active,
    };
  });

  const current = resolved.find((s) => s.active) || resolved[resolved.length - 1];
  const completed = resolved.filter((s) => s.done);

  return { steps: resolved, current, completed, total: steps.length };
}
