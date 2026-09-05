'use client';

import { FormEvent, useEffect, useState } from 'react';
import { BookOpen, Code2, GraduationCap, Info, Save, Trash2, UserRound } from 'lucide-react';

import { ErrorAlert, InfoAlert, SuccessAlert } from '@/components/common/Alerts';
import AuthRequiredState, { AuthLoadingState } from '@/components/auth/AuthRequiredState';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import FieldLabel from '@/components/common/FieldLabel';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import { useAuth } from '@/contexts/AuthContext';
import { deleteProfile, getProfile, saveProfile } from '@/lib/api';
import type { PartnerProfile, ProfilePayload, UserProfile } from '@/lib/types';
import { inputClassName } from '@/lib/ui';

const emptyUserProfile: UserProfile = {
  nickname: '',
  primary_language: 'C# / .NET',
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
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [userProfile, setUserProfile] = useState<UserProfile>(emptyUserProfile);
  const [partnerProfile, setPartnerProfile] = useState<PartnerProfile>(emptyPartnerProfile);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  useEffect(() => {
    if (authLoading || !isAuthenticated) {
      return;
    }

    getProfile()
      .then((profile) => {
        setUserProfile(profile.user_profile);
        setPartnerProfile(profile.partner_profile ?? emptyPartnerProfile);
      })
      .catch(() => setErrorMessage('Vui lòng đăng nhập để tải hoặc lưu hồ sơ.'));
  }, [authLoading, isAuthenticated]);

  const updateUserProfile = (field: keyof UserProfile, value: string) => {
    setUserProfile((current) => ({ ...current, [field]: value }));
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
        eyebrow="Hồ sơ học viên"
        title="Thiết lập thông tin học tập C# OOP"
        description="Thông tin giúp Gia sư CodeSense AI điều chỉnh mức độ gợi ý từng bước (Socratic guidance) phù hợp với trình độ của bạn."
        action={<Badge tone="teal">Cá nhân hóa gợi ý</Badge>}
      />

      {authLoading ? (
        <AuthLoadingState />
      ) : !isAuthenticated ? (
        <AuthRequiredState
          title="Đăng nhập để quản lý hồ sơ"
          description="Hồ sơ học viên được lưu theo từng tài khoản. Bạn cần đăng nhập Google trước khi xem hoặc chỉnh sửa hồ sơ."
        />
      ) : (
        <>
          <InfoAlert>
            <span className="inline-flex items-start gap-2">
              <Info className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              Thông tin hồ sơ học viên chỉ dùng để điều chỉnh cách diễn đạt và độ khó của gợi ý lập trình. Bạn có thể xóa hồ sơ bất cứ lúc nào.
            </span>
          </InfoAlert>

          <form onSubmit={handleSubmit} className="space-y-6">
            {statusMessage && <SuccessAlert>{statusMessage}</SuccessAlert>}
            {errorMessage && <ErrorAlert>{errorMessage}</ErrorAlert>}

            <Card
              title="Thông tin học viên"
              description="Thiết lập tên hiển thị, trình độ hiện tại và mục tiêu môn học OOP."
            >
              <div className="mb-5 flex items-center gap-3 font-mono text-xs font-bold uppercase tracking-[0.12em] text-rose-700">
                <UserRound className="h-4 w-4" aria-hidden="true" />
                Học viên hiện tại
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <TextField
                  id="user-nickname"
                  label="Biệt danh"
                  hint="Tên hoặc biệt danh bạn muốn Gia sư AI dùng khi xưng hô."
                  value={userProfile.nickname}
                  onChange={(value) => updateUserProfile('nickname', value)}
                />

                <TextField
                  id="primary-language"
                  label="Ngôn ngữ chính"
                  hint="Ngôn ngữ lập trình chính bạn đang theo học (mặc định C# / .NET)."
                  value={userProfile.primary_language}
                  onChange={(value) => updateUserProfile('primary_language', value)}
                />

                <TextField
                  id="communication-style"
                  label="Phong cách học & Trình độ"
                  hint="Ví dụ: Mới học C# OOP, cần giải thích kỹ về cấu trúc lớp..."
                  placeholder="Ví dụ: Nhập môn C# OOP, thích ví dụ thực tế..."
                  value={userProfile.communication_style}
                  onChange={(value) => updateUserProfile('communication_style', value)}
                />

                <TextField
                  id="learning-goal"
                  label="Mục tiêu môn học"
                  hint="Ví dụ: Nắm vững 4 tính chất OOP để làm đồ án môn học..."
                  placeholder="Ví dụ: Nắm vững Lớp, Kế thừa, Đa hình..."
                  value={userProfile.relationship_status}
                  onChange={(value) => updateUserProfile('relationship_status', value)}
                />
              </div>
            </Card>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <Button type="submit" isLoading={isSaving} aria-label="Lưu hồ sơ cá nhân hóa">
                <Save className="h-4 w-4" aria-hidden="true" />
                {isSaving ? 'Đang lưu' : 'Lưu hồ sơ học viên'}
              </Button>

              <Button
                type="button"
                variant="danger"
                disabled={isDeleting}
                onClick={() => setIsDeleteDialogOpen(true)}
                aria-label="Xóa hồ sơ cá nhân hóa"
              >
                <Trash2 className="h-4 w-4" aria-hidden="true" />
                Xóa hồ sơ học viên
              </Button>
            </div>
          </form>

          <ConfirmDialog
            open={isDeleteDialogOpen}
            title="Xóa hồ sơ cá nhân hóa?"
            description="Thao tác này xóa thông tin học viên của bạn khỏi hệ thống. Lịch sử bài tập không bị ảnh hưởng."
            confirmLabel="Xóa hồ sơ cá nhân hóa"
            isBusy={isDeleting}
            onCancel={() => setIsDeleteDialogOpen(false)}
            onConfirm={handleDeleteProfile}
          />
        </>
      )}
    </PageShell>
  );
}

function TextField({
  id,
  label,
  value,
  placeholder,
  hint,
  onChange,
}: {
  id?: string;
  label: string;
  value: string;
  placeholder?: string;
  hint?: string;
  onChange: (value: string) => void;
}) {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-');
  return (
    <FieldLabel htmlFor={inputId} label={label} hint={hint}>
      <input
        id={inputId}
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        className={inputClassName}
      />
    </FieldLabel>
  );
}
