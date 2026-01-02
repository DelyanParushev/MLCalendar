import React, { useState, useEffect } from 'react';
import { DateTime } from 'luxon';

const EventViewModal = ({ isOpen, onClose, event, onUpdate, onDelete, isDarkMode }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedEvent, setEditedEvent] = useState({
    title: '',
    date: '',
    startTime: '',
    endTime: ''
  });

  useEffect(() => {
    if (event) {
      // Parse as local time without timezone conversion
      const startDt = DateTime.fromISO(event.start, { zone: 'local' });
      const endDt = event.end ? DateTime.fromISO(event.end, { zone: 'local' }) : null;
      
      setEditedEvent({
        title: event.title || '',
        date: startDt.toFormat('yyyy-MM-dd'),
        startTime: startDt.toFormat('HH:mm'),
        endTime: endDt ? endDt.toFormat('HH:mm') : ''
      });
    }
  }, [event]);

  if (!isOpen || !event) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
      setIsEditing(false);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    // Reset to original values
    if (event) {
      const startDt = DateTime.fromISO(event.start, { zone: 'local' });
      const endDt = event.end ? DateTime.fromISO(event.end, { zone: 'local' }) : null;
      
      setEditedEvent({
        title: event.title || '',
        date: startDt.toFormat('yyyy-MM-dd'),
        startTime: startDt.toFormat('HH:mm'),
        endTime: endDt ? endDt.toFormat('HH:mm') : ''
      });
    }
  };

  const handleSave = async () => {
    try {
      // Combine date and time into ISO format (keep as local time, no timezone conversion)
      const startDateTime = DateTime.fromFormat(
        `${editedEvent.date} ${editedEvent.startTime}`,
        'yyyy-MM-dd HH:mm',
        { zone: 'local' }
      );
      
      const endDateTime = editedEvent.endTime
        ? DateTime.fromFormat(
            `${editedEvent.date} ${editedEvent.endTime}`,
            'yyyy-MM-dd HH:mm',
            { zone: 'local' }
          )
        : startDateTime.plus({ hours: 1 });

      // Convert to ISO string without timezone offset (treat as local time)
      const updatedEvent = {
        title: editedEvent.title,
        start: startDateTime.toFormat("yyyy-MM-dd'T'HH:mm:ss"),
        end: endDateTime.toFormat("yyyy-MM-dd'T'HH:mm:ss")
      };

      await onUpdate(event.id, updatedEvent);
      setIsEditing(false);
      onClose();
    } catch (error) {
      console.error('Error saving event:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Сигурни ли сте, че искате да изтриете това събитие?')) {
      try {
        await onDelete(event.id);
        onClose();
      } catch (error) {
        console.error('Error deleting event:', error);
      }
    }
  };

  const formatDateTime = (isoString) => {
    return DateTime.fromISO(isoString, { zone: 'local' }).toFormat('cccc, dd LLLL yyyy, HH:mm');
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-[color:var(--md-sys-color-surface-container)] rounded-2xl sm:rounded-3xl shadow-level-4 w-full max-w-md overflow-hidden animate-slide-in">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-[color:var(--md-sys-color-outline)]">
          <h2 className="text-lg sm:text-xl font-medium text-[color:var(--md-sys-color-on-surface)]">
            {isEditing ? 'Редактирай събитие' : 'Преглед на събитие'}
          </h2>
          <button
            onClick={() => {
              onClose();
              setIsEditing(false);
            }}
            className="rounded-full p-2 bg-[color:var(--md-sys-color-surface-container-highest)] hover:bg-[color:var(--md-sys-color-surface-container-high)] text-[color:var(--md-sys-color-on-surface-variant)] hover:text-[color:var(--md-sys-color-on-surface)] transition-all duration-200 border border-[color:var(--md-sys-color-outline)]"
          >
            <span className="material-icons text-xl sm:text-2xl">close</span>
          </button>
        </div>
        
        {/* Modal Content */}
        <div className="p-4 sm:p-6">
          {!isEditing ? (
            // View Mode
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] block mb-2">
                  Заглавие
                </label>
                <div className="text-lg font-medium text-[color:var(--md-sys-color-on-surface)]">
                  {event.title}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] block mb-2">
                  Начало
                </label>
                <div className="flex items-center gap-2 text-[color:var(--md-sys-color-on-surface)]">
                  <span className="material-icons text-sm">schedule</span>
                  <span>{formatDateTime(event.start)}</span>
                </div>
              </div>

              {event.end && (
                <div>
                  <label className="text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] block mb-2">
                    Край
                  </label>
                  <div className="flex items-center gap-2 text-[color:var(--md-sys-color-on-surface)]">
                    <span className="material-icons text-sm">schedule</span>
                    <span>{formatDateTime(event.end)}</span>
                  </div>
                </div>
              )}

              {/* Action Buttons - View Mode */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleEdit}
                  className="flex-1 rounded-full px-4 py-2.5 text-sm font-medium transition-all duration-200 
                    bg-[color:var(--md-sys-color-primary)]
                    text-[color:var(--md-sys-color-on-primary)]
                    hover:bg-[color:var(--md-sys-color-primary-container)]
                    hover:text-[color:var(--md-sys-color-on-primary-container)]
                    shadow-level-1 hover:shadow-level-2
                    flex items-center justify-center gap-2"
                >
                  <span className="material-icons text-lg">edit</span>
                  Редактирай
                </button>
                <button
                  onClick={handleDelete}
                  className="rounded-full px-4 py-2.5 text-sm font-medium transition-all duration-200 
                    bg-[color:var(--md-sys-color-error-container)]
                    text-[color:var(--md-sys-color-on-error-container)]
                    hover:bg-[color:var(--md-sys-color-error)]
                    hover:text-[color:var(--md-sys-color-on-error)]
                    shadow-level-1 hover:shadow-level-2
                    flex items-center justify-center gap-2"
                >
                  <span className="material-icons text-lg">delete</span>
                  Изтрий
                </button>
              </div>
            </div>
          ) : (
            // Edit Mode
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] block mb-2">
                  Заглавие
                </label>
                <input
                  type="text"
                  value={editedEvent.title}
                  onChange={(e) => setEditedEvent({ ...editedEvent, title: e.target.value })}
                  className="w-full rounded-xl p-3 
                    bg-[color:var(--md-sys-color-surface)] 
                    border border-[color:var(--md-sys-color-outline)]
                    text-[color:var(--md-sys-color-on-surface)]
                    placeholder-[color:var(--md-sys-color-on-surface-variant)] placeholder-opacity-50
                    shadow-level-1 transition-all duration-200 
                    hover:shadow-level-2 focus:shadow-level-2 
                    focus:border-[color:var(--md-sys-color-primary)] outline-none"
                  placeholder="Заглавие на събитието"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] block mb-2">
                  Дата
                </label>
                <div className="relative">
                  <span className="material-icons absolute left-3 top-1/2 -translate-y-1/2 text-[color:var(--md-sys-color-on-surface)] pointer-events-none" style={{ fontSize: '20px' }}>
                    calendar_today
                  </span>
                  <input
                    type="date"
                    value={editedEvent.date}
                    onChange={(e) => setEditedEvent({ ...editedEvent, date: e.target.value })}
                    className="w-full rounded-xl p-3 pl-11
                      bg-[color:var(--md-sys-color-surface)] 
                      border-2 border-[color:var(--md-sys-color-outline)]
                      text-[color:var(--md-sys-color-on-surface)]
                      shadow-level-1 transition-all duration-200 
                      hover:shadow-level-2 focus:shadow-level-2 
                      focus:border-[color:var(--md-sys-color-primary)] outline-none
                      cursor-pointer font-medium"
                    style={{ minHeight: '52px', fontSize: '16px', colorScheme: isDarkMode ? 'dark' : 'light' }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] block mb-2">
                    Начален час
                  </label>
                  <div className="relative">
                    <span className="material-icons absolute left-3 top-1/2 -translate-y-1/2 text-[color:var(--md-sys-color-on-surface)] pointer-events-none" style={{ fontSize: '20px' }}>
                      schedule
                    </span>
                    <input
                      type="time"
                      value={editedEvent.startTime}
                      onChange={(e) => setEditedEvent({ ...editedEvent, startTime: e.target.value })}
                      step="900"
                      className="w-full rounded-xl p-3 pl-11
                        bg-[color:var(--md-sys-color-surface)] 
                        border-2 border-[color:var(--md-sys-color-outline)]
                        text-[color:var(--md-sys-color-on-surface)]
                        shadow-level-1 transition-all duration-200 
                        hover:shadow-level-2 focus:shadow-level-2 
                        focus:border-[color:var(--md-sys-color-primary)] outline-none
                        cursor-pointer font-medium"
                      style={{ minHeight: '52px', fontSize: '16px', colorScheme: isDarkMode ? 'dark' : 'light' }}
                    />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] block mb-2">
                    Краен час
                  </label>
                  <div className="relative">
                    <span className="material-icons absolute left-3 top-1/2 -translate-y-1/2 text-[color:var(--md-sys-color-on-surface)] pointer-events-none" style={{ fontSize: '20px' }}>
                      schedule
                    </span>
                    <input
                      type="time"
                      value={editedEvent.endTime}
                      onChange={(e) => setEditedEvent({ ...editedEvent, endTime: e.target.value })}
                      step="900"
                      className="w-full rounded-xl p-3 pl-11
                        bg-[color:var(--md-sys-color-surface)] 
                        border-2 border-[color:var(--md-sys-color-outline)]
                        text-[color:var(--md-sys-color-on-surface)]
                        shadow-level-1 transition-all duration-200 
                        hover:shadow-level-2 focus:shadow-level-2 
                        focus:border-[color:var(--md-sys-color-primary)] outline-none
                        cursor-pointer font-medium"
                      style={{ minHeight: '52px', fontSize: '16px', colorScheme: isDarkMode ? 'dark' : 'light' }}
                    />
                  </div>
                </div>
              </div>

              {/* Action Buttons - Edit Mode */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleCancel}
                  className="flex-1 rounded-full px-4 py-2.5 text-sm font-medium transition-all duration-200 
                    bg-[color:var(--md-sys-color-surface-container-highest)]
                    text-[color:var(--md-sys-color-on-surface)]
                    hover:bg-[color:var(--md-sys-color-surface-container-high)]
                    border border-[color:var(--md-sys-color-outline)]
                    shadow-level-1 hover:shadow-level-2"
                >
                  Откажи
                </button>
                <button
                  onClick={handleSave}
                  className="flex-1 rounded-full px-4 py-2.5 text-sm font-medium transition-all duration-200 
                    bg-[color:var(--md-sys-color-primary)]
                    text-[color:var(--md-sys-color-on-primary)]
                    hover:bg-[color:var(--md-sys-color-primary-container)]
                    hover:text-[color:var(--md-sys-color-on-primary-container)]
                    shadow-level-1 hover:shadow-level-2
                    flex items-center justify-center gap-2"
                >
                  <span className="material-icons text-lg">save</span>
                  Запази
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EventViewModal;
