import { describe, expect, it } from "vitest";
import {
  formatSvtTokenInput,
  isValidSvtToken,
  normalizeSvtToken,
} from "@/utils/svtToken";

describe("svtToken", () => {
  it("formats partial input while typing", () => {
    expect(formatSvtTokenInput("vb7f")).toBe("VB-7F");
    expect(formatSvtTokenInput("vb7f4k92xm")).toBe("VB-7F4K-92XM");
  });

  it("normalizes pasted codes with or without prefix", () => {
    expect(normalizeSvtToken("SVT-9K4M-X72P")).toBe("VB-9K4M-X72P");
    expect(normalizeSvtToken("vb7f4k92xm")).toBe("VB-7F4K-92XM");
  });

  it("validates complete formatted tokens", () => {
    expect(isValidSvtToken("VB-7F4K-92XM")).toBe(true);
    expect(isValidSvtToken("VB-DEMO-0001")).toBe(true);
    expect(isValidSvtToken("123456")).toBe(false);
  });

  it("preserves demo pool formatting", () => {
    expect(formatSvtTokenInput("vb-demo-0007")).toBe("VB-DEMO-0007");
    expect(normalizeSvtToken("VB-DEMO-0010")).toBe("VB-DEMO-0010");
  });
});
