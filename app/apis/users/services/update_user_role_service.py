from apis.auth.utils import RolesBasedAuthChecker, get_current_user, update_user
from apis.users.schemas import UserRoleUpdate
from db import models
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing_extensions import Annotated

router = APIRouter()


@router.put("/users/update_role", response_model=UserRoleUpdate)
async def update_user_role(
    user: UserRoleUpdate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    auth=Depends(RolesBasedAuthChecker([models.UserRole.EMPLOYEE, models.UserRole.CHEF])),
):
    # this method allows staff (Employee or Chef) to give Employee role to other users
    # Chef role is restricted
    if user.role == models.UserRole.CHEF.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only Chef is authorized to add Chef role!",
        )

    # Only a Chef may modify the account of an existing Chef.
    target = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if (
        target is not None
        and target.role == models.UserRole.CHEF
        and current_user.role != models.UserRole.CHEF
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Chef is authorized to modify a Chef account!",
        )

    db_user = update_user(db, user.username, user)
    return current_user
