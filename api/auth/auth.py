# FastAPI
from fastapi import HTTPException, status, Depends, APIRouter, Query
from fastapi.responses import JSONResponse
import main

from core import security

from schemas.shemas import UserAdd, UserLogin, ChangeUserRole, ChangeUserName


auth_router = APIRouter(tags=["auth"], prefix="/auth")


@auth_router.post("/add-user")
def add_user(user_data: UserAdd):
    user_password = user_data.password
    user_hashed_password = security.hash_password(user_password)

    try:
        main.cursor.execute(
            """SELECT user_email FROM users WHERE user_email = %s""",
            (user_data.email,))
        check_email = main.cursor.fetchone()

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if check_email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email is already exists")


    try:
        main.cursor.execute("""INSERT INTO users (user_name, user_email, user_password)
                            VALUES (%s, %s, %s) RETURNING *""",
                            (user_data.name,
                             user_data.email,
                             user_hashed_password,
                             ))
        main.conn.commit()

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error
        )

@auth_router.post("/login")
def login(user_data: UserLogin):
    try:
        main.cursor.execute(
            "SELECT * FROM users WHERE user_email = %s",
            (user_data.email,)
        )
        user_row = main.cursor.fetchone()

        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        user_info = dict(user_row)

        user_hashed_password = user_info["user_password"]
        user_id = user_info["user_id"]
        role = user_info["role"]

        if not security.verify_password(user_data.password, user_hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        token_data = {
            "user_id": user_id,
            "user_email": user_data.email,
            "role": role
        }

        access_token = security.create_access_token(token_data)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"access_token": access_token, "token_type": "bearer"})

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )


@auth_router.get("/get-user-by-id/{user_id}")
def get_user_by_id(user_id: int, user=Depends(security.get_current_user)):
    security.check_admin(user)

    try:
        main.cursor.execute("""SELECT * FROM users WHERE user_id=%s""",
                            (user_id,))

        user_info = main.cursor.fetchone()

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=f"{user_info}")

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User didn't found"
        )


@auth_router.delete("/delete-user/{user_id}")
def delete_user(user_id: int, user=Depends(security.get_current_user)):
    security.check_admin(user)

    try:
        main.cursor.execute("""SELECT user_id FROM users WHERE user_id=%s""",
                            (user_id,))
        checked_user_id = main.cursor.fetchone()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if checked_user_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": "user didn't find"})

    try:
        main.cursor.execute("""delete from users where user_id=%s""",
                            (user_id,))

        main.conn.commit()
    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "Successfully deleted"})


@auth_router.get("/get-all-users")
def get_all_users(user=Depends(security.get_current_user)):
    security.check_admin(user)

    try:
        main.cursor.execute("""SELECT * FROM users""")

        users = main.cursor.fetchall()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=f"{users}")


@auth_router.put("/change-user-role-by-id/{user_id}")
def change_user_role_by_id(user_id: int, new_user_role: ChangeUserRole, user=Depends(security.get_current_user)):
    security.check_admin(user)

    try:
        main.cursor.execute("""SELECT role FROM users WHERE user_id=%s""",
                            (user_id,))
        checked_user_role = main.cursor.fetchone()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if checked_user_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"message": "user didn't find"})

    try:
        main.cursor.execute("""UPDATE users SET role = %s WHERE user_id = %s""",
                            (new_user_role.role, user_id))
        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "role successfully changed!"})


@auth_router.put("/change-user-name-by-id/{user_id}")
def change_user_name_by_id(user_id: int, new_user_name: ChangeUserName, user=Depends(security.get_current_user)):
    current_user_id = dict(user).get("user_id")

    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "You can't change another user's name!"}
        )

    try:
        main.cursor.execute("SELECT user_name FROM users WHERE user_id = %s", (user_id,))
        current_name_row = main.cursor.fetchone()

        if not current_name_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail={"message": "User not found"})

        current_name = current_name_row["user_name"]

        if new_user_name.name == current_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"message": "This is already your current name"})

        main.cursor.execute("SELECT user_id FROM users WHERE user_name = %s AND user_id != %s",
                            (new_user_name.name, user_id))
        if main.cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Name is already taken"})

        main.cursor.execute("UPDATE users SET user_name = %s WHERE user_id = %s",
                            (new_user_name.name, user_id))
        main.conn.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Name successfully changed to {new_user_name.name}"}
        )

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": str(error)})
