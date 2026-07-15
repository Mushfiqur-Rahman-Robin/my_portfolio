import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const indexHtml = readFileSync(resolve(process.cwd(), 'index.html'), 'utf-8');

describe('index.html critical shell contract', () => {
  it('declares the document language and mobile viewport', () => {
    expect(indexHtml).toMatch(/<html lang="en">/);
    expect(indexHtml).toMatch(
      /<meta name="viewport" content="width=device-width, initial-scale=1.0" \/>/,
    );
  });

  it('has a descriptive <title> and meta description for SEO', () => {
    expect(indexHtml).toMatch(/<title>Portfolio of Mushfiq<\/title>/);
    expect(indexHtml).toMatch(/<meta name="description" content=".+" \/>/);
    expect(indexHtml).toMatch(/<meta name="robots" content="index, follow" \/>/);
  });

  it('declares a canonical URL and Open Graph image for agentic indexability', () => {
    expect(indexHtml).toMatch(
      /<link rel="canonical" href="https:\/\/mushfiqurrahmanrobin.com" \/>/,
    );
    expect(indexHtml).toMatch(/<meta property="og:image" content=".+" \/>/);
    expect(indexHtml).toMatch(/<meta property="og:type" content="website" \/>/);
  });

  it('preconnects to the API origin early in the head', () => {
    expect(indexHtml).toMatch(
      /<link rel="preconnect" href="https:\/\/api\.mushfiqurrahmanrobin\.com" \/>/,
    );
  });

  it('renders the hero inline so the LCP element paints before JS', () => {
    expect(indexHtml).toMatch(/<section class="hero-banner">/);
    expect(indexHtml).toContain(
      "<h1>Hello, I'm Md Mushfiqur Rahman</h1>",
    );
  });

  it('keeps the entry script deferred (module) so it does not block the shell', () => {
    expect(indexHtml).toMatch(/<script type="module" src="\/src\/main\.tsx"><\/script>/);
  });
});
