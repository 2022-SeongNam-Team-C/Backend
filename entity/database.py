from .model import db

def get_all(model):
    data = model.query.all()
    return data

def add_instance(model, **kwargs):
    instance = model(**kwargs)
    db.session.add(instance)
    commit_changes()

def delete_instance(model, user_id):
    model.query.filter_by(user_id=user_id).delete()
    commit_changes()

def edit_instance(model, user_id, **kwargs):
    instance = model.query.filter_by(user_id=user_id).all()[0]
    for attr, new_value in kwargs.items():
        setattr(instance, attr, new_value)
    commit_changes()

def commit_changes():
    db.session.commit()
