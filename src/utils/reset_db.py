import sys
from typing import Literal

from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector

from .Populate.Faker import fake
from .Populate.Usurper import Usurper
from .singleton import Singleton

load_dotenv()


class ResetDatabase(metaclass=Singleton):
    """
    Resetting the DB
    """

    def startreset(self, schema: str = ("project, test"), prod: Literal["True", "False"] = "False"):
        if "project" in schema:
            print(prod)
            self.reset_project(prod)
        if "test" in schema:
            self.reset_test()

        print("DB reset completed")
        return True

    def reset_project(self, prod: Literal["True", "False"]):
        print("Initiating project DB reset...")
        dbconnector = DBConnector()

        init_db = open("database_scripts/init_db.sql", encoding="utf-8")
        init_db_as_string = init_db.read()
        populate_users = open("database_scripts/populate_users.sql", encoding="utf-8")
        populate_users_as_string = populate_users.read()

        try:
            dbconnector.sql_query(query=init_db_as_string, return_type="none")
            dbconnector.sql_query(query=populate_users_as_string, return_type="none")
            print(prod)
            if prod == "False":
                usurper = Usurper(fake, dbconnector)
                usurper.populate_database()
            else:
                populate_orderables = open(
                    "database_scripts/populate_orderables.sql", encoding="utf-8"
                )
                populate_orderables_as_string = populate_orderables.read()
                dbconnector.sql_query(query=populate_orderables_as_string, return_type="none")

        except Exception as e:
            print(e)
            raise
        return True

    def reset_test(self):
        print("Initiating test DB reset...")
        dbconnector = DBConnector(test=True)

        init_db = open("database_scripts/init_db_test.sql", encoding="utf-8")
        init_db_as_string = init_db.read()
        print("Tests DB reset - Database structure created ")
        # print(init_db_as_string[:7])
        # pop_db = open("database_scripts/pop_db.sql", encoding="utf-8")
        # pop_db_as_string = pop_db.read()

        try:
            dbconnector.sql_query(query=init_db_as_string, return_type="none")
        except Exception as e:
            print(e)
            raise
        # TODO : confirm return type
        return True


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) == 1 or len(sys.argv) == 3:
        ResetDatabase().startreset()
    else:
        ResetDatabase().startreset(schema=sys.argv[1:2], prod=sys.argv[3])
