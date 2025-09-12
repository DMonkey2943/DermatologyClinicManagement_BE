from typing_extensions import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


AuthCredentialDepend = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]