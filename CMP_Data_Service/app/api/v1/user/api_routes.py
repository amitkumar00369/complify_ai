from fastapi import APIRouter
from app.controllers.user.user_controller import create_user,verifyOtp,editProfile, login,logout,deleteAccount,resentOtp
userRouter: APIRouter = APIRouter()

# User Auhtentication apis

# userRouter.post("/create")(create_user)
# userRouter.post("/login")(login)
# userRouter.post("/verifyOtp")(verifyOtp)
# userRouter.post("/sentOtp")(resentOtp)
# userRouter.put("/edit")(editProfile)
# userRouter.get("/logout")(logout)
# userRouter.delete("/delete")(deleteAccount)


# userRouter.post("/analyze")(analyze)
