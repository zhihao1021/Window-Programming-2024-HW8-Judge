from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pymssql import connect

from typing import Annotated

from config import SQL_SERVER, SQL_ADMIN, SQL_ADMIN_PASSWORD
from validation import JWTManager, JWTDataWithPassword


class ResetResult(BaseModel):
    success: bool = True


UserDepend = Annotated[
    JWTDataWithPassword,
    Depends(JWTManager.validation_function)
]

router = APIRouter(
    prefix="/reset",
    tags=["Reset"]
)


def reset(user: JWTDataWithPassword):
    username = user.username.upper()
    password = user.password

    conn = connect(
        server=SQL_SERVER,
        user=SQL_ADMIN,
        password=SQL_ADMIN_PASSWORD,
        autocommit=True
    )
    cursor = conn.cursor()

    # Logout all session
    cursor.execute(f"""
    SELECT session_id
    FROM sys.dm_exec_sessions
    WHERE login_name = '{username}'
    """)
    logined_sessions = cursor.fetchall()
    if logined_sessions:
        for session in logined_sessions:
            cursor.execute(f"KILL {session[0]}")

    # Drop User
    cursor.execute(f"""
    USE [master]
    DROP LOGIN [{username}]
    """)
    # Drop DB
    cursor.execute(f"""
    EXEC msdb.dbo.sp_delete_database_backuphistory @database_name = N'{username}_db'
    use [master];
    ALTER DATABASE [{username}_db] SET  SINGLE_USER WITH ROLLBACK IMMEDIATE
    DROP DATABASE [{username}_db]
    """)

    # Create User
    cursor.execute(f"""
    USE [master]
    CREATE LOGIN [{username}] WITH PASSWORD=N'{password}', DEFAULT_DATABASE=[master], CHECK_EXPIRATION=OFF, CHECK_POLICY=OFF
    GRANT VIEW ANY DEFINITION TO [{username}]
    DENY VIEW ANY DATABASE TO [{username}]
    """)
    cursor.execute(f"""
    CREATE DATABASE [{username}_db]
    CONTAINMENT = NONE
    ON  PRIMARY 
    ( NAME = N'{username}_db', FILENAME = N'/var/opt/mssql/data/{username}_db.mdf' , SIZE = 8192KB , FILEGROWTH = 65536KB )
    LOG ON 
    ( NAME = N'{username}_db_log', FILENAME = N'/var/opt/mssql/data/{username}_db_log.ldf' , SIZE = 8192KB , FILEGROWTH = 65536KB )
    WITH LEDGER = OFF
    """)
    cursor.execute(f"""
    ALTER DATABASE [{username}_db] SET COMPATIBILITY_LEVEL = 160
    ALTER DATABASE [{username}_db] SET ANSI_NULL_DEFAULT OFF 
    ALTER DATABASE [{username}_db] SET ANSI_NULLS OFF 
    ALTER DATABASE [{username}_db] SET ANSI_PADDING OFF 
    ALTER DATABASE [{username}_db] SET ANSI_WARNINGS OFF 
    ALTER DATABASE [{username}_db] SET ARITHABORT OFF 
    ALTER DATABASE [{username}_db] SET AUTO_CLOSE OFF 
    ALTER DATABASE [{username}_db] SET AUTO_SHRINK OFF 
    ALTER DATABASE [{username}_db] SET AUTO_CREATE_STATISTICS ON(INCREMENTAL = OFF)
    ALTER DATABASE [{username}_db] SET AUTO_UPDATE_STATISTICS ON 
    ALTER DATABASE [{username}_db] SET CURSOR_CLOSE_ON_COMMIT OFF 
    ALTER DATABASE [{username}_db] SET CURSOR_DEFAULT  GLOBAL 
    ALTER DATABASE [{username}_db] SET CONCAT_NULL_YIELDS_NULL OFF 
    ALTER DATABASE [{username}_db] SET NUMERIC_ROUNDABORT OFF 
    ALTER DATABASE [{username}_db] SET QUOTED_IDENTIFIER OFF 
    ALTER DATABASE [{username}_db] SET RECURSIVE_TRIGGERS OFF 
    ALTER DATABASE [{username}_db] SET  DISABLE_BROKER 
    ALTER DATABASE [{username}_db] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
    ALTER DATABASE [{username}_db] SET DATE_CORRELATION_OPTIMIZATION OFF 
    ALTER DATABASE [{username}_db] SET PARAMETERIZATION SIMPLE 
    ALTER DATABASE [{username}_db] SET READ_COMMITTED_SNAPSHOT OFF 
    ALTER DATABASE [{username}_db] SET  READ_WRITE 
    ALTER DATABASE [{username}_db] SET RECOVERY FULL 
    ALTER DATABASE [{username}_db] SET  MULTI_USER 
    ALTER DATABASE [{username}_db] SET PAGE_VERIFY CHECKSUM  
    ALTER DATABASE [{username}_db] SET TARGET_RECOVERY_TIME = 60 SECONDS 
    ALTER DATABASE [{username}_db] SET DELAYED_DURABILITY = DISABLED 

    USE [{username}_db]
    ALTER DATABASE SCOPED CONFIGURATION SET LEGACY_CARDINALITY_ESTIMATION = Off;
    ALTER DATABASE SCOPED CONFIGURATION FOR SECONDARY SET LEGACY_CARDINALITY_ESTIMATION = Primary;
    ALTER DATABASE SCOPED CONFIGURATION SET MAXDOP = 0;
    ALTER DATABASE SCOPED CONFIGURATION FOR SECONDARY SET MAXDOP = PRIMARY;
    ALTER DATABASE SCOPED CONFIGURATION SET PARAMETER_SNIFFING = On;
    ALTER DATABASE SCOPED CONFIGURATION FOR SECONDARY SET PARAMETER_SNIFFING = Primary;
    ALTER DATABASE SCOPED CONFIGURATION SET QUERY_OPTIMIZER_HOTFIXES = Off;
    ALTER DATABASE SCOPED CONFIGURATION FOR SECONDARY SET QUERY_OPTIMIZER_HOTFIXES = Primary;
    IF NOT EXISTS (SELECT name FROM sys.filegroups WHERE is_default=1 AND name = N'PRIMARY') ALTER DATABASE [{username}_db] MODIFY FILEGROUP [PRIMARY] DEFAULT
    CREATE USER {username} for login {username};
    EXEC sp_addrolemember N'db_owner', N'{username}'
    """)

    cursor.close()
    conn.close()


@router.put(
    path="",
    response_model=ResetResult
)
def reset_db(user: UserDepend) -> ResetResult:
    try:
        reset(user=user)
        return ResetResult(success=True)
    except:
        return ResetResult(success=False)
