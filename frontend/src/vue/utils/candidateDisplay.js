/** Parse seeded / structured manifesto lines for student-facing candidate cards. */

export function parseCandidateMeta(manifesto = "", department = "") {
  const lines = String(manifesto || "").split("\n");
  let faculty = "";
  let dept = department || "";
  let indexNumber = "";

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("Faculty:")) faculty = trimmed.replace(/^Faculty:\s*/i, "");
    if (trimmed.startsWith("Department:")) dept = trimmed.replace(/^Department:\s*/i, "");
    if (trimmed.startsWith("Index:")) indexNumber = trimmed.replace(/^Index:\s*/i, "");
  }

  const manifestoSummary = lines
    .filter((line) => !/^(Faculty|Department|Index):/i.test(line.trim()))
    .join(" ")
    .trim()
    .slice(0, 220);

  return { faculty, department: dept, indexNumber, manifestoSummary };
}

export function groupCandidatesByPosition(candidates = []) {
  const map = new Map();
  for (const candidate of candidates) {
    const key = candidate.position_title || candidate.position_uuid || "Other";
    if (!map.has(key)) {
      map.set(key, {
        positionTitle: key,
        positionUuid: candidate.position_uuid,
        candidates: [],
      });
    }
    map.get(key).candidates.push(candidate);
  }
  return Array.from(map.values());
}
