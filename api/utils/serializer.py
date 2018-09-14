#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework import serializers

from api.models import *

class CourseSerializer(serializers.ModelSerializer):
    level = serializers.CharField(source='get_level_display')
    why_studys = serializers.CharField(source='coursedetail.why_study')
    price = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['name', 'course_img', 'level', 'why_studys', 'price']
    def get_price(self, obj):
        return obj.price_policy.all().order_by('price').first().price

class SingleCourseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='course.name')
    course_type = serializers.CharField(source='course.get_course_type_display')
    period = serializers.CharField(source='course.period')
    level = serializers.CharField(source='course.get_level_display')

    recommend_courses = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    courseoutlines = serializers.SerializerMethodField()
    oftenAskedquestions = serializers.SerializerMethodField()
    pricepolicy = serializers.SerializerMethodField()

    class Meta:
        model = CourseDetail
        fields = ['name', 'course_type', 'period', 'level', 'video_brief_link', 'why_study',
                  'what_to_study_brief', 'career_improvement', 'prerequisite', 'recommend_courses', 'teachers',
                  'courseoutlines', 'oftenAskedquestions', 'pricepolicy']
    def get_recommend_courses(self, obj):
        return [item.name for item in obj.recommend_courses.all()]

    def get_teachers(self, obj):
        queryset = obj.teachers.all()
        return [{'name': item.name, 'title': item.title, 'signature': item.signature, 'image': item.image,
                 'brief': item.brief, 'role': item.get_role_display()} for item in queryset]

    def get_courseoutlines(self, obj):
        queryset = obj.courseoutline_set.all()
        return [{'title': item.title, 'content': item.content} for item in queryset]

    def get_oftenAskedquestions(self, obj):
        return [{'question': item.question, 'answer': item.answer} for item in obj.course.asked_question.all()]

    def get_pricepolicy(self, obj):
        return [{"valid_period":item.get_valid_period_display(), 'price':item.price} for item in obj.course.price_policy.all()]


class NewsSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source='source.name')
    article_type = serializers.CharField(source='get_article_type_display')
    position = serializers.CharField(source='get_position_display')

    class Meta:
        model = Article
        fields = ["id", "title", "source", "article_type", 'head_img', 'brief', 'pub_date', 'comment_num', 'agree_num',
                  'view_num', 'collect_num', 'position']

class SingleNewsSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source='source.name')
    class Meta:
        model = Article
        fields = ['title', 'pub_date', 'agree_num', 'view_num', 'collect_num', 'comment_num', 'source', 'content',
                  'head_img']