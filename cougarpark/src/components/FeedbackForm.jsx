import { useState } from 'react';
import { API_URL } from '../config';
import './FeedbackForm.css';

export default function FeedbackForm({ prediction, onFeedbackSubmitted }) {
  const [foundParking, setFoundParking] = useState(null);
  const [searchDuration, setSearchDuration] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  if (!prediction || !prediction.occupancy) {
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (foundParking === null) {
      alert('Please indicate if you found parking');
      return;
    }

    setSubmitting(true);

    const feedbackData = {
      zone: prediction.zone,
      datetime: prediction.datetime,
      predicted_occupancy: prediction.occupancy.occupancy_count,
      predicted_available: prediction.occupancy.available_spaces,
      found_parking: foundParking,
      search_duration_minutes: searchDuration ? parseInt(searchDuration) : null
    };

    try {
      const response = await fetch(`${API_URL}/api/feedback/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData)
      });

      if (response.ok) {
        setSubmitted(true);
        setTimeout(() => {
          setSubmitted(false);
          setFoundParking(null);
          setSearchDuration('');
          if (onFeedbackSubmitted) onFeedbackSubmitted();
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="feedback-form success">
        <h3>Thank You!</h3>
        <p>Your feedback helps improve our predictions</p>
      </div>
    );
  }

  return (
    <div className="feedback-form">
      <h3>Did you find parking?</h3>
      <p>Help us improve by sharing your experience</p>

      <form onSubmit={handleSubmit}>
        <div className="feedback-buttons">
          <button
            type="button"
            className={`feedback-btn ${foundParking === true ? 'selected yes' : ''}`}
            onClick={() => setFoundParking(true)}
          >
            Yes, I found parking
          </button>
          <button
            type="button"
            className={`feedback-btn ${foundParking === false ? 'selected no' : ''}`}
            onClick={() => setFoundParking(false)}
          >
            No, I did not find parking
          </button>
        </div>

        <div className="input-group">
          <label htmlFor="search-duration">
            How long did you search? (minutes, optional)
          </label>
          <input
            id="search-duration"
            type="number"
            min="0"
            max="60"
            value={searchDuration}
            onChange={(e) => setSearchDuration(e.target.value)}
            placeholder="e.g., 5"
          />
        </div>

        <button
          type="submit"
          className="submit-btn"
          disabled={submitting || foundParking === null}
        >
          {submitting ? 'Submitting...' : 'Submit Feedback'}
        </button>
      </form>
    </div>
  );
}
