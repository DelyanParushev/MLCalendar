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

  // Custom time indicator effect
  useEffect(() => {
    const updateTimeIndicator = () => {
      const now = new Date();
      const currentHour = now.getHours();
      const currentMinute = now.getMinutes();
      
      console.log(`Current system time: ${currentHour}:${currentMinute.toString().padStart(2, '0')}`);
      
      // Debug: List ALL FullCalendar elements to understand the structure
      console.log('=== DEBUGGING CALENDAR STRUCTURE ===');
      const allFcElements = document.querySelectorAll('[class*="fc-"]');
      console.log(`Found ${allFcElements.length} FullCalendar elements total`);
      
      // Get unique class names to understand what's available
      const uniqueClasses = new Set();
      allFcElements.forEach(el => {
        el.classList.forEach(cls => {
          if (cls.includes('fc-')) uniqueClasses.add(cls);
        });
      });
      console.log('Available FullCalendar classes:', Array.from(uniqueClasses).sort());
      
      // Check what view we're in using multiple methods
      const calendarView = document.querySelector('.fc-view');
      const viewClasses = calendarView ? calendarView.className : '';
      console.log(`Calendar view classes: "${viewClasses}"`);
      
      // Check for current view type specifically
      const currentViewElement = document.querySelector('.fc-view');
      if (currentViewElement) {
        const classList = Array.from(currentViewElement.classList);
        console.log('Current view element classes:', classList);
        
        const isMonthView = classList.some(cls => cls.includes('month') || cls.includes('dayGrid'));
        const isWeekView = classList.some(cls => cls.includes('week') || cls.includes('timeGrid'));
        const isDayView = classList.some(cls => cls.includes('day') && cls.includes('timeGrid'));
        
        console.log(`View type detection: Month=${isMonthView}, Week=${isWeekView}, Day=${isDayView}`);
        
        if (isMonthView) {
          console.log('🗓️ You are in MONTH view - time indicator only works in WEEK or DAY view');
          console.log('👆 Please click "Week" or "Day" button in the calendar toolbar to see the time indicator');
          return;
        }
      }
      
      // Also check for specific view type elements
      const hasTimeGrid = document.querySelector('.fc-timegrid-view') || 
                          document.querySelector('.fc-timeGridWeek-view') || 
                          document.querySelector('.fc-timeGridDay-view') ||
                          document.querySelector('[class*="timegrid"]') ||
                          document.querySelector('[class*="timeGrid"]');
      
      const hasTimeSlots = document.querySelector('.fc-timegrid-slot') || 
                          document.querySelector('.fc-timegrid-axis') ||
                          document.querySelector('[class*="timegrid-slot"]');
      
      console.log(`Has time grid elements: ${!!hasTimeGrid}, Has time slots: ${!!hasTimeSlots}`);
      
      // Only proceed if we can find time grid elements (more reliable than class checking)
      if (!hasTimeGrid && !hasTimeSlots) {
        console.log('❌ Not in a time grid view - no time grid elements found');
        console.log('💡 To see the current time indicator:');
        console.log('   1. Look for buttons like "Month", "Week", "Day" at the top of the calendar');
        console.log('   2. Click on "Week" or "Day" button');
        console.log('   3. The red time indicator line will appear');
        return;
      }
      
      console.log('✅ Time grid view detected - proceeding with indicator');
      console.log('=== END DEBUG INFO ===');
      
      // Wait a bit for FullCalendar to fully render time grid elements
      setTimeout(() => {
        // Find time grid views and add indicator using multiple selectors
        const timeGridBodies = document.querySelectorAll('.fc-timegrid-body');
        const alternativeBodies = document.querySelectorAll('.fc-scroller[class*="body"]');
        const allBodies = [...timeGridBodies, ...alternativeBodies].filter((body, index, arr) => 
          arr.indexOf(body) === index // Remove duplicates
        );
        
        console.log(`Found ${timeGridBodies.length} time grid bodies, ${alternativeBodies.length} alternative bodies, ${allBodies.length} total unique bodies`);
        
        if (allBodies.length === 0) {
          console.log('No time grid body elements found - trying to add indicator to time grid container');
          
          // Fallback: add to any time grid container we can find
          const timeGridContainer = document.querySelector('.fc-timegrid') || 
                                   document.querySelector('[class*="timegrid"]');
          
          if (timeGridContainer) {
            allBodies.push(timeGridContainer);
            console.log('Added time grid container as fallback body');
          }
        }
        
        allBodies.forEach((body, bodyIndex) => {
          // Remove existing indicator
          const existingIndicator = body.querySelector('.custom-time-indicator');
          if (existingIndicator) {
            existingIndicator.remove();
          }

          // Get all time slots to understand the structure
          const timeSlots = body.querySelectorAll('.fc-timegrid-slot');
          console.log(`Body ${bodyIndex}: Found ${timeSlots.length} time slots`);
          
          if (timeSlots.length > 0) {
            // Get the first slot to determine slot height
            const slotHeight = timeSlots[0].offsetHeight;
            console.log(`Body ${bodyIndex}: Slot height: ${slotHeight}px`);
            
            // Try multiple ways to find the first time label
            const timeLabels = document.querySelectorAll('.fc-timegrid-slot-label, .fc-timegrid-axis-cushion');
            console.log(`Found ${timeLabels.length} time labels`);
            
            let startHour = 0;
            let firstTimeLabelText = '00:00';
            
            if (timeLabels.length > 0) {
              // Filter out "all-day" labels and find the first actual time
              const actualTimeLabels = Array.from(timeLabels).filter(label => {
                const text = label.textContent.trim();
                return text.includes(':') || text.match(/\d+(AM|PM)/);
              });
              
              if (actualTimeLabels.length > 0) {
                firstTimeLabelText = actualTimeLabels[0].textContent.trim();
              } else if (timeLabels.length > 1) {
                // If no time format found, try the second label (skip all-day)
                firstTimeLabelText = timeLabels[1].textContent.trim();
              }
              
              console.log(`First actual time label text: "${firstTimeLabelText}"`);
              
              // Try to parse the time - handle different formats
              if (firstTimeLabelText.includes(':')) {
                const timePart = firstTimeLabelText.split(':')[0];
                startHour = parseInt(timePart) || 0;
              } else if (firstTimeLabelText.includes('AM') || firstTimeLabelText.includes('PM')) {
                // Handle 12-hour format
                const match = firstTimeLabelText.match(/(\d+)/);
                if (match) {
                  startHour = parseInt(match[1]);
                  if (firstTimeLabelText.includes('PM') && startHour !== 12) {
                    startHour += 12;
                  } else if (firstTimeLabelText.includes('AM') && startHour === 12) {
                    startHour = 0;
                  }
                }
              } else if (firstTimeLabelText === 'all-day') {
                // Default to 6 AM if we still got all-day
                startHour = 6;
                console.log('Using default start hour of 6 AM since only all-day label found');
              }
            }
            
            console.log(`Body ${bodyIndex}: Calendar starts at hour: ${startHour}`);
            
            // Calculate position relative to the calendar's start time
            const hoursFromStart = currentHour - startHour + (currentMinute / 60);
            const topPosition = hoursFromStart * slotHeight;
            
            console.log(`Body ${bodyIndex}: Hours from start: ${hoursFromStart.toFixed(2)}, Position: ${topPosition}px`);
            
            // Only add indicator if current time is within reasonable range
            if (hoursFromStart >= -1 && topPosition >= -slotHeight) {
              const indicator = document.createElement('div');
              indicator.className = 'custom-time-indicator';
              indicator.style.top = `${Math.max(0, topPosition)}px`;
              body.appendChild(indicator);
              console.log(`Body ${bodyIndex}: ✅ Indicator added at position: ${Math.max(0, topPosition)}px`);
            } else {
              console.log(`Body ${bodyIndex}: Current time is outside visible range (hours from start: ${hoursFromStart.toFixed(2)})`);
            }
          } else {
            console.log(`Body ${bodyIndex}: No time slots found in this body`);
          }
        });
      }, 200); // Reduced timeout since we're being more aggressive about detection
    };

    // Update immediately and then every minute
    const interval = setInterval(updateTimeIndicator, 60000);
    updateTimeIndicator();

    return () => clearInterval(interval);
  }, []);

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
              <h1 className="text-2xl sm:text-4xl font-medium transition-colors duration-200">Caltivity</h1>
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
                firstDay={1} // Start week from Monday (1) instead of Sunday (0)
                nowIndicator={false} // Disable built-in indicator, using custom one
                datesSet={() => {
                  // Update custom time indicator when view changes
                  setTimeout(() => {
                    const updateTimeIndicator = () => {
                      const now = new Date();
                      const currentHour = now.getHours();
                      const currentMinute = now.getMinutes();

                      // Find time grid views and add indicator
                      const timeGridBodies = document.querySelectorAll('.fc-timegrid-body');
                      timeGridBodies.forEach(body => {
                        // Remove existing indicator
                        const existingIndicator = body.querySelector('.custom-time-indicator');
                        if (existingIndicator) {
                          existingIndicator.remove();
                        }

                        // Only add indicator if we're in a time grid view
                        const viewType = document.querySelector('.fc-view')?.className || '';
                        if (viewType.includes('fc-timegrid')) {
                          // Get the actual slot height from FullCalendar
                          const timeSlots = body.querySelectorAll('.fc-timegrid-slot');
                          if (timeSlots.length > 0) {
                            const slotHeight = timeSlots[0].offsetHeight;
                            
                            // Find what time the first slot represents
                            const firstTimeLabel = document.querySelector('.fc-timegrid-slot-label');
                            const firstTimeLabelText = firstTimeLabel ? firstTimeLabel.textContent : '00:00';
                            
                            // Parse the first time slot time
                            let startHour = 0;
                            if (firstTimeLabelText.includes(':')) {
                              const parts = firstTimeLabelText.split(':');
                              startHour = parseInt(parts[0]);
                            }
                            
                            // Calculate position relative to the calendar's start time
                            const hoursFromStart = currentHour - startHour + (currentMinute / 60);
                            const topPosition = hoursFromStart * slotHeight;
                            
                            // Only add indicator if current time is within the visible range
                            if (hoursFromStart >= 0 && topPosition >= 0) {
                              const indicator = document.createElement('div');
                              indicator.className = 'custom-time-indicator';
                              indicator.style.top = `${topPosition}px`;
                              body.appendChild(indicator);
                            }
                          }
                        }
                      });
                    };
                    updateTimeIndicator();
                  }, 100);
                }}
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
