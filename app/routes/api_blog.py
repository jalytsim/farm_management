import os, uuid
from datetime import datetime
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User

bp = Blueprint('api_blog', __name__, url_prefix='/api/blog')

# Dossier où sont stockés les fichiers .md
BLOG_CONTENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'blog_content')
os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)
# Liste tous les articles (métadonnées seulement, sans body)
@bp.route('/posts/', methods=['GET'])
def list_posts():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return jsonify([p.to_dict() for p in posts])


# Récupère le contenu d'un article (le .md)
@bp.route('/posts/<slug>/content/', methods=['GET'])
def get_content(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    body = _read_content(slug)
    return jsonify({'slug': slug, 'body': body})


# Crée un article
@bp.route('/posts/', methods=['POST'])
@jwt_required()
def create_post():
    identity = get_jwt_identity()
    data = request.json or {}

    body = data.get('body', '').strip()
    slug = _make_slug(data.get('title', 'article'))

    post = BlogPost(
        slug       = slug,
        title      = data.get('title', '').strip(),
        excerpt    = data.get('excerpt', '').strip(),
        author     = data.get('author', '').strip(),
        category   = data.get('category', ''),
        tags       = data.get('tags', []),
        read_time  = _calc_read_time(body),
        created_by = identity.get('id'),
    )
    db.session.add(post)
    db.session.commit()

    if body:
        _write_content(slug, body)

    return jsonify(post.to_dict()), 201


# Modifie un article
@bp.route('/posts/<int:post_id>/', methods=['PATCH'])
@jwt_required()
def update_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    data = request.json or {}
    body = data.get('body', None)

    for field in ('title', 'excerpt', 'author', 'category', 'tags'):
        if field in data:
            setattr(post, field, data[field])

    if body is not None:
        post.read_time = _calc_read_time(body)
        _write_content(post.slug, body)

    db.session.commit()
    return jsonify(post.to_dict())


# Supprime un article
@bp.route('/posts/<int:post_id>/', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    _delete_content(post.slug)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'msg': 'Article supprimé.'})