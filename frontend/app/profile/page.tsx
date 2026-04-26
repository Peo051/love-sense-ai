'use client';

import UserProfileForm from '@/components/profile/UserProfileForm';
import PartnerProfileForm from '@/components/profile/PartnerProfileForm';
import PreferenceForm from '@/components/profile/PreferenceForm';
import CommunicationStyleForm from '@/components/profile/CommunicationStyleForm';

export default function ProfilePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Hồ sơ của bạn</h1>
      
      <div className="space-y-8">
        <UserProfileForm />
        <PartnerProfileForm />
        <PreferenceForm />
        <CommunicationStyleForm />
      </div>
    </div>
  );
}
