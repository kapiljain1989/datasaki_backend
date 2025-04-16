from app.utils.logging import logger
class MLService:
    def train(self,user_email):
        logger.info(f"Model training initiated by user: {user_email}")
        return {"message": f"Training ML model...{user_email}"}
