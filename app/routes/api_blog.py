import os, uuid, re, json
from datetime import datetime
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('api_blog', __name__, url_prefix='/api/blog')

BASE_DIR        = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BLOG_CONTENT_DIR = os.path.join(BASE_DIR, 'blog_content')
COVERS_DIR      = os.path.join(BASE_DIR, 'blog_content', 'covers')
META_DIR        = os.path.join(BASE_DIR, 'blog_content', 'meta')

os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# ── helpers ────────────────────────────────────────────────────────────────────

def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def _make_slug(title):
    base = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-') or 'article'
    return f"{base}-{uuid.uuid4().hex[:6]}"

def _calc_read_time(body):
    words = len((body or '').split())
    return f"{max(1, round(words / 200))} min"

def _meta_path(post_id):
    return os.path.join(META_DIR, f"{post_id}.json")

def _content_path(post_id):
    return os.path.join(BLOG_CONTENT_DIR, f"{post_id}.md")

def _load_meta(post_id):
    path = _meta_path(post_id)
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def _save_meta(meta):
    with open(_meta_path(meta['id']), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def _delete_meta(post_id):
    path = _meta_path(post_id)
    if os.path.exists(path):
        os.remove(path)

def _read_content(post_id):
    path = _content_path(post_id)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return f.read()
    return ''

def _write_content(post_id, body):
    with open(_content_path(post_id), 'w', encoding='utf-8') as f:
        f.write(body)

def _delete_content(post_id):
    path = _content_path(post_id)
    if os.path.exists(path):
        os.remove(path)

def _save_cover(post_id, file):
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{post_id}.{ext}"
    file.save(os.path.join(COVERS_DIR, filename))
    return f"/api/blog/covers/{filename}"

def _delete_cover_file(cover_url):
    if not cover_url:
        return
    filename = cover_url.split('/')[-1]
    path = os.path.join(COVERS_DIR, filename)
    if os.path.exists(path):
        os.remove(path)

def _all_posts():
    posts = []
    for fname in os.listdir(META_DIR):
        if fname.endswith('.json'):
            post_id = fname[:-5]
            meta = _load_meta(post_id)
            if meta:
                posts.append(meta)
    posts.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    return posts

# ── routes ────────────────────────────────────────────────────────────────────

@bp.route('/covers/<filename>')
def serve_cover(filename):
    return send_from_directory(COVERS_DIR, filename)


@bp.route('/posts/', methods=['GET'])
def list_posts():
    return jsonify(_all_posts())


@bp.route('/posts/<post_id>/', methods=['GET'])
def get_post(post_id):
    meta = _load_meta(post_id)
    if not meta:
        return jsonify({'error': 'Not found'}), 404
    meta['body'] = _read_content(post_id)
    return jsonify(meta)


@bp.route('/posts/', methods=['POST'])
@jwt_required()
def create_post():
    title    = (request.form.get('title',    '') or '').strip()
    excerpt  = (request.form.get('excerpt',  '') or '').strip()
    author   = (request.form.get('author',   '') or '').strip()
    category = (request.form.get('category', '') or '').strip()
    body     = (request.form.get('body',     '') or '').strip()
    tags_raw = request.form.get('tags', '[]')

    try:
        tags = json.loads(tags_raw)
    except Exception:
        tags = [t.strip() for t in tags_raw.split(',') if t.strip()]

    post_id = _make_slug(title)

    cover_url = None
    cover_file = request.files.get('cover_image')
    if cover_file and cover_file.filename and _allowed(cover_file.filename):
        cover_url = _save_cover(post_id, cover_file)

    meta = {
        'id':         post_id,
        'title':      title,
        'excerpt':    excerpt,
        'author':     author,
        'category':   category,
        'tags':       tags,
        'read_time':  _calc_read_time(body),
        'cover_image': cover_url,
        'created_at': datetime.utcnow().isoformat(),
    }
    _save_meta(meta)
    _write_content(post_id, body)

    return jsonify(meta), 201


@bp.route('/posts/<post_id>/', methods=['PATCH'])
@jwt_required()
def update_post(post_id):
    meta = _load_meta(post_id)
    if not meta:
        return jsonify({'error': 'Not found'}), 404

    for field in ('title', 'excerpt', 'author', 'category'):
        val = request.form.get(field)
        if val is not None:
            meta[field] = val.strip()

    tags_raw = request.form.get('tags')
    if tags_raw is not None:
        try:
            meta['tags'] = json.loads(tags_raw)
        except Exception:
            meta['tags'] = [t.strip() for t in tags_raw.split(',') if t.strip()]

    body = request.form.get('body')
    if body is not None:
        body = body.strip()
        meta['read_time'] = _calc_read_time(body)
        _write_content(post_id, body)

    if request.form.get('remove_cover') == 'true':
        _delete_cover_file(meta.get('cover_image'))
        meta['cover_image'] = None
    else:
        cover_file = request.files.get('cover_image')
        if cover_file and cover_file.filename and _allowed(cover_file.filename):
            _delete_cover_file(meta.get('cover_image'))
            meta['cover_image'] = _save_cover(post_id, cover_file)

    _save_meta(meta)
    return jsonify(meta)


@bp.route('/posts/<post_id>/', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    meta = _load_meta(post_id)
    if not meta:
        return jsonify({'error': 'Not found'}), 404

    _delete_content(post_id)
    _delete_cover_file(meta.get('cover_image'))
    _delete_meta(post_id)
    return jsonify({'msg': 'Article supprimé.'})