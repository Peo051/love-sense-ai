import { signInWithPopup, signOut } from 'firebase/auth';

import { clearAuthToken } from '@/lib/api';
import { auth, googleProvider, isFirebaseConfigured } from '@/lib/firebase';

export async function loginWithGoogle() {
  if (!isFirebaseConfigured) {
    throw new Error('Firebase chưa được cấu hình. Vui lòng kiểm tra biến môi trường NEXT_PUBLIC_FIREBASE_*.');
  }

  return signInWithPopup(auth, googleProvider);
}

export async function logout() {
  clearAuthToken();
  return signOut(auth);
}
