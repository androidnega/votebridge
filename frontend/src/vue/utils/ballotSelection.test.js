import { describe, expect, it } from "vitest";
import { applyMultiSelection, applySingleSelection } from "./ballotSelection";

describe("applySingleSelection", () => {
  it("selects one candidate", () => {
    expect(applySingleSelection([], "a")).toEqual(["a"]);
  });

  it("replaces the previous selection", () => {
    expect(applySingleSelection(["a"], "b")).toEqual(["b"]);
  });

  it("clears when the same candidate is clicked again", () => {
    expect(applySingleSelection(["b"], "b")).toEqual([]);
  });
});

describe("applyMultiSelection", () => {
  it("adds up to max votes", () => {
    expect(applyMultiSelection([], "a", 2)).toEqual(["a"]);
    expect(applyMultiSelection(["a"], "b", 2)).toEqual(["a", "b"]);
    expect(applyMultiSelection(["a"], "c", 2)).toEqual(["a"]);
  });
});
