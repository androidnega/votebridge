const REMEMBER_KEY = "vb_remember_identity";

export function getRememberedIdentifier() {
  return localStorage.getItem(REMEMBER_KEY) || "";
}

export function setRememberedIdentifier(identity) {
  if (identity) {
    localStorage.setItem(REMEMBER_KEY, identity.trim());
  } else {
    localStorage.removeItem(REMEMBER_KEY);
  }
}
