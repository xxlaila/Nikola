# -*- coding: utf8 -*-

from asset.myauth import MyUser
from asset import models
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyUser
        fields = ('url', 'name', 'email')


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Asset
        depth=2
        fields = ('name', 'sn','server','networkdevice')


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Server
        #fields = ('name', 'sn','server')