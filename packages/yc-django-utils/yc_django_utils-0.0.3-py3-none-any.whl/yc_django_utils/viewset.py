"""
Created on 2024-02-26
@author:刘飞
@description: 自定义视图集
"""
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from .json_response import SuccessResponse, ErrorResponse, DetailResponse


class CustomModelViewSet(ModelViewSet):
    """
    自定义的ModelViewSet:
    统一标准的返回格式;新增,查询,修改可使用不同序列化器
    (1)ORM性能优化, 尽可能使用values_queryset形式
    (2)xxx_serializer_class 某个方法下使用的序列化器(xxx=create|update|list|retrieve|destroy)
    (3)filter_fields = '__all__' 默认支持全部model中的字段查询(除json字段外)
    """
    values_queryset = None
    ordering_fields = '__all__'
    create_serializer_class = None
    update_serializer_class = None
    filter_fields = '__all__'
    search_fields = ()
    extra_filter_class = []

    def filter_queryset(self, queryset):
        for backend in set(set(self.filter_backends) | set(self.extra_filter_class or [])):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_queryset(self):
        if getattr(self, 'values_queryset', None):
            return self.values_queryset
        return super().get_queryset()

    def get_serializer_class(self):
        action_serializer_name = f"{self.action}_serializer_class"
        action_serializer_class = getattr(self, action_serializer_name, None)
        if action_serializer_class:
            return action_serializer_class
        return super().get_serializer_class()

    # 通过many=True直接改造原有的API，使其可以批量创建
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        if isinstance(self.request.data, list):
            with transaction.atomic():
                return serializer_class(many=True, *args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)

    @extend_schema(summary="新增数据")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, request=request)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return DetailResponse(data=serializer.data, msg="新增成功")

    @extend_schema(summary="查询数据列表")
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    @extend_schema(summary="查询数据详情")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, request=request)
        return DetailResponse(data=serializer.data, msg="获取成功")

    @extend_schema(summary="更新数据")
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, request=request, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return DetailResponse(data=serializer.data, msg="更新成功")

    @extend_schema(summary="删除数据")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return DetailResponse(data=[], msg="删除成功")

    @extend_schema(summary="批量删除", parameters=[
        OpenApiParameter(
            name='keys',
            type={'type': 'array', 'items': {'type': 'integer'}},  # 使用字典定义数组及其元素类型,
            location=OpenApiParameter.QUERY,
            description='要删除的实例的主键-例如：keys=1,2,3',
            required=True,
            style='form',
            explode=False,  # 设置为False表示数组以逗号分隔的形式传递，例如：keys=1,2,3
        ),
    ])
    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        keys = request.query_params.get('keys') or request.data.get('keys')
        if keys:
            key_list = [int(key) for key in keys.split(',')]
            self.get_queryset().filter(id__in=key_list).delete()
            return DetailResponse(msg="删除成功")
        else:
            return ErrorResponse(msg="未获取到keys字段")
