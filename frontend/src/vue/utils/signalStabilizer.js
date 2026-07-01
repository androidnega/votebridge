/**
 * Debounce boolean signals to prevent UI flicker (face detected / aligned).
 */
export function createSignalStabilizer({ enterCount = 3, exitCount = 6 } = {}) {
  let consecutiveOn = 0;
  let consecutiveOff = 0;
  let stable = false;

  function reset() {
    consecutiveOn = 0;
    consecutiveOff = 0;
    stable = false;
  }

  function update(sample) {
    if (sample) {
      consecutiveOn += 1;
      consecutiveOff = 0;
      if (!stable && consecutiveOn >= enterCount) {
        stable = true;
      }
    } else {
      consecutiveOff += 1;
      consecutiveOn = 0;
      if (stable && consecutiveOff >= exitCount) {
        stable = false;
      }
    }
    return stable;
  }

  return {
    update,
    reset,
    get stable() {
      return stable;
    },
  };
}
