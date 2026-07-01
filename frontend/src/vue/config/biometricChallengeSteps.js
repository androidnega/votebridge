/** Maps backend challenge_type values to UX progress steps (display only). */

const STEP = {
  camera: { id: "camera", label: "Camera ready" },
  face: { id: "face", label: "Face detected" },
  blink: { id: "blink", label: "Blink detected" },
  blink2: { id: "blink2", label: "Second blink" },
  turn_left: { id: "turn_left", label: "Turn left" },
  turn_right: { id: "turn_right", label: "Turn right" },
  ready: { id: "ready", label: "Challenge complete" },
};

const CHALLENGE_STEP_MAP = {
  blink_once: [STEP.camera, STEP.face, STEP.blink, STEP.ready],
  blink_twice: [STEP.camera, STEP.face, STEP.blink, STEP.blink2, STEP.ready],
  turn_left: [STEP.camera, STEP.face, STEP.turn_left, STEP.ready],
  turn_right: [STEP.camera, STEP.face, STEP.turn_right, STEP.ready],
  turn_left_then_right: [STEP.camera, STEP.face, STEP.turn_left, STEP.turn_right, STEP.ready],
  blink_then_left: [STEP.camera, STEP.face, STEP.blink, STEP.turn_left, STEP.ready],
  blink_then_right: [STEP.camera, STEP.face, STEP.blink, STEP.turn_right, STEP.ready],
};

export function stepsForChallenge(challengeType) {
  return CHALLENGE_STEP_MAP[challengeType] || [STEP.camera, STEP.face, STEP.ready];
}

const CHALLENGE_ACTION_LABELS = {
  blink_once: "Blink once",
  blink_twice: "Blink twice",
  turn_left: "Turn head left",
  turn_right: "Turn head right",
  turn_left_then_right: "Turn left, then right",
  blink_then_left: "Blink, then turn left",
  blink_then_right: "Blink, then turn right",
  enrollment_sequence: "Blink & head movement",
};

export function challengeActionLabel(challengeType) {
  return CHALLENGE_ACTION_LABELS[challengeType] || "Complete challenge";
}

export { STEP };
