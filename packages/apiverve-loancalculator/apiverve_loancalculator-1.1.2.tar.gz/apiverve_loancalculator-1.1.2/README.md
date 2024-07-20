Loan Calculator API
============

Loan Payment Calculator is a simple tool for calculating loan payments. It returns the monthly payment, total interest, and more.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [Loan Calculator API](https://apiverve.com/marketplace/api/loanpaymentcalculator)

---

## Installation
	pip install apiverve-loancalculator

---

## Configuration

Before using the loanpaymentcalculator API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The Loan Calculator API documentation is found here: [https://docs.apiverve.com/api/loanpaymentcalculator](https://docs.apiverve.com/api/loanpaymentcalculator).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_loancalculator.apiClient import LoanpaymentcalculatorAPIClient

# Initialize the client with your APIVerve API key
api = LoanpaymentcalculatorAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = {  "loanAmount": 32000,  "interestRate": 8.5,  "loanTerm": 6 }
```

###### Simple Request

```
# Make a request to the API
result = api.execute(query)

# Print the result
print(result)
```

###### Example Response

```
{
  "status": "ok",
  "error": null,
  "data": {
    "loanAmount": 32000,
    "downpayment": 0,
    "interestRate": 8.5,
    "loanTerm": 6,
    "monthly_payment": 568.91,
    "total_interest_paid": 8961.4,
    "amortization_schedule": [
      {
        "month": 1,
        "interest_payment": 226.67,
        "principal_payment": 342.24,
        "remaining_balance": 31657.76
      },
      {
        "month": 2,
        "interest_payment": 224.24,
        "principal_payment": 344.67,
        "remaining_balance": 31313.09
      },
      {
        "month": 3,
        "interest_payment": 221.8,
        "principal_payment": 347.11,
        "remaining_balance": 30965.99
      },
      {
        "month": 4,
        "interest_payment": 219.34,
        "principal_payment": 349.57,
        "remaining_balance": 30616.42
      },
      {
        "month": 5,
        "interest_payment": 216.87,
        "principal_payment": 352.04,
        "remaining_balance": 30264.38
      },
      {
        "month": 6,
        "interest_payment": 214.37,
        "principal_payment": 354.54,
        "remaining_balance": 29909.84
      },
      {
        "month": 7,
        "interest_payment": 211.86,
        "principal_payment": 357.05,
        "remaining_balance": 29552.79
      },
      {
        "month": 8,
        "interest_payment": 209.33,
        "principal_payment": 359.58,
        "remaining_balance": 29193.22
      },
      {
        "month": 9,
        "interest_payment": 206.79,
        "principal_payment": 362.12,
        "remaining_balance": 28831.1
      },
      {
        "month": 10,
        "interest_payment": 204.22,
        "principal_payment": 364.69,
        "remaining_balance": 28466.41
      },
      {
        "month": 11,
        "interest_payment": 201.64,
        "principal_payment": 367.27,
        "remaining_balance": 28099.14
      },
      {
        "month": 12,
        "interest_payment": 199.04,
        "principal_payment": 369.87,
        "remaining_balance": 27729.26
      },
      {
        "month": 13,
        "interest_payment": 196.42,
        "principal_payment": 372.49,
        "remaining_balance": 27356.77
      },
      {
        "month": 14,
        "interest_payment": 193.78,
        "principal_payment": 375.13,
        "remaining_balance": 26981.64
      },
      {
        "month": 15,
        "interest_payment": 191.12,
        "principal_payment": 377.79,
        "remaining_balance": 26603.85
      },
      {
        "month": 16,
        "interest_payment": 188.44,
        "principal_payment": 380.46,
        "remaining_balance": 26223.39
      },
      {
        "month": 17,
        "interest_payment": 185.75,
        "principal_payment": 383.16,
        "remaining_balance": 25840.23
      },
      {
        "month": 18,
        "interest_payment": 183.03,
        "principal_payment": 385.87,
        "remaining_balance": 25454.35
      },
      {
        "month": 19,
        "interest_payment": 180.3,
        "principal_payment": 388.61,
        "remaining_balance": 25065.75
      },
      {
        "month": 20,
        "interest_payment": 177.55,
        "principal_payment": 391.36,
        "remaining_balance": 24674.39
      },
      {
        "month": 21,
        "interest_payment": 174.78,
        "principal_payment": 394.13,
        "remaining_balance": 24280.26
      },
      {
        "month": 22,
        "interest_payment": 171.99,
        "principal_payment": 396.92,
        "remaining_balance": 23883.33
      },
      {
        "month": 23,
        "interest_payment": 169.17,
        "principal_payment": 399.73,
        "remaining_balance": 23483.6
      },
      {
        "month": 24,
        "interest_payment": 166.34,
        "principal_payment": 402.57,
        "remaining_balance": 23081.03
      },
      {
        "month": 25,
        "interest_payment": 163.49,
        "principal_payment": 405.42,
        "remaining_balance": 22675.62
      },
      {
        "month": 26,
        "interest_payment": 160.62,
        "principal_payment": 408.29,
        "remaining_balance": 22267.33
      },
      {
        "month": 27,
        "interest_payment": 157.73,
        "principal_payment": 411.18,
        "remaining_balance": 21856.14
      },
      {
        "month": 28,
        "interest_payment": 154.81,
        "principal_payment": 414.09,
        "remaining_balance": 21442.05
      },
      {
        "month": 29,
        "interest_payment": 151.88,
        "principal_payment": 417.03,
        "remaining_balance": 21025.02
      },
      {
        "month": 30,
        "interest_payment": 148.93,
        "principal_payment": 419.98,
        "remaining_balance": 20605.04
      },
      {
        "month": 31,
        "interest_payment": 145.95,
        "principal_payment": 422.96,
        "remaining_balance": 20182.09
      },
      {
        "month": 32,
        "interest_payment": 142.96,
        "principal_payment": 425.95,
        "remaining_balance": 19756.13
      },
      {
        "month": 33,
        "interest_payment": 139.94,
        "principal_payment": 428.97,
        "remaining_balance": 19327.17
      },
      {
        "month": 34,
        "interest_payment": 136.9,
        "principal_payment": 432.01,
        "remaining_balance": 18895.16
      },
      {
        "month": 35,
        "interest_payment": 133.84,
        "principal_payment": 435.07,
        "remaining_balance": 18460.09
      },
      {
        "month": 36,
        "interest_payment": 130.76,
        "principal_payment": 438.15,
        "remaining_balance": 18021.94
      },
      {
        "month": 37,
        "interest_payment": 127.66,
        "principal_payment": 441.25,
        "remaining_balance": 17580.69
      },
      {
        "month": 38,
        "interest_payment": 124.53,
        "principal_payment": 444.38,
        "remaining_balance": 17136.31
      },
      {
        "month": 39,
        "interest_payment": 121.38,
        "principal_payment": 447.53,
        "remaining_balance": 16688.78
      },
      {
        "month": 40,
        "interest_payment": 118.21,
        "principal_payment": 450.7,
        "remaining_balance": 16238.09
      },
      {
        "month": 41,
        "interest_payment": 115.02,
        "principal_payment": 453.89,
        "remaining_balance": 15784.2
      },
      {
        "month": 42,
        "interest_payment": 111.8,
        "principal_payment": 457.1,
        "remaining_balance": 15327.1
      },
      {
        "month": 43,
        "interest_payment": 108.57,
        "principal_payment": 460.34,
        "remaining_balance": 14866.75
      },
      {
        "month": 44,
        "interest_payment": 105.31,
        "principal_payment": 463.6,
        "remaining_balance": 14403.15
      },
      {
        "month": 45,
        "interest_payment": 102.02,
        "principal_payment": 466.89,
        "remaining_balance": 13936.27
      },
      {
        "month": 46,
        "interest_payment": 98.72,
        "principal_payment": 470.19,
        "remaining_balance": 13466.07
      },
      {
        "month": 47,
        "interest_payment": 95.38,
        "principal_payment": 473.52,
        "remaining_balance": 12992.55
      },
      {
        "month": 48,
        "interest_payment": 92.03,
        "principal_payment": 476.88,
        "remaining_balance": 12515.67
      },
      {
        "month": 49,
        "interest_payment": 88.65,
        "principal_payment": 480.26,
        "remaining_balance": 12035.42
      },
      {
        "month": 50,
        "interest_payment": 85.25,
        "principal_payment": 483.66,
        "remaining_balance": 11551.76
      },
      {
        "month": 51,
        "interest_payment": 81.82,
        "principal_payment": 487.08,
        "remaining_balance": 11064.68
      },
      {
        "month": 52,
        "interest_payment": 78.37,
        "principal_payment": 490.53,
        "remaining_balance": 10574.14
      },
      {
        "month": 53,
        "interest_payment": 74.9,
        "principal_payment": 494.01,
        "remaining_balance": 10080.13
      },
      {
        "month": 54,
        "interest_payment": 71.4,
        "principal_payment": 497.51,
        "remaining_balance": 9582.63
      },
      {
        "month": 55,
        "interest_payment": 67.88,
        "principal_payment": 501.03,
        "remaining_balance": 9081.59
      },
      {
        "month": 56,
        "interest_payment": 64.33,
        "principal_payment": 504.58,
        "remaining_balance": 8577.01
      },
      {
        "month": 57,
        "interest_payment": 60.75,
        "principal_payment": 508.15,
        "remaining_balance": 8068.86
      },
      {
        "month": 58,
        "interest_payment": 57.15,
        "principal_payment": 511.75,
        "remaining_balance": 7557.11
      },
      {
        "month": 59,
        "interest_payment": 53.53,
        "principal_payment": 515.38,
        "remaining_balance": 7041.73
      },
      {
        "month": 60,
        "interest_payment": 49.88,
        "principal_payment": 519.03,
        "remaining_balance": 6522.7
      },
      {
        "month": 61,
        "interest_payment": 46.2,
        "principal_payment": 522.71,
        "remaining_balance": 5999.99
      },
      {
        "month": 62,
        "interest_payment": 42.5,
        "principal_payment": 526.41,
        "remaining_balance": 5473.58
      },
      {
        "month": 63,
        "interest_payment": 38.77,
        "principal_payment": 530.14,
        "remaining_balance": 4943.45
      },
      {
        "month": 64,
        "interest_payment": 35.02,
        "principal_payment": 533.89,
        "remaining_balance": 4409.55
      },
      {
        "month": 65,
        "interest_payment": 31.23,
        "principal_payment": 537.67,
        "remaining_balance": 3871.88
      },
      {
        "month": 66,
        "interest_payment": 27.43,
        "principal_payment": 541.48,
        "remaining_balance": 3330.4
      },
      {
        "month": 67,
        "interest_payment": 23.59,
        "principal_payment": 545.32,
        "remaining_balance": 2785.08
      },
      {
        "month": 68,
        "interest_payment": 19.73,
        "principal_payment": 549.18,
        "remaining_balance": 2235.9
      },
      {
        "month": 69,
        "interest_payment": 15.84,
        "principal_payment": 553.07,
        "remaining_balance": 1682.83
      },
      {
        "month": 70,
        "interest_payment": 11.92,
        "principal_payment": 556.99,
        "remaining_balance": 1125.84
      },
      {
        "month": 71,
        "interest_payment": 7.97,
        "principal_payment": 560.93,
        "remaining_balance": 564.91
      },
      {
        "month": 72,
        "interest_payment": 4,
        "principal_payment": 564.91,
        "remaining_balance": 0
      }
    ]
  }
}
```

---

## Customer Support

Need any assistance? [Get in touch with Customer Support](https://apiverve.com/contact).

---

## Updates
Stay up to date by following [@apiverveHQ](https://twitter.com/apiverveHQ) on Twitter.

---

## Legal

All usage of the APIVerve website, API, and services is subject to the [APIVerve Terms of Service](https://apiverve.com/terms) and all legal documents and agreements.

---

## License
Licensed under the The MIT License (MIT)

Copyright (&copy;) 2024 APIVerve, and Evlar LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.