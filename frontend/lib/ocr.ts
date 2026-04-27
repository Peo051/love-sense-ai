export const MAX_IMAGE_FILE_SIZE_BYTES = 5 * 1024 * 1024;

const ACCEPTED_IMAGE_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp']);
const ACCEPTED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.webp'];

export type OcrProgress = {
  status: string;
  progress: number;
};

export type ImageValidationResult = {
  valid: boolean;
  error?: string;
};

export function validateImageFile(file: File): ImageValidationResult {
  const fileName = file.name.toLowerCase();
  const hasAcceptedExtension = ACCEPTED_IMAGE_EXTENSIONS.some((extension) => fileName.endsWith(extension));

  if (!ACCEPTED_IMAGE_TYPES.has(file.type) && !hasAcceptedExtension) {
    return {
      valid: false,
      error: 'Vui lòng chọn ảnh định dạng PNG, JPG, JPEG hoặc WEBP.',
    };
  }

  if (file.size > MAX_IMAGE_FILE_SIZE_BYTES) {
    return {
      valid: false,
      error: 'Ảnh tối đa 5MB. Vui lòng chọn ảnh nhẹ hơn hoặc cắt lại ảnh trước khi OCR.',
    };
  }

  return { valid: true };
}

export function normalizeOcrText(text: string): string {
  return text
    .replace(/\r\n/g, '\n')
    .split('\n')
    .map((line) => line.replace(/[ \t]+/g, ' ').trim())
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

export async function extractTextFromImage(
  file: File,
  onProgress?: (progress: OcrProgress) => void
): Promise<string> {
  const { recognize } = await import('tesseract.js');

  const result = await recognize(file, 'vie+eng', {
    logger: (message: { progress?: number; status?: string }) => {
      onProgress?.({
        status: message.status ?? 'recognizing text',
        progress: typeof message.progress === 'number' ? Math.max(0, Math.min(1, message.progress)) : 0,
      });
    },
  });

  const text = normalizeOcrText(result.data.text ?? '');

  if (!text) {
    throw new Error('OCR_EMPTY_TEXT');
  }

  return text;
}
