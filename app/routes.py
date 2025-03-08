from flask import Blueprint, request, jsonify, session, send_file
import os
# from flask_login import login_user, current_user
from .models import User, Transaction
from . import db, bcrypt
from datetime import datetime

# Create a Blueprint for routes
main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@main_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')  # Get username from the request
    password = data.get('password')  # Get password from the request

    # Find the user by username
    user = User.query.filter_by(username=username).first()

    # Check if the user exists and the password is correct
    if user and user.check_password(password):
        # Store the user's ID in the session
        session['user_id'] = user.user_id
        session.permanent = True  # Make the session permanent
        return jsonify({'success': True, 'message': 'Login successful'}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401


@main_routes.route('/transactions', methods=['GET', 'POST'])
def transactions():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    if request.method == 'GET':
        # Handle GET request: Fetch all transactions for the logged-in user
        transactions = Transaction.query.filter_by(user_id=session['user_id']).all()
        transaction_list = [{
            'transaction_id': t.transaction_id,
            'user_id': t.user_id,  # Include user_id in the response (optional)
            'amount': t.amount,
            'date': t.date.isoformat(),
            'type': t.type
        } for t in transactions]

        return jsonify(transaction_list), 200

    elif request.method == 'POST':
        # Handle POST request: Add a new transaction
        data = request.get_json()

        # Validate required fields
        if not data or 'amount' not in data or 'date' not in data or 'type' not in data:
            return jsonify({'message': 'Missing required fields (amount, date, type)'}), 400

        try:
            # Parse the date from the frontend format (e.g., "4/16/2021, 7:41:15 PM")
            transaction_date = datetime.strptime(data['date'], '%m/%d/%Y, %I:%M:%S %p')
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use "MM/DD/YYYY, HH:MM:SS AM/PM"'}), 400

        # Create a new transaction
        new_transaction = Transaction(
            user_id=session['user_id'],  # Set the user_id from the session
            amount=data['amount'],
            date=transaction_date,
            type=data['type']
        )

        # Add and commit to the database
        db.session.add(new_transaction)
        db.session.commit()

        return jsonify({'message': 'Transaction added successfully', 'transaction_id': new_transaction.transaction_id}), 201
    

@main_routes.route('/export-db', methods=['GET'])
def export_db():
    # Path to your SQLite database file
    db_path = os.path.join(os.getcwd(), 'instance', 'app.db')
    
    # Check if the file exists
    if not os.path.exists(db_path):
        return jsonify({'message': 'Database file not found'}), 404

    # Send the file as a download
    return send_file(db_path, as_attachment=True)