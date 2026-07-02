/** Parse seeded / structured manifesto lines for student-facing candidate cards. */

/** Recommended uploads: 512×512 px (1:1), JPG/WebP, plain light background, head + shoulders centered. */

const CANDIDATE_PHOTOS = {
  // TTU SRC General Elections 2026
  "Kofi Boateng": "/candidates/male-1.png",
  "Kwame Ansah": "/candidates/male-2.png",
  "Ama Serwaa": "/candidates/female-1.png",
  "Efua Adjei": "/candidates/female-2.png",
  "Daniel Owusu": "/candidates/male-3.png",
  "Selina Agyeman": "/candidates/female-3.png",
  "Adwoa Mensah": "/candidates/female-4.png",
  "Isaac Tetteh": "/candidates/male-4.png",
  "Rebecca Antwi": "/candidates/female-5.png",
  "Akosua Frimpong": "/candidates/female-6.png",
  "Gifty Asare": "/candidates/female-7.png",
  "Naana Dankwa": "/candidates/female-1.png",
  "Prince Boakye": "/candidates/male-1.png",
  "Samuel Osei": "/candidates/male-2.png",
  "Michael Addo": "/candidates/male-3.png",
  "Abena Boateng": "/candidates/female-2.png",
  "Kojo Sarpong": "/candidates/male-4.png",
  "Ama Kwarteng": "/candidates/female-3.png",
  "Kwesi Appiah": "/candidates/male-1.png",
  "Yaw Darko": "/candidates/male-2.png",
  "Richard Nyame": "/candidates/male-3.png",
  // FASSA Elections 2025
  "Nana Agyei": "/candidates/male-4.png",
  "Abigail Ofori": "/candidates/female-4.png",
  "Kweku Annan": "/candidates/male-1.png",
  "Linda Akoto": "/candidates/female-5.png",
  "George Mensah": "/candidates/male-2.png",
  "Esi Mensah": "/candidates/female-6.png",
  "Fiifi Amoah": "/candidates/male-3.png",
  "Joel Ampofo": "/candidates/male-4.png",
  "Ama Osei": "/candidates/female-7.png",
  "Yaa Serwaa": "/candidates/female-1.png",
  "Akosua Danso": "/candidates/female-2.png",
  "Kwabena Owusu": "/candidates/male-1.png",
};

const META_LINE =
  /^(Faculty|Department|Index|Academic Level):/i;

export function getCandidatePhotoUrl(candidate = {}) {
  if (candidate.image_url) {
    const url = candidate.image_url;
    if (url.startsWith("http://localhost:8000")) {
      return url.replace("http://localhost:8000", "");
    }
    if (url.startsWith("http://127.0.0.1:8000")) {
      return url.replace("http://127.0.0.1:8000", "");
    }
    return url;
  }
  return CANDIDATE_PHOTOS[candidate.full_name] || null;
}

export function parseCandidateMeta(manifesto = "", department = "") {
  const lines = String(manifesto || "").split("\n");
  let faculty = "";
  let dept = department || "";
  let academicLevel = "";
  let indexNumber = "";

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("Faculty:")) faculty = trimmed.replace(/^Faculty:\s*/i, "");
    if (trimmed.startsWith("Department:")) dept = trimmed.replace(/^Department:\s*/i, "");
    if (trimmed.startsWith("Index:")) indexNumber = trimmed.replace(/^Index:\s*/i, "");
    if (/^Academic Level:/i.test(trimmed)) {
      academicLevel = trimmed.replace(/^Academic Level:\s*/i, "");
    }
  }

  const manifestoText = lines
    .filter((line) => !META_LINE.test(line.trim()))
    .join("\n")
    .trim();

  const manifestoSummary = manifestoText.replace(/\s+/g, " ").trim();

  return {
    faculty,
    department: dept,
    academicLevel,
    indexNumber,
    manifestoText,
    manifestoSummary,
  };
}

export function candidateNeedsReadMore(meta = {}, limit = 88) {
  return (meta.manifestoSummary || "").length > limit;
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
