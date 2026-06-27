export function required(message = "This field is required.") {
  return (value) => {
    if (value === null || value === undefined || String(value).trim() === "") {
      return message;
    }
    return null;
  };
}

export function email(message = "Enter a valid email address.") {
  return (value) => {
    if (!value) return null;
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(String(value).trim()) ? null : message;
  };
}

export function minLength(min, message) {
  return (value) => {
    if (!value) return null;
    return String(value).length >= min
      ? null
      : message || `Must be at least ${min} characters.`;
  };
}

export function otpCode(message = "Enter a valid verification code.") {
  return (value) => {
    const code = String(value || "").trim();
    if (code.length < 4 || code.length > 10) return message;
    return /^[0-9A-Za-z]+$/.test(code) ? null : message;
  };
}

export function validateFields(values, schema) {
  const errors = {};
  let valid = true;

  for (const [field, rules] of Object.entries(schema)) {
    for (const rule of rules) {
      const error = rule(values[field], values);
      if (error) {
        errors[field] = error;
        valid = false;
        break;
      }
    }
  }

  return { valid, errors };
}
