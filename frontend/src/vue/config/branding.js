import institutionLogoImage from "@/assets/images/institution-logo.png";
import loginCampusImage from "@/assets/images/login-campus.webp";

export const branding = {
  systemName: import.meta.env.VITE_SYSTEM_NAME || "VoteBridge",
  tagline:
    import.meta.env.VITE_SYSTEM_TAGLINE || "Secure Campus Election Platform",
  institutionName:
    import.meta.env.VITE_INSTITUTION_NAME || "Takoradi Technical University",
  institutionLogoUrl:
    import.meta.env.VITE_INSTITUTION_LOGO_URL || institutionLogoImage,
  /** Auth left-panel background — override via VITE_AUTH_PANEL_IMAGE_URL */
  authPanelImageUrl:
    import.meta.env.VITE_AUTH_PANEL_IMAGE_URL || loginCampusImage,
  electionOfficeEmail:
    import.meta.env.VITE_ELECTION_OFFICE_EMAIL || "elections@ttu.edu.gh",
  electionOfficePhone:
    import.meta.env.VITE_ELECTION_OFFICE_PHONE || "+233 31 229 3000",
};
