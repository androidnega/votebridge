export function unwrapPaginatedList(response) {
  const payload = response.data;
  if (payload && typeof payload === "object") {
    const items = Array.isArray(payload.data)
      ? payload.data
      : Array.isArray(payload.results)
        ? payload.results
        : [];
    return {
      items,
      count: payload.count ?? items.length,
      next: payload.next ?? null,
      previous: payload.previous ?? null,
    };
  }
  return { items: [], count: 0, next: null, previous: null };
}
