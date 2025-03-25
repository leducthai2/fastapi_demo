from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file='.env', 
                                    env_file_encoding='utf-8')
  gemini_key: str
  gemini_version: str

  backlog_base_url: str
  backlog_user_apikey: str


settings = Settings()