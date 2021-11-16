from flask import render_template, request, jsonify
from . import main

@main.app_errorhandler(403)
def forbidden(e):
    error_title = 'Forbidden'
    error_msg = 'You shouldn\'t be here.'
    return render_template('error.html', error_title=error_title, error_msg=error_msg), 403

@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    error_title="Page Not Found"
    error_msg="That page doesn't exist."
    return render_template(
        'error.html',
        error_title=error_title,
        error_msg=error_msg), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    error_title = "Internal Server Error"
    error_msg = "Sorry, we seem to be experiencing some technical difficulties"
    return render_template('error.html',
                           error_title=error_title,
                           error_msg=error_msg), 500