"""Sample support-doc chunks for a made-up company, and questions with the chunk that answers each.
All text here is invented for the demo."""

CHUNKS = [
    "Hardware returns: you can return a device within 30 days of delivery for a full refund if it is unused and in its original box.",
    "Subscription refunds: monthly plans can be cancelled at any time; we refund the current month if you cancel within 7 days of being charged.",
    "Warranty: devices have a 12-month warranty against manufacturing faults. Damage from drops or water is not covered.",
    "Battery warranty: the battery is covered for 24 months or 500 full charge cycles, whichever comes first.",
    "Domestic shipping: orders inside the country arrive in 2 to 4 business days with tracking.",
    "International shipping: orders abroad arrive in 7 to 14 business days; customs fees are paid by the buyer.",
    "Password reset: choose 'Forgot password' on the sign-in page and we email a link that works for 30 minutes.",
    "Two-factor reset: if you lost your phone, contact support with your order number to remove two-factor sign-in.",
    "Trade-in: send your old device in the prepaid bag and we credit up to 40% of the new price to your account.",
    "Data deletion: you can ask us to delete your account data from Settings; deletion finishes within 30 days.",
    "Firmware updates: devices check for updates overnight when plugged in and connected to Wi-Fi.",
    "Business orders: orders of 10 or more devices get a dedicated account manager and invoice payment.",
]

# (question, index of the chunk that answers it)
QUESTIONS = [
    ("Can I get my money back if I cancel my plan after three days?", 1),
    ("I dropped my device in a pool, will you fix it for free?", 2),
    ("How long until a parcel shipped overseas gets here?", 5),
    ("My battery only lasts an hour after 18 months, is that covered?", 3),
    ("I got a new phone number and can't sign in with a code.", 7),
    ("What do I get for sending in my old unit?", 8),
    ("The device is still sealed, can I send it back after three weeks?", 0),
    ("How do I make you erase everything you know about me?", 9),
    ("When does the device install new software?", 10),
    ("We want to buy fifteen units and pay by invoice.", 11),
]
