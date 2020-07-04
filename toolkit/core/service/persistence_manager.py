from typing import List, Dict

from ..sqlite.db_manager import DBManager
from ..model.environment import Environment
from ..model.base.entity import PendingEntityBuffer
from ..model.profile import Profile
from ..model.property import Property
from ..log import Log


class PersistenceManager:

    @staticmethod
    def load_environments():
        db = DBManager.db()
        c = db.cursor()
        c.execute("select * from environment")
        rows = c.fetchall()
        column_names = [d[0] for d in c.description]
        c.close()

        environments = []
        for row in rows:
            e = Environment()
            data = {cname: value for (cname, value) in zip(column_names, row)}
            e.deserialize(data)
            PersistenceManager._populate_environment(db, e)
            environments.append(e)

        return environments

    @staticmethod
    def persist_changes(environments: List[Environment]):
        Log.d("Persisting changes to the database")
        try:
            PersistenceManager._create_new_entities(environments)
            PersistenceManager._modify_existing_entities(environments)
            PersistenceManager._delete_entities()
            DBManager.db().commit()
        except Exception as e:
            DBManager.db().rollback()
            Log.e("Error while persisting changes")
            raise e

    @staticmethod
    def _populate_environment(db, environment: Environment):
        c = db.cursor()
        c.execute("select * from profile where environment_id = ?", (environment.id,))
        profile_columns = [d[0] for d in c.description]
        rows = c.fetchall()

        for row in rows:
            profile = Profile()
            data = {cname: value for (cname, value) in zip(profile_columns, row)}
            profile.deserialize(data)

            c.execute("select * from property where profile_id = ?", (profile.id,))
            property_columns = [d[0] for d in c.description]
            property_rows = c.fetchall()
            for property_row in property_rows:
                prop = Property()
                data = {cname: value for (cname, value) in zip(property_columns, property_row)}
                prop.deserialize(data)
                profile.properties.append(prop)

            environment.profiles.append(profile)
        c.close()

    @staticmethod
    def _create_new_entities(environments: List[Environment]):
        new_envs = filter(lambda e: e.new, environments)
        for env in new_envs:
            data = env.serialize()
            if "id" in data:
                del data["id"]
            PersistenceManager._execute_insert_query("environment", data)
            env.new = False
            env.dirty = False

        all_profiles = [p for env in environments for p in env.profiles]
        new_profiles = [p for p in all_profiles if p.new]
        for profile in new_profiles:
            data = profile.serialize()
            if "id" in data:
                del data["id"]
            PersistenceManager._execute_insert_query("profile", data)
            profile.new = False
            profile.dirty = False

        new_props = [prop for profile in all_profiles for prop in profile.properties if prop.new]
        for prop in new_props:
            data = prop.serialize()
            if "id" in data:
                del data["id"]
            PersistenceManager._execute_insert_query("property", data)
            prop.new = False
            prop.dirty = False

    @staticmethod
    def _modify_existing_entities(environments: List[Environment]):
        for env in filter(lambda e: e.dirty, environments):
            PersistenceManager._execute_update_query("environment", env.serialize())
            env.dirty = False

        all_profiles = [p for env in environments for p in env.profiles]
        for profile in filter(lambda x: x.dirty, all_profiles):
            PersistenceManager._execute_update_query("profile", profile.serialize())
            profile.dirty = False

        for prop in [prop for profile in all_profiles for prop in profile.properties if prop.dirty]:
            PersistenceManager._execute_update_query("property", prop.serialize())
            prop.dirty = False

    @staticmethod
    def _delete_entities():
        props = list(filter(lambda e: isinstance(e, Property), PendingEntityBuffer.deleted_entities))
        profiles = list(filter(lambda e: isinstance(e, Profile), PendingEntityBuffer.deleted_entities))
        environments = list(filter(lambda e: isinstance(e, Environment), PendingEntityBuffer.deleted_entities))
        PendingEntityBuffer.deleted_entities.clear()

        profiles += [p for env in environments for p in env.profiles]
        props += [p for profile in profiles for p in profile.properties]

        PersistenceManager._execute_delete_query("environment", [x.id for x in environments])
        PersistenceManager._execute_delete_query("profile", [x.id for x in profiles])
        PersistenceManager._execute_delete_query("property", [x.id for x in props])

    @staticmethod
    def _execute_insert_query(table, values: Dict):
        Log.d("Executing insert query for table {} with values: {}".format(table, str(values)))

        keys = list(values.keys())
        column_names = "({})".format(", ".join(keys))
        placeholders = "(" + ", ".join(["?"] * len(values)) + ")"
        query = "insert into {} {} values {}".format(table, column_names, placeholders)

        c = DBManager.db().cursor()
        c.execute(query, tuple([values[x] for x in keys]))
        c.close()

    @staticmethod
    def _execute_update_query(table, values: Dict):
        Log.d("Executing update query for table {} with values: {}".format(table, values))

        if "id" not in values:
            raise Exception("Id value wasn't found")

        placeholders = []
        replacement_values = []
        for k in values.keys():
            if k == "id":
                continue
            placeholders.append("{} = ?".format(k))
            replacement_values.append(values[k])

        replacement_values.append(values["id"])
        query = "update {} set {} where id = ?".format(table, ", ".join(placeholders))

        c = DBManager.db().cursor()
        c.execute(query, tuple(replacement_values))
        c.close()

    @staticmethod
    def _execute_delete_query(table, values: List):
        if len(values) == 0:
            return

        Log.d("Executing delete query for table {} with values: {}".format(table, values))

        ids = ", ".join(map(str, values))
        query = "delete from {} where id in ({})".format(table, ids)

        c = DBManager.db().cursor()
        c.execute(query)
        c.close()
