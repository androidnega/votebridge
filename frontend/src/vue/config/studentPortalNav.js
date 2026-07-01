import { dashboardPath } from "@/config/routes";

export const studentPrimaryNav = [
  { name: "Home", to: dashboardPath(), icon: "home", key: "home" },
  { name: "My elections", to: dashboardPath("my-elections"), icon: "elections", key: "elections" },
  { name: "Vote history", to: dashboardPath("vote-history"), icon: "analytics", key: "vote-history" },
  { name: "Profile", to: dashboardPath("profile"), icon: "profile", key: "profile" },
];

export const studentSupportNav = [
  {
    name: "Help centre",
    to: "/auth/info/help",
    icon: "notifications",
    key: "help",
  },
];
