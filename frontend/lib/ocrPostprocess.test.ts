import { describe, expect, it } from 'vitest';

import { estimateOcrQuality, normalizeOcrText } from '@/lib/ocrPostprocess';

describe('ocrPostprocess', () => {
  it('normalizes OCR text while preserving chat line breaks', () => {
    const normalized = normalizeOcrText(' A: anh iu ngủ ngon nhó  \n\n\n B: yeuemm 🥺   ');

    expect(normalized).toBe('A: anh iu ngủ ngon nhó\nB: yeuemm 🥺');
  });

  it('flags very short OCR text as low quality', () => {
    const quality = estimateOcrQuality('ok', 42);

    expect(quality.score).toBeLessThan(0.6);
    expect(quality.warnings.join(' ')).toMatch(/quá ít nội dung/i);
  });
});
