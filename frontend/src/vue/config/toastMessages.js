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
    deleted: "Election deleted.",
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
    imported: (summary) => {
      const parts = [];
      if (summary.imported) parts.push(`${summary.imported} added`);
      if (summary.updated) parts.push(`${summary.updated} updated`);
      if (summary.not_found_count) parts.push(`${summary.not_found_count} not found`);
      return parts.length ? `Import complete: ${parts.join(", ")}.` : "Import complete.";
    },
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
    reset: "Biometric profile removed. You will enroll again on next sign-in.",
  },
  profile: {
    updated: "Profile updated successfully.",
  },
  settings: {
    saved: "Settings saved successfully.",
  },
  system: {
    dataReset: "Operational data reset completed.",
  },
  generic: {
    saved: "Changes saved successfully.",
    error: "Something went wrong. Please try again.",
  },
};
