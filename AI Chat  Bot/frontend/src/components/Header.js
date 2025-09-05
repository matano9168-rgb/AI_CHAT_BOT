import React from 'react';
import { useAuthStore } from '../stores/authStore';

const Header = ({ onMenuClick }) => {
  const user = useAuthStore(state => state.user);

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="ml-2 text-lg font-semibold text-gray-900 lg:hidden">
            AI Chatbot
          </h1>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-700">
            Welcome, <span className="font-medium">{user?.username || 'User'}</span>
          </div>
          <div className="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
