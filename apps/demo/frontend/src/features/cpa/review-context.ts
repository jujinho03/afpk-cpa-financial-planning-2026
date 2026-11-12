// Exact canonical evidence context, not a cryptographic authenticity proof.
function canonical(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonical)
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).filter(([, v]) => v !== undefined).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => [k, canonical(v)]))
  }
  return value
}

export function evidenceContext(value: unknown): string {
  return JSON.stringify(canonical(value))
}

export function humanReviewIsCurrent(log: { verdict: string; evidenceContext?: string | null } | undefined, context: string | null): boolean {
  return Boolean(log && log.verdict !== 'unset' && context && log.evidenceContext === context)
}
