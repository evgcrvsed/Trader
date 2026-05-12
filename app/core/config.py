from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///data/database.db"

class SteamAccount(BaseSettings):
    STEAM_LOGIN: str
    STEAM_PASSWORD: str
    STEAM_SHARED_SECRET: str
    STEAM_IDENTITY_SECRET: str
    STEAM_STEAM_ID: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

class BotSettings(BaseSettings):
    steam_minimal_price: int = 270

settings = Settings()
steam_settings = SteamAccount()
bot_settings = BotSettings()




# DEBUG — детали, шум
# INFO — нормальный ход работы
# WARNING — что-то странное, но не критично
# ERROR — ошибка, но программа жива
# CRITICAL — всё плохо, падаем


