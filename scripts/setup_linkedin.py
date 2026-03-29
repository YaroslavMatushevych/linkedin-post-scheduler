"""
One-time helper to get your LinkedIn OAuth access token.

Usage:
  1. Create a LinkedIn App at https://developer.linkedin.com
  2. Add product: "Share on LinkedIn" + "Sign In with LinkedIn using OpenID Connect"
  3. Set Redirect URL to: http://localhost:8888/callback
  4. Run: python scripts/setup_linkedin.py
  5. Copy the printed LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN to GitHub Secrets.
"""
import os
import json
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

CLIENT_ID = input("LinkedIn App Client ID: ").strip()
CLIENT_SECRET = input("LinkedIn App Client Secret: ").strip()
REDIRECT_URI = "http://localhost:8888/callback"

auth_url = (
    "https://www.linkedin.com/oauth/v2/authorization?"
    + urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": "openid profile w_member_social",
        }
    )
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
        self.wfile.write(b"Got it! You can close this tab.")

    def log_message(self, *args):
        pass


print("Waiting for LinkedIn redirect (listening on :8888)...")
server = HTTPServer(("localhost", 8888), CallbackHandler)
server.handle_request()

code = code_holder.get("code")
if not code:
    raise SystemExit("No code received. Did you authorize the app?")

# Exchange code for token
data = urllib.parse.urlencode(
    {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
).encode()

req = urllib.request.Request(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
with urllib.request.urlopen(req) as r:
    token_data = json.loads(r.read())

access_token = token_data["access_token"]
print(f"\nAccess token (expires in {token_data.get('expires_in', '?')}s):\n{access_token}")

# Get profile to find person URN
req2 = urllib.request.Request(
    "https://api.linkedin.com/v2/userinfo",
    headers={"Authorization": f"Bearer {access_token}"},
)
with urllib.request.urlopen(req2) as r:
    profile = json.loads(r.read())

sub = profile.get("sub", "")  # this IS the member ID
print(f"\nLinkedIn Person URN (member ID): {sub}")
print("\n--- Add these to GitHub Secrets ---")
print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
print(f"LINKEDIN_PERSON_URN={sub}")
