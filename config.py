from pydantic_settings import BaseSettings,SettingsConfigDict


class Config(BaseSettings):
    POSTGRES_USER:str 
    POSTGRES_PASSWORD:str 
    POSTGRES_DB:str 
    CLOUDINARY_CLOUD_NAME:str
    CLOUDINARY_API_KEY:str
    CLOUDINARY_API_SECRET:str
    DB_URL:str
    model_config=SettingsConfigDict(env_file='.env')




settings=Config()