/** Compact relative timestamps for notification rows. */

export function formatRelativeTime(value) {
  if (!value) return "";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  const now = Date.now();
  const diffMs = now - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);

  if (diffSec < 60) return "Just now";

  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m`;

  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h`;

  const diffDay = Math.floor(diffHr / 24);
  if (diffDay === 1) return "Yesterday";
  if (diffDay < 7) return `${diffDay}d`;

  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function notificationDateGroup(value) {
  if (!value) return "Earlier";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "Earlier";

  const startOfToday = new Date();
  startOfToday.setHours(0, 0, 0, 0);

  const startOfYesterday = new Date(startOfToday);
  startOfYesterday.setDate(startOfYesterday.getDate() - 1);

  if (date >= startOfToday) return "Today";
  if (date >= startOfYesterday) return "Yesterday";
  return "Earlier";
}

export function groupNotificationsByDate(items) {
  const order = ["Today", "Yesterday", "Earlier"];
  const buckets = Object.fromEntries(order.map((key) => [key, []]));

  for (const item of items) {
    const key = notificationDateGroup(item.created_at);
    buckets[key].push(item);
  }

  return order
    .filter((key) => buckets[key].length)
    .map((key) => ({ label: key, items: buckets[key] }));
}
