import React, { useState, useEffect } from 'react';
import { DateTime } from 'luxon';

const EventViewModal = ({ isOpen, onClose, event, onUpdate, onDelete, isDarkMode }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showStartTimePicker, setShowStartTimePicker] = useState(false);
  const [showEndTimePicker, setShowEndTimePicker] = useState(false);
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
    setShowStartTimePicker(false);
    setShowEndTimePicker(false);
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
      // Close any open dropdowns
      setShowStartTimePicker(false);
      setShowEndTimePicker(false);
      
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

  // Generate time options (00:00 to 23:55 in 5-minute intervals)
  const generateTimeOptions = () => {
    const options = [];
    for (let hour = 0; hour < 24; hour++) {
      for (let minute = 0; minute < 60; minute += 5) {
        const h = hour.toString().padStart(2, '0');
        const m = minute.toString().padStart(2, '0');
        options.push(`${h}:${m}`);
      }
    }
    return options;
  };

  const timeOptions = generateTimeOptions();

  // Format date for display
  const formatDateDisplay = (dateStr) => {
    if (!dateStr) return '';
    return DateTime.fromFormat(dateStr, 'yyyy-MM-dd').toFormat('dd LLLL yyyy');
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
                  <input
                    type="date"
                    value={editedEvent.date}
                    onChange={(e) => setEditedEvent({ ...editedEvent, date: e.target.value })}
                    className="w-full rounded-xl p-3 
                      bg-[color:var(--md-sys-color-surface)] 
                      border border-[color:var(--md-sys-color-outline)]
                      text-[color:var(--md-sys-color-on-surface)]
                      shadow-level-1 transition-all duration-200 
                      hover:shadow-level-2 focus:shadow-level-2 
                      focus:border-[color:var(--md-sys-color-primary)] outline-none
                      cursor-pointer"
                    style={{ minHeight: '44px' }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="relative">
                  <label className="text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] block mb-2">
                    Начален час
                  </label>
                  <div className="relative">
                    <button
                      type="button"
                      onClick={() => {
                        setShowStartTimePicker(!showStartTimePicker);
                        setShowEndTimePicker(false);
                      }}
                      className="w-full rounded-xl p-3 
                        bg-[color:var(--md-sys-color-surface)] 
                        border border-[color:var(--md-sys-color-outline)]
                        text-[color:var(--md-sys-color-on-surface)]
                        shadow-level-1 transition-all duration-200 
                        hover:shadow-level-2 focus:shadow-level-2 
                        focus:border-[color:var(--md-sys-color-primary)] outline-none
                        cursor-pointer text-left flex items-center justify-between"
                      style={{ minHeight: '44px' }}
                    >
                      <span>{editedEvent.startTime || 'Select time'}</span>
                      <span className="material-icons text-sm">schedule</span>
                    </button>
                    {showStartTimePicker && (
                      <div className="absolute z-50 w-full mt-1 bg-[color:var(--md-sys-color-surface-container)] border border-[color:var(--md-sys-color-outline)] rounded-xl shadow-level-3 max-h-60 overflow-y-auto">
                        {timeOptions.map((time) => (
                          <button
                            key={time}
                            type="button"
                            onClick={() => {
                              setEditedEvent({ ...editedEvent, startTime: time });
                              setShowStartTimePicker(false);
                            }}
                            className={`w-full px-3 py-2 text-left hover:bg-[color:var(--md-sys-color-surface-container-high)] transition-colors ${
                              editedEvent.startTime === time ? 'bg-[color:var(--md-sys-color-primary-container)] text-[color:var(--md-sys-color-on-primary-container)]' : ''
                            }`}
                          >
                            {time}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="relative">
                  <label className="text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] block mb-2">
                    Краен час
                  </label>
                  <div className="relative">
                    <button
                      type="button"
                      onClick={() => {
                        setShowEndTimePicker(!showEndTimePicker);
                        setShowStartTimePicker(false);
                      }}
                      className="w-full rounded-xl p-3 
                        bg-[color:var(--md-sys-color-surface)] 
                        border border-[color:var(--md-sys-color-outline)]
                        text-[color:var(--md-sys-color-on-surface)]
                        shadow-level-1 transition-all duration-200 
                        hover:shadow-level-2 focus:shadow-level-2 
                        focus:border-[color:var(--md-sys-color-primary)] outline-none
                        cursor-pointer text-left flex items-center justify-between"
                      style={{ minHeight: '44px' }}
                    >
                      <span>{editedEvent.endTime || 'Select time'}</span>
                      <span className="material-icons text-sm">schedule</span>
                    </button>
                    {showEndTimePicker && (
                      <div className="absolute z-50 w-full mt-1 bg-[color:var(--md-sys-color-surface-container)] border border-[color:var(--md-sys-color-outline)] rounded-xl shadow-level-3 max-h-60 overflow-y-auto">
                        {timeOptions.map((time) => (
                          <button
                            key={time}
                            type="button"
                            onClick={() => {
                              setEditedEvent({ ...editedEvent, endTime: time });
                              setShowEndTimePicker(false);
                            }}
                            className={`w-full px-3 py-2 text-left hover:bg-[color:var(--md-sys-color-surface-container-high)] transition-colors ${
                              editedEvent.endTime === time ? 'bg-[color:var(--md-sys-color-primary-container)] text-[color:var(--md-sys-color-on-primary-container)]' : ''
                            }`}
                          >
                            {time}
                          </button>
                        ))}
                      </div>
                    )}
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
