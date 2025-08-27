import {
    User,
    createUserWithEmailAndPassword,
    onAuthStateChanged,
    signInWithEmailAndPassword,
    signOut,
    updateProfile
} from 'firebase/auth';
import { doc, getDoc, setDoc } from 'firebase/firestore';
import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { auth, db } from '../services/firebase';
import type { UserProfile } from '../types';

interface AuthContextType {
  user: User | null;
  userProfile: UserProfile | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, displayName: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  updateUserProfile: (profile: Partial<UserProfile>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser);
      
      if (firebaseUser) {
        try {
          // Get Firebase ID token
          const token = await firebaseUser.getIdToken();
          
          // Set API token
          apiService.setAuthToken(token);
          
          // Get user profile from Firestore
          const profileDoc = await getDoc(doc(db, 'users', firebaseUser.uid));
          if (profileDoc.exists()) {
            setUserProfile(profileDoc.data() as UserProfile);
          } else {
            // Create default user profile
            const defaultProfile: UserProfile = {
              userId: firebaseUser.uid,
              goals: [],
              themes: [],
              voiceProfile: {
                id: '',
                samples: [],
                tone: { formal: 50, punchy: 50, contrarian: 50 },
                style: { personality: [], vocabulary: [], structure: [] },
                createdAt: new Date(),
                updatedAt: new Date(),
              },
              integrations: [],
              preferences: {
                notifications: {
                  drafts: true,
                  approvals: true,
                  analytics: true,
                  engagement: true,
                },
                posting: {
                  autoApprove: false,
                  bestTimeOnly: true,
                  requireModeration: true,
                },
                consultation: {
                  proactive: true,
                  frequency: 'daily',
                },
              },
            };
            
            await setDoc(doc(db, 'users', firebaseUser.uid), defaultProfile);
            setUserProfile(defaultProfile);
          }
        } catch (error) {
          console.error('Error loading user profile:', error);
        }
      } else {
        setUserProfile(null);
        apiService.setAuthToken('');
      }
      
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const signIn = async (email: string, password: string) => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  };

  const signUp = async (email: string, password: string, displayName: string) => {
    try {
      const { user: newUser } = await createUserWithEmailAndPassword(auth, email, password);
      await updateProfile(newUser, { displayName });
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  };

  const signInWithGoogle = async () => {
    try {
      const { oauthManager } = await import('../services/oauthService');
      const result = await oauthManager.authenticateWithProvider('google');
      
      if (result) {
        // Create or sign in user with Google credentials
        // This would typically create a custom token via your backend
        // and sign in with Firebase using that token
        console.log('Google authentication successful:', result.user);
        
        // For now, we'll throw an error to indicate this needs backend integration
        throw new Error('Google Sign-In requires backend integration to complete');
      } else {
        throw new Error('Google authentication was cancelled');
      }
    } catch (error) {
      console.error('Google Sign-In error:', error);
      throw error;
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  };

  const updateUserProfile = async (profileUpdates: Partial<UserProfile>) => {
    if (!user) throw new Error('No authenticated user');

    try {
      const updatedProfile = { ...userProfile, ...profileUpdates };
      await setDoc(doc(db, 'users', user.uid), updatedProfile, { merge: true });
      setUserProfile(updatedProfile as UserProfile);
    } catch (error) {
      console.error('Error updating user profile:', error);
      throw error;
    }
  };

  const value = {
    user,
    userProfile,
    loading,
    signIn,
    signUp,
    signInWithGoogle,
    signOut: handleSignOut,
    updateUserProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};