import Alpine from "alpinejs";

window.Alpine = Alpine;

Alpine.data("votebridgeApp", () => ({
  sidebarOpen: false,

  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  },

  closeSidebar() {
    this.sidebarOpen = false;
  },
}));

Alpine.start();
