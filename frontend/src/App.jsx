import React, { useState, useEffect } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { DateTime } from "luxon";
import AddEventForm from "./components/AddEventForm";
import AuthForm from "./components/AuthForm";
import UserProfile from "./components/UserProfile";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { listEvents, deleteEvent } from "./services/api";
import "@material-design-icons/font";
import "./fonts.css";
import "./calendar.css";
import "./App.css";

function CalendarApp() {
  const [events, setEvents] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const { isAuthenticated, loading } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      fetchEvents();
    }
    
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialDarkMode = savedTheme === 'dark' || (savedTheme === null && prefersDark);
    
    setIsDarkMode(initialDarkMode);
    document.documentElement.classList.toggle('dark', initialDarkMode);

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e) => {
      if (localStorage.getItem('theme') === null) {
        setIsDarkMode(e.matches);
        document.documentElement.classList.toggle('dark', e.matches);
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [isAuthenticated]);

  const fetchEvents = async () => {
    try {
      const data = await listEvents();
      setEvents(data);
    } catch (error) {
      console.error("Error fetching events:", error);
    }
  };

  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    document.documentElement.classList.toggle('dark', newDarkMode);
    localStorage.setItem('theme', newDarkMode ? 'dark' : 'light');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[color:var(--md-sys-color-surface)]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-[color:var(--md-sys-color-primary)] border-t-transparent rounded-full animate-spin"></div>
          <p className="text-[color:var(--md-sys-color-on-surface-variant)]">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthForm />;
  }

  return (
    <div className="min-h-screen transition-colors duration-200 ease-in-out bg-[color:var(--md-sys-color-surface)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <header className="flex justify-between items-center mb-6 sm:mb-8 relative">
          <div className="flex items-center gap-2 sm:gap-4">
            <div className="flex items-center gap-2 sm:gap-3 text-[color:var(--md-sys-color-on-surface-variant)]">
              <span className="material-icons text-2xl sm:text-3xl text-[color:var(--md-sys-color-primary)]">calendar_today</span>
              <h1 className="text-2xl sm:text-4xl font-medium transition-colors duration-200">NLP Calendar</h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <UserProfile />
            <button
              onClick={toggleDarkMode}
              className="rounded-full p-3 transition-all duration-200 bg-[color:var(--md-sys-color-surface-container-highest)] text-[color:var(--md-sys-color-on-surface-variant)] hover:bg-[color:var(--md-sys-color-surface-container-high)] shadow-level-1 hover:shadow-level-2 focus:ring-2 focus:ring-[color:var(--md-sys-color-primary)] focus:ring-opacity-20 outline-none"
              aria-label="Toggle dark mode"
            >
              <span className="material-icons text-2xl">
                {isDarkMode ? "light_mode" : "dark_mode"}
              </span>
            </button>
          </div>
        </header>

        <div className="space-y-8">
          <div className="overflow-hidden rounded-3xl shadow-level-2 bg-[color:var(--md-sys-color-surface-container)] border border-[color:var(--md-sys-color-outline)] transition-all duration-200 hover:shadow-level-4">
            <div className="p-4 sm:p-8">
              <AddEventForm onSaved={fetchEvents} />
            </div>
          </div>

          <div className="overflow-hidden rounded-3xl shadow-level-2 bg-[color:var(--md-sys-color-surface-container)] border border-[color:var(--md-sys-color-outline)] transition-all duration-200 hover:shadow-level-4">
            <div className="p-2 sm:p-8">
              <FullCalendar
                plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
                initialView="dayGridMonth"
                slotLabelFormat={{
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                }}
                eventTimeFormat={{
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                }}
                headerToolbar={{
                  left: "prev,next today",
                  center: "title",
                  right: "dayGridMonth,timeGridWeek,timeGridDay",
                }}
                events={events.map((e) => ({
                  id: e.id,
                  title: e.title,
                  start: DateTime.fromISO(e.start).toISO(),
                  end: e.end ? DateTime.fromISO(e.end).toISO() : undefined,
                  className: "animate-fade-in rounded-xl",
                  extendedProps: {
                    originalEvent: e
                  }
                }))}
                eventContent={(arg) => {
                  const startTime = arg.event.start ? DateTime.fromJSDate(arg.event.start).toFormat('HH:mm') : '';
                  return (
                    <div className="flex flex-col min-h-[3rem] p-1 relative group">
                      <div className="flex items-center justify-between gap-1 mb-1">
                        <div className="text-xs opacity-80">{startTime}</div>
                        <button
                          className="material-icons text-[14px] opacity-0 group-hover:opacity-100 cursor-pointer hover:bg-[color:var(--md-sys-color-on-primary)] hover:bg-opacity-10 transition-all rounded-full w-5 h-5 flex items-center justify-center"
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent event click from triggering
                            if (window.confirm('Are you sure you want to delete this event?')) {
                              deleteEvent(arg.event.id)
                                .then(() => fetchEvents())
                                .catch((error) => {
                                  console.error('Error deleting event:', error);
                                  alert('Failed to delete event');
                                });
                            }
                          }}
                        >
                          delete
                        </button>
                      </div>
                      <div className="break-words text-sm leading-tight whitespace-normal overflow-hidden">{arg.event.title}</div>
                    </div>
                  )
                }}
                height="auto"
                themeSystem="standard"
                dayMaxEvents={true}
                eventDisplay="block"
                eventBackgroundColor="var(--md-sys-color-primary)"
                eventBorderColor="var(--md-sys-color-primary)"
                eventTextColor="var(--md-sys-color-on-primary)"
                dayCellClassNames="rounded-lg transition-colors duration-200 bg-[color:var(--md-sys-color-surface-container-highest)] text-[color:var(--md-sys-color-on-surface)] hover:bg-[color:var(--md-sys-color-surface-container-high)]"
                dayHeaderClassNames="font-medium text-[color:var(--md-sys-color-on-surface-variant)]"
                viewClassNames="bg-[color:var(--md-sys-color-surface-container-highest)] text-[color:var(--md-sys-color-on-surface)]"
                buttonText={{
                  today: 'Today',
                  month: 'Month',
                  week: 'Week',
                  day: 'Day'
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <CalendarApp />
    </AuthProvider>
  );
}

export default App;
