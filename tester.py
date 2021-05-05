import requests
from time import time_ns

lenders = (1, 3, 4, 5, 6)
borrowers = (2, 7, 8, 9, 10)

loans = (64, 65, 66, 67, 68)

offers_to_accept = (28, 34, 40, 46, 52)

# test lender loan contract creation
# for lender in lenders
# call api to create contract


def testLoanCreation():
    print('Testing loan creation...')
    start = time_ns()
    for lender_id in lenders:
        # create new loan
        print('Lender: %s | creating loan...' % (lender_id))
        tx_start = time_ns()
        payload = {
            'loan_amount': 3500,
            'interest': 15.50,
            'time_frame': 3,
            'platform': 1,
            'lender': lender_id
        }

        tx = requests.post(
            'http://localhost:5000/api/create-loan', json=payload)

        tx_end = time_ns()

        if tx.json()['loan_id'][0]:
            print('Lender: %s | loan with id: %s created after %sns!' % (
                lender_id,
                tx.json()['loan_id'][0],
                tx_end - tx_start
            )
            )
        else:
            print('Error creating loan!')

    end = time_ns()

    print('Loan creation test finished! Elapsed time: %sns' % (end-start))


def testLoanRequest():
    # for borrower in borrowers
    # request loan with default parameters
    print('Testing loan request...')
    start = time_ns()
    for borrower_id in borrowers:
        for loan_id in loans:
            # create new loan
            print('Borrower: %s | requesting loan: %s...' % (borrower_id, loan_id))
            tx_start = time_ns()
            payload = {
                'loan_id': loan_id,
                'borrower_id': borrower_id,
                'loan_amount': 3500,
                'interest': 15.50,
                'time_frame': 3,
                'platform': 1
            }

            tx = requests.post(
                'http://localhost:5000/api/create-offer', json=payload)

            tx_end = time_ns()
            
            print('Borrower: %s | loan with id: %s requested after %sns!' % (
                    borrower_id,
                    loan_id,
                    tx_end - tx_start) )

    end = time_ns()

    print('Loan request test finished! Elapsed time: %sns' % (end-start))


def testLoanAccept():
    # for loan offer in offers
    # lender accept
    print('Testing offer accept...')
    start = time_ns()
    for offer_id in offers_to_accept:
        # create new loan
        print('Accepting offer: %s...' % (offer_id))
        tx_start = time_ns()
        payload = {
            'offer_id': offer_id,
        }

        tx = requests.put(
            'http://localhost:5000/api/accept-offer', json=payload)

        tx_end = time_ns()
            
        print('Offer: %s accepted after %sns!' % (
                offer_id,
                tx_end - tx_start) )

    end = time_ns()

    print('Offer accept test finished! Elapsed time: %sns' % (end-start))


# tester
# testLoanCreation()
# testLoanRequest()
# testLoanAccept()
