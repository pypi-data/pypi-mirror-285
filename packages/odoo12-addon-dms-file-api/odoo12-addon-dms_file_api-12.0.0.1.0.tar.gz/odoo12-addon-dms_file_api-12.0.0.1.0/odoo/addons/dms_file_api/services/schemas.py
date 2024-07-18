S_DMS_FILE_CREATE = {
    "crm_lead_id": {
        "type": "integer",
        "required": True,
        "excludes": ["partner_ref"],
    },
    "partner_ref": {
        "type": "string",
        "required": True,
        "excludes": ["crm_lead_id"],
    },
    "category": {"type": "string", "required": True},
    "files": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "filename": {"type": "string", "required": True},
                "content": {"type": "string", "required": True},
            },
        },
    },
}

LIST_IDS_SCHEMA = {
    "ids": {"type": "list", "schema": {"type": "integer"}, "required": True},
}
