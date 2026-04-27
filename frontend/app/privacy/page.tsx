'use client';

import { useEffect, useState } from 'react';
import { Trash2 } from 'lucide-react';

import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import { clearHistory, deleteProfile, deleteUserData, getConsent, saveConsent } from '@/lib/api';
import type { ConsentSettings } from '@/lib/types';

const defaultConsent: ConsentSettings = {
  history_enabled: true,
  save_input: false,
  save_result: false,
  consent_type: 'privacy_settings',
  is_accepted: false,
  accepted_at: null,
};

export default function PrivacyPage() {
  const [settings, setSettings] = useState<ConsentSettings>(defaultConsent);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    getConsent()
      .then((consent) => setSettings(consent))
      .catch(() => setErrorMessage('Không thể tải cài đặt quyền riêng tư.'));
  }, []);

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

  const handleDeleteProfile = async () => {
    await runDestructiveAction(
      deleteProfile,
      'Đã xóa hồ sơ cá nhân hóa.',
      'Bạn có chắc muốn xóa hồ sơ cá nhân hóa của tài khoản hiện tại không?'
    );
  };

  const handleClearHistory = async () => {
    await runDestructiveAction(
      clearHistory,
      'Đã xóa lịch sử phân tích.',
      'Bạn có chắc muốn xóa toàn bộ lịch sử phân tích của tài khoản hiện tại không?'
    );
  };

  const handleDeleteAllUserData = async () => {
    await runDestructiveAction(
      async () => {
        await deleteUserData();
        setSettings(defaultConsent);
      },
      'Đã xóa toàn bộ dữ liệu cá nhân của tài khoản hiện tại.',
      'Bạn có chắc muốn xóa toàn bộ hồ sơ, lịch sử và cài đặt riêng tư của tài khoản hiện tại không?'
    );
  };

  const runDestructiveAction = async (
    action: () => Promise<void>,
    successMessage: string,
    confirmationMessage: string
  ) => {
    if (!window.confirm(confirmationMessage)) {
      return;
    }

    setStatusMessage('');
    setErrorMessage('');

    try {
      await action();
      setStatusMessage(successMessage);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể xóa dữ liệu.');
    }
  };

  return (
    <div className="mx-auto w-full max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-6 space-y-3">
        <p className="text-sm font-semibold uppercase text-rose-700">Quyền riêng tư</p>
        <h1 className="text-3xl font-bold text-slate-950">Kiểm soát lưu và xóa dữ liệu</h1>
        <p className="max-w-3xl text-sm leading-6 text-slate-600">
          Bạn không bị ép đồng ý lưu dữ liệu. Nếu tắt lưu lịch sử hoặc không chọn checkbox ở trang phân tích, nội dung
          chat sẽ không được ghi vào lịch sử.
        </p>
      </div>

      {statusMessage && (
        <p role="status" className="mb-4 rounded-md bg-teal-50 px-4 py-3 text-sm text-teal-800">
          {statusMessage}
        </p>
      )}
      {errorMessage && (
        <p role="alert" className="mb-4 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
          {errorMessage}
        </p>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Cài đặt lưu dữ liệu">
          <div className="space-y-4">
            <PrivacyToggle
              label="Bật lưu lịch sử"
              description="Khi tắt, backend sẽ không lưu lịch sử phân tích dù request có yêu cầu lưu."
              checked={settings.history_enabled}
              onChange={(checked) => persistSettings({ ...settings, history_enabled: checked })}
            />
            <PrivacyToggle
              label="Bật lưu kết quả phân tích"
              description="Cho phép lưu cảm xúc tổng quan, độ tin cậy, tóm tắt, gợi ý và cảnh báo."
              checked={settings.save_result}
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
              onChange={(checked) =>
                persistSettings({
                  ...settings,
                  save_input: checked,
                  save_result: checked ? true : settings.save_result,
                })
              }
            />
            <Button type="button" disabled={isSaving} onClick={() => persistSettings(settings)}>
              {isSaving ? 'Đang lưu' : 'Lưu cài đặt'}
            </Button>
          </div>
        </Card>

        <Card title="Xóa dữ liệu">
          <div className="space-y-4">
            <p className="text-sm leading-6 text-slate-600">
              Các thao tác xóa bên dưới áp dụng cho dữ liệu thuộc tài khoản đang đăng nhập. Ứng dụng không xóa dữ liệu
              của tài khoản khác.
            </p>
            <Button type="button" variant="secondary" onClick={handleClearHistory} aria-label="Xóa lịch sử phân tích">
              <Trash2 className="h-4 w-4" aria-hidden="true" />
              Xóa lịch sử phân tích
            </Button>
            <Button type="button" variant="secondary" onClick={handleDeleteProfile} aria-label="Xóa hồ sơ cá nhân hóa">
              <Trash2 className="h-4 w-4" aria-hidden="true" />
              Xóa hồ sơ cá nhân hóa
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={handleDeleteAllUserData}
              aria-label="Xóa toàn bộ dữ liệu cá nhân"
            >
              <Trash2 className="h-4 w-4" aria-hidden="true" />
              Xóa toàn bộ dữ liệu cá nhân
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}

interface PrivacyToggleProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

function PrivacyToggle({ label, description, checked, onChange }: PrivacyToggleProps) {
  return (
    <label className="flex items-start gap-3 rounded-lg border border-rose-100 bg-white px-4 py-3">
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className="mt-1 h-4 w-4 rounded border-rose-300 text-rose-600 focus:ring-rose-500"
      />
      <span>
        <span className="block text-sm font-semibold text-slate-950">{label}</span>
        <span className="mt-1 block text-sm leading-6 text-slate-600">{description}</span>
      </span>
    </label>
  );
}
