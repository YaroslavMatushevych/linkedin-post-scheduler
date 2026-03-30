"""
One-time helper to get your LinkedIn OAuth access token.
Run: python scripts/setup_linkedin.py
"""
import json
import os
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID") or input("LinkedIn App Client ID: ").strip()
CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET") or input("LinkedIn App Client Secret: ").strip()
REDIRECT_URI = "http://localhost:8888/callback"

auth_url = (
    "https://www.linkedin.com/oauth/v2/authorization?"
    + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "w_member_social",
    })
)

print(f"\nOpen this URL in your browser:\n\n{auth_url}\n")

code_holder = {}


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        code_holder["code"] = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Done! You can close this tab and go back to the terminal.</h2>")

    def log_message(self, *args):
        pass


print("Waiting for LinkedIn redirect on http://localhost:8888 ...")
server = HTTPServer(("localhost", 8888), CallbackHandler)
server.handle_request()

code = code_holder.get("code")
if not code:
    raise SystemExit("No code received.")

data = urllib.parse.urlencode({
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": REDIRECT_URI,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}).encode()

req = urllib.request.Request(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
with urllib.request.urlopen(req) as r:
    token_data = json.loads(r.read())

access_token = token_data["access_token"]

# Get member ID via token introspection
introspect_data = urllib.parse.urlencode({
    "token": access_token,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}).encode()
req2 = urllib.request.Request(
    "https://www.linkedin.com/oauth/v2/introspectToken",
    data=introspect_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
with urllib.request.urlopen(req2) as r:
    introspect = json.loads(r.read())

# authorized_user looks like "urn:li:member:123456789"
authorized_user = introspect.get("authorized_user", "")
person_urn = authorized_user.split(":")[-1] if authorized_user else ""

print("\n✅ Success! Copy these into your .env.local and GitHub Secrets:\n")
print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
print(f"LINKEDIN_PERSON_URN={person_urn}")
