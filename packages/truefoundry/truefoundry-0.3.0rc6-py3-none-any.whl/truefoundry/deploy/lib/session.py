import os
from typing import Optional

import rich_click as click

from truefoundry.deploy.io.output_callback import OutputCallBack
from truefoundry.deploy.lib.auth.auth_service_client import AuthServiceClient
from truefoundry.deploy.lib.auth.credential_file_manager import CredentialsFileManager
from truefoundry.deploy.lib.auth.credential_provider import EnvCredentialProvider
from truefoundry.deploy.lib.clients.servicefoundry_client import (
    ServiceFoundryServiceClient,
)
from truefoundry.deploy.lib.clients.utils import resolve_base_url
from truefoundry.deploy.lib.const import (
    API_KEY_ENV_NAME,
    HOST_ENV_NAME,
    OLD_SFY_PROFILES_FILEPATH,
    OLD_SFY_SESSIONS_FILEPATH,
    RICH_OUTPUT_CALLBACK,
)
from truefoundry.deploy.lib.messages import (
    PROMPT_ALREADY_LOGGED_OUT,
    PROMPT_LOGOUT_SUCCESSFUL,
)
from truefoundry.deploy.lib.model.entity import CredentialsFileContent, Token
from truefoundry.logger import logger

if OLD_SFY_PROFILES_FILEPATH.exists():
    logger.warning(
        "%s file is deprecated. You can delete this file now.",
        OLD_SFY_PROFILES_FILEPATH,
    )


if OLD_SFY_SESSIONS_FILEPATH.exists():
    logger.warning(
        "%s file is deprecated. You can delete this file now.",
        OLD_SFY_SESSIONS_FILEPATH,
    )


def login(
    api_key: Optional[str] = None,
    host: Optional[str] = None,
    relogin: bool = False,
    output_hook: OutputCallBack = RICH_OUTPUT_CALLBACK,
) -> bool:
    if API_KEY_ENV_NAME in os.environ and HOST_ENV_NAME in os.environ:
        logger.warning(
            "Skipping login because environment variables %s and "
            "%s are set and will be used when running truefoundry. "
            "If you want to relogin then unset these environment keys.",
            HOST_ENV_NAME,
            API_KEY_ENV_NAME,
        )
        return False

    if EnvCredentialProvider.can_provide():
        logger.warning(
            "TFY_API_KEY env var is already set. "
            "When running truefoundry, it will use the api key to authorize.\n"
            "Login will just save the credentials on disk."
        )

    host = resolve_base_url(host).strip("/")

    with CredentialsFileManager() as cred_file:
        if not relogin and cred_file.exists():
            cred_file_content = cred_file.read()
            if host != cred_file_content.host:
                if click.confirm(
                    f"Already logged in to {cred_file_content.host!r}\n"
                    f"Do you want to relogin to {host!r}?"
                ):
                    return login(api_key=api_key, host=host, relogin=True)

            user_info = cred_file_content.to_token().to_user_info()
            user_name_display_info = user_info.email or user_info.user_type.value
            output_hook.print_line(
                f"Already logged in to {cred_file_content.host!r} as "
                f"{user_info.user_id!r} ({user_name_display_info})\n"
                "Please use `tfy login --relogin` or `tfy.login(relogin=True)` "
                "to force relogin"
            )
            return False

        if api_key:
            servicefoundry_client = ServiceFoundryServiceClient(
                init_session=False, base_url=host
            )
            token = _login_with_api_key(
                api_key=api_key, servicefoundry_client=servicefoundry_client
            )
        else:
            auth_service = AuthServiceClient(base_url=host)
            # interactive login
            token = _login_with_device_code(base_url=host, auth_service=auth_service)

        cred_file_content = CredentialsFileContent(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            host=host,
        )
        cred_file.write(cred_file_content)

    user_info = token.to_user_info()
    user_name_display_info = user_info.email or user_info.user_type.value
    output_hook.print_line(
        f"Successfully logged in to {cred_file_content.host!r} as "
        f"{user_info.user_id!r} ({user_name_display_info})"
    )
    return True


def logout(
    output_hook: OutputCallBack = RICH_OUTPUT_CALLBACK,
) -> None:
    with CredentialsFileManager() as cred_file:
        if cred_file.delete():
            output_hook.print_line(PROMPT_LOGOUT_SUCCESSFUL)
        else:
            output_hook.print_line(PROMPT_ALREADY_LOGGED_OUT)


def _login_with_api_key(
    api_key: str, servicefoundry_client: ServiceFoundryServiceClient
) -> Token:
    logger.debug("Logging in with api key")
    return servicefoundry_client.get_token_from_api_key(api_key=api_key)


def _login_with_device_code(
    base_url: str,
    auth_service: AuthServiceClient,
    output_hook: OutputCallBack = RICH_OUTPUT_CALLBACK,
) -> Token:
    logger.debug("Logging in with device code")
    device_code = auth_service.get_device_code()
    url_to_go = device_code.get_user_clickable_url(auth_host=base_url)
    output_hook.print_line(f"Opening:- {url_to_go}")
    output_hook.print(
        "Please click on the above link if it is not "
        "automatically opened in a browser window."
    )
    click.launch(url_to_go)
    return auth_service.get_token_from_device_code(device_code=device_code.device_code)
