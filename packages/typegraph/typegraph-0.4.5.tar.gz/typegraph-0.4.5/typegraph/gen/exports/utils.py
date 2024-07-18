from ..exports import core
from ..intrinsics import _clamp, _decode_utf8, _encode_utf8, _load, _store
from ..types import Err, Ok, Result
import ctypes
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import wasmtime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from .. import Root

Error = core.Error
TypeId = int
@dataclass
class ReduceValue:
    inherit: bool
    payload: Optional[str]

@dataclass
class ReducePath:
    path: List[str]
    value: ReduceValue

@dataclass
class Reduce:
    paths: List[ReducePath]

@dataclass
class AuthProtocolOauth2:
    pass

@dataclass
class AuthProtocolJwt:
    pass

@dataclass
class AuthProtocolBasic:
    pass

AuthProtocol = Union[AuthProtocolOauth2, AuthProtocolJwt, AuthProtocolBasic]

@dataclass
class Auth:
    name: str
    protocol: AuthProtocol
    auth_data: List[Tuple[str, str]]

@dataclass
class QueryDeployParams:
    tg: str
    secrets: Optional[List[Tuple[str, str]]]

@dataclass
class MdkConfig:
    workspace_path: str
    target_name: str
    config_json: str
    tg_json: str

@dataclass
class MdkOutput:
    path: str
    content: str
    overwrite: bool

class Utils:
    component: 'Root'
    
    def __init__(self, component: 'Root') -> None:
        self.component = component
    def gen_reduceb(self, caller: wasmtime.Store, supertype_id: TypeId, data: Reduce) -> Result[TypeId, Error]:
        record = data
        field = record.paths
        vec15 = field
        len17 = len(vec15)
        result16 = self.component._realloc0(caller, 0, 0, 4, len17 * 24)
        assert(isinstance(result16, int))
        for i18 in range(0, len17):
            e = vec15[i18]
            base0 = result16 + i18 * 24
            record1 = e
            field2 = record1.path
            field3 = record1.value
            vec = field2
            len7 = len(vec)
            result = self.component._realloc0(caller, 0, 0, 4, len7 * 8)
            assert(isinstance(result, int))
            for i8 in range(0, len7):
                e4 = vec[i8]
                base5 = result + i8 * 8
                ptr, len6 = _encode_utf8(e4, self.component._realloc0, self.component._core_memory0, caller)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 4, len6)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 0, ptr)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 4, len7)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 0, result)
            record9 = field3
            field10 = record9.inherit
            field11 = record9.payload
            _store(ctypes.c_uint8, self.component._core_memory0, caller, base0, 8, int(field10))
            if field11 is None:
                _store(ctypes.c_uint8, self.component._core_memory0, caller, base0, 12, 0)
            else:
                payload12 = field11
                _store(ctypes.c_uint8, self.component._core_memory0, caller, base0, 12, 1)
                ptr13, len14 = _encode_utf8(payload12, self.component._realloc0, self.component._core_memory0, caller)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 20, len14)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 16, ptr13)
        ret = self.component.lift_callee69(caller, _clamp(supertype_id, 0, 4294967295), result16, len17)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[TypeId, Error]
        if load == 0:
            load19 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            expected = Ok(load19 & 0xffffffff)
        elif load == 1:
            load20 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load21 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr27 = load20
            len28 = load21
            result29: List[str] = []
            for i30 in range(0, len28):
                base22 = ptr27 + i30 * 8
                load23 = _load(ctypes.c_int32, self.component._core_memory0, caller, base22, 0)
                load24 = _load(ctypes.c_int32, self.component._core_memory0, caller, base22, 4)
                ptr25 = load23
                len26 = load24
                list = _decode_utf8(self.component._core_memory0, caller, ptr25, len26)
                result29.append(list)
            expected = Err(core.Error(result29))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return0(caller, ret)
        return expected
    def add_graphql_endpoint(self, caller: wasmtime.Store, graphql: str) -> Result[int, Error]:
        ptr, len0 = _encode_utf8(graphql, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee70(caller, ptr, len0)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[int, Error]
        if load == 0:
            load1 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            expected = Ok(load1 & 0xffffffff)
        elif load == 1:
            load2 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load3 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr9 = load2
            len10 = load3
            result: List[str] = []
            for i11 in range(0, len10):
                base4 = ptr9 + i11 * 8
                load5 = _load(ctypes.c_int32, self.component._core_memory0, caller, base4, 0)
                load6 = _load(ctypes.c_int32, self.component._core_memory0, caller, base4, 4)
                ptr7 = load5
                len8 = load6
                list = _decode_utf8(self.component._core_memory0, caller, ptr7, len8)
                result.append(list)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return0(caller, ret)
        return expected
    def add_auth(self, caller: wasmtime.Store, data: Auth) -> Result[int, Error]:
        record = data
        field = record.name
        field0 = record.protocol
        field1 = record.auth_data
        ptr, len2 = _encode_utf8(field, self.component._realloc0, self.component._core_memory0, caller)
        if isinstance(field0, AuthProtocolOauth2):
            variant = 0
        elif isinstance(field0, AuthProtocolJwt):
            variant = 1
        elif isinstance(field0, AuthProtocolBasic):
            variant = 2
        else:
            raise TypeError("invalid variant specified for AuthProtocol")
        vec = field1
        len11 = len(vec)
        result = self.component._realloc0(caller, 0, 0, 4, len11 * 16)
        assert(isinstance(result, int))
        for i12 in range(0, len11):
            e = vec[i12]
            base5 = result + i12 * 16
            (tuplei,tuplei6,) = e
            ptr7, len8 = _encode_utf8(tuplei, self.component._realloc0, self.component._core_memory0, caller)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 4, len8)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 0, ptr7)
            ptr9, len10 = _encode_utf8(tuplei6, self.component._realloc0, self.component._core_memory0, caller)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 12, len10)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base5, 8, ptr9)
        ret = self.component.lift_callee71(caller, ptr, len2, variant, result, len11)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[int, Error]
        if load == 0:
            load13 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            expected = Ok(load13 & 0xffffffff)
        elif load == 1:
            load14 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load15 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr21 = load14
            len22 = load15
            result23: List[str] = []
            for i24 in range(0, len22):
                base16 = ptr21 + i24 * 8
                load17 = _load(ctypes.c_int32, self.component._core_memory0, caller, base16, 0)
                load18 = _load(ctypes.c_int32, self.component._core_memory0, caller, base16, 4)
                ptr19 = load17
                len20 = load18
                list = _decode_utf8(self.component._core_memory0, caller, ptr19, len20)
                result23.append(list)
            expected = Err(core.Error(result23))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return0(caller, ret)
        return expected
    def add_raw_auth(self, caller: wasmtime.Store, data: str) -> Result[int, Error]:
        ptr, len0 = _encode_utf8(data, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee72(caller, ptr, len0)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[int, Error]
        if load == 0:
            load1 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            expected = Ok(load1 & 0xffffffff)
        elif load == 1:
            load2 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load3 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr9 = load2
            len10 = load3
            result: List[str] = []
            for i11 in range(0, len10):
                base4 = ptr9 + i11 * 8
                load5 = _load(ctypes.c_int32, self.component._core_memory0, caller, base4, 0)
                load6 = _load(ctypes.c_int32, self.component._core_memory0, caller, base4, 4)
                ptr7 = load5
                len8 = load6
                list = _decode_utf8(self.component._core_memory0, caller, ptr7, len8)
                result.append(list)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return0(caller, ret)
        return expected
    def oauth2(self, caller: wasmtime.Store, service_name: str, scopes: str) -> Result[str, Error]:
        ptr, len0 = _encode_utf8(service_name, self.component._realloc0, self.component._core_memory0, caller)
        ptr1, len2 = _encode_utf8(scopes, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee73(caller, ptr, len0, ptr1, len2)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load3 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load4 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr5 = load3
            len6 = load4
            list = _decode_utf8(self.component._core_memory0, caller, ptr5, len6)
            expected = Ok(list)
        elif load == 1:
            load7 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load8 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr15 = load7
            len16 = load8
            result: List[str] = []
            for i17 in range(0, len16):
                base9 = ptr15 + i17 * 8
                load10 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 0)
                load11 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 4)
                ptr12 = load10
                len13 = load11
                list14 = _decode_utf8(self.component._core_memory0, caller, ptr12, len13)
                result.append(list14)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return2(caller, ret)
        return expected
    def oauth2_without_profiler(self, caller: wasmtime.Store, service_name: str, scopes: str) -> Result[str, Error]:
        ptr, len0 = _encode_utf8(service_name, self.component._realloc0, self.component._core_memory0, caller)
        ptr1, len2 = _encode_utf8(scopes, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee74(caller, ptr, len0, ptr1, len2)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load3 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load4 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr5 = load3
            len6 = load4
            list = _decode_utf8(self.component._core_memory0, caller, ptr5, len6)
            expected = Ok(list)
        elif load == 1:
            load7 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load8 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr15 = load7
            len16 = load8
            result: List[str] = []
            for i17 in range(0, len16):
                base9 = ptr15 + i17 * 8
                load10 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 0)
                load11 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 4)
                ptr12 = load10
                len13 = load11
                list14 = _decode_utf8(self.component._core_memory0, caller, ptr12, len13)
                result.append(list14)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return2(caller, ret)
        return expected
    def oauth2_with_extended_profiler(self, caller: wasmtime.Store, service_name: str, scopes: str, extension: str) -> Result[str, Error]:
        ptr, len0 = _encode_utf8(service_name, self.component._realloc0, self.component._core_memory0, caller)
        ptr1, len2 = _encode_utf8(scopes, self.component._realloc0, self.component._core_memory0, caller)
        ptr3, len4 = _encode_utf8(extension, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee75(caller, ptr, len0, ptr1, len2, ptr3, len4)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load5 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load6 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr7 = load5
            len8 = load6
            list = _decode_utf8(self.component._core_memory0, caller, ptr7, len8)
            expected = Ok(list)
        elif load == 1:
            load9 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load10 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr17 = load9
            len18 = load10
            result: List[str] = []
            for i19 in range(0, len18):
                base11 = ptr17 + i19 * 8
                load12 = _load(ctypes.c_int32, self.component._core_memory0, caller, base11, 0)
                load13 = _load(ctypes.c_int32, self.component._core_memory0, caller, base11, 4)
                ptr14 = load12
                len15 = load13
                list16 = _decode_utf8(self.component._core_memory0, caller, ptr14, len15)
                result.append(list16)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return2(caller, ret)
        return expected
    def oauth2_with_custom_profiler(self, caller: wasmtime.Store, service_name: str, scopes: str, profiler: TypeId) -> Result[str, Error]:
        ptr, len0 = _encode_utf8(service_name, self.component._realloc0, self.component._core_memory0, caller)
        ptr1, len2 = _encode_utf8(scopes, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee76(caller, ptr, len0, ptr1, len2, _clamp(profiler, 0, 4294967295))
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load3 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load4 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr5 = load3
            len6 = load4
            list = _decode_utf8(self.component._core_memory0, caller, ptr5, len6)
            expected = Ok(list)
        elif load == 1:
            load7 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load8 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr15 = load7
            len16 = load8
            result: List[str] = []
            for i17 in range(0, len16):
                base9 = ptr15 + i17 * 8
                load10 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 0)
                load11 = _load(ctypes.c_int32, self.component._core_memory0, caller, base9, 4)
                ptr12 = load10
                len13 = load11
                list14 = _decode_utf8(self.component._core_memory0, caller, ptr12, len13)
                result.append(list14)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return2(caller, ret)
        return expected
    def gql_deploy_query(self, caller: wasmtime.Store, params: QueryDeployParams) -> Result[str, Error]:
        record = params
        field = record.tg
        field0 = record.secrets
        ptr, len1 = _encode_utf8(field, self.component._realloc0, self.component._core_memory0, caller)
        if field0 is None:
            variant = 0
            variant11 = 0
            variant12 = 0
        else:
            payload2 = field0
            vec = payload2
            len9 = len(vec)
            result = self.component._realloc0(caller, 0, 0, 4, len9 * 16)
            assert(isinstance(result, int))
            for i10 in range(0, len9):
                e = vec[i10]
                base3 = result + i10 * 16
                (tuplei,tuplei4,) = e
                ptr5, len6 = _encode_utf8(tuplei, self.component._realloc0, self.component._core_memory0, caller)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base3, 4, len6)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base3, 0, ptr5)
                ptr7, len8 = _encode_utf8(tuplei4, self.component._realloc0, self.component._core_memory0, caller)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base3, 12, len8)
                _store(ctypes.c_uint32, self.component._core_memory0, caller, base3, 8, ptr7)
            variant = 1
            variant11 = result
            variant12 = len9
        ret = self.component.lift_callee77(caller, ptr, len1, variant, variant11, variant12)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load13 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load14 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr15 = load13
            len16 = load14
            list = _decode_utf8(self.component._core_memory0, caller, ptr15, len16)
            expected = Ok(list)
        elif load == 1:
            load17 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load18 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr25 = load17
            len26 = load18
            result27: List[str] = []
            for i28 in range(0, len26):
                base19 = ptr25 + i28 * 8
                load20 = _load(ctypes.c_int32, self.component._core_memory0, caller, base19, 0)
                load21 = _load(ctypes.c_int32, self.component._core_memory0, caller, base19, 4)
                ptr22 = load20
                len23 = load21
                list24 = _decode_utf8(self.component._core_memory0, caller, ptr22, len23)
                result27.append(list24)
            expected = Err(core.Error(result27))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return2(caller, ret)
        return expected
    def gql_remove_query(self, caller: wasmtime.Store, tg_name: List[str]) -> Result[str, Error]:
        vec = tg_name
        len2 = len(vec)
        result = self.component._realloc0(caller, 0, 0, 4, len2 * 8)
        assert(isinstance(result, int))
        for i3 in range(0, len2):
            e = vec[i3]
            base0 = result + i3 * 8
            ptr, len1 = _encode_utf8(e, self.component._realloc0, self.component._core_memory0, caller)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 4, len1)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 0, ptr)
        ret = self.component.lift_callee78(caller, result, len2)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[str, Error]
        if load == 0:
            load4 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load5 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr6 = load4
            len7 = load5
            list = _decode_utf8(self.component._core_memory0, caller, ptr6, len7)
            expected = Ok(list)
        elif load == 1:
            load8 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load9 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr16 = load8
            len17 = load9
            result18: List[str] = []
            for i19 in range(0, len17):
                base10 = ptr16 + i19 * 8
                load11 = _load(ctypes.c_int32, self.component._core_memory0, caller, base10, 0)
                load12 = _load(ctypes.c_int32, self.component._core_memory0, caller, base10, 4)
                ptr13 = load11
                len14 = load12
                list15 = _decode_utf8(self.component._core_memory0, caller, ptr13, len14)
                result18.append(list15)
            expected = Err(core.Error(result18))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return2(caller, ret)
        return expected
    def remove_injections(self, caller: wasmtime.Store, type_id: TypeId) -> Result[TypeId, Error]:
        ret = self.component.lift_callee79(caller, _clamp(type_id, 0, 4294967295))
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[TypeId, Error]
        if load == 0:
            load0 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            expected = Ok(load0 & 0xffffffff)
        elif load == 1:
            load1 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load2 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr7 = load1
            len8 = load2
            result: List[str] = []
            for i9 in range(0, len8):
                base3 = ptr7 + i9 * 8
                load4 = _load(ctypes.c_int32, self.component._core_memory0, caller, base3, 0)
                load5 = _load(ctypes.c_int32, self.component._core_memory0, caller, base3, 4)
                ptr = load4
                len6 = load5
                list = _decode_utf8(self.component._core_memory0, caller, ptr, len6)
                result.append(list)
            expected = Err(core.Error(result))
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return0(caller, ret)
        return expected
    def metagen_exec(self, caller: wasmtime.Store, config: MdkConfig) -> Result[List[MdkOutput], str]:
        record = config
        field = record.workspace_path
        field0 = record.target_name
        field1 = record.config_json
        field2 = record.tg_json
        ptr, len3 = _encode_utf8(field, self.component._realloc0, self.component._core_memory0, caller)
        ptr4, len5 = _encode_utf8(field0, self.component._realloc0, self.component._core_memory0, caller)
        ptr6, len7 = _encode_utf8(field1, self.component._realloc0, self.component._core_memory0, caller)
        ptr8, len9 = _encode_utf8(field2, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee80(caller, ptr, len3, ptr4, len5, ptr6, len7, ptr8, len9)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[List[MdkOutput], str]
        if load == 0:
            load10 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load11 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr23 = load10
            len24 = load11
            result: List[MdkOutput] = []
            for i25 in range(0, len24):
                base12 = ptr23 + i25 * 20
                load13 = _load(ctypes.c_int32, self.component._core_memory0, caller, base12, 0)
                load14 = _load(ctypes.c_int32, self.component._core_memory0, caller, base12, 4)
                ptr15 = load13
                len16 = load14
                list = _decode_utf8(self.component._core_memory0, caller, ptr15, len16)
                load17 = _load(ctypes.c_int32, self.component._core_memory0, caller, base12, 8)
                load18 = _load(ctypes.c_int32, self.component._core_memory0, caller, base12, 12)
                ptr19 = load17
                len20 = load18
                list21 = _decode_utf8(self.component._core_memory0, caller, ptr19, len20)
                load22 = _load(ctypes.c_uint8, self.component._core_memory0, caller, base12, 16)
                operand = load22
                if operand == 0:
                    boolean = False
                elif operand == 1:
                    boolean = True
                else:
                    raise TypeError("invalid variant discriminant for bool")
                result.append(MdkOutput(list, list21, boolean))
            expected = Ok(result)
        elif load == 1:
            load26 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load27 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr28 = load26
            len29 = load27
            list30 = _decode_utf8(self.component._core_memory0, caller, ptr28, len29)
            expected = Err(list30)
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return5(caller, ret)
        return expected
    def metagen_write_files(self, caller: wasmtime.Store, items: List[MdkOutput], typegraph_dir: str) -> Result[None, str]:
        vec = items
        len6 = len(vec)
        result = self.component._realloc0(caller, 0, 0, 4, len6 * 20)
        assert(isinstance(result, int))
        for i7 in range(0, len6):
            e = vec[i7]
            base0 = result + i7 * 20
            record = e
            field = record.path
            field1 = record.content
            field2 = record.overwrite
            ptr, len3 = _encode_utf8(field, self.component._realloc0, self.component._core_memory0, caller)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 4, len3)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 0, ptr)
            ptr4, len5 = _encode_utf8(field1, self.component._realloc0, self.component._core_memory0, caller)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 12, len5)
            _store(ctypes.c_uint32, self.component._core_memory0, caller, base0, 8, ptr4)
            _store(ctypes.c_uint8, self.component._core_memory0, caller, base0, 16, int(field2))
        ptr8, len9 = _encode_utf8(typegraph_dir, self.component._realloc0, self.component._core_memory0, caller)
        ret = self.component.lift_callee81(caller, result, len6, ptr8, len9)
        assert(isinstance(ret, int))
        load = _load(ctypes.c_uint8, self.component._core_memory0, caller, ret, 0)
        expected: Result[None, str]
        if load == 0:
            expected = Ok(None)
        elif load == 1:
            load10 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 4)
            load11 = _load(ctypes.c_int32, self.component._core_memory0, caller, ret, 8)
            ptr12 = load10
            len13 = load11
            list = _decode_utf8(self.component._core_memory0, caller, ptr12, len13)
            expected = Err(list)
        else:
            raise TypeError("invalid variant discriminant for expected")
        self.component._post_return6(caller, ret)
        return expected
    