from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_HOST1: str
    SQS_QUEUE_URL: str
    
    DB_PORT: int
    DATABASE_URL: str
    APP_PORT: int
    SALT: str
    SQLITE:  str
    ENV: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    STRIPE_API_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    SECRET_KEY: str
    ALGORITHM: str   # add this
    ACCESS_TOKEN_EXPIRE_MINUTES: int  # add this
    ACCESS_TOKEN_EXPIRE_DAYS: int 
    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION:str
    AWS_BUCKET_NAME: str
    
    LLM_MODEL: str
        

    class Config:
        env_file = ".env"

settings = Settings()