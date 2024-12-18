{
    "name": "Lock Year Process",
    "summary": """Lock Year Process """,
    "version": "18.0.1.0.0",
    "category": "Extra Tools",
    "description": """This Odoo module enables setting closing dates for key documents
    like Sale Orders, Purchase Orders, and Delivery Orders , etc.
    ensuring compliance and minimizing errors.""",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "https://www.serpentcs.com",
    "depends": [
       'base'
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_view.xml",
    ],
    "price": 30,
    'currency': "EUR",
    "license": "LGPL-3",
    "installable": True,
}
