from flask.globals import request
import requests
from time import time_ns

lenders = (1,3,4,5,6)
borrowers = (2,7,8,9,10)

# test lender loan contract creation
# for lender in lenders
# call api to create contract

def testLoanCreation():
    print('Testing sequential loan creation...')
    start = time_ns()
    for lender_id in lenders:
        # create new loan
        print('Lender: %s | creating loan...'%(lender_id))
        tx_start = time_ns()
        payload = {
            'loan_amount':3500,
            'interest': 15.50,
            'time_frame': 3,
            'platform': 1,
            'lender': lender_id
        }

        tx = requests.post('http://localhost:5000/api/create-loan', json=payload)

        tx_end = time_ns()

        if tx.json()['loan_id'][0]:
            print('Lender: %s | loan with id: %s created after %sns!'%(
                lender_id, 
                tx.json()['loan_id'],
                tx_end - tx_start
                )
            )
        else:
            print('Error creating loan!')

    end = time_ns()

    print('Sequential test finished! Elapsed time: %sns'%(end-start))





def testLoanRequest():
    pass

def testLoanAccept():
    pass


# tester
testLoanCreation()