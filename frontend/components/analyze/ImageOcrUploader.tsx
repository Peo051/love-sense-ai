'use client';

import { ChangeEvent, useEffect, useRef, useState } from 'react';
import { AlertTriangle, FileImage, Loader2, ShieldCheck, Trash2, WandSparkles } from 'lucide-react';

import { ErrorAlert, SuccessAlert } from '@/components/common/Alerts';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import { extractChatTextWithVision } from '@/lib/api';
import { extractTextFromImage, validateImageFile, type OcrExtractionResult, type OcrProgress } from '@/lib/ocr';
import { estimateOcrQuality } from '@/lib/ocrPostprocess';

type ImageOcrUploaderProps = {
  onTextExtracted: (text: string, result: OcrExtractionResult) => void;
};

function formatFileSize(bytes: number) {
  return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
}

function progressPercent(progress: number) {
  return Math.round(Math.max(0, Math.min(1, progress)) * 100);
}

function getProgressLabel(status: OcrProgress['status']) {
  const labels: Record<OcrProgress['status'], string> = {
    preprocessing: 'Đang làm rõ ảnh...',
    recognizing: 'Đang nhận diện chữ...',
    postprocessing: 'Đang chuẩn hóa kết quả...',
  };

  return labels[status];
}

export default function ImageOcrUploader({ onTextExtracted }: ImageOcrUploaderProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const activeOcrRunRef = useRef(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [progress, setProgress] = useState<OcrProgress>({ status: 'preprocessing', progress: 0 });
  const [ocrResult, setOcrResult] = useState<OcrExtractionResult | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [useVisionAi, setUseVisionAi] = useState(false);
  const [visionConsent, setVisionConsent] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;

    setErrorMessage('');
    setSuccessMessage('');
    setOcrResult(null);
    setProgress({ status: 'preprocessing', progress: 0 });

    if (!file) {
      return;
    }

    const validation = validateImageFile(file);
    if (!validation.valid) {
      setSelectedFile(null);
      setPreviewUrl(null);
      setErrorMessage(validation.error ?? 'Không thể dùng ảnh này. Vui lòng chọn ảnh khác.');
      event.target.value = '';
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const clearImage = () => {
    activeOcrRunRef.current += 1;
    setSelectedFile(null);
    setPreviewUrl(null);
    setOcrResult(null);
    setProgress({ status: 'preprocessing', progress: 0 });
    setIsExtracting(false);
    setVisionConsent(false);
    setSuccessMessage('');
    setErrorMessage('');

    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const createVisionExtractionResult = (text: string, confidence: number, warnings: string[]): OcrExtractionResult => {
    const localQuality = estimateOcrQuality(text, confidence);

    return {
      text,
      rawText: text,
      confidence,
      language: 'vision',
      quality: {
        score: warnings.length ? Math.min(localQuality.score, 0.72) : localQuality.score,
        warnings: [...new Set([...warnings, ...localQuality.warnings])],
      },
    };
  };

  const applyExtractionResult = (extraction: OcrExtractionResult, message: string) => {
    setOcrResult(extraction);
    onTextExtracted(extraction.text, extraction);
    setSuccessMessage(message);
  };

  const runLocalOcr = async (file: File, runId: number, successPrefix = '') => {
    const extraction = await extractTextFromImage(file, (nextProgress) => {
      if (activeOcrRunRef.current === runId) {
        setProgress(nextProgress);
      }
    });

    if (activeOcrRunRef.current !== runId) {
      return;
    }

    applyExtractionResult(
      extraction,
      `${successPrefix}Đã trích xuất nội dung. Vui lòng kiểm tra và chỉnh sửa lại nếu OCR nhận diện sai.`
    );
  };

  const runVisionOcr = async (file: File, runId: number) => {
    setProgress({ status: 'recognizing', progress: 0.35 });
    const response = await extractChatTextWithVision(file, true);

    if (activeOcrRunRef.current !== runId) {
      return;
    }

    setProgress({ status: 'postprocessing', progress: 0.94 });
    const extraction = createVisionExtractionResult(response.text, response.confidence, response.warnings ?? []);
    applyExtractionResult(
      extraction,
      'AI Vision đã trích xuất nội dung. Vui lòng kiểm tra và chỉnh sửa lại trước khi phân tích.'
    );
  };

  const handleExtractText = async () => {
    if (!selectedFile) {
      setErrorMessage('Vui lòng chọn ảnh chụp đoạn chat trước khi trích xuất chữ.');
      return;
    }

    if (useVisionAi && !visionConsent) {
      setErrorMessage('Bạn cần đồng ý gửi ảnh này đến AI provider trước khi dùng AI Vision.');
      return;
    }

    const runId = activeOcrRunRef.current + 1;
    activeOcrRunRef.current = runId;
    setIsExtracting(true);
    setErrorMessage('');
    setSuccessMessage('');
    setOcrResult(null);
    setProgress({ status: 'preprocessing', progress: 0 });

    try {
      if (useVisionAi) {
        try {
          await runVisionOcr(selectedFile, runId);
        } catch {
          if (activeOcrRunRef.current === runId) {
            await runLocalOcr(
              selectedFile,
              runId,
              'AI Vision chưa sẵn sàng, ứng dụng đã chuyển sang OCR local. '
            );
          }
        }
      } else {
        await runLocalOcr(selectedFile, runId);
      }
    } catch {
      if (activeOcrRunRef.current === runId) {
        setErrorMessage('Không thể nhận diện chữ từ ảnh này. Hãy thử ảnh rõ hơn hoặc nhập thủ công.');
      }
    } finally {
      if (activeOcrRunRef.current === runId) {
        setIsExtracting(false);
      }
    }
  };

  const handleUseExtractedText = () => {
    if (!ocrResult) {
      return;
    }

    onTextExtracted(ocrResult.text, ocrResult);
    setSuccessMessage('Đã đưa nội dung OCR vào ô đoạn chat. Vui lòng kiểm tra lại trước khi phân tích.');
  };

  const currentPercent = progressPercent(progress.progress);
  const hasQualityWarnings = Boolean(ocrResult?.quality.warnings.length);

  return (
    <Card
      title="Nhập từ ảnh chụp đoạn chat"
      description="Tải ảnh do bạn tự chọn lên, trích xuất chữ trên trình duyệt rồi kiểm tra lại trước khi phân tích."
    >
      <div className="space-y-4">
        <div className="rounded-2xl border border-dashed border-rose-200 bg-rose-50/45 p-4">
          <label
            htmlFor="chat_image"
            className="flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl bg-white/75 px-4 py-6 text-center text-sm text-slate-600 transition hover:bg-white focus-within:ring-4 focus-within:ring-rose-100"
          >
            <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-rose-100 text-rose-700">
              <FileImage className="h-5 w-5" aria-hidden="true" />
            </span>
            <span>
              <span className="block font-semibold text-slate-950">Tải ảnh chụp đoạn chat</span>
              <span className="mt-1 block text-xs leading-5 text-slate-500">PNG, JPG, JPEG hoặc WEBP. Tối đa 5MB.</span>
            </span>
            <input
              ref={inputRef}
              id="chat_image"
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="sr-only"
              onChange={handleFileChange}
            />
          </label>
        </div>

        {previewUrl && selectedFile && (
          <div className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-slate-950">{selectedFile.name}</p>
                <p className="mt-1 text-xs text-slate-500">{formatFileSize(selectedFile.size)}</p>
              </div>
              <Button type="button" variant="secondary" size="sm" onClick={clearImage} aria-label="Xóa ảnh đã chọn">
                <Trash2 className="h-4 w-4" aria-hidden="true" />
                Xóa ảnh
              </Button>
            </div>
            <img
              src={previewUrl}
              alt="Ảnh chụp đoạn chat đã chọn"
              className="mt-3 max-h-64 w-full rounded-xl border border-slate-100 object-contain"
            />
          </div>
        )}

        {isExtracting && (
          <div role="status" aria-live="polite" className="rounded-2xl border border-rose-100 bg-white p-4">
            <div className="flex items-center gap-3 text-sm font-semibold text-slate-950">
              <Loader2 className="h-4 w-4 animate-spin text-rose-600" aria-hidden="true" />
              {getProgressLabel(progress.status)}
            </div>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-rose-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-rose-500 to-teal-500 transition-all duration-300"
                style={{ width: `${currentPercent}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-slate-500">{currentPercent}%</p>
          </div>
        )}

        {errorMessage && <ErrorAlert>{errorMessage}</ErrorAlert>}
        {successMessage && <SuccessAlert>{successMessage}</SuccessAlert>}

        <div className="space-y-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-700">
          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={useVisionAi}
              onChange={(event) => {
                const checked = event.target.checked;
                setUseVisionAi(checked);
                if (!checked) {
                  setVisionConsent(false);
                }
              }}
              className="mt-1 h-4 w-4 rounded border-slate-300 text-rose-600 focus:ring-rose-500"
            />
            <span>
              <span className="block font-semibold text-slate-950">Dùng AI Vision để trích xuất chính xác hơn</span>
              <span className="mt-1 block text-xs leading-5 text-slate-500">
                Mặc định ứng dụng dùng OCR local trên trình duyệt. AI Vision có thể đọc layout bong bóng chat tốt hơn nhưng cần gửi ảnh đến provider.
              </span>
            </span>
          </label>

          {useVisionAi && (
            <label className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50/80 px-3 py-2 text-amber-950">
              <input
                type="checkbox"
                checked={visionConsent}
                onChange={(event) => setVisionConsent(event.target.checked)}
                className="mt-1 h-4 w-4 rounded border-amber-300 text-rose-600 focus:ring-rose-500"
              />
              <span>Tôi đồng ý gửi ảnh này đến AI provider để trích xuất nội dung.</span>
            </label>
          )}
        </div>

        {hasQualityWarnings && (
          <div role="alert" className="rounded-2xl border border-amber-200 bg-amber-50/85 px-4 py-3 text-sm leading-6 text-amber-950">
            <div className="flex gap-2">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-700" aria-hidden="true" />
              <div>
                <p className="font-semibold">OCR có thể chưa chính xác.</p>
                <ul className="mt-1 list-disc space-y-1 pl-5">
                  {ocrResult?.quality.warnings.map((warning) => <li key={warning}>{warning}</li>)}
                </ul>
              </div>
            </div>
          </div>
        )}

        {ocrResult && (
          <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-3">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-xs leading-5 text-slate-600">
                Độ tin cậy OCR tham khảo: <span className="font-semibold text-slate-950">{ocrResult.confidence.toFixed(0)}%</span>.
                Hãy rà lại dấu, emoji và thứ tự dòng.
              </p>
              <div className="flex flex-wrap gap-2">
                <Button type="button" variant="secondary" size="sm" onClick={handleUseExtractedText}>
                  Dùng nội dung này
                </Button>
                <Button type="button" variant="secondary" size="sm" onClick={handleExtractText} disabled={isExtracting}>
                  Chạy OCR lại
                </Button>
                <Button type="button" variant="ghost" size="sm" onClick={clearImage}>
                  Xóa ảnh
                </Button>
              </div>
            </div>
          </div>
        )}

        <div className="grid gap-3 sm:grid-cols-[1fr_auto] sm:items-center">
          <div
            role="status"
            className="flex gap-3 rounded-2xl border border-teal-200 bg-teal-50 px-4 py-3 text-sm leading-6 text-teal-900"
          >
            <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-teal-700" aria-hidden="true" />
            <span>Ảnh chỉ được xử lý trên trình duyệt trong phiên hiện tại và không được lưu mặc định.</span>
          </div>
          <Button
            type="button"
            onClick={handleExtractText}
            disabled={!selectedFile || isExtracting}
          >
            {isExtracting ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <WandSparkles className="h-4 w-4" aria-hidden="true" />
            )}
            Trích xuất chữ từ ảnh
          </Button>
        </div>

        <div className="rounded-2xl border border-amber-200 bg-amber-50/80 px-4 py-3 text-sm leading-6 text-amber-950">
          <div className="flex gap-2">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-700" aria-hidden="true" />
            <p>
              OCR có thể nhận diện sai, hãy kiểm tra lại nội dung trước khi phân tích. Hãy che/xóa thông tin nhạy cảm
              nếu không muốn xử lý.
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
}
