import { useState, useEffect, useRef } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import './TimeSelector.css';

export default function TimeSelector({ selectedDateTime, onDateTimeChange, onDurationChange }) {
  const now = new Date();
  const [selectedDate, setSelectedDate] = useState(now);
  const [selectedHour, setSelectedHour] = useState(now.getHours() % 12 || 12);
  const [selectedMinute, setSelectedMinute] = useState(Math.floor(now.getMinutes() / 15) * 15);
  const [selectedPeriod, setSelectedPeriod] = useState(now.getHours() >= 12 ? 'PM' : 'AM');
  const [duration, setDuration] = useState(2);
  const [durationInput, setDurationInput] = useState('2');
  const durationTimeoutRef = useRef(null);

  // Update parent whenever date/time changes
  useEffect(() => {
    updateDateTime();
  }, [selectedDate, selectedHour, selectedMinute, selectedPeriod]);

  useEffect(() => {
    if (onDurationChange) {
      onDurationChange(2);
    }
  }, []);

  const updateDateTime = () => {
    const datetime = new Date(selectedDate);
    let hour24 = selectedHour;

    if (selectedPeriod === 'PM' && selectedHour !== 12) {
      hour24 = selectedHour + 12;
    } else if (selectedPeriod === 'AM' && selectedHour === 12) {
      hour24 = 0;
    }

    datetime.setHours(hour24, selectedMinute, 0, 0);

    // Format as YYYY-MM-DDTHH:mm:ss in LOCAL time (not UTC)
    const year = datetime.getFullYear();
    const month = String(datetime.getMonth() + 1).padStart(2, '0');
    const day = String(datetime.getDate()).padStart(2, '0');
    const hours = String(datetime.getHours()).padStart(2, '0');
    const minutes = String(datetime.getMinutes()).padStart(2, '0');
    const seconds = String(datetime.getSeconds()).padStart(2, '0');

    const localDateTimeString = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
    onDateTimeChange(localDateTimeString);
  };

  const handleDateChange = (date) => {
    if (date) {
      setSelectedDate(date);
    }
  };

  const handleHourChange = (e) => {
    setSelectedHour(parseInt(e.target.value));
  };

  const handleMinuteChange = (e) => {
    setSelectedMinute(parseInt(e.target.value));
  };

  const handlePeriodChange = (e) => {
    setSelectedPeriod(e.target.value);
  };

  const setToNow = () => {
    const now = new Date();
    setSelectedDate(now);
    setSelectedHour(now.getHours() % 12 || 12);
    setSelectedMinute(Math.floor(now.getMinutes() / 15) * 15);
    setSelectedPeriod(now.getHours() >= 12 ? 'PM' : 'AM');
  };

  const handleDurationInputChange = (e) => {
    const value = e.target.value;
    setDurationInput(value);

    // Clear existing timeout
    if (durationTimeoutRef.current) {
      clearTimeout(durationTimeoutRef.current);
    }

    // Set new timeout for debouncing
    durationTimeoutRef.current = setTimeout(() => {
      const parsedValue = parseInt(value);
      if (!isNaN(parsedValue) && parsedValue >= 1 && parsedValue <= 12) {
        setDuration(parsedValue);
        if (onDurationChange) {
          onDurationChange(parsedValue);
        }
      } else if (value === '' || isNaN(parsedValue)) {
        // Allow empty input during editing, but default to 1 if left empty
        const defaultValue = 1;
        setDuration(defaultValue);
        setDurationInput(defaultValue.toString());
        if (onDurationChange) {
          onDurationChange(defaultValue);
        }
      }
    }, 500);
  };

  const handleDurationBlur = () => {
    // On blur, ensure we have a valid value
    const parsedValue = parseInt(durationInput);
    if (isNaN(parsedValue) || parsedValue < 1) {
      setDurationInput('1');
      setDuration(1);
      if (onDurationChange) {
        onDurationChange(1);
      }
    } else if (parsedValue > 12) {
      setDurationInput('12');
      setDuration(12);
      if (onDurationChange) {
        onDurationChange(12);
      }
    } else {
      setDurationInput(parsedValue.toString());
    }
  };

  // Generate current combined datetime for display
  const getDisplayDateTime = () => {
    const datetime = new Date(selectedDate);
    let hour24 = selectedHour;

    if (selectedPeriod === 'PM' && selectedHour !== 12) {
      hour24 = selectedHour + 12;
    } else if (selectedPeriod === 'AM' && selectedHour === 12) {
      hour24 = 0;
    }

    datetime.setHours(hour24, selectedMinute, 0, 0);
    return datetime;
  };

  return (
    <div className="time-selector">
      <h3>Select Date and Time</h3>

      <div className="time-inputs">
        <div className="input-group date-picker-group">
          <label htmlFor="date-input">Date</label>
          <DatePicker
            id="date-input"
            selected={selectedDate}
            onChange={handleDateChange}
            dateFormat="MMMM d, yyyy"
            minDate={new Date('2020-01-01')}
            maxDate={new Date('2025-12-31')}
            className="date-picker-input"
            calendarClassName="wsu-calendar"
          />
        </div>

        <div className="input-group time-selectors">
          <label>Time</label>
          <div className="time-dropdowns">
            <select
              value={selectedHour}
              onChange={handleHourChange}
              className="time-select hour-select"
            >
              {[12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map(h => (
                <option key={h} value={h}>{h}</option>
              ))}
            </select>
            <span className="time-separator">:</span>
            <select
              value={selectedMinute}
              onChange={handleMinuteChange}
              className="time-select minute-select"
            >
              {[0, 15, 30, 45].map(m => (
                <option key={m} value={m}>{m.toString().padStart(2, '0')}</option>
              ))}
            </select>
            <select
              value={selectedPeriod}
              onChange={handlePeriodChange}
              className="time-select period-select"
            >
              <option value="AM">AM</option>
              <option value="PM">PM</option>
            </select>
          </div>
        </div>

        <div className="input-group">
          <label htmlFor="duration-input">Parking Duration (hours)</label>
          <input
            id="duration-input"
            type="number"
            min="1"
            max="12"
            value={durationInput}
            onChange={handleDurationInputChange}
            onBlur={handleDurationBlur}
            placeholder="1-12 hours"
          />
        </div>
      </div>

      <button className="now-button" onClick={setToNow}>
        Set to Current Time
      </button>

      <div className="selected-time">
        Selected: {getDisplayDateTime().toLocaleString('en-US', {
          month: 'long',
          day: 'numeric',
          year: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        })}
      </div>
    </div>
  );
}
