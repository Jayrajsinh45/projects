{
    "name": "Project Checklist",
    "summary": """Project Checklist """,
    "version": "18.0.1.0.0",
    "category": "Services/Project",
    "description": """Project Checklist module provide checklists generation for tasks based on stages.""",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "https://www.serpentcs.com",
    "depends": [ 'project'
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/project_checklist_data.xml",
        "views/checklist_view.xml",
    ],
    'currency': "EUR",
    "license": "LGPL-3",
    "installable": True,
}
