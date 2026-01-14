export function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export function toIsoString(localValue: string): string {
  const date = new Date(localValue);
  return date.toISOString();
}
