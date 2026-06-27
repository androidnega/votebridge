import { ref } from "vue";
import { systemControlApi } from "@/api/systemControl";
import { extractApiError } from "@/api/helpers";
import { useSystemControlStore } from "@/stores/systemControl";
import { useToast } from "@/composables/useToast";

export function useStepUp() {
  const store = useSystemControlStore();
  const toast = useToast();
  const modalOpen = ref(false);
  const challengeId = ref("");
  const otpCode = ref("");
  const verifying = ref(false);
  const requesting = ref(false);
  const pendingAction = ref(null);

  async function requestChallenge() {
    requesting.value = true;
    try {
      const data = await systemControlApi.requestStepUp();
      challengeId.value = data.challenge_id;
      toast.success("Verification code sent.");
      return data;
    } catch (error) {
      toast.error(extractApiError(error));
      throw error;
    } finally {
      requesting.value = false;
    }
  }

  async function verifyAndContinue() {
    verifying.value = true;
    try {
      const data = await systemControlApi.verifyStepUp({
        challenge_id: challengeId.value,
        code: otpCode.value,
      });
      store.setStepUpToken(data.step_up_token, data.expires_in_seconds);
      modalOpen.value = false;
      otpCode.value = "";
      toast.success("Identity verified.");
      if (pendingAction.value) {
        const action = pendingAction.value;
        pendingAction.value = null;
        await action();
      }
      return data;
    } catch (error) {
      toast.error(extractApiError(error));
      throw error;
    } finally {
      verifying.value = false;
    }
  }

  function requireStepUp(action) {
    if (store.hasValidStepUp) {
      return action();
    }
    pendingAction.value = action;
    modalOpen.value = true;
    return requestChallenge();
  }

  function openStepUpModal(action) {
    pendingAction.value = action || null;
    modalOpen.value = true;
    if (!challengeId.value) requestChallenge();
  }

  return {
    modalOpen,
    challengeId,
    otpCode,
    verifying,
    requesting,
    requestChallenge,
    verifyAndContinue,
    requireStepUp,
    openStepUpModal,
  };
}
