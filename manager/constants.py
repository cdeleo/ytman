import dpy

CONSOLE_CLIENT_ID = '955262123852-j4nv7slhidt5lcjve721nj9lo8otmfq5.apps.googleusercontent.com'
WEB_CLIENT_ID = '955262123852-c1gthms5mhs36q6njvg6kgqu4f1b09q7.apps.googleusercontent.com'

CLIENT_IDS = [CONSOLE_CLIENT_ID, WEB_CLIENT_ID]

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/youtube.force-ssl',
]

dpy.Injectable.value(client_id=WEB_CLIENT_ID)
dpy.Injectable.value(scopes=SCOPES)
