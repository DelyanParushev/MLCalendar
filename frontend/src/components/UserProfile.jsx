import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const UserProfile = () => {
  const { user, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  if (!user) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-full bg-[color:var(--md-sys-color-surface-container-highest)] text-[color:var(--md-sys-color-on-surface-variant)] hover:bg-[color:var(--md-sys-color-surface-container-high)] transition-all duration-200 focus:ring-2 focus:ring-[color:var(--md-sys-color-primary)] focus:ring-opacity-20 outline-none"
      >
        <div className="w-8 h-8 rounded-full bg-[color:var(--md-sys-color-primary)] text-[color:var(--md-sys-color-on-primary)] flex items-center justify-center font-medium text-sm">
          {user.username.charAt(0).toUpperCase()}
        </div>
        <span className="hidden sm:block text-sm font-medium">{user.username}</span>
        <span className="material-icons text-lg">
          {isDropdownOpen ? 'keyboard_arrow_up' : 'keyboard_arrow_down'}
        </span>
      </button>

      {isDropdownOpen && (
        <>
          {/* Overlay to close dropdown when clicking outside */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsDropdownOpen(false)}
          />
          
          {/* Dropdown menu */}
          <div className="absolute right-0 mt-2 w-64 rounded-2xl bg-[color:var(--md-sys-color-surface-container)] shadow-level-3 border border-[color:var(--md-sys-color-outline)] z-20 overflow-hidden">
            <div className="p-4 border-b border-[color:var(--md-sys-color-outline)]">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-[color:var(--md-sys-color-primary)] text-[color:var(--md-sys-color-on-primary)] flex items-center justify-center font-medium text-lg">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div className="font-medium text-[color:var(--md-sys-color-on-surface)]">
                    {user.username}
                  </div>
                  <div className="text-sm text-[color:var(--md-sys-color-on-surface-variant)]">
                    {user.email}
                  </div>
                </div>
              </div>
            </div>

            <div className="p-2">
              <button
                onClick={() => {
                  logout();
                  setIsDropdownOpen(false);
                }}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left bg-[color:var(--md-sys-color-error-container)] text-[color:var(--md-sys-color-on-error-container)] hover:bg-[color:var(--md-sys-color-error)] hover:text-[color:var(--md-sys-color-on-error)] transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-[color:var(--md-sys-color-error)] focus:ring-opacity-50 border border-[color:var(--md-sys-color-error)]"
              >
                <span className="material-icons text-xl">logout</span>
                <span className="font-medium">Sign out</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default UserProfile;