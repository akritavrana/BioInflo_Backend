from fastapi import FastAPI, HTTPException
from users_api.users import  users_router
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Initialize FastAPI app
app = FastAPI()

# Include the routers
app.include_router(users_router,prefix = '/users',tags = ['users'])


#welcome Link
@app.get('/')
async def welcome():
    return {" welcome"}


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
