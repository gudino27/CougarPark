import { useState, useEffect, useRef } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import './TimeSelector.css';

export default function TimeSelector({ selectedDateTime, onDateTimeChange, onDurationChange }) {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [duration, setDuration] = useState(2);
  const [durationInput, setDurationInput] = useState('2');
  const durationTimeoutRef = useRef(null);

  useEffect(() => {
    const now = new Date();
    setSelectedDate(now);
    onDateTimeChange(now.toISOString());
    if (onDurationChange) {
      onDurationChange(2);
    }
  }, []);

  const handleDateTimeChange = (date) => {
    if (date) {
      setSelectedDate(date);
      onDateTimeChange(date.toISOString());
    }
  };

  const setToNow = () => {
    const now = new Date();
    setSelectedDate(now);
    onDateTimeChange(now.toISOString());
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

  return (
    <div className="time-selector">
      <h3>Select Date and Time</h3>

      <div className="time-inputs">
        <div className="input-group datetime-picker-group">
          <label htmlFor="datetime-input">Date & Time</label>
          <DatePicker
            id="datetime-input"
            selected={selectedDate}
            onChange={handleDateTimeChange}
            showTimeSelect
            timeFormat="HH:mm"
            timeIntervals={15}
            dateFormat="MMMM d, yyyy h:mm aa"
            minDate={new Date('2020-01-01')}
            maxDate={new Date('2025-12-31')}
            className="datetime-picker-input"
            calendarClassName="wsu-calendar"
          />
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

      {selectedDate && (
        <div className="selected-time">
          Selected: {selectedDate.toLocaleString()}
        </div>
      )}
    </div>
  );
}
