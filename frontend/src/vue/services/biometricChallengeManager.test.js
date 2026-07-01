import { describe, expect, it } from "vitest";
import {
  challengeNeeds,
  getRequiredSteps,
  isChallengeComplete,
} from "@/services/biometricChallengeManager";

describe("biometricChallengeManager", () => {
  it("verification supports blink-only challenges", () => {
    expect(challengeNeeds("blink_once", "blink", "verify")).toBe(true);
    expect(challengeNeeds("blink_twice", "blink", "verify")).toBe(true);
    expect(challengeNeeds("blink_once", "turn_left", "verify")).toBe(false);
    expect(challengeNeeds("turn_left", "turn_left", "verify")).toBe(false);
  });

  it("blink_twice requires two blink steps", () => {
    const steps = new Set(["face", "blink"]);
    expect(isChallengeComplete("blink_twice", steps, "verify")).toBe(false);
    steps.add("blink2");
    expect(isChallengeComplete("blink_twice", steps, "verify")).toBe(true);
  });

  it("enrollment still requires head turns", () => {
    const required = getRequiredSteps("enrollment_sequence", "enrollment");
    expect(required).toContain("turn_left");
    expect(required).toContain("turn_right");
  });
});
