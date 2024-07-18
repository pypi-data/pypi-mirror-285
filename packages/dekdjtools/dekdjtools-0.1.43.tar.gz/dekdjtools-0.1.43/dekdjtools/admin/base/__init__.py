import sys
import functools
import time
from django.db import models
from django.db.models.fields.files import FieldFile
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.main import ChangeList
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import caches, DEFAULT_CACHE_ALIAS
from ...utils.model import ModelFields


class MetaClass(admin.ModelAdmin.__class__):
    def __new__(mcs, name, bases, attrs):
        new_class = super(MetaClass, mcs).__new__(mcs, name, bases, attrs)
        if new_class._model_cls:
            admin.site.register(new_class._model_cls, new_class)
        return new_class


class ModelAdminAbstract(admin.ModelAdmin, metaclass=MetaClass):
    _model_cls = None


class ModelAdminBase(ModelAdminAbstract):
    _img_width = 50

    @property
    def _cl(self) -> ChangeList:
        count = 3  # only be used in custom field function, search for: lookup_field(field_name, result, cl.model_admin)
        while True:
            frame = sys._getframe(count)
            if 'cl' in frame.f_locals:
                cl = frame.f_locals['cl']
                if isinstance(cl, ChangeList):
                    return cl
            count += 1

    def _get_obj_index(self, obj):
        cl = self._cl
        index = 0
        for i, x in enumerate(cl.result_list):
            if obj == x:
                index = i
        return (cl.page_num - 1) * cl.list_per_page + index

    def row_index_(self, obj):
        return self._get_obj_index(obj) + 1

    row_index_.short_description = _("序号")

    _custom_action__doc__ = """
    ### define action method:
    def _custom_action_of_myaction(self, request, form_url='', extra_context=None):
        def core():
            return HttpResponse(b'Done', content_type='text/html')
        return self._custom_action_progress(request, core)

    ### define shortcut method:
    @custom_action_func
    def _custom_action_of_myaction(self, request):
        return HttpResponse(b'Done', content_type='text/html')

    ### templates location: admin/<app_label>/<model_name_lower>/change_list.html

    {% extends "admin/change_list.html" %}
    {% block object-tools-items %}
        <li>
            <a href="my_action/" class="grp-state-focus addlink" target="_blank">MyAction</a>
        </li>
        {{ block.super }}
    {% endblock %}
    """
    _custom_action_prefix = '_custom_action_of_'
    _custom_action_cache_name = DEFAULT_CACHE_ALIAS

    def _custom_action_progress(self, request, func):
        cache = caches[self._custom_action_cache_name]
        key = "%s-%s-%s" % (self._custom_action_prefix, self.model._meta.app_label, self.model._meta.model_name)
        progress = cache.get(key)
        action_session = request.GET.get('__action_session', None)
        if not action_session and not progress:
            uid = str(time.time_ns())
            url = request.get_raw_uri()
            url += '&' if '?' in url else '?'
            url += f"__action_session={uid}"
            cache.set(key, uid, None)
            return HttpResponseRedirect(url)
        elif action_session:
            if progress == action_session:
                cache.set(key, 'working', None)
                rsp = func()
                cache.delete(key)
                return rsp
            else:
                return HttpResponse(b'Current session is expired')
        return HttpResponse(b'Another action is working')

    def get_urls(self):
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return functools.update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        url_actions = []

        for name in dir(self):
            if name.startswith(self._custom_action_prefix):
                view_func = getattr(self, name)
                if callable(view_func):
                    view_name = name[len(self._custom_action_prefix):]
                    url_actions.append(path(f'{view_name}/', wrap(view_func), name=f'%s_%s_{view_name}' % info))

        return url_actions + super().get_urls()

    def _get_ins_attr(self, obj, attr):
        if isinstance(getattr(self._model_cls, attr).field, models.ForeignKey):
            attr += '_id'
        return getattr(obj, attr)

    @staticmethod
    def _get_obj_url(obj):
        if isinstance(obj, FieldFile):
            return obj.url
        return obj

    @classmethod
    def format_self(cls, x):
        return x

    @classmethod
    def format_img(cls, img):
        if img:
            img = cls._get_obj_url(img)
            return format_html('<img src="{0}" width="{1}" height="{1}"/>'.format(img, cls._img_width))
        else:
            return ""

    @classmethod
    def format_aimg(cls, img):
        if img:
            img = cls._get_obj_url(img)
            return format_html(
                '<a href="{0}" target="_blank"><img src="{0}" width="{1}" height="{1}"/></a>'.
                format(img, cls._img_width))
        else:
            return ""

    @classmethod
    def format_imgs(cls, img_list):
        return format_html("".join([cls.format_img(x) for x in img_list]))

    @classmethod
    def format_aimgs(cls, img_list):
        return format_html("".join([cls.format_aimg(x) for x in img_list]))

    @staticmethod
    def format_tags(tags, ml=None, sep=' '):
        if ml is not None:
            tags = sorted(tags, key=lambda x: len(x))
            r = ""
            for tag in tags:
                temp = ""
                if r:
                    temp += sep
                temp += tag
                if len(r) + len(temp) > ml:
                    return r
                r += temp
            return r
        return sep.join(tags)

    @classmethod
    def format_a(cls, url, text=None, target=None):
        if url:
            url = cls._get_obj_url(url)
            target = target or '_blank'
            if callable(text):
                text = text(url)
            elif text == 0:
                text = url.rsplit('/', 1)[-1]
            elif text is None:
                text = url
            return format_html("<a href='{url}' target='{target}'>{text}</a>", url=url, text=text, target=target)
        return ""


def custom_action_func(func):
    def wrapper(self, request, form_url='', extra_context=None):
        return self._custom_action_progress(request, lambda: func(self, request))

    return functools.update_wrapper(wrapper, func)


def calc_list_display(_model_cls, rewrite_set=None, disable_set=None, rewrite_suffix='_'):
    mfs = ModelFields(_model_cls)
    array = [] if mfs.pk in mfs.auto else [ModelAdminBase.row_index_.__name__]
    for name in mfs.sort_fields(mfs.auto.keys(), mfs.common.keys(), mfs.o2o.keys(), mfs.o2m.keys()):
        if disable_set and name in disable_set:
            continue
        if rewrite_set and name in rewrite_set:
            name += rewrite_suffix
        array.append(name)
    return tuple(array)


def calc_search_fields(_model_cls, list_display=None, disable_set=None):
    array = []
    mfs = ModelFields(_model_cls)
    for name in mfs.sort_fields(mfs.auto.keys(), mfs.common.keys(), mfs.o2o.keys(), mfs.o2m.keys()):
        if disable_set and name in disable_set:
            continue
        array.append(name)
    return tuple(item for item in array if item in list_display) if list_display else tuple(array)


def admin_register(_model_cls, list_display=None):
    list_display = list_display or calc_list_display(_model_cls)
    type(
        'admin',
        (ModelAdminBase,),
        {
            '_model_cls': _model_cls,
            'list_display': list_display,
            'search_fields': calc_search_fields(_model_cls, list_display)
        }
    )


def admin_register_batch(_model_cls_list):
    for _model_cls in _model_cls_list:
        admin_register(_model_cls)
