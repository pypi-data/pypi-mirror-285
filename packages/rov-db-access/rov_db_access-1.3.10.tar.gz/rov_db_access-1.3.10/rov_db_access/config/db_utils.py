from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session
from psycopg2 import OperationalError


def init_db_engine(
    db_user: str, db_password: str, db_host: str, db_port: str, db_name: str
) -> Engine:
    """Initializes sqlalchemy engine that connects to postgis database

    Args:
        db_user (str): the user name
        db_password (str): the password
        db_host (str): the url of the database host
        db_port (str): the port of the connection
        db_name (str): the name of the database

    Returns:
        Engine: connection to postgis database
    """
    return create_engine(
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
        # enable the echo flag to see the SQL generated
        # echo=True,
    )


class BaseWorker:
    def __init__(self, db_user, db_password, db_host, db_port, db_name):
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name

        self.engine = self.init_db_engine()
        self.session = Session(self.engine)

    def init_db_engine(self) -> Engine:
        """Initializes sqlalchemy engine that connects to postgis database

        Args:
            db_user (str): the user name
            db_password (str): the password
            db_host (str): the url of the database host
            db_port (str): the port of the connection
            db_name (str): the name of the database

        Returns:
            Engine: connection to postgis database
        """
        return create_engine(
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def check_db_connection(self):
        try:
            self.session.execute(select(1))
        except OperationalError as e:
            print(f"Database connection error: {e}")
            self.reconnect_db()

    def reconnect_db(self):
        self.engine = self.init_db_engine()
        self.session = Session(self.engine)
        print("Reconnected to database")
