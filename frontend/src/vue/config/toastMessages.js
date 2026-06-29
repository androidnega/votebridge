/** Standardized toast copy — Phase 28 PX. */
export const toastMessages = {
  election: {
    created: "Election created successfully.",
    updated: "Election updated successfully.",
    scheduled: "Election scheduled successfully.",
    opened: "Election opened successfully.",
    paused: "Election paused.",
    resumed: "Election resumed.",
    closed: "Election closed successfully.",
    archived: "Election archived.",
  },
  position: {
    added: "Position added successfully.",
    updated: "Position updated successfully.",
    removed: "Position removed.",
  },
  candidate: {
    added: "Candidate added successfully.",
    updated: "Candidate updated successfully.",
    approved: "Candidate approved.",
    rejected: "Candidate rejected.",
    removed: "Candidate removed.",
  },
  eligibility: {
    added: "Voter added to the roll.",
    bulkAdded: (count) => `${count} voters added to the roll.`,
    removed: "Voter removed from the roll.",
  },
  results: {
    certified: "Results certified successfully.",
    published: "Results published successfully.",
    archived: "Results archived.",
  },
  device: {
    renamed: "Device renamed successfully.",
    revoked: "Trusted device revoked.",
    assigned: "Device marked as university managed.",
  },
  biometric: {
    enrolled: "Biometric enrollment completed.",
    verified: "Biometric verification completed.",
  },
  profile: {
    updated: "Profile updated successfully.",
  },
  settings: {
    saved: "Settings saved successfully.",
  },
  generic: {
    saved: "Changes saved successfully.",
    error: "Something went wrong. Please try again.",
  },
};
