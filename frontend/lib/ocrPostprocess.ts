export type OcrQuality = {
  score: number;
  warnings: string[];
};

const OCR_NOISE_PATTERN = /[^\p{L}\p{N}\p{P}\p{S}\p{Zs}\n]/gu;
const SUSPICIOUS_OCR_CHARS_PATTERN = /[|\\[\]{}~^_=<>]/g;

export function removeOcrNoise(text: string): string {
  return text
    .replace(/\u0000/g, '')
    .replace(/[\u200B-\u200D\uFEFF]/g, '')
    .replace(OCR_NOISE_PATTERN, '');
}

export function cleanupChatLines(lines: string[]): string[] {
  return lines
    .map((line) => line.replace(/[ \t]+/g, ' ').trim())
    .map((line) => line.replace(/^[•·*]+\s*/, '').trim())
    .filter((line) => {
      if (!line) {
        return false;
      }

      const letters = line.match(/\p{L}/gu)?.length ?? 0;
      const digits = line.match(/\p{N}/gu)?.length ?? 0;

      return letters + digits > 0 || line.length > 2;
    });
}

export function normalizeOcrText(rawText: string): string {
  const cleanedText = removeOcrNoise(rawText).replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  const lines = cleanupChatLines(cleanedText.split('\n'));

  return lines.join('\n').replace(/\n{3,}/g, '\n\n').trim();
}

export function estimateOcrQuality(text: string, confidence?: number): OcrQuality {
  const normalizedText = normalizeOcrText(text);
  const compactText = normalizedText.replace(/\s/g, '');
  const warnings: string[] = [];

  if (!compactText) {
    return {
      score: 0,
      warnings: ['OCR chưa nhận diện được nội dung. Vui lòng thử ảnh rõ hơn hoặc nhập thủ công.'],
    };
  }

  let score = 1;
  const lineCount = normalizedText.split('\n').filter(Boolean).length;
  const letterCount = compactText.match(/\p{L}/gu)?.length ?? 0;
  const suspiciousCharCount = compactText.match(SUSPICIOUS_OCR_CHARS_PATTERN)?.length ?? 0;
  const letterRatio = letterCount / compactText.length;
  const suspiciousRatio = suspiciousCharCount / compactText.length;

  if (compactText.length < 20) {
    score -= 0.45;
    warnings.push('OCR nhận diện quá ít nội dung, vui lòng thử ảnh rõ hơn hoặc nhập thủ công.');
  }

  if (lineCount < 2) {
    score -= 0.15;
    warnings.push('OCR chỉ nhận diện được rất ít dòng. Hãy kiểm tra xem có thiếu tin nhắn không.');
  }

  if (letterRatio < 0.45) {
    score -= 0.2;
    warnings.push('Kết quả OCR có nhiều ký tự khó đọc. Bạn nên chỉnh sửa lại trước khi phân tích.');
  }

  if (suspiciousRatio > 0.12) {
    score -= 0.2;
    warnings.push('OCR có thể bị nhiễu bởi nền, emoji hoặc bong bóng chat. Hãy rà lại từng dòng.');
  }

  if (typeof confidence === 'number' && confidence > 0 && confidence < 60) {
    score -= 0.25;
    warnings.push('OCR có thể chưa chính xác vì ảnh mờ, nền nhiều họa tiết hoặc chữ nhỏ.');
  }

  return {
    score: Math.max(0, Math.min(1, Number(score.toFixed(2)))),
    warnings: [...new Set(warnings)],
  };
}
