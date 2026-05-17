from fastapi import APIRouter
from app.controllers.admin.auth import create,login,editProfile,logout
from app.controllers.admin.user import getUserList,blockUnblocked,deleteUser


adminRouter:APIRouter= APIRouter()

#  Authentication

adminRouter.post("/create")(create)
adminRouter.post("/login")(login)
# adminRouter.get("/logout")(logout)
adminRouter.patch("/update")(editProfile)

# adminRouter.post("/getUsers")(getUserList)
# adminRouter.post("/blockUnblock/{id}")(blockUnblocked)
# adminRouter.delete("/deleteUser/{id}")(deleleUser)











