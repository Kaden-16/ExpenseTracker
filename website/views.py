from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc, asc
from .models import Note, Expense, FixedExpense
from . import db
from datetime import datetime
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def welcome():
    if current_user.is_authenticated: 
        return redirect(url_for('views.note'))
    else:
        return render_template("welcome.html", user=current_user)

@views.route('/note', methods=['GET', 'POST'])
@login_required
def note():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')
            return redirect(url_for('views.note'))
    return render_template("note.html", user=current_user)

@views.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    if request.method == 'POST':
        description = request.form.get('expense')
        amount = request.form.get('amount')
        date = request.form.get('date')

        fixed_description = request.form.get('fixed_expense')
        fixed_amount = request.form.get('fixed_amount')

        if description and amount and date:
            # Convert the date string to a datetime object
            date = datetime.strptime(date, '%Y-%m-%d').replace(tzinfo=None)

            new_expense = Expense(description=description, amount=float(amount), date=date, user_id=current_user.id)
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense added!', category='success')

            # Redirect to the expenses page to trigger a full-page refresh
            return redirect(url_for('views.expenses'))
        elif fixed_description and fixed_amount:
            fixed_new_expense = FixedExpense(description=fixed_description, amount=float(fixed_amount), user_id=current_user.id)
            db.session.add(fixed_new_expense)
            db.session.commit()
            flash('Expense added!', category='success')
            # Redirect to the expenses page to trigger a full-page refresh
            return redirect(url_for('views.expenses'))
        else:
            flash('Please provide fill in all necessary boxes', category='error')

    # Retrieve the list of expenses and calculate the total
    expenses_query = Expense.query.filter_by(user_id=current_user.id)

    # Sorting logic based on user choice
    sort_by = request.args.get('sort_by', default='default', type=str)
    if sort_by == 'amount_desc':
        expenses_query = expenses_query.order_by(desc(Expense.amount))
    elif sort_by == 'amount_asc':
        expenses_query = expenses_query.order_by(asc(Expense.amount))
    elif sort_by == 'date_desc':
        expenses_query = expenses_query.order_by(desc(Expense.date))
    elif sort_by == 'date_asc':
        expenses_query = expenses_query.order_by(asc(Expense.date))

    expenses = expenses_query.all()
    total_expense = sum(expense.amount for expense in expenses)

    # Fixed Expenses
        # Retrieve the list of expenses and calculate the total
    fixed_expenses_query = FixedExpense.query.filter_by(user_id=current_user.id)

    # Sorting logic based on user choice
    fixed_sort_by = request.args.get('sort_by', default='fixed_default', type=str)
    if fixed_sort_by == 'fixed_amount_desc':
        fixed_expenses_query = fixed_expenses_query.order_by(desc(FixedExpense.amount))
    elif fixed_sort_by == 'fixed_amount_asc':
        fixed_expenses_query = fixed_expenses_query.order_by(asc(FixedExpense.amount))

    fixed_expenses = fixed_expenses_query.all()
    fixed_total_expense = sum(fixed_expense.amount for fixed_expense in fixed_expenses)

    return render_template("expenses.html", user=current_user, expenses=expenses, total_expense=total_expense, fixed_expenses=fixed_expenses, fixed_total_expense=fixed_total_expense)


@views.route('/calculator', methods=['GET'])
@login_required
def calculator():
    return render_template("calculator.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})

@views.route('/delete-expense', methods=['POST'])
def delete_expense():
    expense_data = json.loads(request.data)
    expense_id = expense_data['expenseId']
    expense_type = expense_data.get('expenseType', 'regular')  # Default to regular if not specified

    if expense_type == 'regular':
        expense = Expense.query.get(expense_id)
    elif expense_type == 'fixed':
        expense = FixedExpense.query.get(expense_id)
    else:
        return jsonify({'error': 'Invalid expense type'})

    if expense and expense.user_id == current_user.id:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Expense not found or unauthorized'})
