'use client';

import { FormEvent, useEffect, useState } from 'react';
import { Save, Trash2 } from 'lucide-react';

import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import { deleteProfile, getProfile, saveProfile } from '@/lib/api';
import type { PartnerProfile, ProfilePayload, UserProfile } from '@/lib/types';

const emptyUserProfile: UserProfile = {
  nickname: '',
  primary_language: 'Tiếng Việt',
  communication_style: '',
  relationship_status: '',
};

const emptyPartnerProfile: PartnerProfile = {
  nickname: '',
  likes: '',
  dislikes: '',
  texting_style: '',
  when_happy: '',
  when_sad: '',
  when_angry: '',
  likes_checkins: true,
  dislikes_repeated_questions: true,
  height_cm: null,
  weight_kg: null,
  appearance: '',
  private_notes: '',
};

export default function ProfilePage() {
  const [userProfile, setUserProfile] = useState<UserProfile>(emptyUserProfile);
  const [partnerProfile, setPartnerProfile] = useState<PartnerProfile>(emptyPartnerProfile);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    getProfile()
      .then((profile) => {
        setUserProfile(profile.user_profile);
        setPartnerProfile(profile.partner_profile);
      })
      .catch(() => setErrorMessage('Không thể tải hồ sơ. Bạn vẫn có thể nhập và lưu lại.'));
  }, []);

  const updateUserProfile = (field: keyof UserProfile, value: string) => {
    setUserProfile((current) => ({ ...current, [field]: value }));
  };

  const updatePartnerProfile = (field: keyof PartnerProfile, value: string | boolean | number | null) => {
    setPartnerProfile((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSaving(true);
    setErrorMessage('');
    setStatusMessage('');

    const payload: ProfilePayload = {
      user_profile: userProfile,
      partner_profile: partnerProfile,
    };

    try {
      const savedProfile = await saveProfile(payload);
      setUserProfile(savedProfile.user_profile);
      setPartnerProfile(savedProfile.partner_profile);
      setStatusMessage('Đã lưu hồ sơ cá nhân hóa.');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể lưu hồ sơ.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteProfile = async () => {
    setErrorMessage('');
    setStatusMessage('');

    try {
      await deleteProfile();
      setUserProfile(emptyUserProfile);
      setPartnerProfile(emptyPartnerProfile);
      setStatusMessage('Đã xóa hồ sơ cá nhân hóa.');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể xóa hồ sơ.');
    }
  };

  return (
    <div className="mx-auto w-full max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-3">
          <p className="text-sm font-semibold uppercase text-rose-700">Hồ sơ cá nhân hóa</p>
          <h1 className="text-3xl font-bold text-slate-950">Thông tin dùng để cá nhân hóa gợi ý phản hồi</h1>
          <p className="max-w-3xl text-sm leading-6 text-slate-600">
            Các trường nhạy cảm là tùy chọn. Chiều cao, cân nặng và ngoại hình không được dùng để suy luận
            cảm xúc; chỉ nên dùng làm ghi chú nếu bạn thật sự cần.
          </p>
        </div>

        {statusMessage && <p className="rounded-md bg-teal-50 px-4 py-3 text-sm text-teal-800">{statusMessage}</p>}
        {errorMessage && <p className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{errorMessage}</p>}

        <Card title="Hồ sơ người dùng">
          <div className="grid gap-4 sm:grid-cols-2">
            <TextField
              label="Biệt danh"
              value={userProfile.nickname}
              onChange={(value) => updateUserProfile('nickname', value)}
            />
            <TextField
              label="Ngôn ngữ chính"
              value={userProfile.primary_language}
              onChange={(value) => updateUserProfile('primary_language', value)}
            />
            <TextField
              label="Phong cách giao tiếp"
              value={userProfile.communication_style}
              onChange={(value) => updateUserProfile('communication_style', value)}
            />
            <TextField
              label="Trạng thái mối quan hệ"
              value={userProfile.relationship_status}
              onChange={(value) => updateUserProfile('relationship_status', value)}
            />
          </div>
        </Card>

        <Card title="Hồ sơ người yêu">
          <div className="grid gap-4 sm:grid-cols-2">
            <TextField
              label="Biệt danh"
              value={partnerProfile.nickname}
              onChange={(value) => updatePartnerProfile('nickname', value)}
            />
            <TextField
              label="Phong cách nhắn tin"
              value={partnerProfile.texting_style}
              onChange={(value) => updatePartnerProfile('texting_style', value)}
            />
            <TextArea
              label="Sở thích"
              value={partnerProfile.likes}
              onChange={(value) => updatePartnerProfile('likes', value)}
            />
            <TextArea
              label="Điều không thích"
              value={partnerProfile.dislikes}
              onChange={(value) => updatePartnerProfile('dislikes', value)}
            />
            <TextArea
              label="Khi vui thường biểu hiện thế nào"
              value={partnerProfile.when_happy}
              onChange={(value) => updatePartnerProfile('when_happy', value)}
            />
            <TextArea
              label="Khi buồn thường biểu hiện thế nào"
              value={partnerProfile.when_sad}
              onChange={(value) => updatePartnerProfile('when_sad', value)}
            />
            <TextArea
              label="Khi giận thường biểu hiện thế nào"
              value={partnerProfile.when_angry}
              onChange={(value) => updatePartnerProfile('when_angry', value)}
            />
            <TextArea
              label="Ghi chú riêng"
              value={partnerProfile.private_notes}
              onChange={(value) => updatePartnerProfile('private_notes', value)}
            />
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <CheckboxField
              label="Có thích được hỏi thăm không"
              checked={partnerProfile.likes_checkins}
              onChange={(checked) => updatePartnerProfile('likes_checkins', checked)}
            />
            <CheckboxField
              label="Có thích bị hỏi dồn không"
              checked={!partnerProfile.dislikes_repeated_questions}
              onChange={(checked) => updatePartnerProfile('dislikes_repeated_questions', !checked)}
            />
          </div>
        </Card>

        <Card title="Dữ liệu tùy chọn" description="Không bắt buộc nhập. Các trường này không được dùng để suy luận cảm xúc.">
          <div className="grid gap-4 sm:grid-cols-3">
            <NumberField
              label="Chiều cao"
              value={partnerProfile.height_cm}
              suffix="cm"
              onChange={(value) => updatePartnerProfile('height_cm', value)}
            />
            <NumberField
              label="Cân nặng"
              value={partnerProfile.weight_kg}
              suffix="kg"
              onChange={(value) => updatePartnerProfile('weight_kg', value)}
            />
            <TextField
              label="Ngoại hình"
              value={partnerProfile.appearance}
              onChange={(value) => updatePartnerProfile('appearance', value)}
            />
          </div>
        </Card>

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
          <Button type="button" variant="secondary" onClick={handleDeleteProfile}>
            <Trash2 className="h-4 w-4" aria-hidden="true" />
            Xóa hồ sơ
          </Button>
          <Button type="submit" isLoading={isSaving}>
            <Save className="h-4 w-4" aria-hidden="true" />
            {isSaving ? 'Đang lưu' : 'Lưu hồ sơ'}
          </Button>
        </div>
      </form>
    </div>
  );
}

interface TextFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

function TextField({ label, value, onChange }: TextFieldProps) {
  return (
    <label className="space-y-2 text-sm font-medium text-slate-800">
      <span>{label}</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-md border border-rose-100 px-3 py-2 text-sm outline-none focus:border-rose-400 focus:ring-4 focus:ring-rose-100"
      />
    </label>
  );
}

function TextArea({ label, value, onChange }: TextFieldProps) {
  return (
    <label className="space-y-2 text-sm font-medium text-slate-800">
      <span>{label}</span>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={3}
        className="w-full rounded-md border border-rose-100 px-3 py-2 text-sm outline-none focus:border-rose-400 focus:ring-4 focus:ring-rose-100"
      />
    </label>
  );
}

interface NumberFieldProps {
  label: string;
  value?: number | null;
  suffix: string;
  onChange: (value: number | null) => void;
}

function NumberField({ label, value, suffix, onChange }: NumberFieldProps) {
  return (
    <label className="space-y-2 text-sm font-medium text-slate-800">
      <span>{label}</span>
      <div className="flex rounded-md border border-rose-100 bg-white focus-within:border-rose-400 focus-within:ring-4 focus-within:ring-rose-100">
        <input
          type="number"
          min="0"
          value={value ?? ''}
          onChange={(event) => onChange(event.target.value ? Number(event.target.value) : null)}
          className="w-full rounded-l-md px-3 py-2 text-sm outline-none"
        />
        <span className="border-l border-rose-100 px-3 py-2 text-sm text-slate-500">{suffix}</span>
      </div>
    </label>
  );
}

interface CheckboxFieldProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

function CheckboxField({ label, checked, onChange }: CheckboxFieldProps) {
  return (
    <label className="flex items-center gap-3 rounded-lg border border-rose-100 bg-rose-50/60 px-4 py-3 text-sm text-slate-800">
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className="h-4 w-4 rounded border-rose-300 text-rose-600 focus:ring-rose-500"
      />
      {label}
    </label>
  );
}
