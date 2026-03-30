# Dummy entrypoint so Vercel doesn't complain about missing Python web server.
# The real functionality is in api/webhook.py (serverless function).
def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'OK']
