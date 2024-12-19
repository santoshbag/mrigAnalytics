#  Copyright (c) 2024.
import razorpay
import mrigstatics as ms

class Razorpay():

    client = None
    def __init__(self):
        self.client = razorpay.Client(auth=(ms.RAZORPAY_KEY_ID, ms.RAZORPAY_KEY_SECRET))
        # return client


