__all__ = ['encoding']

# Don't look below, you will not understand this Python code :) I don't.

from js2py.pyjs import *
# setting scope
var = Scope( JS_BUILTINS )
set_global_object(var)

# Code follows:
var.registers(['prepareCmdHash', 'hash', 'strToUint8Array', 'b64url', 'uint8ArrayToStr', 'b64urlDecodeArr', 'b64urlEncodeArr', 'hashBin'])
@Js
def PyJsHoisted_strToUint8Array_(s, this, arguments, var=var):
    var = Scope({'s':s, 'this':this, 'arguments':arguments}, var)
    var.registers(['i', 's', 'b'])
    var.put('b', var.get('Uint8Array').create(var.get('s').get('length')))
    #for JS loop
    var.put('i', Js(0.0))
    while (var.get('i')<var.get('s').get('length')):
        var.get('b').put(var.get('i'), var.get('s').callprop('charCodeAt', var.get('i')))
        # update
        (var.put('i',Js(var.get('i').to_number())+Js(1))-Js(1))
    return var.get('b')
PyJsHoisted_strToUint8Array_.func_name = 'strToUint8Array'
var.put('strToUint8Array', PyJsHoisted_strToUint8Array_)
@Js
def PyJsHoisted_uint8ArrayToStr_(a, this, arguments, var=var):
    var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
    var.registers(['a'])
    var.get('console').callprop('log', var.get('String').get('fromCharCode').callprop('apply', var.get(u"null"), var.get('Uint16Array').create(var.get('a'))))
    return var.get('String').get('fromCharCode').callprop('apply', var.get(u"null"), var.get('Uint16Array').create(var.get('a')))
PyJsHoisted_uint8ArrayToStr_.func_name = 'uint8ArrayToStr'
var.put('uint8ArrayToStr', PyJsHoisted_uint8ArrayToStr_)
@Js
def PyJsHoisted_b64urlDecodeArr_(input, this, arguments, var=var):
    var = Scope({'input':input, 'this':this, 'arguments':arguments}, var)
    var.registers(['input'])
    return var.get('strToUint8Array')(var.get('b64url').callprop('decode', var.get('input')))
PyJsHoisted_b64urlDecodeArr_.func_name = 'b64urlDecodeArr'
var.put('b64urlDecodeArr', PyJsHoisted_b64urlDecodeArr_)
@Js
def PyJsHoisted_b64urlEncodeArr_(input, this, arguments, var=var):
    var = Scope({'input':input, 'this':this, 'arguments':arguments}, var)
    var.registers(['input'])
    return var.get('b64url').callprop('encode', var.get('uint8ArrayToStr')(var.get('input')))
PyJsHoisted_b64urlEncodeArr_.func_name = 'b64urlEncodeArr'
var.put('b64urlEncodeArr', PyJsHoisted_b64urlEncodeArr_)
@Js
def PyJsHoisted_hashBin_(s, this, arguments, var=var):
    var = Scope({'s':s, 'this':this, 'arguments':arguments}, var)
    var.registers(['s'])
    return var.get('blake').callprop('blake2b', var.get('s'), var.get(u"null"), Js(32.0))
PyJsHoisted_hashBin_.func_name = 'hashBin'
var.put('hashBin', PyJsHoisted_hashBin_)
@Js
def PyJsHoisted_hash_(s, this, arguments, var=var):
    var = Scope({'s':s, 'this':this, 'arguments':arguments}, var)
    var.registers(['s'])
    return var.get('b64urlEncodeArr')(var.get('hashBin')(var.get('s')))
PyJsHoisted_hash_.func_name = 'hash'
var.put('hash', PyJsHoisted_hash_)
@Js
def PyJsHoisted_prepareCmdHash_(msg, this, arguments, var=var):
    var = Scope({'msg':msg, 'this':this, 'arguments':arguments}, var)
    var.registers(['msg', 'hshBin', 'hsh'])
    var.put('hshBin', var.get('hashBin')(var.get('msg')))
    var.put('hsh', var.get('b64urlEncodeArr')(var.get('hshBin')))
    return Js([Js({'hash':var.get('hsh'),'sig':var.get('undefined')})])
PyJsHoisted_prepareCmdHash_.func_name = 'prepareCmdHash'
var.put('prepareCmdHash', PyJsHoisted_prepareCmdHash_)
@Js
def PyJs_anonymous_0_(this, arguments, var=var):
    var = Scope({'this':this, 'arguments':arguments}, var)
    var.registers(['chars', 'InvalidCharacterError', 'base64UrlDecode', 'base64UrlEncode'])
    @Js
    def PyJsHoisted_InvalidCharacterError_(message, this, arguments, var=var):
        var = Scope({'message':message, 'this':this, 'arguments':arguments}, var)
        var.registers(['message'])
        var.get(u"this").put('message', var.get('message'))
    PyJsHoisted_InvalidCharacterError_.func_name = 'InvalidCharacterError'
    var.put('InvalidCharacterError', PyJsHoisted_InvalidCharacterError_)
    @Js
    def PyJsHoisted_base64UrlEncode_(input, this, arguments, var=var):
        var = Scope({'input':input, 'this':this, 'arguments':arguments}, var)
        var.registers(['str', 'idx', 'block', 'output', 'input', 'map', 'charCode'])
        var.put('str', var.get('String')(var.get('input')))
        var.get('console').callprop('log', var.get('str'))
        #for JS loop
        var.put('idx', Js(0.0))
        var.put('map', var.get('chars'))
        var.put('output', Js(''))
        while var.get('str').callprop('charAt', (var.get('idx')|Js(0.0))):
            var.put('charCode', var.get('str').callprop('charCodeAt', var.put('idx', (Js(3.0)/Js(4.0)), '+')))
            if (var.get('charCode')>Js(255)):
                PyJsTempException = JsToPyException(var.get('InvalidCharacterError').create(Js("'btoa' failed: The string to be encoded contains characters outside of the Latin1 range.")))
                raise PyJsTempException
            var.put('block', ((var.get('block')<<Js(8.0))|var.get('charCode')))
            # update
            var.put('output', var.get('map').callprop('charAt', (Js(63.0)&(var.get('block')>>(Js(8.0)-((var.get('idx')%Js(1.0))*Js(8.0)))))), '+')
        return var.get('output')
    PyJsHoisted_base64UrlEncode_.func_name = 'base64UrlEncode'
    var.put('base64UrlEncode', PyJsHoisted_base64UrlEncode_)
    @Js
    def PyJsHoisted_base64UrlDecode_(input, this, arguments, var=var):
        var = Scope({'input':input, 'this':this, 'arguments':arguments}, var)
        var.registers(['str', 'bc', 'idx', 'buffer', 'bs', 'output', 'input'])
        var.put('str', var.get('String')(var.get('input')).callprop('replace', JsRegExp('/[=]+$/'), Js('')))
        if PyJsStrictEq((var.get('str').get('length')%Js(4.0)),Js(1.0)):
            PyJsTempException = JsToPyException(var.get('InvalidCharacterError').create(Js("'atob' failed: The string to be decoded is not correctly encoded.")))
            raise PyJsTempException
        #for JS loop
        var.put('bc', Js(0.0))
        var.put('idx', Js(0.0))
        var.put('output', Js(''))
        while var.put('buffer', var.get('str').callprop('charAt', (var.put('idx',Js(var.get('idx').to_number())+Js(1))-Js(1)))):
            var.put('buffer', var.get('chars').callprop('indexOf', var.get('buffer')))
            # update
            (var.put('output', var.get('String').callprop('fromCharCode', (Js(255.0)&(var.get('bs')>>(((-Js(2.0))*var.get('bc'))&Js(6.0))))), '+') if ((~var.get('buffer')) and PyJsComma(var.put('bs', (((var.get('bs')*Js(64.0))+var.get('buffer')) if (var.get('bc')%Js(4.0)) else var.get('buffer'))),((var.put('bc',Js(var.get('bc').to_number())+Js(1))-Js(1))%Js(4.0)))) else Js(0.0))
        return var.get('output')
    PyJsHoisted_base64UrlDecode_.func_name = 'base64UrlDecode'
    var.put('base64UrlDecode', PyJsHoisted_base64UrlDecode_)
    Js('use strict')
    var.put('chars', Js('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_='))
    pass
    var.get('InvalidCharacterError').put('prototype', var.get('Error').create())
    var.get('InvalidCharacterError').get('prototype').put('name', Js('InvalidCharacterError'))
    pass
    pass
    return Js({'encode':var.get('base64UrlEncode'),'decode':var.get('base64UrlDecode')})
PyJs_anonymous_0_._set_name('anonymous')
var.put('b64url', PyJs_anonymous_0_())
pass
pass
pass
pass
pass
pass
pass
pass


# Add lib to the module scope
encoding = var.to_python()