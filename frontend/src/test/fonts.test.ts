import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const indexHtml = readFileSync(resolve(process.cwd(), 'index.html'), 'utf-8');

describe('self-hosted Poppins font contract', () => {
  it('does not request Google Fonts (no render-blocking cross-origin font chain)', () => {
    expect(indexHtml).not.toMatch(/fonts\.googleapis\.com/);
    expect(indexHtml).not.toMatch(/fonts\.gstatic\.com/);
  });

  it('preloads the critical self-hosted woff2 weights (400 and 700)', () => {
    expect(indexHtml).toMatch(
      /<link rel="preload" as="font" type="font\/woff2" href="\/fonts\/poppins-latin-400\.woff2" crossorigin \/>/,
    );
    expect(indexHtml).toMatch(
      /<link rel="preload" as="font" type="font\/woff2" href="\/fonts\/poppins-latin-700\.woff2" crossorigin \/>/,
    );
  });

  it('declares @font-face for body and headings using font-display: optional (no FOUT -> no CLS)', () => {
    const weights = ['300', '400', '500', '600', '700'];
    for (const w of weights) {
      const face = new RegExp(
        `@font-face\\{font-family:'Poppins';font-style:normal;font-display:optional;font-weight:${w};src:url\\(/fonts/poppins-latin-${w}\\.woff2\\) format\\('woff2'\\)`,
      );
      expect(indexHtml).toMatch(face);
    }
  });

  it('applies Poppins as the primary font with a system fallback (safe degradation)', () => {
    expect(indexHtml).toMatch(/font-family:'Poppins',system-ui/);
  });
});
