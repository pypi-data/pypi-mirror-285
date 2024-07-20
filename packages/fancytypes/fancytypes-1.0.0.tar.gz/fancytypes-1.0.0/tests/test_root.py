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
r"""Contains tests for the root of the package :mod:`fancytypes`.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For performing deep copies.
import copy

# For operations related to unit tests.
import pytest

# For removing files.
import pathlib



# For validating and converting objects.
import czekitout.check
import czekitout.convert



# For defining classes that support enforced validation, updatability,
# pre-serialization, and de-serialization.
import fancytypes



##################################
## Define classes and functions ##
##################################



def _check_and_convert_slice_obj(params):
    obj_name = "slice_obj"
    kwargs = {"obj": params[obj_name],
              "obj_name": obj_name,
              "accepted_types": (slice,)}
    czekitout.check.if_instance_of_any_accepted_types(**kwargs)
    slice_obj = copy.deepcopy(params[obj_name])

    return slice_obj



def _check_and_convert_nonnegative_int(params):
    obj_name = "nonnegative_int"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    nonnegative_int = czekitout.convert.to_nonnegative_int(**kwargs)

    return nonnegative_int



def _check_and_convert_word(params):
    obj_name = "word"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    word = czekitout.convert.to_str_from_str_like(**kwargs)

    return word



def _pre_serialize_slice_obj(slice_obj):
    serializable_rep = {"start": slice_obj.start, 
                        "stop": slice_obj.stop, 
                        "step": slice_obj.step}
    
    return serializable_rep



def _pre_serialize_nonnegative_int(nonnegative_int):
    serializable_rep = nonnegative_int
    
    return serializable_rep



def _pre_serialize_word(word):
    serializable_rep = word
    
    return serializable_rep



def _de_pre_serialize_slice_obj(serializable_rep):
    slice_obj = slice(serializable_rep["start"], 
                      serializable_rep["stop"], 
                      serializable_rep["step"])
    
    return slice_obj



def _de_pre_serialize_nonnegative_int(serializable_rep):
    nonnegative_int = serializable_rep
    
    return nonnegative_int



def _de_pre_serialize_word(serializable_rep):
    word = serializable_rep
    
    return word



class PreSerializableAndUpdatableCls1(fancytypes.PreSerializableAndUpdatable):
    ctor_param_names = ("slice_obj", "nonnegative_int")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    del ctor_param_names, kwargs


    
    def __init__(self,
                 slice_obj,
                 nonnegative_int,
                 skip_validation_and_conversion):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = False
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None


    
    @classmethod
    def get_validation_and_conversion_funcs(cls):
        validation_and_conversion_funcs = \
            cls._validation_and_conversion_funcs_.copy()

        return validation_and_conversion_funcs


    
    @classmethod
    def get_pre_serialization_funcs(cls):
        pre_serialization_funcs = \
            cls._pre_serialization_funcs_.copy()

        return pre_serialization_funcs


    
    @classmethod
    def get_de_pre_serialization_funcs(cls):
        de_pre_serialization_funcs = \
            cls._de_pre_serialization_funcs_.copy()

        return de_pre_serialization_funcs



class PreSerializableAndUpdatableCls2(PreSerializableAndUpdatableCls1):
    ctor_param_names = ("slice_obj", "nonnegative_int", "word")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    del ctor_param_names, kwargs


    
    def __init__(self,
                 slice_obj,
                 nonnegative_int,
                 word):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = False
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



class PreSerializableAndUpdatableCls3(PreSerializableAndUpdatableCls1):
    def __init__(self,
                 slice_obj,
                 nonnegative_int,
                 skip_validation_and_conversion,
                 skip_cls_tests=True):
        self._pre_serialization_funcs_["slice_obj"] = max

        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



class PreSerializableAndUpdatableCls4(PreSerializableAndUpdatableCls1):
    def __init__(self,
                 slice_obj,
                 nonnegative_int,
                 skip_validation_and_conversion,
                 skip_cls_tests):
        self._pre_serialization_funcs_["slice_obj"] = slice
        self._de_pre_serialization_funcs_["slice_obj"] = max

        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



class PreSerializableAndUpdatableCls5(PreSerializableAndUpdatableCls1):
    def __init__(self,
                 slice_obj=slice(None),
                 nonnegative_int=0,
                 skip_validation_and_conversion=False):
        self._validation_and_conversion_funcs_["slice_obj"] = None

        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = False
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)



class PreSerializableAndUpdatableCls6(PreSerializableAndUpdatableCls1):
    ctor_param_names = ("slice_obj", "nonnegative_int")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    _pre_serialization_funcs_["slice_obj"] = None

    

    def __init__(self,
                 slice_obj=slice(None),
                 nonnegative_int=0,
                 skip_validation_and_conversion=False):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = False
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)



class PreSerializableAndUpdatableCls7(PreSerializableAndUpdatableCls1):
    ctor_param_names = ("slice_obj", "nonnegative_int")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    _de_pre_serialization_funcs_["slice_obj"] = None

    

    def __init__(self,
                 slice_obj=slice(None),
                 nonnegative_int=0,
                 skip_validation_and_conversion=False):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = False
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)



class PreSerializableAndUpdatableCls8(PreSerializableAndUpdatableCls1):
    ctor_param_names = ("slice_obj", "nonnegative_int")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    _pre_serialization_funcs_["word"] = None

    

    def __init__(self,
                 slice_obj=slice(None),
                 nonnegative_int=0,
                 skip_validation_and_conversion=False):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = False
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)



class PreSerializableAndUpdatableCls9(PreSerializableAndUpdatableCls1):
    ctor_param_names = ("slice_obj", "nonnegative_int")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    _de_pre_serialization_funcs_["word"] = None

    

    def __init__(self,
                 slice_obj=slice(None),
                 nonnegative_int=0,
                 skip_validation_and_conversion=False):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = False
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)



class PreSerializableAndUpdatableCls10(PreSerializableAndUpdatableCls1):
    ctor_param_names = ("slice_obj", "nonnegative_int")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    

    def __init__(self,
                 slice_obj=slice(None),
                 nonnegative_int=0,
                 word="foo",
                 skip_validation_and_conversion=False):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = False
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)



class PreSerializableAndUpdatableCls11(PreSerializableAndUpdatableCls1):
    ctor_param_names = ("slice_obj", "nonnegative_int")
    kwargs = {"namespace_as_dict": globals(),
              "ctor_param_names": ctor_param_names}
    
    _validation_and_conversion_funcs_ = \
        fancytypes.return_validation_and_conversion_funcs(**kwargs)
    _pre_serialization_funcs_ = \
        fancytypes.return_pre_serialization_funcs(**kwargs)
    _de_pre_serialization_funcs_ = \
        fancytypes.return_de_pre_serialization_funcs(**kwargs)

    

    def __init__(self,
                 slice_obj=slice(None),
                 nonnegative_int=0,
                 skip_validation_and_conversion=False):
        ctor_params = {key: val
                       for key, val in locals().items()
                       if (key not in ("self", "__class__"))}
        kwargs = ctor_params
        kwargs["skip_cls_tests"] = True
        fancytypes.PreSerializableAndUpdatable.__init__(self, **kwargs)

        return None



def test_1_of_return_validation_and_conversion_funcs():
    with pytest.raises(KeyError) as err_info:
        kwargs = {"namespace_as_dict": globals(), "ctor_param_names": ("foo",)}
        fancytypes.return_validation_and_conversion_funcs(**kwargs)

    return None



def test_1_of_PreSerializableAndUpdatable():
    slice_obj_1 = slice(None, 6, 1)
    slice_obj_2 = slice(3, None, 1)

    kwargs = {"slice_obj": slice_obj_1,
              "nonnegative_int": 5.0,
              "skip_validation_and_conversion": False}
    fancytype_instance = PreSerializableAndUpdatableCls1(**kwargs)

    new_core_attr_subset_candidate = {"slice_obj": slice_obj_2,
                                      "not_a_core_attr": None}
    kwargs = {"new_core_attr_subset_candidate": new_core_attr_subset_candidate,
              "skip_validation_and_conversion": False}
    fancytype_instance.update(**kwargs)
        
    core_attrs = fancytype_instance.get_core_attrs(deep_copy=False)
    assert core_attrs["slice_obj"] == slice_obj_2
    assert core_attrs["slice_obj"] is not slice_obj_2

    new_core_attr_subset_candidate = {"slice_obj": slice_obj_1}
    kwargs = {"new_core_attr_subset_candidate": new_core_attr_subset_candidate,
              "skip_validation_and_conversion": True}
    fancytype_instance.update(**kwargs)

    core_attrs = fancytype_instance.get_core_attrs(deep_copy=False)
    assert core_attrs["slice_obj"] is slice_obj_1

    core_attrs = fancytype_instance.get_core_attrs(deep_copy=True)
    assert core_attrs["slice_obj"] is not slice_obj_1

    kwargs = {"slice_obj": slice_obj_1,
              "nonnegative_int": 5.0,
              "skip_validation_and_conversion": True}
    fancytype_instance = PreSerializableAndUpdatableCls1(**kwargs)

    core_attrs = fancytype_instance.get_core_attrs(deep_copy=False)
    assert core_attrs["slice_obj"] is slice_obj_1

    fancytype_instance.validation_and_conversion_funcs
    fancytype_instance.pre_serialization_funcs
    fancytype_instance.de_pre_serialization_funcs

    for ctor_param_name in ("slice_obj", "nonnegative_int"):
        kwargs = core_attrs
        kwargs[ctor_param_name] = None
        kwargs["skip_validation_and_conversion"] = False
        with pytest.raises(TypeError) as err_info:
            fancytype_instance = PreSerializableAndUpdatableCls1(**kwargs)
        
    return None



def test_2_of_PreSerializableAndUpdatable():
    kwargs = {"slice_obj": slice(None, 6, 1),
              "nonnegative_int": 5.0,
              "skip_validation_and_conversion": True}
    fancytype_instance_A = PreSerializableAndUpdatableCls1(**kwargs)
    fancytype_instances = (fancytype_instance_A,)

    filename = "fancytype.json"
    fancytype_instance_A.dump(filename, overwrite=True)
    fancytype_instance_A.dump(filename, overwrite=True)
    with pytest.raises(IOError) as err_info:
        fancytype_instance_A.dump(filename, overwrite=False)

    serializable_rep = fancytype_instance_A.pre_serialize()
    serialized_rep = fancytype_instance_A.dumps()

    cls_alias = PreSerializableAndUpdatableCls1
    cls_methods = (cls_alias.loads, cls_alias.load, cls_alias.de_pre_serialize)
    param_name_subset = ("serialized_rep", "filename", "serializable_rep")
    param_val_subset = (serialized_rep, filename, serializable_rep)
    zip_obj = zip(cls_methods, param_name_subset, param_val_subset)

    for cls_method, param_name, param_val in zip_obj:
        for skip_validation_and_conversion in (True, False):
            kwargs = {"skip_validation_and_conversion": \
                      skip_validation_and_conversion,
                      param_name: \
                      param_val}
            fancytype_instance_B = cls_method(**kwargs)

            core_attrs_A = fancytype_instance_A.core_attrs
            core_attrs_B = fancytype_instance_B.core_attrs
            assert (core_attrs_A == core_attrs_B)

    with pytest.raises(ValueError) as err_info:
        cls_alias.loads(serialized_rep="foo")

    pathlib.Path(filename).unlink()

    with pytest.raises(IOError) as err_info:
        kwargs = {"filename": filename, "skip_validation_and_conversion": False}
        cls_alias.load(**kwargs)

    with pytest.raises(ValueError) as err_info:
        serializable_rep["foo"] = None
        kwargs = {"serializable_rep": serializable_rep,
                  "skip_validation_and_conversion": False}
        cls_alias.de_pre_serialize(**kwargs)

    return None



def test_3_of_PreSerializableAndUpdatable():
    slice_obj_1 = slice(None, 6, 1)
    slice_obj_2 = slice(3, None, 1)

    kwargs = {"slice_obj": slice_obj_1,
              "nonnegative_int": 5.0,
              "word": "foo"}
    fancytype_instance = PreSerializableAndUpdatableCls2(**kwargs)

    new_core_attr_subset_candidate = {"slice_obj": slice_obj_2,
                                      "not_a_core_attr": None}
    kwargs = {"new_core_attr_subset_candidate": new_core_attr_subset_candidate,
              "skip_validation_and_conversion": False}
    fancytype_instance.update(**kwargs)
        
    core_attrs = fancytype_instance.get_core_attrs(deep_copy=False)
    assert core_attrs["slice_obj"] == slice_obj_2
    assert core_attrs["slice_obj"] is not slice_obj_2

    new_core_attr_subset_candidate = {"slice_obj": slice_obj_1}
    kwargs = {"new_core_attr_subset_candidate": new_core_attr_subset_candidate,
              "skip_validation_and_conversion": True}
    fancytype_instance.update(**kwargs)

    core_attrs = fancytype_instance.get_core_attrs(deep_copy=False)
    assert core_attrs["slice_obj"] is slice_obj_1

    core_attrs = fancytype_instance.get_core_attrs(deep_copy=True)
    assert core_attrs["slice_obj"] is not slice_obj_1

    kwargs = {"serializable_rep": fancytype_instance.pre_serialize(),
              "skip_validation_and_conversion": False}
    PreSerializableAndUpdatableCls2.de_pre_serialize(**kwargs)
        
    return None



def test_4_of_PreSerializableAndUpdatable():
    cls_set_1 = (fancytypes.Checkable,
                 fancytypes.Updatable,
                 fancytypes.PreSerializable,
                 fancytypes.PreSerializableAndUpdatable)
    for cls in cls_set_1:
        with pytest.raises(NotImplementedError) as err_info:
            cls()

    with pytest.raises(NotImplementedError) as err_info:
        fancytypes.PreSerializable.get_pre_serialization_funcs()
    with pytest.raises(NotImplementedError) as err_info:
        fancytypes.PreSerializable.get_de_pre_serialization_funcs()

    with pytest.raises(ValueError) as err_info:
        kwargs = {"slice_obj": slice(None, 6, 1),
                  "nonnegative_int": 5.0,
                  "skip_validation_and_conversion": False,
                  "skip_cls_tests": False}
        PreSerializableAndUpdatableCls3(**kwargs)

    with pytest.raises(ValueError) as err_info:
        serializable_rep = {"slice_obj": {"start": 0, "stop": 1, "step": 1},
                            "nonnegative_int": 5}
        kwargs = {"serializable_rep": serializable_rep,
                  "skip_validation_and_conversion": False}
        PreSerializableAndUpdatableCls3.de_pre_serialize(**kwargs)

    kwargs = {"slice_obj": slice(None, 6, 1),
              "nonnegative_int": 5.0,
              "skip_validation_and_conversion": False,
              "skip_cls_tests": False}
    with pytest.raises(ValueError) as err_info:
        PreSerializableAndUpdatableCls4(**kwargs)

    kwargs["skip_cls_tests"] = True
    fancytype_instance = PreSerializableAndUpdatableCls4(**kwargs)

    with pytest.raises(IOError) as err_info:
        kwargs = {"filename": "fancytype.json", "overwrite": True}
        fancytype_instance.dump(**kwargs)

    cls_set_2 = (PreSerializableAndUpdatableCls5,
                 PreSerializableAndUpdatableCls6,
                 PreSerializableAndUpdatableCls7)
    for cls in cls_set_2:
        with pytest.raises(TypeError) as err_info:
            cls()
        
    return None



def test_5_of_PreSerializableAndUpdatable():
    cls_set = (PreSerializableAndUpdatableCls8,
               PreSerializableAndUpdatableCls9,
               PreSerializableAndUpdatableCls10)
    for cls in cls_set:
        with pytest.raises(KeyError) as err_info:
            cls()

    PreSerializableAndUpdatableCls11()
        
    return None



###########################
## Define error messages ##
###########################
