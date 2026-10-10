import os
from dotenv import load_dotenv

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dto.static_types import Role

load_dotenv()

class Config:
    CONNECTION_STRING = os.getenv("CONNECTION_STRING", "")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

    JWT_SECRET = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY = int(os.getenv("JWT_EXPIRY", 86400))

    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = os.getenv("SMTP_PORT", 587)
    SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    URL_SERVER = os.getenv("URL_SERVER", "http://localhost:8000/users/verify?token=")
    
class Database:
    async def init_orm(self) -> None:
        self.ENGINE = create_async_engine(Config.CONNECTION_STRING, echo=Config.DEBUG)
        self.SESSION_MAKER = async_sessionmaker(self.ENGINE, expire_on_commit=False)

    async def teardown_orm(self) -> None:
        await self.ENGINE.dispose()

    async def create_default_user(self) -> None:
        from db.user import User
        from services.otp import EmailOTPService
        email_otp_service = EmailOTPService()
        async with self.SESSION_MAKER() as s:
            z = await s.scalar(select(User).where(User.email==Config.ADMIN_EMAIL))
            if z is None:
                await s.scalar(insert(User).values({"email": Config.ADMIN_EMAIL,
                                                    "name": "Msaid",
                                                    "surname": "Vosidov",
                                                    "password": await User.hash_password(Config.ADMIN_PASSWORD),
                                                    "role": Role.admin,
                                                    "is_confirmed": True,
                                                    "confirmation_token": await User.hash_password(await email_otp_service.generate_otp())}))
            await s.commit()

    async def create_default_product(self) -> None:
        from db.application import Product
        async with self.SESSION_MAKER() as s:
            z = await s.scalar(select(Product).where(Product.id==1))
            if z is None:
                await s.scalar(insert(Product).values({"name": "Product 1",
                                                        "description": "Description 1",
                                                        "price": 100}))
            await s.commit()

configs = Config()
db_instance = Database()