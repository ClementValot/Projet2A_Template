from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector

load_dotenv()


class ResetDatabase:
    """
    Resetting the database using DBConnector and SQL files.
    """

    def lancer(self):
        print("Database reset")

        try:
            with open("data/init_db.sql", encoding="utf-8") as init_db:
                init_db_as_string = init_db.read()

            with open("data/pop_db.sql", encoding="utf-8") as pop_db:
                pop_db_as_string = pop_db.read()

            db_connector = DBConnector()

            db_connector.sql_query(init_db_as_string, return_type=None)
            db_connector.sql_query(pop_db_as_string, return_type=None)

            print("Database reset - Completed")
            return True

        except FileNotFoundError as e:
            print(f"Error: SQL file not found : {e}")
            raise
        except Exception as e:
            print(f"Error during reset : {e}")
            raise


if __name__ == "__main__":
    ResetDatabase().lancer()
