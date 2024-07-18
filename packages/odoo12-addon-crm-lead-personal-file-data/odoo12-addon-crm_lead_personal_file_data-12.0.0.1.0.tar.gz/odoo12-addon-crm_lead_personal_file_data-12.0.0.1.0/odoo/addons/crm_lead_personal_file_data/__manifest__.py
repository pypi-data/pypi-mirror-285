# Copyright 2023-SomItCoop SCCL(<https://gitlab.com/somitcoop>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "version": "12.0.0.1.0",
    "name": "Move lead personal data to partner",
    "summary": """
        Move lead pending assigned files to its partner directory under personal data.
    """,
    "depends": ["crm", "dms_res_model_root_directory"],
    "author": """
        Som It Cooperatiu SCCL,
        Som Connexió SCCL,
    """,
    "category": "Auth",
    "website": "https://gitlab.com/somitcoop/erp-research/odoo-helpdesk",
    "license": "AGPL-3",
    "data": [
        "data/dms_storage.xml",
        "data/dms_category.xml",
        "data/dms_directory.xml",
        "views/crm_lead_views.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
}
