const VISITOR_ID_KEY = 'portfolio_visitor_id';

function generateVisitorId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `visitor-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function getVisitorId(): string {
  let id = localStorage.getItem(VISITOR_ID_KEY);
  if (!id) {
    id = generateVisitorId();
    localStorage.setItem(VISITOR_ID_KEY, id);
  }
  return id;
}

const API = import.meta.env.VITE_API_URL;

export function trackVisitorCount(page: string): void {
  fetch(`${API}visitor-count/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ visitor_id: getVisitorId(), page }),
  }).catch(err => console.error('Failed to increment visitor count:', err));
}

export function trackPageVisit(page: string): void {
  fetch(`${API}page-visits/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ visitor_id: getVisitorId(), page }),
  }).catch(err => console.error('Failed to log page visit:', err));
}
