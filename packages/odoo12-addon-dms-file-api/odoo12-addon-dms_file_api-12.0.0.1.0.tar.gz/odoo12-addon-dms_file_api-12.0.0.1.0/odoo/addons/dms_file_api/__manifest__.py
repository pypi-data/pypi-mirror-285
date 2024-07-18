{
    "version": "12.0.0.1.0",
    "name": "DMS File API",
    "summary": """
        Expose an API-Key authenticated API to get and create dms files.
    """,
    "depends": ["api_common_base", "crm", "dms_res_model_root_directory"],
    "author": """
        Som It Cooperatiu SCCL,
        Som Connexió SCCL,
    """,
    "category": "Customer Relationship Management",
    "website": "https://gitlab.com/somitcoop/erp-research/odoo-helpdesk",
    "license": "AGPL-3",
    "data": [
        "views/dms_category.xml",
    ],
    "demo": [
        "demo/dms_category.xml",
    ],
    "application": False,
    "installable": True,
}
