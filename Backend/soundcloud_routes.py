import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

soundcloud_bp = Blueprint('soundcloud', __name__, url_prefix='/api/soundcloud')


@soundcloud_bp.route('/oembed', methods=['GET'])
@jwt_required()
def get_oembed():
    track_url = request.args.get('url', '').strip()

    if not track_url:
        return jsonify({'error': 'Missing url parameter'}), 400

    if 'soundcloud.com' not in track_url:
        return jsonify({'error': 'Not a valid SoundCloud URL'}), 400

    try:
        response = requests.get(
            'https://soundcloud.com/oembed',
            params={
                'format': 'json',
                'url': track_url,
                'maxwidth': 800,
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()

        return jsonify({
            'title': data.get('title', ''),
            'author_name': data.get('author_name', ''),
            'author_url': data.get('author_url', ''),
            'thumbnail_url': data.get('thumbnail_url', ''),
            'html': data.get('html', ''),
        }), 200

    except requests.exceptions.Timeout:
        return jsonify({'error': 'SoundCloud took too long to respond'}), 504
    except requests.exceptions.RequestException as exc:
        return jsonify({'error': f'Failed to fetch oEmbed: {exc}'}), 502
