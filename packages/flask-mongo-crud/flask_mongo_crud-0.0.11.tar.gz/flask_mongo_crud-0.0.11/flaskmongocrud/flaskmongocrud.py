import os
import re
import inspect
import importlib
import json
import traceback

from bson.json_util import dumps
from bson.objectid import ObjectId

# Provides a CRUD System Integrated to Flask
class FlaskMongoCrud(object):
    def __init__(self, app=None, mongo=None) -> None:
        self.app = None
        self.mongo = None

        if app:
            self.init_app(app)


    # Initialize the CRUD System with a Flask application, Flask request & mongo instances.
    def init_app(self, app, request, mongo):
        self.app = app
        self.app.flask_crud = self
        self.request = request
        self.mongo = mongo

        app_configs = self._load_config()

        app.config["MONGO_URI"] = f"mongodb://{app_configs['db_host']}/{app_configs['database_name']}"

        mongo.init_app(app)

        """
            Get Caller Absolute Path
            But Need to figure out how to accommodate other OS (MacOS, Linux, etc)
        """
        callee_abs_path = os.path.abspath((inspect.stack()[0])[1]) # No use at the moment
        abs_path = os.path.abspath((inspect.stack()[1])[1])
        caller_directory = os.path.dirname(abs_path)
        project_root = caller_directory.split("\\")[-1]

        # -------------------------------------------------------------------------------

        routes_models = self.get_models(models_type="routes_models", project_root=project_root)
        db_models = self.get_models(models_type="db_models", project_root=project_root)

        url_prefix = app_configs["url_prefix"]

        for model in routes_models:
            app.route(f"{url_prefix}/{model}", methods=["GET", "POST"])(self.db_interface(
                self.request,
                db_models,
                self.mongo,
                model,
                id=None
            ))
            app.route(f"{url_prefix}/{model}/<id>", methods=["GET", "PUT", "PATCH", "DELETE"])(self.db_interface(
                self.request,
                db_models,
                self.mongo,
                model,
                id
            ))


    # Load the configurations from the Flask configuration
    def _load_config(self):
        options = dict()

        db_username = self.app.config.get("DB_USERNAME")
        if db_username:
            options["db_username"] = db_username

        db_password = self.app.config.get("DB_PASSWORD")
        if db_password:
            options["db_password"] = db_password

        db_host = self.app.config.get("DB_HOST")
        if db_host:
            options["db_host"] = db_host

        database_name = self.app.config.get("DATABASE_NAME")
        if database_name:
            options["database_name"] = database_name

        url_prefix = self.app.config.get("URL_PREFIX")
        if url_prefix:
            options["url_prefix"] = url_prefix


        return options
    

    # GET MODELS
    def get_models(self, models_type, project_root):
        package_name = "models"

        files = os.listdir(package_name)

        models = list()

        for file in files:
            if file not in ["__init__.py", "__pycache__"]:
                if file[-3:] != ".py":
                    continue

                file_name = file[:-3]

                module_name = ".." + package_name + "." + file_name
                
                for name, cls, in inspect.getmembers(importlib.import_module(module_name, package=f"{project_root}.models"), inspect.isclass):
                    split = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).split()

                    new_name = split[0].lower()

                    x = 1

                    if len(split) > 1:
                        while x < len(split):
                            new_name = new_name + f"-{split[x].lower()}"
                            x = x + 1

                    if models_type == "routes_models":
                        models.append(new_name)

                    else:
                        models.append({
                            new_name: cls
                        })

        return models

    # DB INTERFACE
    def db_interface(self, request, models, mongo, model_name, id):
        if id == None:
            def _dynamic_function():
                if request.method == "POST":
                    entity = request.json

                    for model_x in models:
                        for y in model_x:
                            if y == model_name:

                                model_attributes_list = list(inspect.signature(model_x[y]).parameters)

                                new_entity = {}

                                for z in model_attributes_list:
                                    new_entity[z] = entity[z]

                                # Add Data to DB
                                new_entity_id = mongo.db[model_name].insert_one(new_entity).inserted_id

                                new_entity = mongo.db[model_name].find_one({"_id": ObjectId(new_entity_id)})
                                new_entity = json.loads(dumps(new_entity))
                    
                    return new_entity
                    

                elif request.method == "GET":
                    # Some logic here...
                    try:
                        entities =  mongo.db[model_name].find()

                        if entities:
                            entities = json.loads(dumps(entities))

                        else:
                            entities = []

                    except:
                        traceback.print_exc()
                        entities = []

                    return entities
            
            _dynamic_function.__name__ = model_name

            return _dynamic_function

        else:
            def _dynamic_function(id):

                if request.method == "GET":
                    # Some logic here...
                    try:
                        entity =  mongo.db[model_name].find_one({"_id": ObjectId(id)})

                        if entity:
                            entity = json.loads(dumps(entity))

                        else:
                            entity = {}

                    except:
                        traceback.print_exc()
                        entity = {}

                    return entity

                elif request.method == "PUT":
                    entity = request.json

                    for model_x in models:
                        for y in model_x:
                            if y == model_name:
                                
                                model_attributes_list = list(inspect.signature(model_x[y]).parameters)

                                new_entity = {}

                                for z in model_attributes_list:
                                    if entity.get(z) is None:
                                        new_entity[z] = None
                                        continue
                                    new_entity[z] = entity[z]

                                # Add Data to DB
                                old_entity = mongo.db[model_name].find_one({"_id": ObjectId(id)})

                                mongo.db[model_name].update_one(
                                    {"_id": ObjectId(id)},
                                    {"$set": new_entity},
                                    upsert=True
                                )

                                new_entity = mongo.db[model_name].find_one({"_id": ObjectId(id)})
                                new_entity = json.loads(dumps(new_entity))
                    
                    return new_entity

                elif request.method == "PATCH":
                    entity = request.json

                    for model_x in models:
                        for y in model_x:
                            if y == model_name:
                                
                                # model_attributes_list = dir(model_x[y]())
                                model_attributes_list = list(inspect.signature(model_x[y]).parameters)

                                new_entity = {}

                                for z in model_attributes_list:
                                    if entity.get(z) is None:
                                        continue
                                    new_entity[z] = entity[z]

                                # Add Data to DB
                                old_entity = mongo.db[model_name].find_one({"_id": ObjectId(id)})
                                if old_entity == None:
                                    return {
                                        "message": f"{model_name} not found"
                                    }

                                mongo.db[model_name].update_one(
                                    {"_id": ObjectId(id)},
                                    {"$set": new_entity},
                                )

                                new_entity = mongo.db[model_name].find_one({"_id": ObjectId(id)})
                                new_entity = json.loads(dumps(new_entity))
                    
                    return new_entity

                elif request.method == "DELETE":
                    old_entity = mongo.db[model_name].find_one({"_id": ObjectId(id)})
                    if old_entity == None:
                        return {
                            "message": f"{model_name} not found"
                        }

                    mongo.db[model_name].delete_one({"_id": ObjectId(id)})
                    return {
                        "message": f"{model_name} deleted successfully"
                    }
                
            _dynamic_function.__name__ = model_name + "_one"

            return _dynamic_function