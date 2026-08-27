import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getVisitorId, trackVisitorCount, trackPageVisit } from '../utils/visitor';

describe('visitor tracking utility', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('generates and persists a stable visitor id', () => {
    const first = getVisitorId();
    const second = getVisitorId();
    expect(first).toBeTruthy();
    expect(second).toBe(first);
    expect(localStorage.getItem('portfolio_visitor_id')).toBe(first);
  });

  it('reuses an existing stored visitor id', () => {
    localStorage.setItem('portfolio_visitor_id', 'existing-id');
    expect(getVisitorId()).toBe('existing-id');
  });

  it('sends the visitor id and page to the visitor-count endpoint', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal('fetch', fetchMock);

    trackVisitorCount('/');

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toContain('/visitor-count/');
    expect(JSON.parse(options.body)).toMatchObject({
      visitor_id: getVisitorId(),
      page: '/',
    });
  });

  it('sends the visitor id and page to the page-visits endpoint', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal('fetch', fetchMock);

    trackPageVisit('/about');

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toContain('/page-visits/');
    expect(JSON.parse(options.body)).toMatchObject({
      visitor_id: getVisitorId(),
      page: '/about',
    });
  });
});
