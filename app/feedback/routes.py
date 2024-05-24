from app.feedback import bp

@bp.route('/', methods=["POST"])
def index():
    return "home"