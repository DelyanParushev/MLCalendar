import React, { useState } from 'react';
import { DateTime } from 'luxon';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';

const ListView = ({ events, onEventDelete, onDateSelect, selectedDate, onAddEventClick }) => {
  // Get events for the selected date
  const selectedDateStr = DateTime.fromJSDate(selectedDate).toFormat('yyyy-MM-dd');
  const eventsForSelectedDate = events.filter(event => {
    const eventStart = DateTime.fromISO(event.start, { setZone: true });
    return eventStart.toFormat('yyyy-MM-dd') === selectedDateStr;
  }).sort((a, b) => DateTime.fromISO(a.start, { setZone: true }).toMillis() - DateTime.fromISO(b.start, { setZone: true }).toMillis());

  const formatTime = (isoString) => {
    // Parse as local time instead of UTC
    return DateTime.fromISO(isoString, { setZone: true }).toFormat('HH:mm');
  };

  const formatDateTwoLines = (date) => {
    const dt = DateTime.fromJSDate(date);
    const dayName = dt.toFormat('cccc'); // Sunday, Monday, etc.
    const dateString = dt.toFormat('dd LLLL yyyy'); // 28 September 2025
    return { dayName, dateString };
  };

  const handleDateClick = (arg) => {
    onDateSelect(arg.date);
  };

  return (
    <div className="space-y-4 flex flex-col items-center">
      {/* Calendar Grid - Compact for List View */}
      <div className="rounded-2xl shadow-level-2 bg-[color:var(--md-sys-color-surface-container)] border border-[color:var(--md-sys-color-outline)] overflow-hidden" style={{ width: '380px', maxWidth: '380px' }}>
        <div className="list-view-calendar rounded-2xl overflow-hidden" style={{ width: '380px', maxWidth: '380px', overflow: 'hidden', margin: '0 auto' }}>
          <FullCalendar
            plugins={[dayGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            firstDay={1}
            height={420} // Increased height to show full calendar with last row
            aspectRatio={1.0} // Square aspect ratio
            dateClick={handleDateClick}
          headerToolbar={{
            left: "prev,next",
            center: "title",
            right: "today",
          }}
          events={events.map((e) => ({
            id: e.id,
            title: e.title,
            start: e.start, // Use raw datetime string, don't convert timezone
            end: e.end || undefined, // Use raw datetime string
            className: "rounded-lg",
            display: 'background', // Show as background color to indicate there are events
          }))}
          dayMaxEvents={false} // Don't show event titles on the calendar
          eventDisplay="none" // Don't show events as blocks, we'll add dots instead
          dayCellClassNames={(arg) => {
            const cellDateStr = DateTime.fromJSDate(arg.date).toFormat('yyyy-MM-dd');
            const isSelected = cellDateStr === selectedDateStr;
            const hasEvents = events.some(event => {
              const eventStart = DateTime.fromISO(event.start, { setZone: true });
              return eventStart.toFormat('yyyy-MM-dd') === cellDateStr;
            });
            
            return `rounded-lg transition-colors duration-200 cursor-pointer relative ${
              isSelected 
                ? 'bg-[color:var(--md-sys-color-primary)] text-[color:var(--md-sys-color-on-primary)] ring-2 ring-[color:var(--md-sys-color-primary)]' 
                : 'bg-[color:var(--md-sys-color-surface-container-highest)] text-[color:var(--md-sys-color-on-surface)] hover:bg-[color:var(--md-sys-color-surface-container-high)]'
            } ${hasEvents ? 'has-events' : ''}`;
          }}
          dayCellContent={(arg) => {
            const cellDateStr = DateTime.fromJSDate(arg.date).toFormat('yyyy-MM-dd');
            const isSelected = cellDateStr === selectedDateStr;
            const hasEvents = events.some(event => {
              const eventStart = DateTime.fromISO(event.start, { setZone: true });
              return eventStart.toFormat('yyyy-MM-dd') === cellDateStr;
            });
            
            return (
              <div className="w-full h-full flex flex-col items-center justify-center relative">
                <span className="text-sm font-medium">{arg.dayNumberText}</span>
                {hasEvents && (
                  <div className="w-1.5 h-1.5 rounded-full mt-1" style={{
                    backgroundColor: isSelected ? '#ffffff' : '#ff1361'
                  }}></div>
                )}
              </div>
            );
          }}
          dayHeaderClassNames="font-medium text-[color:var(--md-sys-color-on-surface-variant)] text-xs py-2"
          viewClassNames="bg-[color:var(--md-sys-color-surface-container-highest)] text-[color:var(--md-sys-color-on-surface)]"
        />
        </div>
      </div>

      {/* Events List */}
      <div 
        className="rounded-2xl shadow-level-2 bg-[color:var(--md-sys-color-surface-container)] border border-[color:var(--md-sys-color-outline)] overflow-hidden"
        style={{ width: '380px', minWidth: '380px', maxWidth: '380px' }}
      >
        <div 
          className="bg-[color:var(--md-sys-color-surface-container-high)] border-b border-[color:var(--md-sys-color-outline)]"
          style={{ padding: '16px', width: '380px', minWidth: '380px', maxWidth: '380px', boxSizing: 'border-box' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
            <div style={{ textAlign: 'left', flex: '1', minWidth: '0', maxWidth: '280px' }}>
              <div className="text-sm font-medium text-[color:var(--md-sys-color-on-surface)]">
                {formatDateTwoLines(selectedDate).dayName}
              </div>
              <div className="text-xs font-medium text-[color:var(--md-sys-color-on-surface-variant)]">
                {formatDateTwoLines(selectedDate).dateString}
              </div>
              <p className="text-xs text-[color:var(--md-sys-color-on-surface-variant)]" style={{ marginTop: '4px' }}>
                {eventsForSelectedDate.length} {eventsForSelectedDate.length === 1 ? 'събитие' : 'събития'}
              </p>
            </div>
            <div style={{ flexShrink: '0', width: 'auto' }}>
            <button
              onClick={onAddEventClick}
              className="rounded-full bg-[color:var(--md-sys-color-primary)] text-[color:var(--md-sys-color-on-primary)] hover:bg-[color:var(--md-sys-color-primary-container)] hover:text-[color:var(--md-sys-color-on-primary-container)] transition-all duration-200 shadow-level-1 hover:shadow-level-2 font-medium"
              style={{ padding: '8px 12px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <span className="material-icons" style={{ fontSize: '18px' }}>add</span>
              <span>Създай</span>
            </button>
            </div>
          </div>
        </div>

        <div 
          className="max-h-80 overflow-y-auto"
          style={{ width: '380px', minWidth: '380px', maxWidth: '380px' }}
        >
          {eventsForSelectedDate.length === 0 ? (
            <div className="p-4 text-center">
              <div className="flex flex-col items-center gap-3">
                <span className="material-icons text-3xl text-[color:var(--md-sys-color-on-surface-variant)] opacity-50">
                  event_note
                </span>
                <p className="text-[color:var(--md-sys-color-on-surface-variant)] text-sm">
                  Няма събития за този ден
                </p>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-[color:var(--md-sys-color-outline)]">
              {eventsForSelectedDate.map((event) => (
                <div
                  key={event.id}
                  className="hover:bg-[color:var(--md-sys-color-surface-container-high)] transition-colors duration-200 group"
                  style={{ padding: '12px 16px', width: '380px', minWidth: '380px', maxWidth: '380px', boxSizing: 'border-box' }}
                >
                  <div style={{ position: 'relative', width: '100%', minHeight: '40px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ position: 'absolute', left: '0px', top: '50%', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', width: 'calc(100% - 100px)' }}>
                      <div style={{ 
                        width: '6px', 
                        height: '6px', 
                        borderRadius: '50%', 
                        backgroundColor: '#ff1361',
                        flexShrink: '0'
                      }}></div>
                      <h4 
                        className="font-medium text-[color:var(--md-sys-color-on-surface)] break-words"
                        style={{ 
                          fontSize: '15px',
                          margin: '0',
                          paddingLeft: '8px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}
                      >
                        {event.title}
                      </h4>
                    </div>
                    <div style={{ position: 'absolute', right: '0px', top: '50%', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div className="text-xs text-[color:var(--md-sys-color-on-surface-variant)]" style={{ textAlign: 'right', lineHeight: '1.2' }}>
                        <div>{formatTime(event.start)}</div>
                        {event.end && <div>{formatTime(event.end)}</div>}
                      </div>
                      <button
                        onClick={() => {
                          if (window.confirm('Сигурни ли сте, че искате да изтриете това събитие?')) {
                            onEventDelete(event.id);
                          }
                        }}
                        className="material-icons rounded-full opacity-0 group-hover:opacity-100 cursor-pointer bg-[color:var(--md-sys-color-surface-container)] hover:bg-[color:var(--md-sys-color-error-container)] text-[color:var(--md-sys-color-on-surface-variant)] hover:text-[color:var(--md-sys-color-on-error-container)] transition-all duration-200 border border-[color:var(--md-sys-color-outline)]"
                        style={{ 
                          width: '28px', 
                          height: '28px', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center', 
                          fontSize: '16px',
                          flexShrink: '0'
                        }}
                      >
                        delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ListView;