from flask import Blueprint, render_template, redirect, request
from .models import Expense
from .forms import ExpenseForm
from . import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = ExpenseForm()
    query = request.args.get('q', '')

    if form.validate_on_submit():
        new_expense = Expense(
            description=form.description.data,
            amount=float(form.amount.data)
        )
        db.session.add(new_expense)
        db.session.commit()
        return redirect('/')
    
    if query:
        expenses = Expense.query.filter(Expense.description.ilike(f"%{query}%")).all()
    else:
        expenses = Expense.query.all()
    
    total = sum(exp.amount for exp in expenses)

    return render_template('index.html', form=form, expenses=expenses, total=total, query=query)

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

