# -*- coding: utf-8 -*-
# Copyright 2024 Matthew Fitzpatrick.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
"""``fancytypes`` is a simple Python library that defines some classes with
useful features, such as enforced validation, updatability, pre-serialization,
and de-pre-serialization. These classes can be used to define more complicated
classes that inherit some subset of the aforementioned features.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For accessing attributes of functions.
import inspect

# For performing deep copies.
import copy

# For serializing and deserializing JSON objects.
import json

# For performing operations on file and directory paths.
import pathlib



# For validating and converting objects.
import czekitout.check
import czekitout.convert



# Get version of current package.
from fancytypes.version import __version__



##################################
## Define classes and functions ##
##################################

# List of public objects in package.
__all__ = ["Checkable",
           "Updatable",
           "PreSerializable",
           "PreSerializableAndUpdatable",
           "return_validation_and_conversion_funcs",
           "return_pre_serialization_funcs",
           "return_de_pre_serialization_funcs"]



def _check_and_convert_validation_and_conversion_funcs(params):
    current_func_name = inspect.stack()[0][3]
    obj_name = current_func_name.split("_check_and_convert_")[-1]
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    validation_and_conversion_funcs = czekitout.convert.to_dict(**kwargs).copy()

    for key in validation_and_conversion_funcs:
        validation_and_conversion_func = validation_and_conversion_funcs[key]
        if not callable(validation_and_conversion_func):
            err_msg = globals()[current_func_name+"_err_msg_1"]
            raise TypeError(err_msg)

    return validation_and_conversion_funcs



def _check_and_convert_skip_validation_and_conversion(params):
    current_func_name = inspect.stack()[0][3]
    obj_name = current_func_name.split("_check_and_convert_")[-1]
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    skip_validation_and_conversion = czekitout.convert.to_bool(**kwargs)

    return skip_validation_and_conversion



def _check_and_convert_skip_cls_tests(params):
    current_func_name = inspect.stack()[0][3]
    obj_name = current_func_name.split("_check_and_convert_")[-1]
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    skip_cls_tests = czekitout.convert.to_bool(**kwargs)

    return skip_cls_tests



def _check_and_convert_params_to_be_mapped_to_core_attrs(params):
    params["core_attrs_candidate"] = \
        params["params_to_be_mapped_to_core_attrs"]
    params["name_of_obj_alias_of_core_attrs_candidate"] = \
        "params_to_be_mapped_to_core_attrs"
    params_to_be_mapped_to_core_attrs = \
        _check_and_convert_core_attrs_candidate(params)

    del params["core_attrs_candidate"]
    del params["name_of_obj_alias_of_core_attrs_candidate"]

    return params_to_be_mapped_to_core_attrs



def _check_and_convert_core_attrs_candidate(params):
    obj_name = params["name_of_obj_alias_of_core_attrs_candidate"]
    kwargs = {"obj": params["core_attrs_candidate"], "obj_name": obj_name}
    core_attrs_candidate = czekitout.convert.to_dict(**kwargs).copy()

    validation_and_conversion_funcs = params["validation_and_conversion_funcs"]

    for key in core_attrs_candidate:
        if key not in validation_and_conversion_funcs:
            current_func_name = inspect.stack()[0][3]
            unformatted_err_msg = globals()[current_func_name+"_err_msg_1"]
            obj_name = params["name_of_obj_alias_of_core_attrs_candidate"]
            err_msg = unformatted_err_msg.format(obj_name, obj_name, key)
            raise KeyError(err_msg)
                    
    for key in validation_and_conversion_funcs:
        validation_and_conversion_func = validation_and_conversion_funcs[key]
        
        kwargs = {"params": core_attrs_candidate}
        core_attr_candidate = validation_and_conversion_func(**kwargs)
        
        core_attrs_candidate[key] = core_attr_candidate

    return core_attrs_candidate



def _check_and_convert_deep_copy(params):
    current_func_name = inspect.stack()[0][3]
    obj_name = current_func_name.split("_check_and_convert_")[-1]
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    deep_copy = czekitout.convert.to_bool(**kwargs)

    return deep_copy



_default_skip_validation_and_conversion = False
_default_skip_cls_tests = _default_skip_validation_and_conversion
_default_deep_copy = True



class Checkable():
    r"""A type that can perform user-defined validations and conversions of a 
    set of parameters upon construction.

    One cannot construct an instance of the class :class:`fancytypes.Checkable`
    without raising an exception. In order to make use of this class, one must
    create a subclass that inherits from :class:`fancytypes.Checkable` and then
    override the class method
    :class:`~fancytypes.Checkable.get_validation_and_conversion_funcs` in a way
    that is consistent with the method's description.

    Parameters
    ----------
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameters
        ``skip_validation_and_conversion`` and ``skip_cls_tests``, where each
        `dict` key ``key`` is a different constructor parameter name, excluding
        the names ``"skip_validation_and_conversion"`` and ``"skip_cls_tests"``,
        and ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of
        the constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.
    skip_cls_test : `bool`, optional
        If ``skip_cls_test`` is set to ``False``, then upon construction, tests
        will be performed to check whether the class was properly
        defined. If any of the tests fail, an exception will be raised.

        Otherwise, if ``skip_cls_test`` is set to ``True``, these tests will be
        skipped. 

        One should only skip the tests if they are sure that the class is
        properly defined. Skipping the tests will yield some improvement in
        performance.
    **kwargs 
        The remaining constructor parameters.

    """
    def __init__(self,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion,
                 skip_cls_tests=\
                 _default_skip_cls_tests,
                 **kwargs):
        params_to_be_mapped_to_core_attrs = kwargs

        func_alias = _check_and_convert_skip_validation_and_conversion
        params = {"skip_validation_and_conversion": \
                  skip_validation_and_conversion}
        skip_validation_and_conversion = func_alias(params)

        func_alias = _check_and_convert_skip_cls_tests
        params = {"skip_cls_tests": skip_cls_tests}
        skip_cls_tests = func_alias(params)

        param_name = "validation_and_conversion_funcs"
        params = {param_name: self.get_validation_and_conversion_funcs()}
        method_alias = _check_and_convert_validation_and_conversion_funcs
        self._validation_and_conversion_funcs = (method_alias(params)
                                                 if (skip_cls_tests == False)
                                                 else params[param_name])

        if (skip_validation_and_conversion == False):
            func_alias = _check_and_convert_params_to_be_mapped_to_core_attrs
            params = {"validation_and_conversion_funcs": \
                      self._validation_and_conversion_funcs,
                      "params_to_be_mapped_to_core_attrs": \
                      params_to_be_mapped_to_core_attrs,
                      "skip_validation_and_conversion": \
                      skip_validation_and_conversion}
            self._core_attrs = func_alias(params)
        else:
            self._core_attrs = params_to_be_mapped_to_core_attrs.copy()

        return None



    @classmethod
    def get_validation_and_conversion_funcs(cls):
        r"""Return the validation and conversion functions.

        Returns
        -------
        validation_and_conversion_funcs : `dict`
            The attribute 
            :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`.

        """
        raise NotImplementedError(_checkable_err_msg_1)

        return None



    @property
    def validation_and_conversion_funcs(self):
        r"""`dict`: The validation and conversion functions.

        The keys of ``validation_and_conversion_funcs`` are the names of the
        constructor parameters, excluding ``skip_validation_and_conversion`` if
        it exists as a construction parameter.

        Let ``core_attrs`` denote the attribute
        :attr:`~fancytypes.Checkable.core_attrs`, which is also a `dict` object.

        For each `dict` key ``key`` in ``core_attrs``,
        ``validation_and_conversion_funcs[key](core_attrs)`` is expected to not
        raise an exception.

        Note that ``validation_and_conversion_funcs`` should be considered
        **read-only**.

        """
        result = self._validation_and_conversion_funcs.copy()
        
        return result



    def get_core_attrs(self, deep_copy=_default_deep_copy):
        r"""Return the core attributes.

        Parameters
        ----------
        deep_copy : `bool`, optional
            Let ``core_attrs`` denote the attribute
            :attr:`~fancytypes.Checkable.core_attrs`, which is a `dict` object.

            If ``deep_copy`` is set to ``True``, then a deep copy of
            ``core_attrs`` is returned.  Otherwise, a shallow copy of
            ``core_attrs`` is returned.

        Returns
        -------
        core_attrs : `dict`
            The attribute :attr:`~fancytypes.Checkable.core_attrs`.

        """
        params = {"deep_copy": deep_copy}
        deep_copy = _check_and_convert_deep_copy(params)
        
        core_attrs = (self.core_attrs
                      if (deep_copy == True)
                      else self._core_attrs.copy())

        return core_attrs



    @property
    def core_attrs(self):
        r"""`dict`: The "core attributes".

        The keys of ``core_attrs`` are the same as the attribute
        :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`, which is
        also a `dict` object.

        Note that ``core_attrs`` should be considered **read-only**.

        """
        result = copy.deepcopy(self._core_attrs)
        
        return result



def _update_old_core_attr_set_and_return_new_core_attr_set(
        skip_validation_and_conversion,
        new_core_attr_subset_candidate,
        old_core_attr_set,
        validation_and_conversion_funcs):
    params = \
        {"skip_validation_and_conversion": skip_validation_and_conversion}
    skip_validation_and_conversion = \
        _check_and_convert_skip_validation_and_conversion(params)

    kwargs = {"obj": new_core_attr_subset_candidate,
              "obj_name": "new_core_attr_subset_candidate"}
    czekitout.check.if_dict_like(**kwargs)
    
    new_core_attr_set = new_core_attr_subset_candidate.copy()

    for core_attr_name in old_core_attr_set.keys():
        if core_attr_name not in new_core_attr_subset_candidate:
            new_core_attr_candidate = old_core_attr_set[core_attr_name]
            new_core_attr_set[core_attr_name] = new_core_attr_candidate

    names_of_core_attrs_to_update = tuple()
    for core_attr_name in new_core_attr_subset_candidate:
        if core_attr_name not in old_core_attr_set:
            del new_core_attr_set[core_attr_name]
        else:
            names_of_core_attrs_to_update += (core_attr_name,)

    for ctor_param_name in names_of_core_attrs_to_update:
        validation_and_conversion_func = \
            validation_and_conversion_funcs[ctor_param_name]

        if (skip_validation_and_conversion == False):
            new_core_attr = validation_and_conversion_func(new_core_attr_set)
            new_core_attr_set[ctor_param_name] = new_core_attr

    return new_core_attr_set



_default_new_core_attr_subset_candidate = dict()



class Updatable(Checkable):
    r"""A type that can perform user-defined validations and conversions of a 
    set of parameters upon construction, and that has an updatable subset of 
    attributes.

    One cannot construct an instance of the class :class:`fancytypes.Updatable`
    without raising an exception. In order to make use of this class, one must
    create a subclass that inherits from :class:`fancytypes.Updatable` and then
    override the class method
    :class:`~fancytypes.Checkable.get_validation_and_conversion_funcs` in a way
    that is consistent with the method's description.

    Parameters
    ----------
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameters
        ``skip_validation_and_conversion`` and ``skip_cls_tests``, where each
        `dict` key ``key`` is a different constructor parameter name, excluding
        the names ``"skip_validation_and_conversion"`` and ``"skip_cls_tests"``,
        and ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of
        the constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.  
    skip_cls_test : `bool`, optional
        If ``skip_cls_test`` is set to ``False``, then upon construction, tests
        will be performed to check whether the class was properly
        defined. If any of the tests fail, an exception will be raised.

        Otherwise, if ``skip_cls_test`` is set to ``True``, these tests will be
        skipped. 

        One should only skip the tests if they are sure that the class is
        properly defined. Skipping the tests will yield some improvement in
        performance.
    **kwargs 
        The remaining constructor parameters.

    """
    def __init__(self,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion,
                 skip_cls_tests=\
                 _default_skip_cls_tests,
                 **kwargs):
        super().__init__(skip_validation_and_conversion,
                         skip_cls_tests,
                         **kwargs)

        return None



    def update(self,
               new_core_attr_subset_candidate=\
               _default_new_core_attr_subset_candidate,
               skip_validation_and_conversion=\
               _default_skip_validation_and_conversion):
        r"""Update a subset of the core attributes.

        Parameters
        ----------
        new_core_attr_subset_candidate : `dict`, optional
            A `dict` object.
        skip_validation_and_conversion : `bool`, optional
            Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote
            the attributes
            :attr:`~fancytypes.Checkable.validation_and_conversion_funcs` and
            :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
            being `dict` objects.

            If ``skip_validation_and_conversion`` is set to ``False``, then for
            each key ``key`` in ``core_attrs`` that is also in
            ``new_core_attr_subset_candidate``, ``core_attrs[key]`` is set to
            ``validation_and_conversion_funcs[key]
            (new_core_attr_subset_candidate)``.

            Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
            then for each key ``key`` in ``core_attrs`` that is also in
            ``new_core_attr_subset_candidate``, ``core_attrs[key]`` is set to
            ``new_core_attr_subset_candidate[key]``. This option is desired
            primarily when the user wants to avoid potentially expensive deep
            copies and/or conversions of the `dict` values of
            ``new_core_attr_subset_candidate``, as it is guaranteed that no
            copies or conversions are made in this case.

        """
        kwargs = \
            {"skip_validation_and_conversion": \
             skip_validation_and_conversion,
             "new_core_attr_subset_candidate": \
             new_core_attr_subset_candidate,
             "old_core_attr_set": \
             self._core_attrs,
             "validation_and_conversion_funcs": \
             self._validation_and_conversion_funcs}
        self._core_attrs = \
            _update_old_core_attr_set_and_return_new_core_attr_set(**kwargs)

        return None



def _preliminary_check_of_pre_serialization_funcs(params):
    current_func_name = inspect.stack()[0][3]
    obj_name = current_func_name.split("_preliminary_check_of_")[-1]
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    pre_serialization_funcs = czekitout.convert.to_dict(**kwargs)

    validation_and_conversion_funcs = params["validation_and_conversion_funcs"]

    key_set_1 = sorted(list(validation_and_conversion_funcs.keys()))
    key_set_2 = sorted(list(pre_serialization_funcs.keys()))
    if key_set_1 != key_set_2:
        err_msg = globals()[current_func_name+"_err_msg_1"]
        raise KeyError(err_msg)
    
    for key in pre_serialization_funcs:
        pre_serialization_func = pre_serialization_funcs[key]
        if not callable(pre_serialization_func):
            err_msg = globals()[current_func_name+"_err_msg_2"]
            raise TypeError(err_msg)

    return None



def _preliminary_check_of_de_pre_serialization_funcs(params):
    current_func_name = inspect.stack()[0][3]
    obj_name = current_func_name.split("_preliminary_check_of_")[-1]
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    de_pre_serialization_funcs = czekitout.convert.to_dict(**kwargs)

    validation_and_conversion_funcs = params["validation_and_conversion_funcs"]

    key_set_1 = sorted(list(validation_and_conversion_funcs.keys()))
    key_set_2 = sorted(list(de_pre_serialization_funcs.keys()))
    if key_set_1 != key_set_2:
        err_msg = globals()[current_func_name+"_err_msg_1"]
        raise KeyError(err_msg)
    
    for key in de_pre_serialization_funcs:
        de_pre_serialization_func = de_pre_serialization_funcs[key]
        if not callable(de_pre_serialization_func):
            err_msg = globals()[current_func_name+"_err_msg_2"]
            raise TypeError(err_msg)

    return None



def _check_and_convert_overwrite(params):
    current_func_name = inspect.stack()[0][3]
    obj_name = current_func_name.split("_check_and_convert_")[-1]
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    overwrite = czekitout.convert.to_bool(**kwargs)

    return overwrite



_default_serializable_rep = _default_new_core_attr_subset_candidate
_default_filename = "serialized_rep_of_fancytype.json"
_default_overwrite = False
_default_serialized_rep = str(_default_serializable_rep)



class PreSerializable(Checkable):
    r"""A type that is pre-serializable, that can be constructed from a 
    serializable representation, and that can perform user-defined validations 
    and conversions of a set of parameters upon construction.

    We define pre-serialization as the process of converting an object into a
    form that can be subsequently serialized into a JSON format. We refer to
    objects resulting from pre-serialization as serializable objects.

    We define de-pre-serialization as the process of converting a serializable
    object into an instance of the current class, i.e. de-pre-serialization is
    the reverse process of pre-serialization.

    One cannot construct an instance of the class
    :class:`fancytypes.PreSerializable` without raising an exception. In order
    to make use of this class, one must create a subclass that inherits from
    :class:`fancytypes.PreSerializable` and then override the class methods
    :class:`~fancytypes.Checkable.get_validation_and_conversion_funcs`,
    :class:`~fancytypes.PreSerializable.pre_serialization_funcs`, and
    :class:`~fancytypes.PreSerializable.de_pre_serialization_funcs` in ways that
    are consistent with the respective descriptions of the methods.

    Parameters
    ----------
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameters
        ``skip_validation_and_conversion`` and ``skip_cls_tests``, where each
        `dict` key ``key`` is a different constructor parameter name, excluding
        the names ``"skip_validation_and_conversion"`` and ``"skip_cls_tests"``,
        and ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of
        the constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.  
    skip_cls_test : `bool`, optional
        If ``skip_cls_test`` is set to ``False``, then upon construction, tests
        will be performed to check whether the class was properly
        defined. If any of the tests fail, an exception will be raised.

        Otherwise, if ``skip_cls_test`` is set to ``True``, these tests will be
        skipped. 

        One should only skip the tests if they are sure that the class is
        properly defined. Skipping the tests will yield some improvement in
        performance.
    **kwargs 
        The remaining constructor parameters.

    """
    def __init__(self,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion,
                 skip_cls_tests=\
                 _default_skip_cls_tests,
                 **kwargs):
        super().__init__(skip_validation_and_conversion,
                         skip_cls_tests,
                         **kwargs)

        params = {"skip_cls_tests": skip_cls_tests}
        skip_cls_tests = _check_and_convert_skip_cls_tests(params)

        params = {"validation_and_conversion_funcs": \
                  self._validation_and_conversion_funcs,
                  "pre_serialization_funcs": \
                  self.get_pre_serialization_funcs(),
                  "de_pre_serialization_funcs": \
                  self.get_de_pre_serialization_funcs()}
        if (skip_cls_tests == False):
            _preliminary_check_of_pre_serialization_funcs(params)
            _preliminary_check_of_de_pre_serialization_funcs(params)            
        self._pre_serialization_funcs = params["pre_serialization_funcs"]
        self._de_pre_serialization_funcs = params["de_pre_serialization_funcs"]

        if (skip_cls_tests == False):
            try:
                serializable_rep = self.pre_serialize()
            except:
                raise ValueError(_pre_serializable_err_msg_1)
        
            try:
                method_alias = self._construct_core_attrs_candidate
                kwargs = {"serializable_rep": \
                          serializable_rep,
                          "de_pre_serialization_funcs": \
                          self._de_pre_serialization_funcs}
                core_attrs_candidate = method_alias(**kwargs)

                params = {"core_attrs_candidate": \
                          core_attrs_candidate,
                          "name_of_obj_alias_of_core_attrs_candidate": \
                          "core_attrs_candidate",
                          "validation_and_conversion_funcs": \
                          self._validation_and_conversion_funcs}
                _ =_check_and_convert_core_attrs_candidate(params)
            except:
                raise ValueError(_pre_serializable_err_msg_2)
        
        return None



    @classmethod
    def get_pre_serialization_funcs(cls):
        r"""Return the pre-serialization functions.

        Returns
        -------
        pre_serialization_funcs : `dict`
            The attribute 
            :attr:`~fancytypes.PreSerializable.pre_serialization_funcs`.

        """
        raise NotImplementedError(_pre_serializable_err_msg_3)



    @property
    def pre_serialization_funcs(self):
        r"""`dict`: The pre-serialization functions.

        ``pre_serialization_funcs`` has the same keys as the attribute
        :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`, which is
        also a `dict` object.

        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, the last of
        which being a `dict` object as well.

        For each `dict` key ``key`` in ``core_attrs``,
        ``pre_serialization_funcs[key](core_attrs[key])`` is expected to yield a
        serializable object, i.e. it should yield an object that can be passed
        into the function ``json.dumps`` without raising an exception.

        Note that ``pre_serialization_funcs`` should be considered
        **read-only**.

        """
        result = self._pre_serialization_funcs.copy()
        
        return result



    @classmethod
    def get_de_pre_serialization_funcs(cls):
        r"""Return the de-pre-serialization functions.

        Returns
        -------
        de_pre_serialization_funcs : `dict`
            The attribute 
            :attr:`~fancytypes.PreSerializable.de_pre_serialization_funcs`.

        """
        raise NotImplementedError(_pre_serializable_err_msg_4)



    @property
    def de_pre_serialization_funcs(self):
        r"""`dict`: The de-pre-serialization functions.

        ``de_pre_serialization_funcs`` has the same keys as the attribute
        :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`, which is
        also a `dict` object.

        Let ``validation_and_conversion_funcs`` and ``pre_serialization_funcs``
        denote the attributes
        :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        :attr:`~fancytypes.PreSerializable.pre_serialization_funcs`
        respectively, the last of which being a `dict` object as well.

        Let ``core_attrs_candidate_1`` be any `dict` object that has the same
        keys as ``validation_and_conversion_funcs``, where for each `dict` key
        ``key`` in ``core_attrs_candidate_1``,
        ``validation_and_conversion_funcs[key](core_attrs_candidate_1)`` does
        not raise an exception.

        Let ``serializable_rep`` be a `dict` object that has the same keys as
        ``core_attrs_candidate_1``, where for each `dict` key ``key`` in
        ``core_attrs_candidate_1``, ``serializable_rep[key]`` is set to
        ``pre_serialization_funcs[key](core_attrs_candidate_1[key])``.

        The items of ``de_pre_serialization_funcs`` are expected to be set to
        callable objects that would lead to
        ``de_pre_serialization_funcs[key](serializable_rep[key])`` not raising
        an exception for each `dict` key ``key`` in ``serializable_rep``.

        Let ``core_attrs_candidate_2`` be a `dict` object that has the same keys
        as ``serializable_rep``, where for each `dict` key ``key`` in
        ``validation_and_conversion_funcs``, ``core_attrs_candidate_2[key]`` is
        set to ``de_pre_serialization_funcs[key](serializable_rep[key])``.

        The items of ``de_pre_serialization_funcs`` are also expected to be set
        to callable objects that would lead to
        ``validation_and_conversion_funcs[key](core_attrs_candidate_2)`` not
        raising an exception for each `dict` key ``key`` in
        ``core_attrs_candidate_2``.

        Note that ``de_pre_serialization_funcs`` should be considered
        **read-only**.

        """
        result = self._de_pre_serialization_funcs.copy()
        
        return result



    @classmethod
    def _construct_core_attrs_candidate(cls,
                                        serializable_rep,
                                        de_pre_serialization_funcs):
        kwargs = {"obj": serializable_rep, "obj_name": "serializable_rep"}
        serializable_rep = czekitout.convert.to_dict(**kwargs)

        for key in serializable_rep:
            if key not in de_pre_serialization_funcs:
                obj_name = "serializable_rep"
                unformatted_err_msg_1 = _pre_serializable_err_msg_5
                err_msg = unformatted_err_msg_1.format(obj_name, obj_name, key)
                raise KeyError(err_msg)
            
        try:
            core_attrs_candidate = dict()
            
            for key in serializable_rep:
                core_attr_name = \
                    key
                elem_of_serializable_rep = \
                    serializable_rep[key]
                de_pre_serialization_func = \
                    de_pre_serialization_funcs[key]
                core_attr_candidate = \
                    de_pre_serialization_func(elem_of_serializable_rep)
                core_attrs_candidate[core_attr_name] = \
                    core_attr_candidate
        except:
            err_msg = _pre_serializable_err_msg_6
            raise ValueError(err_msg)

        return core_attrs_candidate



    @classmethod
    def de_pre_serialize(cls,
                         serializable_rep=\
                         _default_serializable_rep,
                         skip_validation_and_conversion=\
                         _default_skip_validation_and_conversion):
        r"""Construct an instance from a serializable representation.

        Parameters
        ----------
        serializable_rep : `dict`, optional
            A `dict` object that has the same keys as the attribute
            :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`, which
            is also a `dict` object.

            Let ``validation_and_conversion_funcs`` and
            ``de_pre_serialization_funcs`` denote the attributes
            :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
            :attr:`~fancytypes.PreSerializable.de_pre_serialization_funcs`
            respectively, the last of which being a `dict` object as well.

            The items of ``serializable_rep`` are expected to be objects that
            would lead to
            ``de_pre_serialization_funcs[key](serializable_rep[key])`` not
            raising an exception for each `dict` key ``key`` in
            ``serializable_rep``.

            Let ``core_attrs_candidate`` be a `dict` object that has the same
            keys as ``serializable_rep``, where for each `dict` key ``key`` in
            ``serializable_rep``, ``core_attrs_candidate[key]`` is set to
            de_pre_serialization_funcs[key](serializable_rep[key])``.

            The items of ``serializable_rep`` are also expected to be set to
            objects that would lead to
            ``validation_and_conversion_funcs[key](core_attrs_candidate)`` not
            raising an exception for each `dict` key ``key`` in
            ``serializable_rep``.
        skip_validation_and_conversion : `bool`, optional
            Let ``core_attrs`` denote the attribute
            :attr:`~fancytypes.Checkable.core_attrs`, which is a `dict` object.

            If ``skip_validation_and_conversion`` is set to ``False``, then for
            each key ``key`` in ``serializable_rep``, ``core_attrs[key]`` is set
            to ``validation_and_conversion_funcs[key] (core_attrs_candidate)``,
            with ``validation_and_conversion_funcs`` and
            ``core_attrs_candidate_1`` being introduced in the above description
            of ``serializable_rep``.

            Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
            then ``core_attrs`` is set to ``core_attrs_candidate.copy()``. This
            option is desired primarily when the user wants to avoid potentially
            expensive deep copies and/or conversions of the `dict` values of
            ``core_attrs_candidate``, as it is guaranteed that no copies or
            conversions are made in this case.

        Returns
        -------
        instance_of_current_cls : Current class
            An instance constructed from the serializable representation
            ``serializable_rep``.

        """
        params = {"validation_and_conversion_funcs": \
                  cls.get_validation_and_conversion_funcs(),
                  "pre_serialization_funcs": \
                  cls.get_pre_serialization_funcs(),
                  "de_pre_serialization_funcs": \
                  cls.get_de_pre_serialization_funcs()}
        _preliminary_check_of_de_pre_serialization_funcs(params)
        de_pre_serialization_funcs = params["de_pre_serialization_funcs"]

        try:
            kwargs = \
                {"serializable_rep": serializable_rep,
                 "de_pre_serialization_funcs": de_pre_serialization_funcs}
            core_attrs_candidate = \
                cls._construct_core_attrs_candidate(**kwargs)

            kwargs = core_attrs_candidate
            key = "skip_validation_and_conversion"
            if key in inspect.signature(cls.__init__).parameters:
                kwargs[key] = True
            instance_of_current_cls = cls(**kwargs)

            if (skip_validation_and_conversion == False):
                try:
                    _ = instance_of_current_cls.pre_serialize()
                except:
                    raise ValueError(_pre_serializable_err_msg_1)

                validation_and_conversion_funcs = \
                    instance_of_current_cls._validation_and_conversion_funcs

                params = {"core_attrs_candidate": \
                          instance_of_current_cls._core_attrs,
                          "name_of_obj_alias_of_core_attrs_candidate": \
                          "instance_of_current_cls._core_attrs",
                          "validation_and_conversion_funcs": \
                          validation_and_conversion_funcs}
                core_attrs = _check_and_convert_core_attrs_candidate(params)
                instance_of_current_cls._core_attrs = core_attrs
        except:
            raise ValueError(_pre_serializable_err_msg_7)
                
        return instance_of_current_cls



    def pre_serialize(self):
        r"""Pre-serialize instance.

        Returns
        -------
        serializable_rep : `dict`
            A serializable representation of an instance.

        """
        serializable_rep = dict()
        
        for core_attr_name, core_attr in self._core_attrs.items():
            pre_serialization_func = \
                self._pre_serialization_funcs[core_attr_name]
            elem_of_serializable_rep = \
                pre_serialization_func(core_attr)
            serializable_rep[core_attr_name] = \
                elem_of_serializable_rep

        return serializable_rep



    def dumps(self):
        r"""Serialize instance.
        
        Returns
        -------
        serialized_rep : `dict`
            A serialized representation of an instance.

        """
        serializable_rep = self.pre_serialize()
        serialized_rep = json.dumps(serializable_rep)

        return serialized_rep



    def dump(self, filename=_default_filename, overwrite=_default_overwrite):
        r"""Serialize instance and save the result in a JSON file.

        Parameters
        ----------
        filename : `str`, optional
            The relative or absolute path to the JSON file in which to store the
            serialized representation of an instance.
        overwrite : `bool`, optional
            If ``overwrite`` is set to ``False`` and a file exists at the path
            ``filename``, then the serialized instance is not written to that
            file and an exception is raised. Otherwise, the serialized instance
            will be written to that file barring no other issues occur.

        Returns
        -------

        """
        params = {"overwrite": overwrite}
        overwrite = _check_and_convert_overwrite(params)
        
        kwargs = {"obj": filename, "obj_name": "filename"}
        filename = czekitout.convert.to_str_from_str_like(**kwargs)
        if pathlib.Path(filename).is_file():
            if not overwrite:
                raise IOError(_pre_serializable_err_msg_8.format(filename))

        serializable_rep = self.pre_serialize()

        try:
            with open(filename, "w", encoding="utf-8") as file_obj:
                json.dump(serializable_rep,
                          file_obj,
                          ensure_ascii=False,
                          indent=4)
        except:
            pathlib.Path(filename).unlink(missing_ok=True)
            raise IOError(_pre_serializable_err_msg_9.format(filename))
            
        return None



    @classmethod
    def loads(cls,
              serialized_rep=\
              _default_serialized_rep,
              skip_validation_and_conversion=\
              _default_skip_validation_and_conversion):
        r"""Construct an instance from a serialized representation.

        Users can generate serialized representations using the method
        :meth:`~fancytypes.PreSerializable.dumps`.

        Parameters
        ----------
        serialized_rep : `str` | `bytes` | `bytearray`, optional
            The serialized representation.

            ``serialized_rep`` is expected to be such that
            ``json.loads(serialized_rep)`` does not raise an exception.

            Let ``serializable_rep=json.loads(serialized_rep)``. 

            Let ``validation_and_conversion_funcs`` and
            ``de_pre_serialization_funcs`` denote the attributes
            :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
            :attr:`~fancytypes.PreSerializable.de_pre_serialization_funcs`
            respectively, both of which being `dict` objects as well.

            ``serialized_rep`` is also expected to be such that
            ``de_pre_serialization_funcs[key](serializable_rep[key])`` does not
            raise an exception for each `dict` key ``key`` in
            ``de_pre_serialization_funcs``.

            Let ``core_attrs_candidate`` be a `dict` object that has the same
            keys as ``serializable_rep``, where for each `dict` key ``key`` in
            ``de_pre_serialization_funcs``, ``core_attrs_candidate[key]`` is set
            to de_pre_serialization_funcs[key](serializable_rep[key])``.

            ``serialized_rep`` is also expected to be such that
            ``validation_and_conversion_funcs[key](core_attrs_candidate)`` does
            not raise an exception for each `dict` key ``key`` in
            ``serializable_rep``.
        skip_validation_and_conversion : `bool`, optional
            Let ``core_attrs`` denote the attribute
            :attr:`~fancytypes.Checkable.core_attrs`, which is a `dict` object.

            If ``skip_validation_and_conversion`` is set to ``False``, then for
            each key ``key`` in ``core_attrs_candidate``, ``core_attrs[key]`` is
            set to ``validation_and_conversion_funcs[key]
            (core_attrs_candidate)``, with ``validation_and_conversion_funcs``
            and ``core_attrs_candidate_1`` being introduced in the above
            description of ``serialized_rep``.

            Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
            then ``core_attrs`` is set to ``core_attrs_candidate.copy()``. This
            option is desired primarily when the user wants to avoid potentially
            expensive deep copies and/or conversions of the `dict` values of
            ``core_attrs_candidate``, as it is guaranteed that no copies or
            conversions are made in this case.

        Returns
        -------
        instance_of_current_cls : Current class
            An instance constructed from the serialized representation.

        """
        kwargs = {"obj": serialized_rep,
                  "obj_name": "serialized_rep",
                  "accepted_types": (str, bytes, bytearray)}
        czekitout.check.if_instance_of_any_accepted_types(**kwargs)
        
        try:
            serializable_rep = json.loads(serialized_rep)
        except:
            raise ValueError(_pre_serializable_err_msg_10)

        kwargs = {"serializable_rep": \
                  serializable_rep,
                  "skip_validation_and_conversion": \
                  skip_validation_and_conversion}
        instance_of_current_cls = cls.de_pre_serialize(**kwargs)
                
        return instance_of_current_cls



    @classmethod
    def load(cls,
             filename=\
             _default_filename,
             skip_validation_and_conversion=\
             _default_skip_validation_and_conversion):
        r"""Construct an instance from a serialized representation that is 
        stored in a JSON file.

        Users can save serialized representations to JSON files using the method
        :meth:`fancytypes.PreSerializable.dump`.

        Parameters
        ----------
        filename : `str`, optional
            The relative or absolute path to the JSON file that is storing the
            serialized representation of an instance.

            ``filename`` is expected to be such that ``json.load(open(filename,
            "r"))`` does not raise an exception.

            Let ``serializable_rep=json.load(open(filename, "r"))``.

            Let ``validation_and_conversion_funcs`` and
            ``de_pre_serialization_funcs`` denote the attributes
            :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
            :attr:`~fancytypes.PreSerializable.de_pre_serialization_funcs`
            respectively, both of which being `dict` objects as well.

            ``filename`` is also expected to be such that
            ``de_pre_serialization_funcs[key](serializable_rep[key])`` does not
            raise an exception for each `dict` key ``key`` in
            ``de_pre_serialization_funcs``.

            Let ``core_attrs_candidate`` be a `dict` object that has the same
            keys as ``de_pre_serialization_funcs``, where for each `dict` key
            ``key`` in ``serializable_rep``, ``core_attrs_candidate[key]`` is
            set to de_pre_serialization_funcs[key](serializable_rep[key])``.

            ``filename`` is also expected to be such that
            ``validation_and_conversion_funcs[key](core_attrs_candidate)`` does
            not raise an exception for each `dict` key ``key`` in
            ``serializable_rep``.
        skip_validation_and_conversion : `bool`, optional
            Let ``core_attrs`` denote the attribute
            :attr:`~fancytypes.Checkable.core_attrs`, which is a `dict` object.

            Let ``core_attrs_candidate`` be as defined in the above description
            of ``filename``.

            If ``skip_validation_and_conversion`` is set to ``False``, then for
            each key ``key`` in ``core_attrs_candidate``, ``core_attrs[key]`` is
            set to ``validation_and_conversion_funcs[key]
            (core_attrs_candidate)``, , with ``validation_and_conversion_funcs``
            and ``core_attrs_candidate`` being introduced in the above
            description of ``filename``.

            Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
            then ``core_attrs`` is set to ``core_attrs_candidate.copy()``. This
            option is desired primarily when the user wants to avoid potentially
            expensive deep copies and/or conversions of the `dict` values of
            ``core_attrs_candidate``, as it is guaranteed that no copies or
            conversions are made in this case.

        Returns
        -------
        instance_of_current_cls : Current class
            An instance constructed from the serialized representation
            stored in the JSON file.

        """
        kwargs = {"obj": filename, "obj_name": "filename"}
        filename = czekitout.convert.to_str_from_str_like(**kwargs)
        
        try:
            with open(filename, "r") as file_obj:
                serializable_rep = json.load(file_obj)
        except:
            raise IOError(_pre_serializable_err_msg_11.format(filename))

        kwargs = {"serializable_rep": \
                  serializable_rep,
                  "skip_validation_and_conversion": \
                  skip_validation_and_conversion}
        instance_of_current_cls = cls.de_pre_serialize(**kwargs)
                
        return instance_of_current_cls



class PreSerializableAndUpdatable(PreSerializable, Updatable):
    r"""A type that is pre-serializable, that can be constructed from a 
    serializable representation, that can perform user-defined validations 
    and conversions of a set of parameters upon construction, and that has an
    updatable subset of attributes.

    We define pre-serialization as the process of converting an object into a
    form that can be subsequently serialized into a JSON format. We refer to
    objects resulting from pre-serialization as serializable objects.

    We define de-pre-serialization as the process of converting a serializable
    object into an instance of the current class, i.e. de-pre-serialization is
    the reverse process of pre-serialization.

    One cannot construct an instance of the class
    :class:`fancytypes.PreSerializableAndUpdatable` without raising an
    exception. In order to make use of this class, one must create a subclass
    that inherits from :class:`fancytypes.PreSerializableAndUpdatable` and then
    override the class methods
    :class:`~fancytypes.Checkable.get_validation_and_conversion_funcs`,
    :class:`~fancytypes.PreSerializable.pre_serialization_funcs`, and
    :class:`~fancytypes.PreSerializable.de_pre_serialization_funcs` in ways that
    are consistent with the respective descriptions of the methods.

    Parameters
    ----------
    skip_validation_and_conversion : `bool`, optional
        Let ``validation_and_conversion_funcs`` and ``core_attrs`` denote the
        attributes :attr:`~fancytypes.Checkable.validation_and_conversion_funcs`
        and :attr:`~fancytypes.Checkable.core_attrs` respectively, both of which
        being `dict` objects.

        Let ``params_to_be_mapped_to_core_attrs`` denote the `dict`
        representation of the constructor parameters excluding the parameters
        ``skip_validation_and_conversion`` and ``skip_cls_tests``, where each
        `dict` key ``key`` is a different constructor parameter name, excluding
        the names ``"skip_validation_and_conversion"`` and ``"skip_cls_tests"``,
        and ``params_to_be_mapped_to_core_attrs[key]`` would yield the value of
        the constructor parameter with the name given by ``key``.

        If ``skip_validation_and_conversion`` is set to ``False``, then for each
        key ``key`` in ``params_to_be_mapped_to_core_attrs``,
        ``core_attrs[key]`` is set to ``validation_and_conversion_funcs[key]
        (params_to_be_mapped_to_core_attrs)``.

        Otherwise, if ``skip_validation_and_conversion`` is set to ``True``,
        then ``core_attrs`` is set to
        ``params_to_be_mapped_to_core_attrs.copy()``. This option is desired
        primarily when the user wants to avoid potentially expensive deep copies
        and/or conversions of the `dict` values of
        ``params_to_be_mapped_to_core_attrs``, as it is guaranteed that no
        copies or conversions are made in this case.  
    skip_cls_test : `bool`, optional
        If ``skip_cls_test`` is set to ``False``, then upon construction, tests
        will be performed to check whether the class was properly
        defined. If any of the tests fail, an exception will be raised.

        Otherwise, if ``skip_cls_test`` is set to ``True``, these tests will be
        skipped. 

        One should only skip the tests if they are sure that the class is
        properly defined. Skipping the tests will yield some improvement in
        performance.
    **kwargs 
        The remaining constructor parameters.

    """
    def __init__(self,
                 skip_validation_and_conversion=\
                 _default_skip_validation_and_conversion,
                 skip_cls_tests=\
                 _default_skip_cls_tests,
                 **kwargs):
        PreSerializable.__init__(self,
                                 skip_validation_and_conversion,
                                 skip_cls_tests,
                                 **kwargs)
        
        return None



def _check_and_convert_namespace_as_dict(params):
    current_func_name = inspect.stack()[0][3]
    obj_name = current_func_name.split("_check_and_convert_")[-1]
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    namespace_as_dict = czekitout.convert.to_dict(**kwargs)

    return namespace_as_dict



def _check_and_convert_ctor_param_names(params):
    current_func_name = inspect.stack()[0][3]
    obj_name = current_func_name.split("_check_and_convert_")[-1]
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    ctor_param_names = czekitout.convert.to_tuple_of_strs(**kwargs)

    return ctor_param_names



def _return_subset_of_funcs_from_given_namespace(namespace_as_dict,
                                                 func_name_prefix,
                                                 ctor_param_names):
    params = locals()
    namespace_as_dict = _check_and_convert_namespace_as_dict(params)
    ctor_param_names = _check_and_convert_ctor_param_names(params)

    subset_of_funcs = dict()
    for ctor_param_name in ctor_param_names:
        func_name = func_name_prefix + ctor_param_name
        
        if func_name not in namespace_as_dict:
            current_func_name = inspect.stack()[0][3]
            unformatted_err_msg = globals()[current_func_name+"_err_msg_1"]
            err_msg = unformatted_err_msg.format(func_name)
            raise KeyError(err_msg)
        
        subset_of_funcs[ctor_param_name] = namespace_as_dict[func_name]

        kwargs = {"obj": subset_of_funcs[ctor_param_name],
                  "obj_name": func_name}
        czekitout.check.if_callable(**kwargs)

    return subset_of_funcs



def return_validation_and_conversion_funcs(namespace_as_dict, ctor_param_names):
    r"""Get a set of callables that are assumed to be validation and conversion
    functions, from a given namespace, according to a given set of construction 
    parameter names.

    For a discussion on validation and conversion functions, see the
    documentation for
    :attr:`fancytypes.Checkable.validation_and_conversion_funcs` for a
    description.

    Parameters
    ----------
    namespace_as_dict : `dict`
        A `dict` representation of the namespace from which to get the 
        callables. An example of such a `dict` representation is the output of
        ``globals()``, which returns a `dict` representation of the namespace of
        the module in which ``globals`` is called.
    ctor_param_names : `array_like` (`str`, ndim=1)
        The construction parameter names of interest.

    Returns
    -------
    validation_and_conversion_funcs : `dict`
        A `dict` object storing the callables that are assumed to be validation
        and conversion functions. The keys of
        ``validation_and_conversion_funcs`` are the strings stored in
        ``ctor_param_names``. For each string ``ctor_param_name`` in
        ``ctor_param_names``,
        ``validation_and_conversion_funcs[ctor_param_name]`` is set to
        ``namespace_as_dict["_check_and_convert_"+ctor_param_name]``.

    """
    kwargs = locals()
    kwargs["func_name_prefix"] = "_check_and_convert_"
    subset_of_funcs = _return_subset_of_funcs_from_given_namespace(**kwargs)
    validation_and_conversion_funcs = subset_of_funcs

    return validation_and_conversion_funcs



def return_pre_serialization_funcs(namespace_as_dict, ctor_param_names):
    r"""Get a set of callables that are assumed to be pre-serialization
    functions, from a given namespace, according to a given set of construction 
    parameter names.

    For a discussion on pre-serialization functions, see the documentation for
    :attr:`fancytypes.PreSerializable.pre_serialization_funcs` for a
    description.

    Parameters
    ----------
    namespace_as_dict : `dict`
        A `dict` representation of the namespace from which to get the 
        callables. An example of such a `dict` representation is the output of
        ``globals()``, which returns a `dict` representation of the namespace of
        the module in which ``globals`` is called.
    ctor_param_names : `array_like` (`str`, ndim=1)
        The construction parameter names of interest.

    Returns
    -------
    pre_serialization_funcs : `dict`
        A `dict` object storing the callables that are assumed to be
        pre-serialization functions. The keys of ``pre_serialization_funcs`` are
        the strings stored in ``ctor_param_names``. For each string
        ``ctor_param_name`` in ``ctor_param_names``,
        ``pre_serialization_funcs[ctor_param_name]`` is set to
        ``namespace_as_dict["_pre_serialize_"+ctor_param_name]``.

    """
    kwargs = locals()
    kwargs["func_name_prefix"] = "_pre_serialize_"
    subset_of_funcs = _return_subset_of_funcs_from_given_namespace(**kwargs)
    pre_serialization_funcs = subset_of_funcs

    return pre_serialization_funcs



def return_de_pre_serialization_funcs(namespace_as_dict, ctor_param_names):
    r"""Get a set of callables that are assumed to be de-pre-serialization
    functions, from a given namespace, according to a given set of construction 
    parameter names.

    For a discussion on de-pre-serialization functions, see the documentation
    for :attr:`fancytypes.PreSerializable.de_pre_serialization_funcs` for a
    description.

    Parameters
    ----------
    namespace_as_dict : `dict`
        A `dict` representation of the namespace from which to get the 
        callables. An example of such a `dict` representation is the output of
        ``globals()``, which returns a `dict` representation of the namespace of
        the module in which ``globals`` is called.
    ctor_param_names : `array_like` (`str`, ndim=1)
        The construction parameter names of interest.

    Returns
    -------
    de_pre_serialization_funcs : `dict`
        A `dict` object storing the callables that are assumed to be
        de-pre-serialization functions. The keys of
        ``de_pre_serialization_funcs`` are the strings stored in
        ``ctor_param_names``. For each string ``ctor_param_name`` in
        ``ctor_param_names``, ``de_pre_serialization_funcs[ctor_param_name]`` is
        set to ``namespace_as_dict["_de_pre_serialize_"+ctor_param_name]``.

    """
    kwargs = locals()
    kwargs["func_name_prefix"] = "_de_pre_serialize_"
    subset_of_funcs = _return_subset_of_funcs_from_given_namespace(**kwargs)
    de_pre_serialization_funcs = subset_of_funcs

    return de_pre_serialization_funcs



###########################
## Define error messages ##
###########################

_check_and_convert_validation_and_conversion_funcs_err_msg_1 = \
    ("The object ``validation_and_conversion_funcs`` must be a dictionary with "
     "values set to only callable objects.")

_check_and_convert_core_attrs_candidate_err_msg_1 = \
    ("The object ``{}`` needs to have a key set that is a subset of that of "
     "the object ``validation_and_conversion_funcs``: the object ``{}`` "
     "possesses the key ``'{}'`` which is not in the object "
     "``validation_and_conversion_funcs``.")

_checkable_err_msg_1 = \
    ("The class method ``get_validation_and_conversion_funcs`` has not been "
     "implemented.")

_preliminary_check_of_pre_serialization_funcs_err_msg_1 = \
    ("The objects ``pre_serialization_funcs`` and "
     "``validation_and_conversion_funcs`` must have matching key sets.")
_preliminary_check_of_pre_serialization_funcs_err_msg_2 = \
    ("The objects ``pre_serialization_funcs`` must be a dictionary with values "
     "set to only callable objects.")

_preliminary_check_of_de_pre_serialization_funcs_err_msg_1 = \
    ("The objects ``de_pre_serialization_funcs`` and "
     "``validation_and_conversion_funcs`` must have matching key sets.")
_preliminary_check_of_de_pre_serialization_funcs_err_msg_2 = \
    ("The objects ``de_pre_serialization_funcs`` must be a dictionary with "
     "values set to only callable objects.")

_pre_serializable_err_msg_1 = \
    ("An error occurred in testing the instance method ``pre_serialize``: see "
     "the remaining traceback for details.")
_pre_serializable_err_msg_2 = \
    ("An error occurred in testing part of the de-pre-serialization process of "
     "the class: see the remaining traceback for details.")
_pre_serializable_err_msg_3 = \
    ("The class method ``get_pre_serialization_funcs`` has not been "
     "implemented.")
_pre_serializable_err_msg_4 = \
    ("The class method ``get_de_pre_serialization_funcs`` has not been "
     "implemented.")
_pre_serializable_err_msg_5 = \
    _check_and_convert_core_attrs_candidate_err_msg_1
_pre_serializable_err_msg_6 = \
    ("An error occurred in attempting to de-pre-serialize the object "
     "``serializable_rep``.")
_pre_serializable_err_msg_7 = \
    ("Failed to perform de-pre-serialization: see the remaining traceback for "
     "details.")
_pre_serializable_err_msg_8 = \
    ("Cannot save the serialized representation to a file at the path ``'{}'`` "
     "because a file already exists there and the object ``overwrite`` was set "
     "to ``False``, which prohibits overwriting the original file.")
_pre_serializable_err_msg_9 = \
    ("An error occurred in trying to save the serialized representation to the "
     "file at the path ``'{}'``: see the traceback for details.")
_pre_serializable_err_msg_10 = \
    ("The object ``serialized_rep`` must be a valid JSON document.")
_pre_serializable_err_msg_11 = \
    ("The filename ``'{}'`` is invalid: see the traceback for details.")

_return_subset_of_funcs_from_given_namespace_err_msg_1 = \
    ("The object ``namespace_as_dict`` is missing the key ``'{}'``.")
