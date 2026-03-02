"""
Flask app to simulate the events API for Airflow DAG examples.
Serves events at http://localhost:5001/events with optional date filtering.
"""

from datetime import datetime, timedelta
import random
from flask import Flask, jsonify, request

app = Flask(__name__)

# Generate sample events data
def generate_events(start_date=None, end_date=None):
    """
    Generate sample events data.
    
    Args:
        start_date: Optional start date (datetime object)
        end_date: Optional end date (datetime object)
    
    Returns:
        List of event dictionaries with 'date' and 'user' fields
    """
    events = []
    
    # Default date range: Jan 1-10, 2019
    if start_date is None:
        start_date = datetime(2019, 1, 1)
    if end_date is None:
        end_date = datetime(2019, 1, 10)
    
    # Generate events for each day in the range
    current_date = start_date
    users = ['alice', 'bob', 'charlie', 'diana', 'eve']
    
    while current_date <= end_date:
        # Generate 5-15 events per day
        num_events = random.randint(5, 15)
        
        for _ in range(num_events):
            event = {
                'date': current_date.strftime('%Y-%m-%d'),
                'user': random.choice(users),
                'event_type': random.choice(['click', 'view', 'purchase', 'login']),
                'value': random.randint(1, 100)
            }
            events.append(event)
        
        current_date += timedelta(days=1)
    
    return events


@app.route('/events', methods=['GET'])
def get_events():
    """
    Endpoint to retrieve events.
    
    Query parameters:
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
    
    Returns:
        JSON array of events
    """
    try:
        # Parse query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Generate and filter events
        events = generate_events(start_date=start_date, end_date=end_date)
        
        return jsonify(events)
    
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

