# TODO: write tests


def to_model(decorated):  # pragma: no cover
    import collections

    def decorator(self, *args, **kwargs):
        serialized_models = decorated(self, *args, **kwargs)

        if serialized_models is None:
            return None

        if isinstance(serialized_models, collections.Sequence):
            return map(self._model.load, serialized_models)
        return self._model.load(serialized_models)

    return decorator


class BaseRepository:  # pragma: no cover
    def __init__(self, db):
        self.__db = db
        # While this was indeed a good idea for small apps, it is troublesome
        # for apps that have huge databases, because
        #
        #  1) It prevents the DBA to optimize indexes, should the optimized
        #     indexes have a different structure than the hardcoded ones
        #  2) It doesn't let us choose when to create the index, sometimes
        #     it may be better to run production code with missing indexes
        #     (and accept slower queries) instead of risking a overall
        #     performance issue due to indices being created
        #
        # self._ensure_indexes()

    def save(self, model):
        doc = model.serialize()
        if "_id" in doc:
            self._collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)
            return doc["_id"]
        else:
            res = self._collection.insert_one(doc)
            return res.inserted_id

    def bulk_insert(self, models):
        return self._collection.insert_many([model.serialize() for model in models])

    def remove(self, *args, **kwargs):
        return self._collection.delete_one(*args, **kwargs)

    @to_model
    def find_by_id(self, _id):
        return self._collection.find_one({"_id": _id})

    # Be careful! Calling this method can be slow without the necessary indexes
    @to_model
    def find_by(self, filters):
        return list(self._collection.find(filters))

    @to_model
    def find_one_by(self, filters):
        return self._collection.find_one(filters)

    @property
    def _collection(self):
        return self.__db[self._collection_name]

    def _ensure_indexes(self):
        pass

    def ensure_indexes(self):
        self._ensure_indexes()
