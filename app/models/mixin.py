class ModelMixin:
    def update(self, update_data: dict):
        for key, value in update_data.items():
            setattr(self, key, value)