# Option Chain History View

from flask import render_template, request, Blueprint
import os
import csv

history_bp = Blueprint('history', __name__)

@history_bp.route('/option_chain_history')
def option_chain_history():
    # Get date from query param, default to today
    from datetime import datetime
    date_str = request.args.get('date') or datetime.now().strftime('%Y-%m-%d')
    filename = os.path.join('option_chain_snapshots', f'{date_str}.csv')
    snapshots = []
    if os.path.exists(filename):
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                snapshots.append(row)
    # Group by timestamp for display
    grouped = {}
    for row in snapshots:
        grouped.setdefault(row['timestamp'], []).append(row)
    # Sort timestamps
    sorted_times = sorted(grouped.keys())
    return render_template('option_chain_history.html',
                           grouped=grouped,
                           sorted_times=sorted_times,
                           date_str=date_str)
