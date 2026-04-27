import { estimateOcrQuality, normalizeOcrText, type OcrQuality } from '@/lib/ocrPostprocess';

export const MAX_IMAGE_FILE_SIZE_BYTES = 5 * 1024 * 1024;
const MAX_PREPROCESSED_IMAGE_SIDE = 2400;
const MIN_TARGET_TEXT_SIDE = 900;

const ACCEPTED_IMAGE_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp']);
const ACCEPTED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.webp'];

export type OcrProgress = {
  status: 'preprocessing' | 'recognizing' | 'postprocessing';
  progress: number;
};

export type OcrExtractionResult = {
  text: string;
  rawText: string;
  confidence: number;
  language: string;
  quality: OcrQuality;
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

function getPreprocessScale(width: number, height: number): number {
  const minSide = Math.min(width, height);
  const maxSide = Math.max(width, height);
  const upscaleFactor = minSide < MIN_TARGET_TEXT_SIDE ? Math.min(3, MIN_TARGET_TEXT_SIDE / Math.max(minSide, 1)) : 1;
  const maxSideFactor = MAX_PREPROCESSED_IMAGE_SIDE / Math.max(maxSide, 1);

  return Math.max(0.35, Math.min(upscaleFactor, maxSideFactor));
}

function canvasToBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob);
      } else {
        reject(new Error('OCR_CANVAS_EXPORT_FAILED'));
      }
    }, 'image/png');
  });
}

function loadImage(file: File): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const imageUrl = URL.createObjectURL(file);
    const image = new Image();

    image.onload = () => {
      URL.revokeObjectURL(imageUrl);
      resolve(image);
    };
    image.onerror = () => {
      URL.revokeObjectURL(imageUrl);
      reject(new Error('OCR_IMAGE_LOAD_FAILED'));
    };
    image.src = imageUrl;
  });
}

function enhanceImageData(imageData: ImageData) {
  const { data, width, height } = imageData;
  const grayscale = new Uint8ClampedArray(width * height);

  for (let index = 0; index < data.length; index += 4) {
    const gray = data[index] * 0.299 + data[index + 1] * 0.587 + data[index + 2] * 0.114;
    const contrasted = Math.max(0, Math.min(255, (gray - 128) * 1.45 + 128));
    const enhanced = contrasted > 235 ? 255 : contrasted < 60 ? 0 : contrasted;
    grayscale[index / 4] = enhanced;
  }

  const shouldSharpen = width * height <= 4_500_000;
  const output = shouldSharpen ? new Uint8ClampedArray(grayscale) : grayscale;

  if (shouldSharpen) {
    for (let y = 1; y < height - 1; y += 1) {
      for (let x = 1; x < width - 1; x += 1) {
        const currentIndex = y * width + x;
        const sharpened =
          grayscale[currentIndex] * 5 -
          grayscale[currentIndex - 1] -
          grayscale[currentIndex + 1] -
          grayscale[currentIndex - width] -
          grayscale[currentIndex + width];

        output[currentIndex] = Math.max(0, Math.min(255, sharpened * 0.35 + grayscale[currentIndex] * 0.65));
      }
    }
  }

  for (let pixelIndex = 0; pixelIndex < output.length; pixelIndex += 1) {
    const dataIndex = pixelIndex * 4;
    data[dataIndex] = output[pixelIndex];
    data[dataIndex + 1] = output[pixelIndex];
    data[dataIndex + 2] = output[pixelIndex];
    data[dataIndex + 3] = 255;
  }
}

async function preprocessImageForOcr(file: File, onProgress?: (progress: OcrProgress) => void): Promise<Blob> {
  onProgress?.({ status: 'preprocessing', progress: 0.08 });

  const image = await loadImage(file);
  const scale = getPreprocessScale(image.naturalWidth, image.naturalHeight);
  const targetWidth = Math.max(1, Math.round(image.naturalWidth * scale));
  const targetHeight = Math.max(1, Math.round(image.naturalHeight * scale));
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d', { willReadFrequently: true });

  if (!context) {
    throw new Error('OCR_CANVAS_CONTEXT_UNAVAILABLE');
  }

  canvas.width = targetWidth;
  canvas.height = targetHeight;
  context.imageSmoothingEnabled = true;
  context.imageSmoothingQuality = 'high';
  context.drawImage(image, 0, 0, targetWidth, targetHeight);

  const imageData = context.getImageData(0, 0, targetWidth, targetHeight);
  enhanceImageData(imageData);
  context.putImageData(imageData, 0, 0);

  onProgress?.({ status: 'preprocessing', progress: 0.22 });

  return canvasToBlob(canvas);
}

type TesseractRecognizeResult = {
  data: {
    text?: string;
    confidence?: number;
  };
};

async function recognizeWithFallback(
  image: Blob,
  onProgress?: (progress: OcrProgress) => void
): Promise<{ result: TesseractRecognizeResult; language: string }> {
  const { recognize } = await import('tesseract.js');
  const createLogger =
    (baseProgress: number) =>
    (message: { progress?: number }) => {
      const tesseractProgress = typeof message.progress === 'number' ? Math.max(0, Math.min(1, message.progress)) : 0;
      onProgress?.({ status: 'recognizing', progress: baseProgress + tesseractProgress * 0.68 });
    };

  try {
    const result = (await recognize(image, 'vie+eng', { logger: createLogger(0.24) })) as TesseractRecognizeResult;
    return { result, language: 'vie+eng' };
  } catch {
    const result = (await recognize(image, 'eng', { logger: createLogger(0.24) })) as TesseractRecognizeResult;
    return { result, language: 'eng' };
  }
}

export async function extractTextFromImage(
  file: File,
  onProgress?: (progress: OcrProgress) => void
): Promise<OcrExtractionResult> {
  const preprocessedImage = await preprocessImageForOcr(file, onProgress);
  const { result, language } = await recognizeWithFallback(preprocessedImage, onProgress);

  onProgress?.({ status: 'postprocessing', progress: 0.94 });

  const rawText = result.data.text ?? '';
  const confidence = typeof result.data.confidence === 'number' ? result.data.confidence : 0;
  const text = normalizeOcrText(rawText);
  if (!text) {
    throw new Error('OCR_EMPTY_TEXT');
  }

  return {
    text,
    rawText,
    confidence,
    language,
    quality: estimateOcrQuality(text, confidence),
  };
}
