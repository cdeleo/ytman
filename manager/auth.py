import dpy
import endpoints

import users

@dpy.Injectable.named('credentials')
@dpy.Singleton
def _provide_credentials(users_client=dpy.IN):
  return users_client.get_credentials()

def require_auth(f):
  @dpy.Scope
  def _inner_f(*args, **kwargs):
    user = endpoints.get_current_user()
    if not user:
     raise endpoints.UnauthorizedException
    dpy.Injectable.value(user_id=user.user_id())
    return f(*args, **kwargs)
  return _inner_f
