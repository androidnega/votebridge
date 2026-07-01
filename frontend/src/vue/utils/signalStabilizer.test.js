import { describe, expect, it } from "vitest";
import { createSignalStabilizer } from "@/utils/signalStabilizer";

describe("createSignalStabilizer", () => {
  it("requires consecutive samples before turning on", () => {
    const s = createSignalStabilizer({ enterCount: 3, exitCount: 2 });
    expect(s.update(true)).toBe(false);
    expect(s.update(true)).toBe(false);
    expect(s.update(true)).toBe(true);
  });

  it("requires consecutive misses before turning off", () => {
    const s = createSignalStabilizer({ enterCount: 1, exitCount: 3 });
    expect(s.update(true)).toBe(true);
    expect(s.update(false)).toBe(true);
    expect(s.update(false)).toBe(true);
    expect(s.update(false)).toBe(false);
  });
});
