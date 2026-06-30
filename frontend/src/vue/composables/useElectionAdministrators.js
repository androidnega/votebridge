import { computed, ref } from "vue";
import { usersApi } from "@/api/users";

export function useElectionAdministrators() {
  const administrators = ref([]);
  const loading = ref(false);
  const actionLoading = ref(false);
  const error = ref(null);
  const totalCount = ref(0);

  async function loadAdministrators() {
    loading.value = true;
    error.value = null;
    try {
      const result = await usersApi.list({ role: "admin", page_size: 50 });
      administrators.value = result.items || [];
      totalCount.value = result.count ?? administrators.value.length;
    } catch (err) {
      error.value = err?.message || "Could not load election administrators.";
    } finally {
      loading.value = false;
    }
  }

  async function createAdministrator(payload) {
    actionLoading.value = true;
    error.value = null;
    try {
      const user = await usersApi.create({ ...payload, role_name: "admin" });
      await loadAdministrators();
      return user;
    } catch (err) {
      error.value = err?.message || "Could not create election administrator.";
      throw err;
    } finally {
      actionLoading.value = false;
    }
  }

  async function setActiveStatus(uuid, isActive) {
    actionLoading.value = true;
    error.value = null;
    try {
      if (isActive) {
        await usersApi.activate(uuid);
      } else {
        await usersApi.deactivate(uuid);
      }
      await loadAdministrators();
    } catch (err) {
      error.value = err?.message || "Could not update administrator status.";
      throw err;
    } finally {
      actionLoading.value = false;
    }
  }

  async function resetMfa(uuid) {
    actionLoading.value = true;
    error.value = null;
    try {
      await usersApi.unverify(uuid);
      await loadAdministrators();
    } catch (err) {
      error.value = err?.message || "Could not reset administrator verification.";
      throw err;
    } finally {
      actionLoading.value = false;
    }
  }

  const activeCount = computed(() => administrators.value.filter((user) => user.is_active).length);

  return {
    administrators,
    loading,
    actionLoading,
    error,
    totalCount,
    activeCount,
    loadAdministrators,
    createAdministrator,
    setActiveStatus,
    resetMfa,
  };
}
