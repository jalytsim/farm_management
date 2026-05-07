import os, uuid, re
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models import BlogPost

bp = Blueprint('api_blog', __name__, url_prefix='/api/blog')

# Dossier de stockage des fichiers .md
BLOG_CONTENT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'blog_content'
)
os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)

# Dossier de stockage des images de couverture
BLOG_UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'app', 'static', 'uploads', 'blog'
)
os.makedirs(BLOG_UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _file_path(slug: str) -> str:
    return os.path.join(BLOG_CONTENT_DIR, f"{slug}.md")

def _write_content(slug: str, body: str):
    with open(_file_path(slug), 'w', encoding='utf-8') as f:
        f.write(body)

def _read_content(slug: str) -> str:
    path = _file_path(slug)
    if not os.path.exists(path):
        return ''
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def _delete_content(slug: str):
    path = _file_path(slug)
    if os.path.exists(path):
        os.remove(path)

def _delete_cover(filename: str):
    """Supprime l'ancienne image de couverture du disque."""
    if not filename:
        return
    # filename peut être une URL complète ou juste le nom du fichier
    basename = os.path.basename(filename)
    path = os.path.join(BLOG_UPLOAD_DIR, basename)
    if os.path.exists(path):
        os.remove(path)

def _calc_read_time(body: str) -> str:
    words = len((body or '').split())
    return f"{max(1, round(words / 200))} min"

def _make_slug(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = slug[:80]
    return f"{slug}-{uuid.uuid4().hex[:6]}"

def _save_cover_image(file) -> str:
    """Sauvegarde l'image et retourne l'URL publique."""
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(BLOG_UPLOAD_DIR, unique_name)
    file.save(save_path)
    # URL publique accessible depuis le front
    return f"http://localhost:5000/static/uploads/blog/{unique_name}"

# ── Routes ────────────────────────────────────────────────────────────────────

@bp.route('/posts/', methods=['GET'])
def list_posts():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return jsonify([p.to_dict() for p in posts])


@bp.route('/posts/<slug>/content/', methods=['GET'])
def get_content(slug):
    BlogPost.query.filter_by(slug=slug).first_or_404()
    body = _read_content(slug)
    return jsonify({'slug': slug, 'body': body})


@bp.route('/posts/', methods=['POST'])
@jwt_required()
def create_post():
    """
    Accepte multipart/form-data OU application/json.
    Si multipart : les champs texte sont dans request.form,
                   l'image dans request.files['cover_image'].
    """
    identity = get_jwt_identity()

    # ── Lecture des champs selon le content-type ──────────────────────────
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form
        tags_raw = data.get('tags', '[]')
        import json
        try:
            tags = json.loads(tags_raw)
        except Exception:
            tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
    else:
        data = request.json or {}
        tags = data.get('tags', [])

    body = data.get('body', '').strip()
    slug = _make_slug(data.get('title', 'article'))

    # ── Image de couverture (optionnelle) ─────────────────────────────────
    cover_url = None
    file = request.files.get('cover_image')
    if file and file.filename and _allowed_file(file.filename):
        cover_url = _save_cover_image(file)

    post = BlogPost(
        slug        = slug,
        title       = data.get('title', '').strip(),
        excerpt     = data.get('excerpt', '').strip(),
        author      = data.get('author', '').strip(),
        category    = data.get('category', ''),
        tags        = tags,
        read_time   = _calc_read_time(body),
        cover_image = cover_url,
        created_by  = identity.get('id'),
    )
    db.session.add(post)
    db.session.commit()

    if body:
        _write_content(slug, body)

    return jsonify(post.to_dict()), 201


@bp.route('/posts/<int:post_id>/', methods=['PATCH'])
@jwt_required()
def update_post(post_id):
    """
    Accepte multipart/form-data OU application/json.
    Si une nouvelle image est envoyée, l'ancienne est supprimée.
    """
    post = BlogPost.query.get_or_404(post_id)

    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form
        tags_raw = data.get('tags')
        if tags_raw is not None:
            import json
            try:
                post.tags = json.loads(tags_raw)
            except Exception:
                post.tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
    else:
        data = request.json or {}
        if 'tags' in data:
            post.tags = data['tags']

    for field in ('title', 'excerpt', 'author', 'category'):
        if field in data:
            setattr(post, field, data[field])

    body = data.get('body', None)
    if body is not None:
        post.read_time = _calc_read_time(body)
        _write_content(post.slug, body)

    # ── Nouvelle image de couverture ───────────────────────────────────────
    file = request.files.get('cover_image')
    if file and file.filename and _allowed_file(file.filename):
        _delete_cover(post.cover_image)          # supprime l'ancienne
        post.cover_image = _save_cover_image(file)

    # ── Suppression explicite de l'image ──────────────────────────────────
    if data.get('remove_cover') in (True, 'true', '1'):
        _delete_cover(post.cover_image)
        post.cover_image = None

    db.session.commit()
    return jsonify(post.to_dict())


@bp.route('/posts/<int:post_id>/', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    _delete_cover(post.cover_image)
    _delete_content(post.slug)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'msg': 'Article supprimé.'})