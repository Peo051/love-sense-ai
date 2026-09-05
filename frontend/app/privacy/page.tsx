'use client';

import { useEffect, useState } from 'react';
import { Database, FileX2, ShieldCheck, Trash2, type LucideIcon } from 'lucide-react';

import { ErrorAlert, SuccessAlert } from '@/components/common/Alerts';
import AuthRequiredState, { AuthLoadingState } from '@/components/auth/AuthRequiredState';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import { useAuth } from '@/contexts/AuthContext';
import { clearHistory, deleteProfile, deleteUserData, getConsent, saveConsent } from '@/lib/api';
import type { ConsentSettings } from '@/lib/types';

type PendingPrivacyDelete = 'history' | 'profile' | 'all' | null;

const defaultConsent: ConsentSettings = {
  history_enabled: true,
  save_input: false,
  save_result: false,
  consent_type: 'privacy_settings',
  is_accepted: false,
  accepted_at: null,
};

const deleteDialogCopy: Record<Exclude<PendingPrivacyDelete, null>, { title: string; description: string; label: string }> = {
  history: {
    title: 'Xóa lịch sử phân tích?',
    description: 'Thao tác này xóa toàn bộ lịch sử phân tích đã lưu của tài khoản hiện tại. Hồ sơ cá nhân hóa vẫn được giữ lại.',
    label: 'Xóa lịch sử phân tích',
  },
  profile: {
    title: 'Xóa hồ sơ cá nhân hóa?',
    description: 'Thao tác này xóa hồ sơ học viên của bạn. Lịch sử bài nộp không bị xóa trong thao tác này.',
    label: 'Xóa hồ sơ cá nhân hóa',
  },
  all: {
    title: 'Xóa toàn bộ dữ liệu cá nhân?',
    description: 'Thao tác này xóa hồ sơ, lịch sử và cài đặt riêng tư của tài khoản hiện tại. Dữ liệu đã xóa không thể khôi phục.',
    label: 'Xóa toàn bộ dữ liệu cá nhân',
  },
};

export default function PrivacyPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [settings, setSettings] = useState<ConsentSettings>(defaultConsent);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<PendingPrivacyDelete>(null);

  useEffect(() => {
    if (authLoading || !isAuthenticated) {
      return;
    }

    getConsent()
      .then((consent) => setSettings(consent))
      .catch(() => setErrorMessage('Không thể tải cài đặt quyền riêng tư.'));
  }, [authLoading, isAuthenticated]);

  const persistSettings = async (nextSettings: ConsentSettings) => {
    setIsSaving(true);
    setStatusMessage('');
    setErrorMessage('');

    try {
      const savedSettings = await saveConsent({
        ...nextSettings,
        consent_type: 'privacy_settings',
        is_accepted: nextSettings.save_input || nextSettings.save_result,
      });
      setSettings(savedSettings);
      setStatusMessage('Đã lưu cài đặt quyền riêng tư.');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể lưu cài đặt.');
    } finally {
      setIsSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!pendingDelete) {
      return;
    }

    setStatusMessage('');
    setErrorMessage('');
    setIsDeleting(true);

    try {
      if (pendingDelete === 'history') {
        await clearHistory();
        setStatusMessage('Đã xóa lịch sử phân tích.');
      }

      if (pendingDelete === 'profile') {
        await deleteProfile();
        setStatusMessage('Đã xóa hồ sơ cá nhân hóa.');
      }

      if (pendingDelete === 'all') {
        await deleteUserData();
        setSettings(defaultConsent);
        setStatusMessage('Đã xóa toàn bộ dữ liệu cá nhân của tài khoản hiện tại.');
      }

      setPendingDelete(null);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể xóa dữ liệu.');
    } finally {
      setIsDeleting(false);
    }
  };

  const dialogCopy = pendingDelete ? deleteDialogCopy[pendingDelete] : null;

  return (
    <PageShell size="normal" className="space-y-8 pb-12">
      <SectionHeader
        eyebrow="Quyền riêng tư"
        title="Kiểm soát dữ liệu được lưu và xóa"
        description="Bạn luôn có quyền chọn dữ liệu nào được lưu. Nội dung chat không được lưu mặc định và tùy chọn consent luôn hiển thị rõ."
        action={<Badge tone="teal">Không ép consent</Badge>}
      />

      {authLoading ? (
        <AuthLoadingState />
      ) : !isAuthenticated ? (
        <AuthRequiredState
          title="Đăng nhập để quản lý dữ liệu"
          description="Cài đặt consent, lịch sử, hồ sơ và thao tác xóa dữ liệu được gắn với tài khoản. Vui lòng đăng nhập trước khi quản lý dữ liệu cá nhân."
        />
      ) : (
        <>
      {statusMessage && <SuccessAlert>{statusMessage}</SuccessAlert>}
      {errorMessage && <ErrorAlert>{errorMessage}</ErrorAlert>}

      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <Card title="Cài đặt lưu dữ liệu" description="Các lựa chọn này áp dụng cho tài khoản hiện tại.">
          <div className="space-y-4">
            <PrivacyToggle
              label="Bật lưu lịch sử"
              description="Khi tắt, backend sẽ không lưu lịch sử phân tích dù request có yêu cầu lưu."
              checked={settings.history_enabled}
              disabled={isSaving}
              onChange={(checked) => persistSettings({ ...settings, history_enabled: checked })}
            />
            <PrivacyToggle
              label="Bật lưu kết quả phân tích"
              description="Cho phép lưu cảm xúc tổng quan, độ tin cậy, tóm tắt, gợi ý và cảnh báo."
              checked={settings.save_result}
              disabled={isSaving}
              onChange={(checked) =>
                persistSettings({
                  ...settings,
                  save_result: checked,
                  save_input: checked ? settings.save_input : false,
                })
              }
            />
            <PrivacyToggle
              label="Bật lưu nội dung chat"
              description="Chỉ nên bật khi bạn thật sự muốn xem lại đoạn chat gốc trong lịch sử."
              checked={settings.save_input}
              disabled={isSaving}
              onChange={(checked) =>
                persistSettings({
                  ...settings,
                  save_input: checked,
                  save_result: checked ? true : settings.save_result,
                })
              }
            />
            <Button type="button" disabled={isSaving} isLoading={isSaving} onClick={() => persistSettings(settings)}>
              {isSaving ? 'Đang lưu' : 'Lưu cài đặt'}
            </Button>
          </div>
        </Card>

        <div className="space-y-6">
          <Card title="Dữ liệu được lưu khi có consent">
            <div className="grid gap-3 text-sm text-slate-700">
              <PrivacyInfo icon={Database} text="Hồ sơ học viên và cài đặt consent theo user_id." />
              <PrivacyInfo icon={ShieldCheck} text="Kết quả phân tích bài nộp chỉ lưu khi bật lưu lịch sử hoặc save_result." />
              <PrivacyInfo icon={FileX2} text="Mã nguồn gốc không lưu mặc định, chỉ lưu khi save_input=true." />
            </div>
          </Card>

          <Card title="AI Vision consent" description="Ảnh chụp bài tập hoặc mã nguồn chỉ được gửi đến provider khi bạn bật tùy chọn AI Vision và tick consent riêng trong trang gia sư.">
            <div className="rounded-2xl border border-teal-200 bg-teal-50/80 px-4 py-3 text-sm leading-6 text-slate-700 shadow-sm">
              Backend không lưu ảnh, không log ảnh/base64 và frontend vẫn yêu cầu bạn review nội dung OCR trước khi phân tích.
            </div>
          </Card>

          <Card
            title="Xóa dữ liệu"
            description="Các thao tác này chỉ áp dụng cho dữ liệu của tài khoản đang đăng nhập. Mỗi thao tác đều mở hộp xác nhận trước khi xóa."
            className="border-red-100"
          >
            <div className="mb-4 rounded-2xl border-2 border-red-900 bg-red-50 px-4 py-3 text-sm leading-6 text-red-800 shadow-[4px_4px_0_rgba(127,29,29,0.12)]">
              Đây là vùng thao tác nhạy cảm. Hãy chọn đúng loại dữ liệu cần xóa, sau đó xác nhận trong hộp thoại.
            </div>
            <div className="grid gap-3">
              <Button type="button" variant="danger" onClick={() => setPendingDelete('history')} aria-label="Xóa lịch sử phân tích">
                <Trash2 className="h-4 w-4" aria-hidden="true" />
                Xóa lịch sử phân tích
              </Button>
              <Button type="button" variant="danger" onClick={() => setPendingDelete('profile')} aria-label="Xóa hồ sơ cá nhân hóa">
                <Trash2 className="h-4 w-4" aria-hidden="true" />
                Xóa hồ sơ cá nhân hóa
              </Button>
              <Button
                type="button"
                variant="danger"
                onClick={() => setPendingDelete('all')}
                aria-label="Xóa toàn bộ dữ liệu cá nhân"
              >
                <Trash2 className="h-4 w-4" aria-hidden="true" />
                Xóa toàn bộ dữ liệu cá nhân
              </Button>
            </div>
          </Card>
        </div>
      </div>

      <ConfirmDialog
        open={pendingDelete !== null}
        title={dialogCopy?.title ?? ''}
        description={dialogCopy?.description ?? ''}
        confirmLabel={dialogCopy?.label ?? 'Xóa dữ liệu'}
        isBusy={isDeleting}
        onCancel={() => setPendingDelete(null)}
        onConfirm={confirmDelete}
      />
        </>
      )}
    </PageShell>
  );
}

interface PrivacyToggleProps {
  label: string;
  description: string;
  checked: boolean;
  disabled?: boolean;
  onChange: (checked: boolean) => void;
}

function PrivacyToggle({ label, description, checked, disabled = false, onChange }: PrivacyToggleProps) {
  return (
    <label className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm transition hover:-translate-y-0.5 hover:bg-rose-50/60">
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.target.checked)}
        className="mt-1 h-4 w-4 rounded border-slate-900 text-rose-600 focus:ring-rose-500 disabled:cursor-not-allowed disabled:opacity-60"
      />
      <span>
        <span className="block text-sm font-semibold text-slate-950">{label}</span>
        <span className="mt-1 block text-sm leading-6 text-slate-600">{description}</span>
      </span>
    </label>
  );
}

function PrivacyInfo({ icon: Icon, text }: { icon: LucideIcon; text: string }) {
  return (
    <div className="flex gap-3 rounded-2xl bg-slate-50 px-4 py-3">
      <Icon className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" aria-hidden="true" />
      <p className="leading-6">{text}</p>
    </div>
  );
}
