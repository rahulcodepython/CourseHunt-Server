class MongoDBRouter:
    """
    A router to control all database operations on models for specific apps.
    """
    route_app_labels = {'your_mongo_app'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read models go to MongoDB.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'mongodb'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write models go to MongoDB.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'mongodb'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both models are in the same database.
        """
        if (
            obj1._meta.app_label in self.route_app_labels and
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        elif (
            obj1._meta.app_label not in self.route_app_labels and
            obj2._meta.app_label not in self.route_app_labels
        ):
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that the 'your_mongo_app' app's models get created on the right database.
        """
        if app_label in self.route_app_labels:
            return db == 'mongodb'
        return db == 'default'
