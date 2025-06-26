from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse


import main
from core import security
from schemas.shemas import AddTVShows

show_router = APIRouter(tags=["shows"], prefix="/shows")


@show_router.post("/add-show")
def add_show(show_data: AddTVShows, user=Depends(security.get_current_user)):
    security.check_admin(user)

    try:
        main.cursor.execute(
            """INSERT INTO tv_shows (tv_show_name, tv_show_image_url)
            VALUES (%s, %s)""",
            (show_data.show_name, show_data.tv_show_image)
        )
        main.conn.commit()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Show added successfully"}
    )


@show_router.get("/get-show-by-id/{tv_show_id}")
def get_tv_show_by_id(tv_show_id: int):
    try:
        main.cursor.execute("""SELECT tv_show_id FROM tv_shows WHERE tv_show_id=%s""",
                            (tv_show_id,))
        checked_id = main.cursor.fetchone()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if checked_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"message": "tv show didn't find"})

    try:
        main.cursor.execute("""SELECT * FROM tv_shows WHERE tv_show_id=%s""",
                            (tv_show_id,))
        show_info = dict(main.cursor.fetchone())

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"tv show": f"{show_info}"})


@show_router.get("/get-all-shows")
def get_all_shows():
    try:
        main.cursor.execute("""SELECT * FROM tv_shows""")

        all_shows = main.cursor.fetchall()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"tv shows": f"{all_shows}"})


@show_router.delete("/delete-show-by-id/{tv_show_id}")
def delete_show_by_id(tv_show_id: int, user=Depends(security.get_current_user)):
    security.check_admin(user)

    try:
        main.cursor.execute("""SELECT tv_show_id FROM tv_shows WHERE tv_show_id=%s""",
                            (tv_show_id,))
        checked_show_id = main.cursor.fetchone()

    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})

    if checked_show_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": "show didn't find"})

    try:
        main.cursor.execute("""delete from tv_shows where tv_show_id=%s""",
                            (tv_show_id,))

        main.conn.commit()
    except Exception as error:
        main.conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"message": error})
