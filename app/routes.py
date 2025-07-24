from flask import Blueprint, render_template, redirect, request
from .models import Expense
from .forms import ExpenseForm
from . import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = ExpenseForm()

    if form.validate_on_submit():
        new_expense = Expense(
            description=form.description.data,
            amount=float(form.amount.data)
        )
        db.session.add(new_expense)
        db.session.commit()
        return redirect('/')
    
    expenses = Expense.query.all()
    return render_template('index.html', form=form, expenses=expenses)
