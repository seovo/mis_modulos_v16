# -*- coding: utf-8 -*-
{
    "name": "Asistencia Osmar",
    "summary": "Asistencia Osmar",
    "description": """
        Asistencia Osmar
    """,
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "17.0",
    "depends": ["hr_attendance","planning"],
    "data": [
        "security/group.xml",
        "security/ir.model.access.csv",
        'views/planning_slot.xml',
        'data/attendance_check_state.xml',
        'wizard/planning_slot_wizard.xml'

    ],
    "application": False,
    "installable": True,
    "auto_install": False,


}
