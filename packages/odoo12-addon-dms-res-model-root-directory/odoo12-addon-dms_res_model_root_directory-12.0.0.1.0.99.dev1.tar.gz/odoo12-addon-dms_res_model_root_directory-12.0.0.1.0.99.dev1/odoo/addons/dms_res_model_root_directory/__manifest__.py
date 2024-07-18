# Copyright 2023-SomItCoop SCCL(<https://gitlab.com/somitcoop>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "version": "12.0.0.1.0",
    "name": "Organize root directories by model and category",
    "summary": """
        Implement a new dms directory structure based on unique root directory by
        model and category.
        Each file can be created in a model instance particular directory under
        a root directory.
    """,
    "depends": ["dms", "contacts", "component_event"],
    "author": """
        Som It Cooperatiu SCCL,
        Som Connexió SCCL,
    """,
    "category": "Auth",
    "website": "https://gitlab.com/somitcoop/erp-research/odoo-helpdesk",
    "license": "AGPL-3",
    "data": [
        "demo/dms_category.xml",
        "demo/dms_directory.xml",
        "wizards/add_dms_file/add_dms_file.xml",
        "views/res_partner_views.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
}
