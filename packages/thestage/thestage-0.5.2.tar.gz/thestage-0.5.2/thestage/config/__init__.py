# Init project settings by ENV environment variable
import locale
from pathlib import Path

import typer
import dotenv
from python_gettext_translations.translations import init_translations

from thestage.config.env_base import *

path_env = Path(__file__).parent.parent.resolve()

env_file = path_env.joinpath('.env')

if not env_file.exists():
    path_env = Path(__file__).parent.parent.parent.resolve()
    env_file = path_env.joinpath('.env')

config = None
if env_file:
    # пока не будет делать, затирает все что делаем
    #dotenv.load_dotenv(env_file, override=True)
    config = dotenv.dotenv_values(env_file)

THESTAGE_LOCAL_LANGUAGE = 'en_GB'
if locale.getlocale():
    THESTAGE_LOCAL_LANGUAGE = locale.getlocale()[0]

translation = Path(f'i18n/')

if translation.exists() and translation.is_dir():
    init_translations(f'i18n/')

ENV: str = config.get("THESTAGE_CLI_ENV", "DEV") if config else 'DEV'

if ENV == "PROD":
    from thestage.config.env_prod import *
elif ENV == "STAGE":
    from thestage.config.env_stage import *
else:
    from thestage.config.env_dev import *
