from flask import jsonify

def jsonify_failed(message):
    return jsonify({
        "message": message,
        "status": "Failed"
    })

def jsonify_success(message):
    return jsonify({
        "message": message,
        "status": "Success"
    })

