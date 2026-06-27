import { ref } from "vue";

const toasts = ref([]);
const MAX_TOASTS = 3;
let nextId = 1;

export function useToast() {
  function show(message, options = {}) {
    const id = nextId++;
    const toast = {
      id,
      message,
      variant: options.variant || "info",
      duration: options.duration ?? 4000,
    };

    toasts.value = [...toasts.value, toast].slice(-MAX_TOASTS);

    if (toast.duration > 0) {
      window.setTimeout(() => dismiss(id), toast.duration);
    }

    return id;
  }

  function dismiss(id) {
    toasts.value = toasts.value.filter((toast) => toast.id !== id);
  }

  return {
    toasts,
    show,
    success: (message, options) => show(message, { ...options, variant: "success" }),
    error: (message, options) => show(message, { ...options, variant: "error" }),
    warning: (message, options) => show(message, { ...options, variant: "warning" }),
    info: (message, options) => show(message, { ...options, variant: "info" }),
    dismiss,
  };
}
