from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required


def register_role_permission_routes(app, *, User, Role, db, serialize_role, get_role_metadata, set_role_metadata, normalize_permission_keys):
    role_permissions_bp = Blueprint('role_permissions_bp', __name__)

    def current_user():
        identity = get_jwt_identity()
        return User.query.get(int(identity)) if identity else None

    def can_manage_roles(user):
        if not user:
            return False
        user_permissions = set()
        for role in user.roles:
            metadata = get_role_metadata(role)
            user_permissions.update(metadata.get('permissions', []))
        return 'manage_roles' in user_permissions or any(role.name.lower() in ['admin', 'developer'] for role in user.roles)

    @role_permissions_bp.route('/api/roles/<int:role_id>', methods=['PUT'])
    @jwt_required()
    def update_role(role_id):
        user = current_user()
        if not can_manage_roles(user):
            return jsonify({"msg": "Only users with role management access can update roles"}), 403

        role = Role.query.get(role_id)
        if not role:
            return jsonify({"msg": "Role not found"}), 404

        payload = request.get_json() or {}
        metadata = get_role_metadata(role)

        if not metadata.get('system_role'):
            requested_name = (payload.get('name') or '').strip()
            if requested_name:
                existing_role = Role.query.filter(db.func.lower(Role.name) == requested_name.lower(), Role.id != role.id).first()
                if existing_role:
                    return jsonify({"msg": f"Role '{existing_role.name}' already exists"}), 409
                role.name = requested_name

        requested_color = (payload.get('badge_color') or '').strip()
        if requested_color:
            role.badge_color = requested_color

        requested_icon = payload.get('badge_icon')
        if requested_icon is not None:
            role.badge_icon = requested_icon

        metadata['dashboard_flavor'] = payload.get('dashboard_flavor') or metadata.get('dashboard_flavor') or 'default'
        set_role_metadata(role, metadata)
        db.session.add(role)
        db.session.commit()
        return jsonify({"msg": "Role updated", "role": serialize_role(role)}), 200

    @role_permissions_bp.route('/api/roles/<int:role_id>/permissions', methods=['PUT'])
    @jwt_required()
    def update_role_permissions(role_id):
        user = current_user()
        if not can_manage_roles(user):
            return jsonify({"msg": "Only users with role management access can update permissions"}), 403

        role = Role.query.get(role_id)
        if not role:
            return jsonify({"msg": "Role not found"}), 404

        payload = request.get_json() or {}
        metadata = get_role_metadata(role)
        metadata['permissions'] = normalize_permission_keys(payload.get('permissions', []))
        set_role_metadata(role, metadata)
        db.session.commit()
        return jsonify({"msg": "Role permissions updated", "role": serialize_role(role)}), 200

    @role_permissions_bp.route('/api/roles/<int:role_id>/members', methods=['POST'])
    @jwt_required()
    def add_role_member(role_id):
        user = current_user()
        if not can_manage_roles(user):
            return jsonify({"msg": "Only users with role management access can manage members"}), 403

        role = Role.query.get(role_id)
        if not role:
            return jsonify({"msg": "Role not found"}), 404

        payload = request.get_json() or {}
        member = User.query.get(payload.get('user_id'))
        if not member:
            return jsonify({"msg": "User not found"}), 404

        if role not in member.roles:
            member.roles.append(role)
            db.session.commit()

        return jsonify({
            "msg": "Member added to role",
            "role": serialize_role(role),
            "user": {
                "id": member.id,
                "roles": [serialize_role(item) for item in member.roles],
            }
        }), 200

    @role_permissions_bp.route('/api/roles/<int:role_id>/members/<int:user_id>', methods=['DELETE'])
    @jwt_required()
    def remove_role_member(role_id, user_id):
        user = current_user()
        if not can_manage_roles(user):
            return jsonify({"msg": "Only users with role management access can manage members"}), 403

        role = Role.query.get(role_id)
        if not role:
            return jsonify({"msg": "Role not found"}), 404

        member = User.query.get(user_id)
        if not member:
            return jsonify({"msg": "User not found"}), 404

        if role in member.roles:
            member.roles.remove(role)
            db.session.commit()

        return jsonify({
            "msg": "Member removed from role",
            "role": serialize_role(role),
            "user": {
                "id": member.id,
                "roles": [serialize_role(item) for item in member.roles],
            }
        }), 200

    app.register_blueprint(role_permissions_bp)
