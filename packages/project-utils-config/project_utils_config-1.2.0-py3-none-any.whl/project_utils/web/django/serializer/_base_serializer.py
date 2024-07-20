from typing import Dict
from asgiref.sync import sync_to_async
from rest_framework.serializers import ModelSerializer

from ..model import IDModel


class BaseSerializer(ModelSerializer):
    def create(self, validated_data: Dict):
        validated_data.update({"id": IDModel.create_id()})
        return super().create(validated_data)

    async def async_save(self):
        return await sync_to_async(self.save)()
