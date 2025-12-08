# Nothing to import here — keep file empty or only export blueprints

mongo_service = None

def init_mongo(app):
    global mongo_service
    mongo_uri = app.config.get("MONGODB_URI")
    db_name = app.config.get("MONGODB_DBNAME")
    mongo_service = MongoService(uri=mongo_uri, db_name=db_name)
    # attach to app so you can access as current_app.extensions['mongo'] if desired
    app.extensions = getattr(app, "extensions", {})
    app.extensions["mongo"] = mongo_service