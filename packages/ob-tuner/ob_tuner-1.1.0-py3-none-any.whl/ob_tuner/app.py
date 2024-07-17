import requests
import uvicorn
import jwt
from fastapi import Request, FastAPI, Depends
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, JSONResponse, FileResponse
from ob_tuner.main_page import main_block as io
from ob_tuner.landing_page import landing_page
from ob_tuner.util import *

CUSTOM_PATH = "/gradio"

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/login")
def login():
    # Redirect to the Cognito Hosted UI

    cognito_login_url = (
        f"{COGNITO_DOMAIN}/login?client_id={CLIENT_ID}" f"&response_type=code&scope=email+openid&redirect_uri={DEPLOYMENT_URL}/callback"
    )
    # logger.info(f"Redirecting to: {cognito_login_url}")
    return RedirectResponse(cognito_login_url)


@app.get("/callback")
def callback(request: Request, code: str):
    token_url = f"{COGNITO_DOMAIN}/oauth2/token"
#     logger.info(f"Back from callback- token URL: {token_url}")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": DEPLOYMENT_URL + '/callback',
    }
#     logger.info(f"Data: {data}")
    try:
        response = requests.post(token_url, headers=headers, data=data)
    except requests.exceptions.RequestException as e:
#         logger.error(f"Could not get token from {COGNITO_DOMAIN}/oauth2/token")
        return JSONResponse(status_code=500, content={"message": f"Authentication failed - can't find {COGNITO_DOMAIN}/oauth2/token"})
    except Exception as e:
#         logger.error(f"Error getting token: {e}")
        return JSONResponse(status_code=500, content={"message": "Authentication failed WTF"})

    if response.status_code == 200:
#         logger.info(f"Succesfully got token from {token_url}: {response.json()}")
        url = "/gradio?__theme=dark"
        tokens = response.json()
        id_token = tokens.get("id_token")
        response = RedirectResponse(url)

        response.set_cookie(key="id_token", value=id_token, httponly=True, secure=True)
        return response
    else:
        # Handle error response
        # add data headers and token_url to the response for troubleshooting

        response_message = {
            "message": f"Authentication failed - {response.status_code}",
            "data": data,
            "headers": headers,
            "token_url": token_url,
        }
#         logger.error(response_message)

        return JSONResponse(status_code=response.status_code, content={"message": "Authentication failed"})


def ensure_user_exists(decoded_token: dict, disable=True):
    if disable:
        return
    groups = decoded_token.get("cognito:groups")
    email_verified = decoded_token.get("email_verified")
    preferred_role = decoded_token.get("cognito:preferred_role")
    username = decoded_token.get("cognito:username")
    roles = decoded_token.get("cognito:roles")
    token_use = decoded_token.get("token_use")
    email = decoded_token.get("email")

    try:
        user = Client.get(email=email)
        # update the user
        user.groups = groups
        user.email_verified = email_verified
        user.preferred_role = preferred_role
        user.username = username
        user.roles = roles
        user.token_use = token_use
    except Exception as e:
        user = Client(
            email=email,
            groups=groups,
            email_verified=email_verified,
            preferred_role=preferred_role,
            username=username,
            roles=roles,
            token_use=token_use,
            location_id="UNKNOWN",
            lls_api_key=None,
            leadmo_api_key=None,
        )
    user.save()

def get_user(request: Request) -> str or None:
#     logger.info(f"Trying to get user from request: {request}")
    try:
        id_token = request.cookies["id_token"]
    except KeyError:
        id_token = None

    if id_token:
        try:
            # Decode the token. Add 'options={"verify_signature": False}' if you don't want to verify the token's signature
            decoded_token = jwt.decode(id_token, options={"verify_signature": False}, algorithms=["RS256"])
            # Extract the email address and return it
            ensure_user_exists(decoded_token)
            email = decoded_token.get("email")
            # logger.info("Successfully got client_id from token")
            return email
        except jwt.PyJWTError as e:
            # Handle decoding error (e.g., token is expired or invalid)
#             logger.warning(f"Token decoding error: {e}")
            print(f"Token decoding error: {e}")
            return None
#     logger.warning(f"No token received in request")

    return None

@app.get('/')
def public(user: dict = Depends(get_user)):
    if user:
        return RedirectResponse(url='/gradio')
    else:
        return RedirectResponse(url='/login-demo')

@app.route('/signup')
async def signup(request: Request):
    signup_url = f"{COGNITO_DOMAIN}/signup?client_id={CLIENT_ID}" f"&response_type=code&scope=email+openid&redirect_uri={DEPLOYMENT_URL}/callback"
    return RedirectResponse(signup_url)


@app.route('/logout')
async def logout(request: Request):
    # logout_url = f"{COGNITO_DOMAIN}/logout?response_type=token&client_id={CLIENT_ID}&redirect_uri={CALLBACK_URL}"
    # logout_url = f"{COGNITO_DOMAIN}/logout?client_id={CLIENT_ID}&logout_uri={CALLBACK_URL}
    logout_url = f"{COGNITO_DOMAIN}/logout?client_id={CLIENT_ID}&logout_uri={DEPLOYMENT_URL}/login-demo"
    return RedirectResponse(logout_url)

    # request.session.pop('user', None)
    # return RedirectResponse(url='/')
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('resources/favicon/favicon.ico')


app = gr.mount_gradio_app(app, landing_page, path="/login-demo")

# app  = gr.mount_gradio_app(app, landing_page, path='/')

app = gr.mount_gradio_app(app, io, path=CUSTOM_PATH, auth_dependency=get_user)


if __name__ == "__main__":
    if os.getenv("GRADIO_PORT", False) or os.getenv("GRADIO_HOST", False):
        gradio_host = os.getenv("GRADIO_HOST", '0.0.0.0')
        gradio_port = int(os.getenv("GRADIO_PORT", 8000))
        uvicorn.run(app, host=gradio_host, port=gradio_port)
    else:
        uvicorn.run(app, host="0.0.0.0", port=80)
