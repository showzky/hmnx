from flask import Blueprint, request, redirect
import base64, hashlib, hmac, urllib.parse
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import User  # adjust as needed

sso_bp = Blueprint('sso', __name__)

SSO_SECRET = 'ca7d1c78cef959144eae8eee30249309b97829ef7c7a4a5e768e48cdee6646cf'
DISCOURSE_SSO_CALLBACK = 'https://forum.hmnmentalpasienter.no/session/sso_login'

@sso_bp.route('/sso', methods=['GET'])
@jwt_required()
def sso():
    sso_payload = request.args.get('sso')
    sig = request.args.get('sig')
    if not sso_payload or not sig:
        return "Missing parameters", 400

    computed_sig = hmac.new(SSO_SECRET.encode('utf-8'),
                            sso_payload.encode('utf-8'),
                            hashlib.sha256).hexdigest()
    if computed_sig != sig:
        return "Invalid signature", 403

    try:
        decoded = base64.b64decode(sso_payload).decode('utf-8')
    except Exception as e:
        return f"Error decoding payload: {e}", 400

    qs = urllib.parse.parse_qs(decoded)
    nonce = qs.get('nonce', [None])[0]
    if not nonce:
        return "Missing nonce", 400

    current_user_id = get_jwt_identity()
    if not current_user_id:
        return "User not authenticated", 403

    user = User.query.get(current_user_id)
    if not user:
        return "User not found", 404

    roles = [role.name for role in user.roles]
    role_str = ','.join(roles) if roles else 'member'

    payload_dict = {
        'nonce': nonce,
        'email': user.email,
        'external_id': str(user.id),
        'username': user.username,
        'role': role_str
    }

    payload_str = urllib.parse.urlencode(payload_dict)
    payload_base64 = base64.b64encode(payload_str.encode('utf-8')).decode('utf-8')
    new_sig = hmac.new(SSO_SECRET.encode('utf-8'),
                       payload_base64.encode('utf-8'),
                       hashlib.sha256).hexdigest()
    redirect_url = f"{DISCOURSE_SSO_CALLBACK}?sso={urllib.parse.quote(payload_base64)}&sig={new_sig}"
    return redirect(redirect_url)
