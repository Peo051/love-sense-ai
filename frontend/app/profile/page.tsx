'use client';

import { FormEvent, useEffect, useState } from 'react';
import { Info, Save, Trash2, UserRound, UsersRound } from 'lucide-react';

import { ErrorAlert, InfoAlert, SuccessAlert } from '@/components/common/Alerts';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import FieldLabel from '@/components/common/FieldLabel';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import { deleteProfile, getProfile, saveProfile } from '@/lib/api';
import type { PartnerProfile, ProfilePayload, UserProfile } from '@/lib/types';
import { inputClassName, textareaClassName } from '@/lib/ui';

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
  const [isDeleting, setIsDeleting] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  useEffect(() => {
    getProfile()
      .then((profile) => {
        setUserProfile(profile.user_profile);
        setPartnerProfile(profile.partner_profile);
      })
      .catch(() => setErrorMessage('Vui lòng đăng nhập tại trang Tài khoản để tải hoặc lưu hồ sơ.'));
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
    setIsDeleting(true);
    setErrorMessage('');
    setStatusMessage('');

    try {
      await deleteProfile();
      setUserProfile(emptyUserProfile);
      setPartnerProfile(emptyPartnerProfile);
      setStatusMessage('Đã xóa hồ sơ cá nhân hóa.');
      setIsDeleteDialogOpen(false);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể xóa hồ sơ.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <PageShell size="normal" className="space-y-8 pb-12">
      <SectionHeader
        eyebrow="Hồ sơ cá nhân hóa"
        title="Thêm bối cảnh để gợi ý phản hồi phù hợp hơn"
        description="Các trường đều là tùy chọn. Dữ liệu nhạy cảm không bắt buộc và không được dùng để suy luận cảm xúc."
        action={<Badge tone="amber">Không dùng chiều cao/cân nặng để suy luận</Badge>}
      />

      <InfoAlert>
        <span className="inline-flex items-start gap-2">
          <Info className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          Hồ sơ chỉ dùng để cá nhân hóa cách diễn đạt gợi ý phản hồi. Bạn có thể xóa hồ sơ bất cứ lúc nào.
        </span>
      </InfoAlert>

      <form onSubmit={handleSubmit} className="space-y-6">
        {statusMessage && <SuccessAlert>{statusMessage}</SuccessAlert>}
        {errorMessage && <ErrorAlert>{errorMessage}</ErrorAlert>}

        <Card
          title="Hồ sơ của bạn"
          description="Thông tin này giúp hệ thống điều chỉnh cách diễn đạt gợi ý cho phù hợp với bạn."
        >
          <div className="mb-5 flex items-center gap-3 text-sm font-semibold text-rose-700">
            <UserRound className="h-4 w-4" aria-hidden="true" />
            Người dùng hiện tại
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <TextField label="Biệt danh" value={userProfile.nickname} onChange={(value) => updateUserProfile('nickname', value)} />
            <TextField
              label="Ngôn ngữ chính"
              value={userProfile.primary_language}
              onChange={(value) => updateUserProfile('primary_language', value)}
            />
            <TextField
              label="Phong cách giao tiếp"
              value={userProfile.communication_style}
              placeholder="Ví dụ: nhẹ nhàng, trực tiếp, cần thời gian suy nghĩ..."
              onChange={(value) => updateUserProfile('communication_style', value)}
            />
            <TextField
              label="Trạng thái mối quan hệ"
              value={userProfile.relationship_status}
              placeholder="Ví dụ: đang tìm hiểu, đang yêu xa..."
              onChange={(value) => updateUserProfile('relationship_status', value)}
            />
          </div>
        </Card>

        <Card
          title="Hồ sơ người ấy"
          description="Chỉ nhập những gì bạn thấy cần thiết để cá nhân hóa gợi ý phản hồi. Không cần nhập dữ liệu nhạy cảm."
        >
          <div className="mb-5 flex items-center gap-3 text-sm font-semibold text-rose-700">
            <UsersRound className="h-4 w-4" aria-hidden="true" />
            Bối cảnh giao tiếp
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <TextField
              label="Biệt danh người ấy"
              value={partnerProfile.nickname}
              onChange={(value) => updatePartnerProfile('nickname', value)}
            />
            <TextField
              label="Phong cách nhắn tin"
              value={partnerProfile.texting_style}
              placeholder="Ví dụ: trả lời chậm khi bận, dùng ít emoji..."
              onChange={(value) => updatePartnerProfile('texting_style', value)}
            />
            <TextArea label="Sở thích" value={partnerProfile.likes} onChange={(value) => updatePartnerProfile('likes', value)} />
            <TextArea
              label="Điều không thích"
              value={partnerProfile.dislikes}
              onChange={(value) => updatePartnerProfile('dislikes', value)}
            />
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-3">
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
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
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

        <Card
          title="Ghi chú riêng và dữ liệu tùy chọn"
          description="Chiều cao, cân nặng và ngoại hình chỉ là context phụ nếu bạn muốn ghi lại; không dùng để kết luận cảm xúc."
        >
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
          <div className="mt-4">
            <TextArea
              label="Ghi chú riêng"
              value={partnerProfile.private_notes}
              placeholder="Ghi chú chỉ dùng làm bối cảnh phụ khi bạn cần."
              onChange={(value) => updatePartnerProfile('private_notes', value)}
            />
          </div>
        </Card>

        <div className="flex flex-col gap-3 rounded-2xl border border-rose-100 bg-white/90 p-4 shadow-sm sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="danger"
            onClick={() => setIsDeleteDialogOpen(true)}
            aria-label="Xóa hồ sơ cá nhân hóa"
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
            Xóa hồ sơ
          </Button>
          <Button type="submit" isLoading={isSaving} size="lg">
            <Save className="h-4 w-4" aria-hidden="true" />
            {isSaving ? 'Đang lưu' : 'Lưu hồ sơ'}
          </Button>
        </div>
      </form>

      <ConfirmDialog
        open={isDeleteDialogOpen}
        title="Xóa hồ sơ cá nhân hóa?"
        description="Thao tác này xóa hồ sơ của bạn và hồ sơ người ấy khỏi tài khoản hiện tại. Lịch sử phân tích không bị xóa trong thao tác này."
        confirmLabel="Xóa hồ sơ cá nhân hóa"
        isBusy={isDeleting}
        onCancel={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteProfile}
      />
    </PageShell>
  );
}

interface TextFieldProps {
  label: string;
  value: string;
  placeholder?: string;
  onChange: (value: string) => void;
}

function TextField({ label, value, placeholder, onChange }: TextFieldProps) {
  return (
    <FieldLabel label={label}>
      <input value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} className={inputClassName} />
    </FieldLabel>
  );
}

function TextArea({ label, value, placeholder, onChange }: TextFieldProps) {
  return (
    <FieldLabel label={label}>
      <textarea
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        rows={3}
        className={textareaClassName}
      />
    </FieldLabel>
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
    <FieldLabel label={label}>
      <div className="flex rounded-xl border border-rose-100 bg-white transition focus-within:border-rose-400 focus-within:ring-4 focus-within:ring-rose-100">
        <input
          type="number"
          min="0"
          value={value ?? ''}
          onChange={(event) => onChange(event.target.value ? Number(event.target.value) : null)}
          className="w-full rounded-l-xl px-4 py-3 text-sm outline-none"
        />
        <span className="border-l border-rose-100 px-3 py-3 text-sm text-slate-500">{suffix}</span>
      </div>
    </FieldLabel>
  );
}

interface CheckboxFieldProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

function CheckboxField({ label, checked, onChange }: CheckboxFieldProps) {
  return (
    <label className="flex items-center gap-3 rounded-2xl border border-rose-100 bg-rose-50/60 px-4 py-3 text-sm text-slate-800 transition hover:border-rose-200 hover:bg-rose-50">
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
