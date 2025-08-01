from flask import Blueprint, render_template, redirect, request
from .models import Expense, Category
from .forms import ExpenseForm
from . import db
import datetime

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = ExpenseForm()
    query = request.args.get('q', '')
    cat_id = request.args.get('cat_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    categories = Category.query.all()

    if form.validate_on_submit():
        category_id = request.form.get('category_id') or None
        new_expense = Expense(
            description=form.description.data,
            amount=float(form.amount.data),
            category_id=category_id,
            date=datetime.date.today()
        )
        db.session.add(new_expense)
        db.session.commit()
        return redirect('/')
    
    expenses_query = Expense.query

    if query:
        expenses_query = expenses_query.filter(Expense.description.ilike(f"%{query}%"))
    if cat_id:
        expenses_query = expenses_query.filter_by(category_id=cat_id)

    if start_date_str:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        expenses_query = expenses_query.filter(Expense.date >= start_date)
    else:
        start_date = None
    
    if end_date_str:
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        expenses_query = expenses_query.filter(Expense.date <= end_date)
    else:
        end_date = None

    expenses = expenses_query.all()
    total = sum(exp.amount for exp in expenses)

    # Totals per category

    from collections import defaultdict
    category_totals = defaultdict(float)
    for exp in expenses:
        if exp.category:
            category_totals[exp.category.name] += exp.amount

    return render_template(
        'index.html',
        form=form,
        expenses=expenses,
        total=total, query=query,
        categories=categories,
        selected_cat_id=cat_id,
        category_totals=category_totals,
        start_date=start_date_str,
        end_date=end_date_str
    )

@main.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    form = ExpenseForm(obj=expense)

    if form.validate_on_submit():
        expense.description = form.description.data
        expense.amount = float(form.amount.data)
        db.session.commit()
        return redirect('/')
    
    return render_template('edit.html', form=form)

@main.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return redirect('/')

