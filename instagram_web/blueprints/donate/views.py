from flask import Blueprint, render_template, redirect, url_for, request, flash

from flask_login import current_user

from helpers import gateway

import braintree

donate_blueprint = Blueprint('donate',
                            __name__,
                            template_folder='templates')

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]

@donate_blueprint.route('/process', methods=['POST'])
def create_checkout():
    result = gateway.transaction.sale({
        'amount': request.form['amount'],
        'payment_method_nonce': request.form['payment_method_nonce'],
        # 'options': {
        #     "submit_for_settlement": True
        # }
    })

    if result.is_success or result.transaction:
        return redirect(url_for('donate.show_checkout', transaction_id=result.transaction.id))
    else:
        for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
        return redirect(url_for('donate.new_checkout'))

    # result = gateway.transaction.sale({
    #     "amount": "10.00",
    #     "payment_method_nonce": nonce,
    #     "options": {
    #         "submit_for_settlement": True
    #     }
    # })

    return "WIP"

@donate_blueprint.route("/new", methods=["GET"])
def new_checkout():
    client_token = gateway.client_token.generate()
    return render_template('donate/form.html', 
        client_token=client_token,
    )

@donate_blueprint.route("/receipt/<transaction_id>", methods=["GET"])
def show_checkout(transaction_id):
    transaction = gateway.transaction.find(transaction_id)
    result = {}
    if transaction.status in TRANSACTION_SUCCESS_STATUSES:
        result = {
            'header': 'Sweet Success!',
            'icon': 'success',
            'message': 'Your test transaction has been successfully processed. See the Braintree API response and try again.'
        }
    else:
        result = {
            'header': 'Transaction Failed',
            'icon': 'fail',
            'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
        }

    return render_template('donate/show.html', transaction=transaction, result=result)