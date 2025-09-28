import React from 'react';
import AddEventForm from './AddEventForm';

const AddEventModal = ({ isOpen, onClose, onSaved, isDarkMode }) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleSaved = () => {
    onSaved?.();
    onClose();
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 sm:p-6"
      onClick={handleBackdropClick}
    >
      <div className="bg-[color:var(--md-sys-color-surface-container)] rounded-2xl sm:rounded-3xl shadow-level-4 w-full max-w-2xl max-h-[95vh] sm:max-h-[90vh] overflow-hidden animate-slide-in">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-[color:var(--md-sys-color-outline)]">
          <h2 className="text-lg sm:text-xl font-medium text-[color:var(--md-sys-color-on-surface)]">
            Създай събитие
          </h2>
          <button
            onClick={onClose}
            className="rounded-full p-2 bg-[color:var(--md-sys-color-surface-container-highest)] hover:bg-[color:var(--md-sys-color-surface-container-high)] text-[color:var(--md-sys-color-on-surface-variant)] hover:text-[color:var(--md-sys-color-on-surface)] transition-all duration-200 border border-[color:var(--md-sys-color-outline)]"
          >
            <span className="material-icons text-xl sm:text-2xl">close</span>
          </button>
        </div>
        
        {/* Modal Content */}
        <div className="p-4 sm:p-6 overflow-y-auto max-h-[calc(95vh-80px)] sm:max-h-[calc(90vh-80px)]">
          <AddEventForm onSaved={handleSaved} isDarkMode={isDarkMode} />
        </div>
      </div>
    </div>
  );
};

export default AddEventModal;