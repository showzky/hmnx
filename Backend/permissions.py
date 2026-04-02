DEFAULT_DASHBOARD_FLAVOR = 'default'

PERMISSION_DEFINITIONS = [
    {"group": "management", "key": "access_management", "label": "Access management", "description": "Gir tilgang til management-dashboardet."},
    {"group": "management", "key": "manage_users", "label": "Manage users", "description": "Kan håndtere brukere og medlemskap."},
    {"group": "management", "key": "manage_roles", "label": "Manage roles", "description": "Kan opprette og slette roller."},
    {"group": "content", "key": "publish_bedriftsmeldinger", "label": "Publish bedriftsmeldinger", "description": "Kan publisere nye bedriftsmeldinger."},
    {"group": "content", "key": "edit_bedriftsmeldinger", "label": "Edit bedriftsmeldinger", "description": "Kan redigere eksisterende bedriftsmeldinger."},
    {"group": "content", "key": "delete_bedriftsmeldinger", "label": "Delete bedriftsmeldinger", "description": "Kan slette bedriftsmeldinger."},
    {"group": "content", "key": "manage_events", "label": "Manage events", "description": "Kan opprette og endre hendelser."},
    {"group": "content", "key": "manage_news", "label": "Manage news", "description": "Kan publisere og endre news."},
    {"group": "content", "key": "manage_changelog", "label": "Manage changelog", "description": "Kan administrere changelog-innhold."},
    {"group": "music", "key": "manage_music", "label": "Manage music", "description": "Kan laste opp og styre Bangerfabrikken."},
    {"group": "system", "key": "manage_settings", "label": "Manage settings", "description": "Kan endre system- og maintenance-innstillinger."},
    {"group": "system", "key": "manage_team", "label": "Manage team", "description": "Kan endre team manager."},
    {"group": "system", "key": "manage_shop", "label": "Manage shop", "description": "Kan administrere shop-elementer."},
]

PERMISSION_KEYS = {item["key"] for item in PERMISSION_DEFINITIONS}

SYSTEM_ROLE_DEFAULTS = {
    "admin": {
        "system_role": True,
        "dashboard_flavor": DEFAULT_DASHBOARD_FLAVOR,
        "permissions": sorted(PERMISSION_KEYS),
    },
    "developer": {
        "system_role": True,
        "dashboard_flavor": DEFAULT_DASHBOARD_FLAVOR,
        "permissions": sorted(PERMISSION_KEYS),
    },
    "producer": {
        "system_role": True,
        "dashboard_flavor": "music",
        "permissions": [
            "access_management",
            "manage_music",
            "publish_bedriftsmeldinger",
            "edit_bedriftsmeldinger",
            "manage_events",
        ],
    },
    "member": {
        "system_role": True,
        "dashboard_flavor": DEFAULT_DASHBOARD_FLAVOR,
        "permissions": [],
    },
}


def normalize_permission_keys(keys):
    if not isinstance(keys, list):
        return []
    normalized = []
    seen = set()
    for key in keys:
        if not isinstance(key, str):
            continue
        cleaned = key.strip().lower()
        if cleaned in PERMISSION_KEYS and cleaned not in seen:
            normalized.append(cleaned)
            seen.add(cleaned)
    return normalized


def default_role_metadata(role_name):
    normalized_name = str(role_name or "").strip().lower()
    if normalized_name in SYSTEM_ROLE_DEFAULTS:
        default_data = SYSTEM_ROLE_DEFAULTS[normalized_name]
        return {
            "system_role": bool(default_data.get("system_role")),
            "dashboard_flavor": default_data.get("dashboard_flavor", DEFAULT_DASHBOARD_FLAVOR),
            "permissions": normalize_permission_keys(default_data.get("permissions", [])),
        }
    return {
        "system_role": False,
        "dashboard_flavor": DEFAULT_DASHBOARD_FLAVOR,
        "permissions": [],
    }
