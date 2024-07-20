from oauth2_provider.models import AccessToken, Application
from django.conf import settings

def create_app(app_name, secret="secret123!@###$@"):    
    app = Application.objects.filter(name=app_name)
    if not app:
        print(f"创建application {app_name}")
        newapp = Application(name=app_name, 
                                client_id=app_name,
                                redirect_uris="",
                                client_type="implicit",
                                client_secret=secret,
                                authorization_grant_type="openid-hybrid",
                                )
        newapp.save()
        
    else:
        print(f"oauth app {app_name}, 已存在，跳过创建")
        
def setup_default_app():
    defaultAppName = settings.MTXCMS_DEFAULT_OAUTH_APP_NAME
    try:
        create_app(defaultAppName)
        create_app('app2')

    except Exception as e:
        print(f"出错: {e}")