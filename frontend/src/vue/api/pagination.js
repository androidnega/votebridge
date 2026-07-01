function extractPaginatedItems(payload) {
  if (Array.isArray(payload.data)) {
    return payload.data;
  }
  if (Array.isArray(payload.results)) {
    return payload.results;
  }
  if (
    payload.results &&
    typeof payload.results === "object" &&
    Array.isArray(payload.results.data)
  ) {
    return payload.results.data;
  }
  return [];
}

export function unwrapPaginatedList(response) {
  const payload = response.data;
  if (payload && typeof payload === "object") {
    const items = extractPaginatedItems(payload);
    return {
      items,
      count: payload.count ?? items.length,
      next: payload.next ?? null,
      previous: payload.previous ?? null,
    };
  }
  return { items: [], count: 0, next: null, previous: null };
}
