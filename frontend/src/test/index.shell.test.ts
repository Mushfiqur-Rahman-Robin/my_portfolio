import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const html = readFileSync(resolve(process.cwd(), 'index.html'), 'utf-8');

describe('index.html shell contract', () => {
  it('declares lang and mobile viewport', () => {
    expect(html).toMatch(/<html lang="en">/);
    expect(html).toMatch(
      /<meta name="viewport" content="width=device-width, initial-scale=1.0" \/>/,
    );
  });

  it('has SEO title, description, and robots', () => {
    expect(html).toMatch(/<title>Portfolio of Mushfiq<\/title>/);
    expect(html).toMatch(/<meta name="description" content=".+" \/>/);
    expect(html).toMatch(/<meta name="robots" content="index, follow" \/>/);
  });

  it('has canonical URL and Open Graph image with matching dimensions', () => {
    expect(html).toMatch(
      /<link rel="canonical" href="https:\/\/mushfiqurrahmanrobin\.com" \/>/,
    );
    expect(html).toMatch(/<meta property="og:image" content=".+" \/>/);
    expect(html).toMatch(/<meta property="og:type" content="website" \/>/);
    expect(html).toMatch(/<meta property="og:image:width" content="1200" \/>/);
    expect(html).toMatch(/<meta property="og:image:height" content="630" \/>/);
  });

  it('preconnects to the API origin', () => {
    expect(html).toMatch(
      /<link rel="preconnect" href="https:\/\/api\.mushfiqurrahmanrobin\.com" \/>/,
    );
  });

  it('preloads the self-hosted Poppins font files', () => {
    const preloads = html.match(/<link rel="preload" href="\/fonts\/poppins-\d+\.woff2"[^>]*>/g) || [];
    expect(preloads.length).toBeGreaterThanOrEqual(4);
  });

  it('does not depend on external font hosts', () => {
    expect(html).not.toMatch(/fonts\.googleapis\.com/);
    expect(html).not.toMatch(/fonts\.gstatic\.com/);
  });

  it('defers the entry script so it does not block the shell', () => {
    expect(html).toMatch(
      /<script type="module" src="\/src\/main\.tsx"><\/script>/,
    );
  });

  it('renders the app into an empty root container', () => {
    expect(html).toMatch(/<div id="root"><\/div>/);
  });
});
