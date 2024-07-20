function se() {
  const I = {};
  typeof document < "u" && document.currentScript !== null && new URL(document.currentScript.src, location.href).toString();
  let b, d = 0, A = null;
  function F() {
    return (A === null || A.byteLength === 0) && (A = new Uint8Array(b.memory.buffer)), A;
  }
  const E = typeof TextEncoder < "u" ? new TextEncoder("utf-8") : { encode: () => {
    throw Error("TextEncoder not available");
  } }, j = typeof E.encodeInto == "function" ? function(n, e) {
    return E.encodeInto(n, e);
  } : function(n, e) {
    const t = E.encode(n);
    return e.set(t), {
      read: n.length,
      written: t.length
    };
  };
  function m(n, e, t) {
    if (t === void 0) {
      const a = E.encode(n), w = e(a.length, 1) >>> 0;
      return F().subarray(w, w + a.length).set(a), d = a.length, w;
    }
    let r = n.length, _ = e(r, 1) >>> 0;
    const c = F();
    let o = 0;
    for (; o < r; o++) {
      const a = n.charCodeAt(o);
      if (a > 127)
        break;
      c[_ + o] = a;
    }
    if (o !== r) {
      o !== 0 && (n = n.slice(o)), _ = t(_, r, r = o + n.length * 3, 1) >>> 0;
      const a = F().subarray(_ + o, _ + r), w = j(n, a);
      o += w.written, _ = t(_, r, o, 1) >>> 0;
    }
    return d = o, _;
  }
  function g(n) {
    return n == null;
  }
  let P = null;
  function u() {
    return (P === null || P.byteLength === 0) && (P = new Int32Array(b.memory.buffer)), P;
  }
  const O = typeof TextDecoder < "u" ? new TextDecoder("utf-8", { ignoreBOM: !0, fatal: !0 }) : { decode: () => {
    throw Error("TextDecoder not available");
  } };
  typeof TextDecoder < "u" && O.decode();
  function i(n, e) {
    return n = n >>> 0, O.decode(F().subarray(n, n + e));
  }
  let T = null;
  function H() {
    return (T === null || T.byteLength === 0) && (T = new Float64Array(b.memory.buffer)), T;
  }
  function C(n) {
    const e = typeof n;
    if (e == "number" || e == "boolean" || n == null)
      return `${n}`;
    if (e == "string")
      return `"${n}"`;
    if (e == "symbol") {
      const _ = n.description;
      return _ == null ? "Symbol" : `Symbol(${_})`;
    }
    if (e == "function") {
      const _ = n.name;
      return typeof _ == "string" && _.length > 0 ? `Function(${_})` : "Function";
    }
    if (Array.isArray(n)) {
      const _ = n.length;
      let c = "[";
      _ > 0 && (c += C(n[0]));
      for (let o = 1; o < _; o++)
        c += ", " + C(n[o]);
      return c += "]", c;
    }
    const t = /\[object ([^\]]+)\]/.exec(toString.call(n));
    let r;
    if (t.length > 1)
      r = t[1];
    else
      return toString.call(n);
    if (r == "Object")
      try {
        return "Object(" + JSON.stringify(n) + ")";
      } catch {
        return "Object";
      }
    return n instanceof Error ? `${n.name}: ${n.message}
${n.stack}` : r;
  }
  const z = typeof FinalizationRegistry > "u" ? { register: () => {
  }, unregister: () => {
  } } : new FinalizationRegistry((n) => {
    b == null || b.__wbindgen_export_3.get(n.dtor)(n.a, n.b);
  });
  function x(n, e, t, r) {
    const _ = { a: n, b: e, cnt: 1, dtor: t }, c = (...o) => {
      _.cnt++;
      const a = _.a;
      _.a = 0;
      try {
        return r(a, _.b, ...o);
      } finally {
        --_.cnt === 0 ? (b.__wbindgen_export_3.get(_.dtor)(a, _.b), z.unregister(_)) : _.a = a;
      }
    };
    return c.original = _, z.register(c, _, _), c;
  }
  function M(n) {
    const e = b.__wbindgen_export_2.get(n);
    return b.__externref_table_dealloc(n), e;
  }
  function K(n, e, t) {
    try {
      const c = b.__wbindgen_add_to_stack_pointer(-16);
      b.closure157_externref_shim(c, n, e, t);
      var r = u()[c / 4 + 0], _ = u()[c / 4 + 1];
      if (_)
        throw M(r);
    } finally {
      b.__wbindgen_add_to_stack_pointer(16);
    }
  }
  function Q(n, e) {
    b.wasm_bindgen__convert__closures__invoke0_mut__h71277427381bcdff(n, e);
  }
  function N(n, e) {
    b._dyn_core__ops__function__FnMut_____Output___R_as_wasm_bindgen__closure__WasmClosure___describe__invoke__h481a4c2bb2473fc6(n, e);
  }
  function W(n, e, t) {
    b.closure5313_externref_shim(n, e, t);
  }
  function X(n, e) {
    try {
      const _ = b.__wbindgen_add_to_stack_pointer(-16);
      b.wasm_bindgen__convert__closures__invoke0_mut__h0a7a075e54c6df92(_, n, e);
      var t = u()[_ / 4 + 0], r = u()[_ / 4 + 1];
      if (r)
        throw M(t);
    } finally {
      b.__wbindgen_add_to_stack_pointer(16);
    }
  }
  function U(n, e, t) {
    b.closure8038_externref_shim(n, e, t);
  }
  function R(n, e, t) {
    b.closure11634_externref_shim(n, e, t);
  }
  function Y(n, e, t) {
    b.closure14103_externref_shim(n, e, t);
  }
  function $(n, e, t) {
    b.closure14828_externref_shim(n, e, t);
  }
  function Z(n, e, t) {
    b.closure14841_externref_shim(n, e, t);
  }
  function J(n, e) {
    const t = e(n.length * 1, 1) >>> 0;
    return F().set(n, t / 1), d = n.length, t;
  }
  I.set_email = function(n) {
    const e = m(n, b.__wbindgen_malloc, b.__wbindgen_realloc), t = d;
    b.set_email(e, t);
  };
  function s(n) {
    const e = b.__externref_table_alloc();
    return b.__wbindgen_export_2.set(e, n), e;
  }
  function f(n, e) {
    try {
      return n.apply(this, e);
    } catch (t) {
      const r = s(t);
      b.__wbindgen_exn_store(r);
    }
  }
  let D = null;
  function ee() {
    return (D === null || D.byteLength === 0) && (D = new Uint32Array(b.memory.buffer)), D;
  }
  function v(n, e) {
    return n = n >>> 0, ee().subarray(n / 4, n / 4 + e);
  }
  function V(n) {
    return () => {
      throw new Error(`${n} is not defined`);
    };
  }
  function B(n, e) {
    return n = n >>> 0, u().subarray(n / 4, n / 4 + e);
  }
  let k = null;
  function te() {
    return (k === null || k.byteLength === 0) && (k = new Float32Array(b.memory.buffer)), k;
  }
  function y(n, e) {
    return n = n >>> 0, te().subarray(n / 4, n / 4 + e);
  }
  function ne(n, e, t, r) {
    b.closure17225_externref_shim(n, e, t, r);
  }
  const re = typeof FinalizationRegistry > "u" ? { register: () => {
  }, unregister: () => {
  } } : new FinalizationRegistry((n) => b.__wbg_intounderlyingbytesource_free(n >>> 0));
  class _e {
    __destroy_into_raw() {
      const e = this.__wbg_ptr;
      return this.__wbg_ptr = 0, re.unregister(this), e;
    }
    free() {
      const e = this.__destroy_into_raw();
      b.__wbg_intounderlyingbytesource_free(e);
    }
    /**
    * @returns {string}
    */
    get type() {
      let e, t;
      try {
        const c = b.__wbindgen_add_to_stack_pointer(-16);
        b.intounderlyingbytesource_type(c, this.__wbg_ptr);
        var r = u()[c / 4 + 0], _ = u()[c / 4 + 1];
        return e = r, t = _, i(r, _);
      } finally {
        b.__wbindgen_add_to_stack_pointer(16), b.__wbindgen_free(e, t, 1);
      }
    }
    /**
    * @returns {number}
    */
    get autoAllocateChunkSize() {
      return b.intounderlyingbytesource_autoAllocateChunkSize(this.__wbg_ptr) >>> 0;
    }
    /**
    * @param {ReadableByteStreamController} controller
    */
    start(e) {
      b.intounderlyingbytesource_start(this.__wbg_ptr, e);
    }
    /**
    * @param {ReadableByteStreamController} controller
    * @returns {Promise<any>}
    */
    pull(e) {
      return b.intounderlyingbytesource_pull(this.__wbg_ptr, e);
    }
    /**
    */
    cancel() {
      const e = this.__destroy_into_raw();
      b.intounderlyingbytesource_cancel(e);
    }
  }
  I.IntoUnderlyingByteSource = _e;
  const ce = typeof FinalizationRegistry > "u" ? { register: () => {
  }, unregister: () => {
  } } : new FinalizationRegistry((n) => b.__wbg_intounderlyingsink_free(n >>> 0));
  class be {
    __destroy_into_raw() {
      const e = this.__wbg_ptr;
      return this.__wbg_ptr = 0, ce.unregister(this), e;
    }
    free() {
      const e = this.__destroy_into_raw();
      b.__wbg_intounderlyingsink_free(e);
    }
    /**
    * @param {any} chunk
    * @returns {Promise<any>}
    */
    write(e) {
      return b.intounderlyingsink_write(this.__wbg_ptr, e);
    }
    /**
    * @returns {Promise<any>}
    */
    close() {
      const e = this.__destroy_into_raw();
      return b.intounderlyingsink_close(e);
    }
    /**
    * @param {any} reason
    * @returns {Promise<any>}
    */
    abort(e) {
      const t = this.__destroy_into_raw();
      return b.intounderlyingsink_abort(t, e);
    }
  }
  I.IntoUnderlyingSink = be;
  const oe = typeof FinalizationRegistry > "u" ? { register: () => {
  }, unregister: () => {
  } } : new FinalizationRegistry((n) => b.__wbg_intounderlyingsource_free(n >>> 0));
  class fe {
    __destroy_into_raw() {
      const e = this.__wbg_ptr;
      return this.__wbg_ptr = 0, oe.unregister(this), e;
    }
    free() {
      const e = this.__destroy_into_raw();
      b.__wbg_intounderlyingsource_free(e);
    }
    /**
    * @param {ReadableStreamDefaultController} controller
    * @returns {Promise<any>}
    */
    pull(e) {
      return b.intounderlyingsource_pull(this.__wbg_ptr, e);
    }
    /**
    */
    cancel() {
      const e = this.__destroy_into_raw();
      b.intounderlyingsource_cancel(e);
    }
  }
  I.IntoUnderlyingSource = fe;
  const ae = typeof FinalizationRegistry > "u" ? { register: () => {
  }, unregister: () => {
  } } : new FinalizationRegistry((n) => b.__wbg_webhandle_free(n >>> 0));
  class ue {
    __destroy_into_raw() {
      const e = this.__wbg_ptr;
      return this.__wbg_ptr = 0, ae.unregister(this), e;
    }
    free() {
      const e = this.__destroy_into_raw();
      b.__wbg_webhandle_free(e);
    }
    /**
    * @param {any} app_options
    */
    constructor(e) {
      try {
        const c = b.__wbindgen_add_to_stack_pointer(-16);
        b.webhandle_new(c, e);
        var t = u()[c / 4 + 0], r = u()[c / 4 + 1], _ = u()[c / 4 + 2];
        if (_)
          throw M(r);
        return this.__wbg_ptr = t >>> 0, this;
      } finally {
        b.__wbindgen_add_to_stack_pointer(16);
      }
    }
    /**
    * - `url` is an optional URL to either an .rrd file over http, or a Rerun WebSocket server.
    * - `manifest_url` is an optional URL to an `examples_manifest.json` file over http.
    * - `force_wgpu_backend` is an optional string to force a specific backend, either `webgl` or `webgpu`.
    * @param {string} canvas_id
    * @returns {Promise<void>}
    */
    start(e) {
      const t = m(e, b.__wbindgen_malloc, b.__wbindgen_realloc), r = d;
      return b.webhandle_start(this.__wbg_ptr, t, r);
    }
    /**
    * @param {boolean | undefined} [value]
    */
    toggle_panel_overrides(e) {
      b.webhandle_toggle_panel_overrides(this.__wbg_ptr, g(e) ? 16777215 : e ? 1 : 0);
    }
    /**
    * @param {string} panel
    * @param {string | undefined} [state]
    */
    override_panel_state(e, t) {
      try {
        const a = b.__wbindgen_add_to_stack_pointer(-16), w = m(e, b.__wbindgen_malloc, b.__wbindgen_realloc), l = d;
        var r = g(t) ? 0 : m(t, b.__wbindgen_malloc, b.__wbindgen_realloc), _ = d;
        b.webhandle_override_panel_state(a, this.__wbg_ptr, w, l, r, _);
        var c = u()[a / 4 + 0], o = u()[a / 4 + 1];
        if (o)
          throw M(c);
      } finally {
        b.__wbindgen_add_to_stack_pointer(16);
      }
    }
    /**
    */
    destroy() {
      b.webhandle_destroy(this.__wbg_ptr);
    }
    /**
    * @returns {boolean}
    */
    has_panicked() {
      return b.webhandle_has_panicked(this.__wbg_ptr) !== 0;
    }
    /**
    * @returns {string | undefined}
    */
    panic_message() {
      try {
        const r = b.__wbindgen_add_to_stack_pointer(-16);
        b.webhandle_panic_message(r, this.__wbg_ptr);
        var e = u()[r / 4 + 0], t = u()[r / 4 + 1];
        let _;
        return e !== 0 && (_ = i(e, t).slice(), b.__wbindgen_free(e, t * 1, 1)), _;
      } finally {
        b.__wbindgen_add_to_stack_pointer(16);
      }
    }
    /**
    * @returns {string | undefined}
    */
    panic_callstack() {
      try {
        const r = b.__wbindgen_add_to_stack_pointer(-16);
        b.webhandle_panic_callstack(r, this.__wbg_ptr);
        var e = u()[r / 4 + 0], t = u()[r / 4 + 1];
        let _;
        return e !== 0 && (_ = i(e, t).slice(), b.__wbindgen_free(e, t * 1, 1)), _;
      } finally {
        b.__wbindgen_add_to_stack_pointer(16);
      }
    }
    /**
    * Add a new receiver streaming data from the given url.
    *
    * If `follow_if_http` is `true`, and the url is an HTTP source, the viewer will open the stream
    * in `Following` mode rather than `Playing` mode.
    *
    * Websocket streams are always opened in `Following` mode.
    *
    * It is an error to open a channel twice with the same id.
    * @param {string} url
    * @param {boolean | undefined} [follow_if_http]
    */
    add_receiver(e, t) {
      const r = m(e, b.__wbindgen_malloc, b.__wbindgen_realloc), _ = d;
      b.webhandle_add_receiver(this.__wbg_ptr, r, _, g(t) ? 16777215 : t ? 1 : 0);
    }
    /**
    * @param {string} url
    */
    remove_receiver(e) {
      const t = m(e, b.__wbindgen_malloc, b.__wbindgen_realloc), r = d;
      b.webhandle_remove_receiver(this.__wbg_ptr, t, r);
    }
    /**
    * Open a new channel for streaming data.
    *
    * It is an error to open a channel twice with the same id.
    * @param {string} id
    * @param {string} channel_name
    */
    open_channel(e, t) {
      const r = m(e, b.__wbindgen_malloc, b.__wbindgen_realloc), _ = d, c = m(t, b.__wbindgen_malloc, b.__wbindgen_realloc), o = d;
      b.webhandle_open_channel(this.__wbg_ptr, r, _, c, o);
    }
    /**
    * Close an existing channel for streaming data.
    *
    * No-op if the channel is already closed.
    * @param {string} id
    */
    close_channel(e) {
      const t = m(e, b.__wbindgen_malloc, b.__wbindgen_realloc), r = d;
      b.webhandle_close_channel(this.__wbg_ptr, t, r);
    }
    /**
    * Add an rrd to the viewer directly from a byte array.
    * @param {string} id
    * @param {Uint8Array} data
    */
    send_rrd_to_channel(e, t) {
      const r = m(e, b.__wbindgen_malloc, b.__wbindgen_realloc), _ = d, c = J(t, b.__wbindgen_malloc), o = d;
      b.webhandle_send_rrd_to_channel(this.__wbg_ptr, r, _, c, o);
    }
  }
  I.WebHandle = ue;
  async function ie(n, e) {
    if (typeof Response == "function" && n instanceof Response) {
      if (typeof WebAssembly.instantiateStreaming == "function")
        try {
          return await WebAssembly.instantiateStreaming(n, e);
        } catch (r) {
          if (n.headers.get("Content-Type") != "application/wasm")
            console.warn("`WebAssembly.instantiateStreaming` failed because your server does not serve wasm with `application/wasm` MIME type. Falling back to `WebAssembly.instantiate` which is slower. Original error:\n", r);
          else
            throw r;
        }
      const t = await n.arrayBuffer();
      return await WebAssembly.instantiate(t, e);
    } else {
      const t = await WebAssembly.instantiate(n, e);
      return t instanceof WebAssembly.Instance ? { instance: t, module: n } : t;
    }
  }
  function G() {
    const n = {};
    return n.wbg = {}, n.wbg.__wbindgen_string_get = function(e, t) {
      const r = t, _ = typeof r == "string" ? r : void 0;
      var c = g(_) ? 0 : m(_, b.__wbindgen_malloc, b.__wbindgen_realloc), o = d;
      u()[e / 4 + 1] = o, u()[e / 4 + 0] = c;
    }, n.wbg.__wbindgen_is_function = function(e) {
      return typeof e == "function";
    }, n.wbg.__wbindgen_boolean_get = function(e) {
      const t = e;
      return typeof t == "boolean" ? t ? 1 : 0 : 2;
    }, n.wbg.__wbindgen_is_falsy = function(e) {
      return !e;
    }, n.wbg.__wbindgen_cb_drop = function(e) {
      const t = e.original;
      return t.cnt-- == 1 ? (t.a = 0, !0) : !1;
    }, n.wbg.__wbindgen_error_new = function(e, t) {
      return new Error(i(e, t));
    }, n.wbg.__wbindgen_is_object = function(e) {
      const t = e;
      return typeof t == "object" && t !== null;
    }, n.wbg.__wbindgen_is_undefined = function(e) {
      return e === void 0;
    }, n.wbg.__wbindgen_in = function(e, t) {
      return e in t;
    }, n.wbg.__wbindgen_is_string = function(e) {
      return typeof e == "string";
    }, n.wbg.__wbindgen_number_new = function(e) {
      return e;
    }, n.wbg.__wbindgen_is_null = function(e) {
      return e === null;
    }, n.wbg.__wbg_structuredClone_cb6b360867481795 = function() {
      return f(function(e) {
        return window.structuredClone(e);
      }, arguments);
    }, n.wbg.__wbindgen_string_new = function(e, t) {
      return i(e, t);
    }, n.wbg.__wbindgen_jsval_loose_eq = function(e, t) {
      return e == t;
    }, n.wbg.__wbindgen_number_get = function(e, t) {
      const r = t, _ = typeof r == "number" ? r : void 0;
      H()[e / 8 + 1] = g(_) ? 0 : _, u()[e / 4 + 0] = !g(_);
    }, n.wbg.__wbindgen_as_number = function(e) {
      return +e;
    }, n.wbg.__wbg_getwithrefkey_edc2c8960f0f1191 = function(e, t) {
      return e[t];
    }, n.wbg.__wbg_set_f975102236d3c502 = function(e, t, r) {
      e[t] = r;
    }, n.wbg.__wbg_error_d2d279fddc1936c2 = function(e, t) {
      let r, _;
      try {
        r = e, _ = t, console.error(i(e, t));
      } finally {
        b.__wbindgen_free(r, _, 1);
      }
    }, n.wbg.__wbg_new_a337b459b99ce6cf = function() {
      return new Error();
    }, n.wbg.__wbg_stack_3cb0faed69ec1c1c = function(e, t) {
      const r = t.stack, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_new_8227756754f09e14 = function() {
      return new Error();
    }, n.wbg.__wbg_stack_c25c38c424629cce = function(e, t) {
      const r = t.stack, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_getPreferredCanvasFormat_012ef9f3b0238ffa = function(e) {
      return e.getPreferredCanvasFormat();
    }, n.wbg.__wbg_requestAdapter_e6f12701c7a38391 = function(e, t) {
      return e.requestAdapter(t);
    }, n.wbg.__wbg_features_4991b2a28904a253 = function(e) {
      return e.features;
    }, n.wbg.__wbg_limits_1aa8a49e0a8442cc = function(e) {
      return e.limits;
    }, n.wbg.__wbg_queue_2bddd1700cb0bec2 = function(e) {
      return e.queue;
    }, n.wbg.__wbg_lost_42410660a8cd8819 = function(e) {
      return e.lost;
    }, n.wbg.__wbg_setonuncapturederror_4e4946a65c61f3ef = function(e, t) {
      e.onuncapturederror = t;
    }, n.wbg.__wbg_createBindGroup_2d6778f92445c8bf = function(e, t) {
      return e.createBindGroup(t);
    }, n.wbg.__wbg_createBindGroupLayout_313b4151e718ff1f = function(e, t) {
      return e.createBindGroupLayout(t);
    }, n.wbg.__wbg_createBuffer_65c2fc555c46aa07 = function(e, t) {
      return e.createBuffer(t);
    }, n.wbg.__wbg_createCommandEncoder_1db1770ea9eab9af = function(e, t) {
      return e.createCommandEncoder(t);
    }, n.wbg.__wbg_createComputePipeline_02674342979c6288 = function(e, t) {
      return e.createComputePipeline(t);
    }, n.wbg.__wbg_createPipelineLayout_9134c6c32c505ec8 = function(e, t) {
      return e.createPipelineLayout(t);
    }, n.wbg.__wbg_createQuerySet_424dbf8130140914 = function(e, t) {
      return e.createQuerySet(t);
    }, n.wbg.__wbg_createRenderBundleEncoder_32896e68340fabc6 = function(e, t) {
      return e.createRenderBundleEncoder(t);
    }, n.wbg.__wbg_createRenderPipeline_2bfc852ce09914fc = function(e, t) {
      return e.createRenderPipeline(t);
    }, n.wbg.__wbg_createSampler_942022241ecf4277 = function(e, t) {
      return e.createSampler(t);
    }, n.wbg.__wbg_createShaderModule_036b780a18124d9e = function(e, t) {
      return e.createShaderModule(t);
    }, n.wbg.__wbg_createTexture_5adbcf0db3fd41b4 = function(e, t) {
      return e.createTexture(t);
    }, n.wbg.__wbg_destroy_4f7ed2bbb4742899 = function(e) {
      e.destroy();
    }, n.wbg.__wbg_popErrorScope_f8f0d4b6d5c635f9 = function(e) {
      return e.popErrorScope();
    }, n.wbg.__wbg_pushErrorScope_a09c8b037ab27e15 = function(e, t) {
      e.pushErrorScope(t);
    }, n.wbg.__wbg_instanceof_GpuDeviceLostInfo_22f963b61044b3b1 = function(e) {
      let t;
      try {
        t = e instanceof GPUDeviceLostInfo;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_instanceof_GpuAdapter_32bc80c8c30adaa0 = function(e) {
      let t;
      try {
        t = e instanceof GPUAdapter;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_getBindGroupLayout_a0d36a72bd39bb04 = function(e, t) {
      return e.getBindGroupLayout(t >>> 0);
    }, n.wbg.__wbg_createView_0ab0576f1665c9ad = function(e, t) {
      return e.createView(t);
    }, n.wbg.__wbg_destroy_57694ff5aabbf32d = function(e) {
      e.destroy();
    }, n.wbg.__wbg_instanceof_GpuOutOfMemoryError_3621d9e8ec05691e = function(e) {
      let t;
      try {
        t = e instanceof GPUOutOfMemoryError;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_instanceof_GpuValidationError_776dc042f9752ecb = function(e) {
      let t;
      try {
        t = e instanceof GPUValidationError;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_instanceof_GpuCanvasContext_b3bff0de75efe6fd = function(e) {
      let t;
      try {
        t = e instanceof GPUCanvasContext;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_gpu_1f3675e2d4aa88f4 = function(e) {
      return e.gpu;
    }, n.wbg.__wbg_message_e73620d927b54373 = function(e, t) {
      const r = t.message, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_getBindGroupLayout_abc654a192f85d5e = function(e, t) {
      return e.getBindGroupLayout(t >>> 0);
    }, n.wbg.__wbg_has_1509b2ce6759dc2a = function(e, t, r) {
      return e.has(i(t, r));
    }, n.wbg.__wbg_error_c4453561fa6c2209 = function(e) {
      return e.error;
    }, n.wbg.__wbg_reason_3af8e4afbe0efdd8 = function(e) {
      return e.reason;
    }, n.wbg.__wbg_message_3bef8c43f84eab9c = function(e, t) {
      const r = t.message, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_maxTextureDimension1D_ea59b0f0cc2e29cd = function(e) {
      return e.maxTextureDimension1D;
    }, n.wbg.__wbg_maxTextureDimension2D_00984ba245729ced = function(e) {
      return e.maxTextureDimension2D;
    }, n.wbg.__wbg_maxTextureDimension3D_95c3d3adb6d66ec5 = function(e) {
      return e.maxTextureDimension3D;
    }, n.wbg.__wbg_maxTextureArrayLayers_68f4a1218a54fa93 = function(e) {
      return e.maxTextureArrayLayers;
    }, n.wbg.__wbg_maxBindGroups_e76fb8650a4459d7 = function(e) {
      return e.maxBindGroups;
    }, n.wbg.__wbg_maxBindingsPerBindGroup_2af20f39aef3fd86 = function(e) {
      return e.maxBindingsPerBindGroup;
    }, n.wbg.__wbg_maxDynamicUniformBuffersPerPipelineLayout_074c891075b375b7 = function(e) {
      return e.maxDynamicUniformBuffersPerPipelineLayout;
    }, n.wbg.__wbg_maxDynamicStorageBuffersPerPipelineLayout_b91e3e6efb7b7a8c = function(e) {
      return e.maxDynamicStorageBuffersPerPipelineLayout;
    }, n.wbg.__wbg_maxSampledTexturesPerShaderStage_76354979d03a2b27 = function(e) {
      return e.maxSampledTexturesPerShaderStage;
    }, n.wbg.__wbg_maxSamplersPerShaderStage_fe8d223de90e5459 = function(e) {
      return e.maxSamplersPerShaderStage;
    }, n.wbg.__wbg_maxStorageBuffersPerShaderStage_bced69629145d26d = function(e) {
      return e.maxStorageBuffersPerShaderStage;
    }, n.wbg.__wbg_maxStorageTexturesPerShaderStage_fcf51f22620c0092 = function(e) {
      return e.maxStorageTexturesPerShaderStage;
    }, n.wbg.__wbg_maxUniformBuffersPerShaderStage_b3b013238400f0c0 = function(e) {
      return e.maxUniformBuffersPerShaderStage;
    }, n.wbg.__wbg_maxUniformBufferBindingSize_194fd7147cf2e95a = function(e) {
      return e.maxUniformBufferBindingSize;
    }, n.wbg.__wbg_maxStorageBufferBindingSize_78504383af63ac53 = function(e) {
      return e.maxStorageBufferBindingSize;
    }, n.wbg.__wbg_maxVertexBuffers_78c71ff19beac74b = function(e) {
      return e.maxVertexBuffers;
    }, n.wbg.__wbg_maxBufferSize_0c7ed57407582d40 = function(e) {
      return e.maxBufferSize;
    }, n.wbg.__wbg_maxVertexAttributes_c11cb018a9c5a224 = function(e) {
      return e.maxVertexAttributes;
    }, n.wbg.__wbg_maxVertexBufferArrayStride_c53560cc036cb477 = function(e) {
      return e.maxVertexBufferArrayStride;
    }, n.wbg.__wbg_minUniformBufferOffsetAlignment_4880e6786cb7ec5d = function(e) {
      return e.minUniformBufferOffsetAlignment;
    }, n.wbg.__wbg_minStorageBufferOffsetAlignment_9913f200aee2c749 = function(e) {
      return e.minStorageBufferOffsetAlignment;
    }, n.wbg.__wbg_maxInterStageShaderComponents_f9243ac86242eb18 = function(e) {
      return e.maxInterStageShaderComponents;
    }, n.wbg.__wbg_maxColorAttachments_d33b1d22c06a6fc5 = function(e) {
      return e.maxColorAttachments;
    }, n.wbg.__wbg_maxColorAttachmentBytesPerSample_637fd3ac394c14ee = function(e) {
      return e.maxColorAttachmentBytesPerSample;
    }, n.wbg.__wbg_maxComputeWorkgroupStorageSize_7e5bc378e5a62367 = function(e) {
      return e.maxComputeWorkgroupStorageSize;
    }, n.wbg.__wbg_maxComputeInvocationsPerWorkgroup_1ed5b24d52720f8a = function(e) {
      return e.maxComputeInvocationsPerWorkgroup;
    }, n.wbg.__wbg_maxComputeWorkgroupSizeX_56b713fb17f8c261 = function(e) {
      return e.maxComputeWorkgroupSizeX;
    }, n.wbg.__wbg_maxComputeWorkgroupSizeY_13040bdf12fd4e65 = function(e) {
      return e.maxComputeWorkgroupSizeY;
    }, n.wbg.__wbg_maxComputeWorkgroupSizeZ_8c8594730967472d = function(e) {
      return e.maxComputeWorkgroupSizeZ;
    }, n.wbg.__wbg_maxComputeWorkgroupsPerDimension_4094c8501eea36ce = function(e) {
      return e.maxComputeWorkgroupsPerDimension;
    }, n.wbg.__wbg_getMappedRange_1216b00d6d7803de = function(e, t, r) {
      return e.getMappedRange(t, r);
    }, n.wbg.__wbg_Window_94d759f1f207a15b = function(e) {
      return e.Window;
    }, n.wbg.__wbg_WorkerGlobalScope_b13c8cef62388de9 = function(e) {
      return e.WorkerGlobalScope;
    }, n.wbg.__wbg_requestDevice_727ad8687b0d6553 = function(e, t) {
      return e.requestDevice(t);
    }, n.wbg.__wbg_features_b56ebab8f515839e = function(e) {
      return e.features;
    }, n.wbg.__wbg_limits_be2f592b5e154a3d = function(e) {
      return e.limits;
    }, n.wbg.__wbg_configure_6cde48f0c99a3497 = function(e, t) {
      e.configure(t);
    }, n.wbg.__wbg_getCurrentTexture_95b5b88416fdb0c2 = function(e) {
      return e.getCurrentTexture();
    }, n.wbg.__wbg_mapAsync_3b0a03a892fb22b3 = function(e, t, r, _) {
      return e.mapAsync(t >>> 0, r, _);
    }, n.wbg.__wbg_unmap_7a0dddee82ac6ed3 = function(e) {
      e.unmap();
    }, n.wbg.__wbg_destroy_199808599201ee27 = function(e) {
      e.destroy();
    }, n.wbg.__wbg_copyBufferToBuffer_667953bc6dccb6b4 = function(e, t, r, _, c, o) {
      e.copyBufferToBuffer(t, r, _, c, o);
    }, n.wbg.__wbg_copyBufferToTexture_ca5b298687bed60a = function(e, t, r, _) {
      e.copyBufferToTexture(t, r, _);
    }, n.wbg.__wbg_copyTextureToBuffer_cdf8118386295eb4 = function(e, t, r, _) {
      e.copyTextureToBuffer(t, r, _);
    }, n.wbg.__wbg_copyTextureToTexture_67678f03fd20bd23 = function(e, t, r, _) {
      e.copyTextureToTexture(t, r, _);
    }, n.wbg.__wbg_beginComputePass_a148b983810f6795 = function(e, t) {
      return e.beginComputePass(t);
    }, n.wbg.__wbg_end_28d311f5d435aa6d = function(e) {
      e.end();
    }, n.wbg.__wbg_beginRenderPass_0b83360fd99b5810 = function(e, t) {
      return e.beginRenderPass(t);
    }, n.wbg.__wbg_end_e3cea1776c95d64f = function(e) {
      e.end();
    }, n.wbg.__wbg_label_175c4f59b3eca611 = function(e, t) {
      const r = t.label, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_finish_d1d9eb9915c96a79 = function(e, t) {
      return e.finish(t);
    }, n.wbg.__wbg_finish_ce7d5c15fce975aa = function(e) {
      return e.finish();
    }, n.wbg.__wbg_clearBuffer_2cc723ab6b818737 = function(e, t, r) {
      e.clearBuffer(t, r);
    }, n.wbg.__wbg_clearBuffer_78a94a2eda97eb5a = function(e, t, r, _) {
      e.clearBuffer(t, r, _);
    }, n.wbg.__wbg_resolveQuerySet_22e31015a36a09d5 = function(e, t, r, _, c, o) {
      e.resolveQuerySet(t, r >>> 0, _ >>> 0, c, o >>> 0);
    }, n.wbg.__wbg_finish_2115db9e679c5aae = function(e) {
      return e.finish();
    }, n.wbg.__wbg_finish_4a754149a60eddc0 = function(e, t) {
      return e.finish(t);
    }, n.wbg.__wbg_writeBuffer_4245ce84e6d772c9 = function(e, t, r, _, c, o) {
      e.writeBuffer(t, r, _, c, o);
    }, n.wbg.__wbg_usage_5e9a3548afbc3ebb = function(e) {
      return e.usage;
    }, n.wbg.__wbg_size_fc880d60ff425a47 = function(e) {
      return e.size;
    }, n.wbg.__wbg_writeTexture_686a8160c3c5ddbb = function(e, t, r, _, c) {
      e.writeTexture(t, r, _, c);
    }, n.wbg.__wbg_copyExternalImageToTexture_87bdcc3260c6efba = function(e, t, r, _) {
      e.copyExternalImageToTexture(t, r, _);
    }, n.wbg.__wbg_setPipeline_8630b264a9c4ec4b = function(e, t) {
      e.setPipeline(t);
    }, n.wbg.__wbg_setBindGroup_17e73587d3c1be08 = function(e, t, r) {
      e.setBindGroup(t >>> 0, r);
    }, n.wbg.__wbg_setBindGroup_5a450a0e97199c15 = function(e, t, r, _, c, o, a) {
      e.setBindGroup(t >>> 0, r, v(_, c), o, a >>> 0);
    }, n.wbg.__wbg_dispatchWorkgroups_4bc133944e89d5e0 = function(e, t, r, _) {
      e.dispatchWorkgroups(t >>> 0, r >>> 0, _ >>> 0);
    }, n.wbg.__wbg_dispatchWorkgroupsIndirect_8050acb60dd74a34 = function(e, t, r) {
      e.dispatchWorkgroupsIndirect(t, r);
    }, n.wbg.__wbg_setPipeline_a95b89d99620ba34 = function(e, t) {
      e.setPipeline(t);
    }, n.wbg.__wbg_setBindGroup_58e27d4cd266f187 = function(e, t, r) {
      e.setBindGroup(t >>> 0, r);
    }, n.wbg.__wbg_setBindGroup_f70bb0d0a5ace56d = function(e, t, r, _, c, o, a) {
      e.setBindGroup(t >>> 0, r, v(_, c), o, a >>> 0);
    }, n.wbg.__wbg_setIndexBuffer_747e1ba3f58d7227 = function(e, t, r, _) {
      e.setIndexBuffer(t, r, _);
    }, n.wbg.__wbg_setIndexBuffer_3f1635c89f72d661 = function(e, t, r, _, c) {
      e.setIndexBuffer(t, r, _, c);
    }, n.wbg.__wbg_setVertexBuffer_94a88edbfb4b07f8 = function(e, t, r, _) {
      e.setVertexBuffer(t >>> 0, r, _);
    }, n.wbg.__wbg_setVertexBuffer_407067a9522118df = function(e, t, r, _, c) {
      e.setVertexBuffer(t >>> 0, r, _, c);
    }, n.wbg.__wbg_draw_60508d893ce4e012 = function(e, t, r, _, c) {
      e.draw(t >>> 0, r >>> 0, _ >>> 0, c >>> 0);
    }, n.wbg.__wbg_drawIndexed_d5c5dff02437a4f0 = function(e, t, r, _, c, o) {
      e.drawIndexed(t >>> 0, r >>> 0, _ >>> 0, c, o >>> 0);
    }, n.wbg.__wbg_drawIndirect_54f93ae4ccc85358 = function(e, t, r) {
      e.drawIndirect(t, r);
    }, n.wbg.__wbg_drawIndexedIndirect_bf668464170261b3 = function(e, t, r) {
      e.drawIndexedIndirect(t, r);
    }, n.wbg.__wbg_setPipeline_d7c9c55035f118a6 = function(e, t) {
      e.setPipeline(t);
    }, n.wbg.__wbg_setBindGroup_c6ab2e9583489b58 = function(e, t, r) {
      e.setBindGroup(t >>> 0, r);
    }, n.wbg.__wbg_setBindGroup_0bf976b9657f99bd = function(e, t, r, _, c, o, a) {
      e.setBindGroup(t >>> 0, r, v(_, c), o, a >>> 0);
    }, n.wbg.__wbg_setIndexBuffer_ea39707d8842fe03 = function(e, t, r, _) {
      e.setIndexBuffer(t, r, _);
    }, n.wbg.__wbg_setIndexBuffer_04ba4ea48c8f80be = function(e, t, r, _, c) {
      e.setIndexBuffer(t, r, _, c);
    }, n.wbg.__wbg_setVertexBuffer_907c60acf6dca161 = function(e, t, r, _) {
      e.setVertexBuffer(t >>> 0, r, _);
    }, n.wbg.__wbg_setVertexBuffer_9a336bb112a33317 = function(e, t, r, _, c) {
      e.setVertexBuffer(t >>> 0, r, _, c);
    }, n.wbg.__wbg_draw_540a514f996a5d0d = function(e, t, r, _, c) {
      e.draw(t >>> 0, r >>> 0, _ >>> 0, c >>> 0);
    }, n.wbg.__wbg_drawIndexed_f717a07602ee2d18 = function(e, t, r, _, c, o) {
      e.drawIndexed(t >>> 0, r >>> 0, _ >>> 0, c, o >>> 0);
    }, n.wbg.__wbg_drawIndirect_c588ff54fb149aee = function(e, t, r) {
      e.drawIndirect(t, r);
    }, n.wbg.__wbg_drawIndexedIndirect_bb5585ec7f45d269 = function(e, t, r) {
      e.drawIndexedIndirect(t, r);
    }, n.wbg.__wbg_setBlendConstant_496a0b5cc772c236 = function(e, t) {
      e.setBlendConstant(t);
    }, n.wbg.__wbg_setScissorRect_9b7e673d03036c37 = function(e, t, r, _, c) {
      e.setScissorRect(t >>> 0, r >>> 0, _ >>> 0, c >>> 0);
    }, n.wbg.__wbg_setViewport_85d18ceefd5180eb = function(e, t, r, _, c, o, a) {
      e.setViewport(t, r, _, c, o, a);
    }, n.wbg.__wbg_setStencilReference_b4b1f7e586967a4d = function(e, t) {
      e.setStencilReference(t >>> 0);
    }, n.wbg.__wbg_executeBundles_16985086317c358a = function(e, t) {
      e.executeBundles(t);
    }, n.wbg.__wbg_submit_afbd82b0d5056194 = function(e, t) {
      e.submit(t);
    }, n.wbg.__wbg_getReader_ab94afcb5cb7689a = function() {
      return f(function(e) {
        return e.getReader();
      }, arguments);
    }, n.wbg.__wbg_done_2ffa852272310e47 = function(e) {
      return e.done;
    }, n.wbg.__wbg_value_9f6eeb1e2aab8d96 = function(e) {
      return e.value;
    }, n.wbg.__wbg_queueMicrotask_481971b0d87f3dd4 = typeof queueMicrotask == "function" ? queueMicrotask : V("queueMicrotask"), n.wbg.__wbg_queueMicrotask_3cbae2ec6b6cd3d6 = function(e) {
      return e.queueMicrotask;
    }, n.wbg.__wbg_instanceof_Window_f401953a2cf86220 = function(e) {
      let t;
      try {
        t = e instanceof Window;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_document_5100775d18896c16 = function(e) {
      const t = e.document;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_location_2951b5ee34f19221 = function(e) {
      return e.location;
    }, n.wbg.__wbg_history_bc4057de66a2015f = function() {
      return f(function(e) {
        return e.history;
      }, arguments);
    }, n.wbg.__wbg_navigator_6c8fa55c5cc8796e = function(e) {
      return e.navigator;
    }, n.wbg.__wbg_devicePixelRatio_efc553b59506f64c = function(e) {
      return e.devicePixelRatio;
    }, n.wbg.__wbg_localStorage_e381d34d0c40c761 = function() {
      return f(function(e) {
        const t = e.localStorage;
        return g(t) ? 0 : s(t);
      }, arguments);
    }, n.wbg.__wbg_performance_3298a9628a5c8aa4 = function(e) {
      const t = e.performance;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_isSecureContext_3dd59a5324a1c6d5 = function(e) {
      return e.isSecureContext;
    }, n.wbg.__wbg_getComputedStyle_078292ffe423aded = function() {
      return f(function(e, t) {
        const r = e.getComputedStyle(t);
        return g(r) ? 0 : s(r);
      }, arguments);
    }, n.wbg.__wbg_matchMedia_66bb21e3ef19270c = function() {
      return f(function(e, t, r) {
        const _ = e.matchMedia(i(t, r));
        return g(_) ? 0 : s(_);
      }, arguments);
    }, n.wbg.__wbg_open_cc82b8aaf0c296c1 = function() {
      return f(function(e, t, r, _, c) {
        const o = e.open(i(t, r), i(_, c));
        return g(o) ? 0 : s(o);
      }, arguments);
    }, n.wbg.__wbg_cancelAnimationFrame_111532f326e480af = function() {
      return f(function(e, t) {
        e.cancelAnimationFrame(t);
      }, arguments);
    }, n.wbg.__wbg_requestAnimationFrame_549258cfa66011f0 = function() {
      return f(function(e, t) {
        return e.requestAnimationFrame(t);
      }, arguments);
    }, n.wbg.__wbg_clearInterval_4368213fd2b325b0 = function(e, t) {
      e.clearInterval(t);
    }, n.wbg.__wbg_fetch_c4b6afebdb1f918e = function(e, t) {
      return e.fetch(t);
    }, n.wbg.__wbg_setTimeout_c172d5704ef82276 = function() {
      return f(function(e, t, r) {
        return e.setTimeout(t, r);
      }, arguments);
    }, n.wbg.__wbg_instanceof_WebGl2RenderingContext_6b8f92d566ced9e1 = function(e) {
      let t;
      try {
        t = e instanceof WebGL2RenderingContext;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_beginQuery_3d6bb95151ccc499 = function(e, t, r) {
      e.beginQuery(t >>> 0, r);
    }, n.wbg.__wbg_bindBufferRange_e7b7d4cd65a6f94d = function(e, t, r, _, c, o) {
      e.bindBufferRange(t >>> 0, r >>> 0, _, c, o);
    }, n.wbg.__wbg_bindSampler_065f0bdf49888ff1 = function(e, t, r) {
      e.bindSampler(t >>> 0, r);
    }, n.wbg.__wbg_bindVertexArray_239574d42dbbd203 = function(e, t) {
      e.bindVertexArray(t);
    }, n.wbg.__wbg_blitFramebuffer_4d77c70dcb183e0c = function(e, t, r, _, c, o, a, w, l, p, h) {
      e.blitFramebuffer(t, r, _, c, o, a, w, l, p >>> 0, h >>> 0);
    }, n.wbg.__wbg_bufferData_194f0914aaada840 = function(e, t, r, _) {
      e.bufferData(t >>> 0, r, _ >>> 0);
    }, n.wbg.__wbg_bufferData_c787516945ba48c2 = function(e, t, r, _) {
      e.bufferData(t >>> 0, r, _ >>> 0);
    }, n.wbg.__wbg_bufferSubData_7f5ddd4fdc628963 = function(e, t, r, _) {
      e.bufferSubData(t >>> 0, r, _);
    }, n.wbg.__wbg_clearBufferiv_519fe97abe38622e = function(e, t, r, _, c) {
      e.clearBufferiv(t >>> 0, r, B(_, c));
    }, n.wbg.__wbg_clearBufferuiv_1ae6df4bc96ffe37 = function(e, t, r, _, c) {
      e.clearBufferuiv(t >>> 0, r, v(_, c));
    }, n.wbg.__wbg_clientWaitSync_8f9f625ae9a42de6 = function(e, t, r, _) {
      return e.clientWaitSync(t, r >>> 0, _ >>> 0);
    }, n.wbg.__wbg_compressedTexSubImage2D_f77856eab95e8671 = function(e, t, r, _, c, o, a, w, l, p) {
      e.compressedTexSubImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l, p);
    }, n.wbg.__wbg_compressedTexSubImage2D_87d89d4b3f413805 = function(e, t, r, _, c, o, a, w, l) {
      e.compressedTexSubImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l);
    }, n.wbg.__wbg_compressedTexSubImage3D_b69e67d3cd62b756 = function(e, t, r, _, c, o, a, w, l, p, h, S) {
      e.compressedTexSubImage3D(t >>> 0, r, _, c, o, a, w, l, p >>> 0, h, S);
    }, n.wbg.__wbg_compressedTexSubImage3D_ff8eceb18a7ea2d6 = function(e, t, r, _, c, o, a, w, l, p, h) {
      e.compressedTexSubImage3D(t >>> 0, r, _, c, o, a, w, l, p >>> 0, h);
    }, n.wbg.__wbg_copyBufferSubData_db2c040cc06be689 = function(e, t, r, _, c, o) {
      e.copyBufferSubData(t >>> 0, r >>> 0, _, c, o);
    }, n.wbg.__wbg_copyTexSubImage3D_0a3f60d0ee6409c7 = function(e, t, r, _, c, o, a, w, l, p) {
      e.copyTexSubImage3D(t >>> 0, r, _, c, o, a, w, l, p);
    }, n.wbg.__wbg_createQuery_576d391ec549ed5e = function(e) {
      const t = e.createQuery();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createSampler_49de055e495fedf8 = function(e) {
      const t = e.createSampler();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createVertexArray_4f450ed4d4a69acf = function(e) {
      const t = e.createVertexArray();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_deleteQuery_9aaca8e15da5bc9c = function(e, t) {
      e.deleteQuery(t);
    }, n.wbg.__wbg_deleteSampler_93e35dc696f633c9 = function(e, t) {
      e.deleteSampler(t);
    }, n.wbg.__wbg_deleteSync_80326e1fc23a1016 = function(e, t) {
      e.deleteSync(t);
    }, n.wbg.__wbg_deleteVertexArray_67635c7fe59aa660 = function(e, t) {
      e.deleteVertexArray(t);
    }, n.wbg.__wbg_drawArraysInstanced_3f02ae8708f8c4c7 = function(e, t, r, _, c) {
      e.drawArraysInstanced(t >>> 0, r, _, c);
    }, n.wbg.__wbg_drawBuffers_6d32a0c370b9cb7f = function(e, t) {
      e.drawBuffers(t);
    }, n.wbg.__wbg_drawElementsInstanced_981861e70f6f9991 = function(e, t, r, _, c, o) {
      e.drawElementsInstanced(t >>> 0, r, _ >>> 0, c, o);
    }, n.wbg.__wbg_endQuery_f256667aaa2e9fac = function(e, t) {
      e.endQuery(t >>> 0);
    }, n.wbg.__wbg_fenceSync_f9c8da648fd4e444 = function(e, t, r) {
      const _ = e.fenceSync(t >>> 0, r >>> 0);
      return g(_) ? 0 : s(_);
    }, n.wbg.__wbg_framebufferTextureLayer_45cb5a2978de4939 = function(e, t, r, _, c, o) {
      e.framebufferTextureLayer(t >>> 0, r >>> 0, _, c, o);
    }, n.wbg.__wbg_getBufferSubData_7f31bd9ec3682832 = function(e, t, r, _) {
      e.getBufferSubData(t >>> 0, r, _);
    }, n.wbg.__wbg_getIndexedParameter_ad00bfb1210dbb28 = function() {
      return f(function(e, t, r) {
        return e.getIndexedParameter(t >>> 0, r >>> 0);
      }, arguments);
    }, n.wbg.__wbg_getQueryParameter_ea4da47c69182e79 = function(e, t, r) {
      return e.getQueryParameter(t, r >>> 0);
    }, n.wbg.__wbg_getSyncParameter_295178259afc15d8 = function(e, t, r) {
      return e.getSyncParameter(t, r >>> 0);
    }, n.wbg.__wbg_getUniformBlockIndex_091bee5be624ff21 = function(e, t, r, _) {
      return e.getUniformBlockIndex(t, i(r, _));
    }, n.wbg.__wbg_invalidateFramebuffer_99c0131e9e958f49 = function() {
      return f(function(e, t, r) {
        e.invalidateFramebuffer(t >>> 0, r);
      }, arguments);
    }, n.wbg.__wbg_readBuffer_c02ab6ce6d95c99b = function(e, t) {
      e.readBuffer(t >>> 0);
    }, n.wbg.__wbg_readPixels_40ba392d7aaf6ac0 = function() {
      return f(function(e, t, r, _, c, o, a, w) {
        e.readPixels(t, r, _, c, o >>> 0, a >>> 0, w);
      }, arguments);
    }, n.wbg.__wbg_readPixels_db02ea1a888b611a = function() {
      return f(function(e, t, r, _, c, o, a, w) {
        e.readPixels(t, r, _, c, o >>> 0, a >>> 0, w);
      }, arguments);
    }, n.wbg.__wbg_renderbufferStorageMultisample_37c0b1b9e8a4f342 = function(e, t, r, _, c, o) {
      e.renderbufferStorageMultisample(t >>> 0, r, _ >>> 0, c, o);
    }, n.wbg.__wbg_samplerParameterf_f60306a8facede3e = function(e, t, r, _) {
      e.samplerParameterf(t, r >>> 0, _);
    }, n.wbg.__wbg_samplerParameteri_da5225ffbb653046 = function(e, t, r, _) {
      e.samplerParameteri(t, r >>> 0, _);
    }, n.wbg.__wbg_texImage2D_2558a70047650d54 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p) {
        e.texImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l >>> 0, p);
      }, arguments);
    }, n.wbg.__wbg_texImage3D_7987a4b692d91b21 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p, h) {
        e.texImage3D(t >>> 0, r, _, c, o, a, w, l >>> 0, p >>> 0, h);
      }, arguments);
    }, n.wbg.__wbg_texStorage2D_0fff70234489e5a8 = function(e, t, r, _, c, o) {
      e.texStorage2D(t >>> 0, r, _ >>> 0, c, o);
    }, n.wbg.__wbg_texStorage3D_7d322e9790add281 = function(e, t, r, _, c, o, a) {
      e.texStorage3D(t >>> 0, r, _ >>> 0, c, o, a);
    }, n.wbg.__wbg_texSubImage2D_b4ac5eac47418cc5 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p) {
        e.texSubImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l >>> 0, p);
      }, arguments);
    }, n.wbg.__wbg_texSubImage2D_b962ba533b866161 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p) {
        e.texSubImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l >>> 0, p);
      }, arguments);
    }, n.wbg.__wbg_texSubImage2D_0b72a7308c3e78d3 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p) {
        e.texSubImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l >>> 0, p);
      }, arguments);
    }, n.wbg.__wbg_texSubImage2D_8f2db7871647d37a = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p) {
        e.texSubImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l >>> 0, p);
      }, arguments);
    }, n.wbg.__wbg_texSubImage2D_defc51298c31c0e3 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p) {
        e.texSubImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l >>> 0, p);
      }, arguments);
    }, n.wbg.__wbg_texSubImage3D_bd2fd28608206fe5 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p, h, S) {
        e.texSubImage3D(t >>> 0, r, _, c, o, a, w, l, p >>> 0, h >>> 0, S);
      }, arguments);
    }, n.wbg.__wbg_texSubImage3D_895cc20d45e04909 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p, h, S) {
        e.texSubImage3D(t >>> 0, r, _, c, o, a, w, l, p >>> 0, h >>> 0, S);
      }, arguments);
    }, n.wbg.__wbg_texSubImage3D_f75ab42a48d9b789 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p, h, S) {
        e.texSubImage3D(t >>> 0, r, _, c, o, a, w, l, p >>> 0, h >>> 0, S);
      }, arguments);
    }, n.wbg.__wbg_texSubImage3D_2b48a701e63f042e = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p, h, S) {
        e.texSubImage3D(t >>> 0, r, _, c, o, a, w, l, p >>> 0, h >>> 0, S);
      }, arguments);
    }, n.wbg.__wbg_texSubImage3D_f983428ce1099b7f = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p, h, S) {
        e.texSubImage3D(t >>> 0, r, _, c, o, a, w, l, p >>> 0, h >>> 0, S);
      }, arguments);
    }, n.wbg.__wbg_uniform1ui_71145d62b7bd13f4 = function(e, t, r) {
      e.uniform1ui(t, r >>> 0);
    }, n.wbg.__wbg_uniform2fv_4bd352337ccc4530 = function(e, t, r, _) {
      e.uniform2fv(t, y(r, _));
    }, n.wbg.__wbg_uniform2iv_829bd2f635ddf819 = function(e, t, r, _) {
      e.uniform2iv(t, B(r, _));
    }, n.wbg.__wbg_uniform2uiv_6ae4fe2845703965 = function(e, t, r, _) {
      e.uniform2uiv(t, v(r, _));
    }, n.wbg.__wbg_uniform3fv_3d2854c81603e498 = function(e, t, r, _) {
      e.uniform3fv(t, y(r, _));
    }, n.wbg.__wbg_uniform3iv_71333eb685ad9616 = function(e, t, r, _) {
      e.uniform3iv(t, B(r, _));
    }, n.wbg.__wbg_uniform3uiv_998cd5452e009d35 = function(e, t, r, _) {
      e.uniform3uiv(t, v(r, _));
    }, n.wbg.__wbg_uniform4fv_39cdcce4b1acc767 = function(e, t, r, _) {
      e.uniform4fv(t, y(r, _));
    }, n.wbg.__wbg_uniform4iv_f54116c4cfdcd96e = function(e, t, r, _) {
      e.uniform4iv(t, B(r, _));
    }, n.wbg.__wbg_uniform4uiv_c1b79c253aa0271f = function(e, t, r, _) {
      e.uniform4uiv(t, v(r, _));
    }, n.wbg.__wbg_uniformBlockBinding_52117c1104e3ac8a = function(e, t, r, _) {
      e.uniformBlockBinding(t, r >>> 0, _ >>> 0);
    }, n.wbg.__wbg_uniformMatrix2fv_756ddcf41f02aa75 = function(e, t, r, _, c) {
      e.uniformMatrix2fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_uniformMatrix2x3fv_b11505178375085e = function(e, t, r, _, c) {
      e.uniformMatrix2x3fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_uniformMatrix2x4fv_9a96ca1263d07814 = function(e, t, r, _, c) {
      e.uniformMatrix2x4fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_uniformMatrix3fv_f26b98137276fd3d = function(e, t, r, _, c) {
      e.uniformMatrix3fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_uniformMatrix3x2fv_8e447d81dfee8f45 = function(e, t, r, _, c) {
      e.uniformMatrix3x2fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_uniformMatrix3x4fv_0b4125c5150e9ebc = function(e, t, r, _, c) {
      e.uniformMatrix3x4fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_uniformMatrix4fv_5d8e0e047546456b = function(e, t, r, _, c) {
      e.uniformMatrix4fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_uniformMatrix4x2fv_15b6f3535fd4ce98 = function(e, t, r, _, c) {
      e.uniformMatrix4x2fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_uniformMatrix4x3fv_5550b8543a32bbbd = function(e, t, r, _, c) {
      e.uniformMatrix4x3fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_vertexAttribDivisor_8479e8b81c913ed6 = function(e, t, r) {
      e.vertexAttribDivisor(t >>> 0, r >>> 0);
    }, n.wbg.__wbg_vertexAttribIPointer_69f2f4bd74cf0bcb = function(e, t, r, _, c, o) {
      e.vertexAttribIPointer(t >>> 0, r, _ >>> 0, c, o);
    }, n.wbg.__wbg_activeTexture_d42cec3a26e47a5b = function(e, t) {
      e.activeTexture(t >>> 0);
    }, n.wbg.__wbg_attachShader_2112634b3ffa9e9f = function(e, t, r) {
      e.attachShader(t, r);
    }, n.wbg.__wbg_bindAttribLocation_e05596ff4f5413c3 = function(e, t, r, _, c) {
      e.bindAttribLocation(t, r >>> 0, i(_, c));
    }, n.wbg.__wbg_bindBuffer_90d4fb91538001d5 = function(e, t, r) {
      e.bindBuffer(t >>> 0, r);
    }, n.wbg.__wbg_bindFramebuffer_4f950b884dc4be83 = function(e, t, r) {
      e.bindFramebuffer(t >>> 0, r);
    }, n.wbg.__wbg_bindRenderbuffer_1e0b14f526ed7a9d = function(e, t, r) {
      e.bindRenderbuffer(t >>> 0, r);
    }, n.wbg.__wbg_bindTexture_75a698c47a923814 = function(e, t, r) {
      e.bindTexture(t >>> 0, r);
    }, n.wbg.__wbg_blendColor_7d3bf5e5214b44f7 = function(e, t, r, _, c) {
      e.blendColor(t, r, _, c);
    }, n.wbg.__wbg_blendEquation_6ca8e567e79464a4 = function(e, t) {
      e.blendEquation(t >>> 0);
    }, n.wbg.__wbg_blendEquationSeparate_34aa4cecd02882ab = function(e, t, r) {
      e.blendEquationSeparate(t >>> 0, r >>> 0);
    }, n.wbg.__wbg_blendFunc_cffe61957c92e9ac = function(e, t, r) {
      e.blendFunc(t >>> 0, r >>> 0);
    }, n.wbg.__wbg_blendFuncSeparate_3c342f57887c2900 = function(e, t, r, _, c) {
      e.blendFuncSeparate(t >>> 0, r >>> 0, _ >>> 0, c >>> 0);
    }, n.wbg.__wbg_clear_8e2508724944df18 = function(e, t) {
      e.clear(t >>> 0);
    }, n.wbg.__wbg_clearColor_480962bfac4e1cbd = function(e, t, r, _, c) {
      e.clearColor(t, r, _, c);
    }, n.wbg.__wbg_clearDepth_f5b4a73c4b8050eb = function(e, t) {
      e.clearDepth(t);
    }, n.wbg.__wbg_clearStencil_1e4bb9932be75fce = function(e, t) {
      e.clearStencil(t);
    }, n.wbg.__wbg_colorMask_21a93d0180bcbffa = function(e, t, r, _, c) {
      e.colorMask(t !== 0, r !== 0, _ !== 0, c !== 0);
    }, n.wbg.__wbg_compileShader_f40e0c51a7a836fd = function(e, t) {
      e.compileShader(t);
    }, n.wbg.__wbg_copyTexSubImage2D_65140521b061c61b = function(e, t, r, _, c, o, a, w, l) {
      e.copyTexSubImage2D(t >>> 0, r, _, c, o, a, w, l);
    }, n.wbg.__wbg_createBuffer_7f57647465d111f0 = function(e) {
      const t = e.createBuffer();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createFramebuffer_8ebfde8c77472024 = function(e) {
      const t = e.createFramebuffer();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createProgram_7759fb2effb5d9b3 = function(e) {
      const t = e.createProgram();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createRenderbuffer_340b1c428d564bfd = function(e) {
      const t = e.createRenderbuffer();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createShader_b474ef421ec0f80b = function(e, t) {
      const r = e.createShader(t >>> 0);
      return g(r) ? 0 : s(r);
    }, n.wbg.__wbg_createTexture_18b4a88c14cb086e = function(e) {
      const t = e.createTexture();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_cullFace_fe427cdf8d0ea4e2 = function(e, t) {
      e.cullFace(t >>> 0);
    }, n.wbg.__wbg_deleteBuffer_fca5d765302c9a4e = function(e, t) {
      e.deleteBuffer(t);
    }, n.wbg.__wbg_deleteFramebuffer_da681ed1dfa6d543 = function(e, t) {
      e.deleteFramebuffer(t);
    }, n.wbg.__wbg_deleteProgram_a06d69620332cc70 = function(e, t) {
      e.deleteProgram(t);
    }, n.wbg.__wbg_deleteRenderbuffer_5dcdde247a392125 = function(e, t) {
      e.deleteRenderbuffer(t);
    }, n.wbg.__wbg_deleteShader_138a810cc0ca9986 = function(e, t) {
      e.deleteShader(t);
    }, n.wbg.__wbg_deleteTexture_eae7abcfa3015f09 = function(e, t) {
      e.deleteTexture(t);
    }, n.wbg.__wbg_depthFunc_5527d3ee35e25a8d = function(e, t) {
      e.depthFunc(t >>> 0);
    }, n.wbg.__wbg_depthMask_9120207d491c649a = function(e, t) {
      e.depthMask(t !== 0);
    }, n.wbg.__wbg_depthRange_d8d5ad00fd133fc0 = function(e, t, r) {
      e.depthRange(t, r);
    }, n.wbg.__wbg_disable_f0ef6e9a7ac6ddd7 = function(e, t) {
      e.disable(t >>> 0);
    }, n.wbg.__wbg_disableVertexAttribArray_e4f458e34e54fe78 = function(e, t) {
      e.disableVertexAttribArray(t >>> 0);
    }, n.wbg.__wbg_drawArrays_5bf0d92947e472af = function(e, t, r, _) {
      e.drawArrays(t >>> 0, r, _);
    }, n.wbg.__wbg_enable_8b3019da8846ce76 = function(e, t) {
      e.enable(t >>> 0);
    }, n.wbg.__wbg_enableVertexAttribArray_9d7b7e199f86e09b = function(e, t) {
      e.enableVertexAttribArray(t >>> 0);
    }, n.wbg.__wbg_framebufferRenderbuffer_0144c6e35e2edb19 = function(e, t, r, _, c) {
      e.framebufferRenderbuffer(t >>> 0, r >>> 0, _ >>> 0, c);
    }, n.wbg.__wbg_framebufferTexture2D_a6ad7148f7983ae6 = function(e, t, r, _, c, o) {
      e.framebufferTexture2D(t >>> 0, r >>> 0, _ >>> 0, c, o);
    }, n.wbg.__wbg_frontFace_41ab8e7ce3e48cae = function(e, t) {
      e.frontFace(t >>> 0);
    }, n.wbg.__wbg_getExtension_bef4112494c87f34 = function() {
      return f(function(e, t, r) {
        const _ = e.getExtension(i(t, r));
        return g(_) ? 0 : s(_);
      }, arguments);
    }, n.wbg.__wbg_getParameter_aa9af66884d2b210 = function() {
      return f(function(e, t) {
        return e.getParameter(t >>> 0);
      }, arguments);
    }, n.wbg.__wbg_getProgramInfoLog_4d189135f8d5a2de = function(e, t, r) {
      const _ = t.getProgramInfoLog(r);
      var c = g(_) ? 0 : m(_, b.__wbindgen_malloc, b.__wbindgen_realloc), o = d;
      u()[e / 4 + 1] = o, u()[e / 4 + 0] = c;
    }, n.wbg.__wbg_getProgramParameter_7b04ca71a79d9047 = function(e, t, r) {
      return e.getProgramParameter(t, r >>> 0);
    }, n.wbg.__wbg_getShaderInfoLog_d5de3e4eab06fc46 = function(e, t, r) {
      const _ = t.getShaderInfoLog(r);
      var c = g(_) ? 0 : m(_, b.__wbindgen_malloc, b.__wbindgen_realloc), o = d;
      u()[e / 4 + 1] = o, u()[e / 4 + 0] = c;
    }, n.wbg.__wbg_getShaderParameter_4ddb51279bb1500b = function(e, t, r) {
      return e.getShaderParameter(t, r >>> 0);
    }, n.wbg.__wbg_getSupportedExtensions_7a174085f9e1983a = function(e) {
      const t = e.getSupportedExtensions();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_getUniformLocation_51ec30e3755e574d = function(e, t, r, _) {
      const c = e.getUniformLocation(t, i(r, _));
      return g(c) ? 0 : s(c);
    }, n.wbg.__wbg_linkProgram_eabc664217816e72 = function(e, t) {
      e.linkProgram(t);
    }, n.wbg.__wbg_pixelStorei_162a23ba7872b886 = function(e, t, r) {
      e.pixelStorei(t >>> 0, r);
    }, n.wbg.__wbg_polygonOffset_9f20aa27db3ea0a2 = function(e, t, r) {
      e.polygonOffset(t, r);
    }, n.wbg.__wbg_renderbufferStorage_ff5740fb95ecf231 = function(e, t, r, _, c) {
      e.renderbufferStorage(t >>> 0, r >>> 0, _, c);
    }, n.wbg.__wbg_scissor_726eea865bbd6809 = function(e, t, r, _, c) {
      e.scissor(t, r, _, c);
    }, n.wbg.__wbg_shaderSource_7943d06f24862a3b = function(e, t, r, _) {
      e.shaderSource(t, i(r, _));
    }, n.wbg.__wbg_stencilFuncSeparate_c16750a621e43580 = function(e, t, r, _, c) {
      e.stencilFuncSeparate(t >>> 0, r >>> 0, _, c >>> 0);
    }, n.wbg.__wbg_stencilMask_9abfc669d9c2a893 = function(e, t) {
      e.stencilMask(t >>> 0);
    }, n.wbg.__wbg_stencilMaskSeparate_a1f8f805de62aac5 = function(e, t, r) {
      e.stencilMaskSeparate(t >>> 0, r >>> 0);
    }, n.wbg.__wbg_stencilOpSeparate_2f2cc25254360270 = function(e, t, r, _, c) {
      e.stencilOpSeparate(t >>> 0, r >>> 0, _ >>> 0, c >>> 0);
    }, n.wbg.__wbg_texParameteri_8f70dffce11d7da1 = function(e, t, r, _) {
      e.texParameteri(t >>> 0, r >>> 0, _);
    }, n.wbg.__wbg_uniform1f_9b9e5339e7560722 = function(e, t, r) {
      e.uniform1f(t, r);
    }, n.wbg.__wbg_uniform1i_bdcd75be097285e6 = function(e, t, r) {
      e.uniform1i(t, r);
    }, n.wbg.__wbg_uniform4f_b143081575a3bb56 = function(e, t, r, _, c, o) {
      e.uniform4f(t, r, _, c, o);
    }, n.wbg.__wbg_useProgram_757fab437af29c20 = function(e, t) {
      e.useProgram(t);
    }, n.wbg.__wbg_vertexAttribPointer_4416f0325c02aa13 = function(e, t, r, _, c, o, a) {
      e.vertexAttribPointer(t >>> 0, r, _ >>> 0, c !== 0, o, a);
    }, n.wbg.__wbg_viewport_7414e7e2a83afc72 = function(e, t, r, _, c) {
      e.viewport(t, r, _, c);
    }, n.wbg.__wbg_instanceof_Element_6945fc210db80ea9 = function(e) {
      let t;
      try {
        t = e instanceof Element;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_id_e0c4392b9418f9b0 = function(e, t) {
      const r = t.id, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_setid_37bacc3f09f555aa = function(e, t, r) {
      e.id = i(t, r);
    }, n.wbg.__wbg_setinnerHTML_26d69b59e1af99c7 = function(e, t, r) {
      e.innerHTML = i(t, r);
    }, n.wbg.__wbg_getBoundingClientRect_91e6d57c4e65f745 = function(e) {
      return e.getBoundingClientRect();
    }, n.wbg.__wbg_remove_49b0a5925a04b955 = function(e) {
      e.remove();
    }, n.wbg.__wbg_body_edb1908d3ceff3a1 = function(e) {
      const t = e.body;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_activeElement_fa7feca08f5028c0 = function(e) {
      const t = e.activeElement;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createElement_8bae7856a4bb7411 = function() {
      return f(function(e, t, r) {
        return e.createElement(i(t, r));
      }, arguments);
    }, n.wbg.__wbg_getElementById_c369ff43f0db99cf = function(e, t, r) {
      const _ = e.getElementById(i(t, r));
      return g(_) ? 0 : s(_);
    }, n.wbg.__wbg_querySelector_a5f74efc5fa193dd = function() {
      return f(function(e, t, r) {
        const _ = e.querySelector(i(t, r));
        return g(_) ? 0 : s(_);
      }, arguments);
    }, n.wbg.__wbg_querySelectorAll_4e0fcdb64cda2cd5 = function() {
      return f(function(e, t, r) {
        return e.querySelectorAll(i(t, r));
      }, arguments);
    }, n.wbg.__wbg_elementFromPoint_2816f49709db4437 = function(e, t, r) {
      const _ = e.elementFromPoint(t, r);
      return g(_) ? 0 : s(_);
    }, n.wbg.__wbg_instanceof_HtmlElement_3bcc4ff70cfdcba5 = function(e) {
      let t;
      try {
        t = e instanceof HTMLElement;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_setinnerText_087b7e3f90d97466 = function(e, t, r) {
      e.innerText = i(t, r);
    }, n.wbg.__wbg_settabIndex_27de1972b86c0f4c = function(e, t) {
      e.tabIndex = t;
    }, n.wbg.__wbg_style_c3fc3dd146182a2d = function(e) {
      return e.style;
    }, n.wbg.__wbg_setonclick_4fd9bd8531d33a17 = function(e, t) {
      e.onclick = t;
    }, n.wbg.__wbg_blur_51f7b635f18a0eec = function() {
      return f(function(e) {
        e.blur();
      }, arguments);
    }, n.wbg.__wbg_focus_39d4b8ba8ff9df14 = function() {
      return f(function(e) {
        e.focus();
      }, arguments);
    }, n.wbg.__wbg_navigator_56803b85352a0575 = function(e) {
      return e.navigator;
    }, n.wbg.__wbg_items_5070ce38a6d53ed2 = function(e) {
      return e.items;
    }, n.wbg.__wbg_files_a2848a7a7424820f = function(e) {
      const t = e.files;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_getData_35c5974f5cd7e02c = function() {
      return f(function(e, t, r, _) {
        const c = t.getData(i(r, _)), o = m(c, b.__wbindgen_malloc, b.__wbindgen_realloc), a = d;
        u()[e / 4 + 1] = a, u()[e / 4 + 0] = o;
      }, arguments);
    }, n.wbg.__wbg_length_a23c520109d9ba0a = function(e) {
      return e.length;
    }, n.wbg.__wbg_get_0fa6ec8bd6a5c256 = function(e, t) {
      const r = e[t >>> 0];
      return g(r) ? 0 : s(r);
    }, n.wbg.__wbg_addEventListener_53b787075bd5e003 = function() {
      return f(function(e, t, r, _) {
        e.addEventListener(i(t, r), _);
      }, arguments);
    }, n.wbg.__wbg_removeEventListener_92cb9b3943463338 = function() {
      return f(function(e, t, r, _) {
        e.removeEventListener(i(t, r), _);
      }, arguments);
    }, n.wbg.__wbg_instanceof_HtmlAnchorElement_5fc0eb2fbc8672d8 = function(e) {
      let t;
      try {
        t = e instanceof HTMLAnchorElement;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_setdownload_65ac7e7c800d764e = function(e, t, r) {
      e.download = i(t, r);
    }, n.wbg.__wbg_sethref_b0712139dd35e2fd = function(e, t, r) {
      e.href = i(t, r);
    }, n.wbg.__wbg_read_e7d0f8a49be01d86 = function(e) {
      return e.read();
    }, n.wbg.__wbg_releaseLock_5c49db976c08b864 = function(e) {
      e.releaseLock();
    }, n.wbg.__wbg_cancel_6ee33d4006737aef = function(e) {
      return e.cancel();
    }, n.wbg.__wbg_href_7bfb3b2fdc0a6c3f = function(e, t) {
      const r = t.href, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_searchParams_bc5845fe67587f77 = function(e) {
      return e.searchParams;
    }, n.wbg.__wbg_new_67853c351755d2cf = function() {
      return f(function(e, t) {
        return new URL(i(e, t));
      }, arguments);
    }, n.wbg.__wbg_createObjectURL_ad8244759309f204 = function() {
      return f(function(e, t) {
        const r = URL.createObjectURL(t), _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_state_9cc3f933b7d50acb = function() {
      return f(function(e) {
        return e.state;
      }, arguments);
    }, n.wbg.__wbg_back_eed6c9ffd402e26e = function() {
      return f(function(e) {
        e.back();
      }, arguments);
    }, n.wbg.__wbg_forward_124e6df53a7e8a2c = function() {
      return f(function(e) {
        e.forward();
      }, arguments);
    }, n.wbg.__wbg_pushState_b8e8d346f8bb33fd = function() {
      return f(function(e, t, r, _, c, o) {
        e.pushState(t, i(r, _), c === 0 ? void 0 : i(c, o));
      }, arguments);
    }, n.wbg.__wbg_instanceof_HtmlInputElement_307512fe1252c849 = function(e) {
      let t;
      try {
        t = e instanceof HTMLInputElement;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_setaccept_e9aecafb8dbc1efa = function(e, t, r) {
      e.accept = i(t, r);
    }, n.wbg.__wbg_files_8b6e6eff43af0f6d = function(e) {
      const t = e.files;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_setmultiple_df7c9f1022e04575 = function(e, t) {
      e.multiple = t !== 0;
    }, n.wbg.__wbg_settype_12715bd23e119883 = function(e, t, r) {
      e.type = i(t, r);
    }, n.wbg.__wbg_value_47fe6384562f52ab = function(e, t) {
      const r = t.value, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_setvalue_78cb4f1fef58ae98 = function(e, t, r) {
      e.value = i(t, r);
    }, n.wbg.__wbg_bindVertexArrayOES_abe2fd389c6a2f56 = function(e, t) {
      e.bindVertexArrayOES(t);
    }, n.wbg.__wbg_createVertexArrayOES_886be8a08db32ce6 = function(e) {
      const t = e.createVertexArrayOES();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_deleteVertexArrayOES_153f352862874f30 = function(e, t) {
      e.deleteVertexArrayOES(t);
    }, n.wbg.__wbg_close_a994f9425dab445c = function() {
      return f(function(e) {
        e.close();
      }, arguments);
    }, n.wbg.__wbg_enqueue_ea194723156c0cc2 = function() {
      return f(function(e, t) {
        e.enqueue(t);
      }, arguments);
    }, n.wbg.__wbg_instanceof_ResizeObserverSize_54b26135ae24a941 = function(e) {
      let t;
      try {
        t = e instanceof ResizeObserverSize;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_inlineSize_ff0e40258cefeba2 = function(e) {
      return e.inlineSize;
    }, n.wbg.__wbg_blockSize_73f4e5608c08713d = function(e) {
      return e.blockSize;
    }, n.wbg.__wbg_writeText_4f1bf9bc5850bc26 = function(e, t, r) {
      return e.writeText(i(t, r));
    }, n.wbg.__wbg_type_e55aae30eb601b13 = function(e, t) {
      const r = t.type, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_message_730094b985f3ba2e = function(e, t) {
      const r = t.message, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_error_b481da0f7765cbca = function(e) {
      return e.error;
    }, n.wbg.__wbg_length_4db38705d5c8ba2f = function(e) {
      return e.length;
    }, n.wbg.__wbg_get_58f6d5f6aee3f846 = function(e, t) {
      const r = e[t >>> 0];
      return g(r) ? 0 : s(r);
    }, n.wbg.__wbg_now_4e659b3d15f470d9 = function(e) {
      return e.now();
    }, n.wbg.__wbg_setonopen_ce7a4c51e5cf5788 = function(e, t) {
      e.onopen = t;
    }, n.wbg.__wbg_setonerror_39a785302b0cd2e9 = function(e, t) {
      e.onerror = t;
    }, n.wbg.__wbg_setonclose_b9929b1c1624dff3 = function(e, t) {
      e.onclose = t;
    }, n.wbg.__wbg_setonmessage_2af154ce83a3dc94 = function(e, t) {
      e.onmessage = t;
    }, n.wbg.__wbg_setbinaryType_b0cf5103cd561959 = function(e, t) {
      e.binaryType = t;
    }, n.wbg.__wbg_new_6c74223c77cfabad = function() {
      return f(function(e, t) {
        return new WebSocket(i(e, t));
      }, arguments);
    }, n.wbg.__wbg_close_acd9532ff5c093ea = function() {
      return f(function(e) {
        e.close();
      }, arguments);
    }, n.wbg.__wbg_error_8e3928cfb8a43e2b = typeof console.error == "function" ? console.error : V("console.error"), n.wbg.__wbg_drawArraysInstancedANGLE_6afae595a484db93 = function(e, t, r, _, c) {
      e.drawArraysInstancedANGLE(t >>> 0, r, _, c);
    }, n.wbg.__wbg_drawElementsInstancedANGLE_f175a178d553357e = function(e, t, r, _, c, o) {
      e.drawElementsInstancedANGLE(t >>> 0, r, _ >>> 0, c, o);
    }, n.wbg.__wbg_vertexAttribDivisorANGLE_b258d7388e466921 = function(e, t, r) {
      e.vertexAttribDivisorANGLE(t >>> 0, r >>> 0);
    }, n.wbg.__wbg_getPropertyValue_fa32ee1811f224cb = function() {
      return f(function(e, t, r, _) {
        const c = t.getPropertyValue(i(r, _)), o = m(c, b.__wbindgen_malloc, b.__wbindgen_realloc), a = d;
        u()[e / 4 + 1] = a, u()[e / 4 + 0] = o;
      }, arguments);
    }, n.wbg.__wbg_setProperty_ea7d15a2b591aa97 = function() {
      return f(function(e, t, r, _, c) {
        e.setProperty(i(t, r), i(_, c));
      }, arguments);
    }, n.wbg.__wbg_instanceof_HtmlButtonElement_534f7aa847dae46f = function(e) {
      let t;
      try {
        t = e instanceof HTMLButtonElement;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_clipboard_45ef2514e9ece120 = function(e) {
      const t = e.clipboard;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_userAgent_e94c7cbcdac01fea = function() {
      return f(function(e, t) {
        const r = t.userAgent, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_touches_c0f077e3c2429577 = function(e) {
      return e.touches;
    }, n.wbg.__wbg_changedTouches_d044c818dbcb83b1 = function(e) {
      return e.changedTouches;
    }, n.wbg.__wbg_width_1e8430024cb82aba = function(e) {
      return e.width;
    }, n.wbg.__wbg_height_0c1394f089d7bb71 = function(e) {
      return e.height;
    }, n.wbg.__wbg_top_c4e2234a035a3d25 = function(e) {
      return e.top;
    }, n.wbg.__wbg_right_4659608ec17bdea7 = function(e) {
      return e.right;
    }, n.wbg.__wbg_bottom_91d8cb531cf1afd2 = function(e) {
      return e.bottom;
    }, n.wbg.__wbg_left_fe0a839abdd508f4 = function(e) {
      return e.left;
    }, n.wbg.__wbg_instanceof_HtmlCanvasElement_46bdbf323b0b18d1 = function(e) {
      let t;
      try {
        t = e instanceof HTMLCanvasElement;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_width_aee8b8809b033b05 = function(e) {
      return e.width;
    }, n.wbg.__wbg_setwidth_080107476e633963 = function(e, t) {
      e.width = t >>> 0;
    }, n.wbg.__wbg_height_80053d3c71b338e0 = function(e) {
      return e.height;
    }, n.wbg.__wbg_setheight_dc240617639f1f51 = function(e, t) {
      e.height = t >>> 0;
    }, n.wbg.__wbg_getContext_df50fa48a8876636 = function() {
      return f(function(e, t, r) {
        const _ = e.getContext(i(t, r));
        return g(_) ? 0 : s(_);
      }, arguments);
    }, n.wbg.__wbg_getContext_fec464290556673c = function() {
      return f(function(e, t, r, _) {
        const c = e.getContext(i(t, r), _);
        return g(c) ? 0 : s(c);
      }, arguments);
    }, n.wbg.__wbg_view_7f0ce470793a340f = function(e) {
      const t = e.view;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_respond_b1a43b2e3a06d525 = function() {
      return f(function(e, t) {
        e.respond(t >>> 0);
      }, arguments);
    }, n.wbg.__wbg_getItem_164e8e5265095b87 = function() {
      return f(function(e, t, r, _) {
        const c = t.getItem(i(r, _));
        var o = g(c) ? 0 : m(c, b.__wbindgen_malloc, b.__wbindgen_realloc), a = d;
        u()[e / 4 + 1] = a, u()[e / 4 + 0] = o;
      }, arguments);
    }, n.wbg.__wbg_setItem_ba2bb41d73dac079 = function() {
      return f(function(e, t, r, _, c) {
        e.setItem(i(t, r), i(_, c));
      }, arguments);
    }, n.wbg.__wbg_delete_808f42904ec49124 = function() {
      return f(function(e, t, r) {
        delete e[i(t, r)];
      }, arguments);
    }, n.wbg.__wbg_length_679e0f1f9f0744bd = function(e) {
      return e.length;
    }, n.wbg.__wbg_item_2b1028b3d39463e9 = function(e, t) {
      const r = e.item(t >>> 0);
      return g(r) ? 0 : s(r);
    }, n.wbg.__wbg_get_cbca0027ab731230 = function(e, t) {
      const r = e[t >>> 0];
      return g(r) ? 0 : s(r);
    }, n.wbg.__wbg_new_4c501d7c115d20a6 = function() {
      return f(function() {
        return new URLSearchParams();
      }, arguments);
    }, n.wbg.__wbg_append_dea955946927e41e = function(e, t, r, _, c) {
      e.append(i(t, r), i(_, c));
    }, n.wbg.__wbg_set_533a7249149a73e8 = function(e, t, r, _, c) {
      e.set(i(t, r), i(_, c));
    }, n.wbg.__wbg_deltaX_206576827ededbe5 = function(e) {
      return e.deltaX;
    }, n.wbg.__wbg_deltaY_032e327e216f2b2b = function(e) {
      return e.deltaY;
    }, n.wbg.__wbg_deltaMode_294b2eaf54047265 = function(e) {
      return e.deltaMode;
    }, n.wbg.__wbg_instanceof_Blob_83ad3dd4c9c406f0 = function(e) {
      let t;
      try {
        t = e instanceof Blob;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_size_9c7e57fbd4f0f4b5 = function(e) {
      return e.size;
    }, n.wbg.__wbg_type_020d4abf13839639 = function(e, t) {
      const r = t.type, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_newwithu8arraysequenceandoptions_366f462e1b363808 = function() {
      return f(function(e, t) {
        return new Blob(e, t);
      }, arguments);
    }, n.wbg.__wbg_arrayBuffer_307ddd1bd1d04e23 = function(e) {
      return e.arrayBuffer();
    }, n.wbg.__wbg_result_77ceeec1e3a16df7 = function() {
      return f(function(e) {
        return e.result;
      }, arguments);
    }, n.wbg.__wbg_setonload_0af77109dbfaa065 = function(e, t) {
      e.onload = t;
    }, n.wbg.__wbg_setonloadend_1a1d3155e6949495 = function(e, t) {
      e.onloadend = t;
    }, n.wbg.__wbg_new_c1e4a76f0b5c28b8 = function() {
      return f(function() {
        return new FileReader();
      }, arguments);
    }, n.wbg.__wbg_readAsArrayBuffer_4f4ed73c7dc0ce42 = function() {
      return f(function(e, t) {
        e.readAsArrayBuffer(t);
      }, arguments);
    }, n.wbg.__wbg_width_0e2f1c393242f16e = function(e) {
      return e.width;
    }, n.wbg.__wbg_height_d6c8a3041eff461a = function(e) {
      return e.height;
    }, n.wbg.__wbg_keyCode_2af7775f99bf8e33 = function(e) {
      return e.keyCode;
    }, n.wbg.__wbg_altKey_2e6c34c37088d8b1 = function(e) {
      return e.altKey;
    }, n.wbg.__wbg_ctrlKey_bb5b6fef87339703 = function(e) {
      return e.ctrlKey;
    }, n.wbg.__wbg_shiftKey_5911baf439ab232b = function(e) {
      return e.shiftKey;
    }, n.wbg.__wbg_metaKey_6bf4ae4e83a11278 = function(e) {
      return e.metaKey;
    }, n.wbg.__wbg_isComposing_a0b97b7ba6491ed6 = function(e) {
      return e.isComposing;
    }, n.wbg.__wbg_key_dccf9e8aa1315a8e = function(e, t) {
      const r = t.key, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_matches_dd4fdea75008ad05 = function(e) {
      return e.matches;
    }, n.wbg.__wbg_instanceof_MessageEvent_feb4c20d69f898a5 = function(e) {
      let t;
      try {
        t = e instanceof MessageEvent;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_data_3ce7c145ca4fbcdc = function(e) {
      return e.data;
    }, n.wbg.__wbg_width_6aa39fc77f088914 = function(e) {
      return e.width;
    }, n.wbg.__wbg_setwidth_83d936c4b04dcbec = function(e, t) {
      e.width = t >>> 0;
    }, n.wbg.__wbg_height_05a87854adf24d83 = function(e) {
      return e.height;
    }, n.wbg.__wbg_setheight_6025ba0d58e6cc8c = function(e, t) {
      e.height = t >>> 0;
    }, n.wbg.__wbg_getContext_c102f659d540d068 = function() {
      return f(function(e, t, r) {
        const _ = e.getContext(i(t, r));
        return g(_) ? 0 : s(_);
      }, arguments);
    }, n.wbg.__wbg_getContext_c9fc178d1fa6f8fe = function() {
      return f(function(e, t, r, _) {
        const c = e.getContext(i(t, r), _);
        return g(c) ? 0 : s(c);
      }, arguments);
    }, n.wbg.__wbg_drawBuffersWEBGL_4c663e042e093892 = function(e, t) {
      e.drawBuffersWEBGL(t);
    }, n.wbg.__wbg_name_f35eb93a73d94973 = function(e, t) {
      const r = t.name, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_lastModified_e774a1d2d0384c3b = function(e) {
      return e.lastModified;
    }, n.wbg.__wbg_matches_e14ed9ff8291cf24 = function(e) {
      return e.matches;
    }, n.wbg.__wbg_appendChild_580ccb11a660db68 = function() {
      return f(function(e, t) {
        return e.appendChild(t);
      }, arguments);
    }, n.wbg.__wbg_get_8cd5eba00ab6304f = function(e, t) {
      const r = e[t >>> 0];
      return g(r) ? 0 : s(r);
    }, n.wbg.__wbg_state_1eb4a1e39cc326c0 = function(e) {
      return e.state;
    }, n.wbg.__wbg_instanceof_ReadableStream_68ecb420c904a644 = function(e) {
      let t;
      try {
        t = e instanceof ReadableStream;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_dataTransfer_cef7816623bd8478 = function(e) {
      const t = e.dataTransfer;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_href_706b235ecfe6848c = function() {
      return f(function(e, t) {
        const r = t.href, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_origin_ee93e29ace71f568 = function() {
      return f(function(e, t) {
        const r = t.origin, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_protocol_b7292c581cfe1e5c = function() {
      return f(function(e, t) {
        const r = t.protocol, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_host_8f1b8ead257c8135 = function() {
      return f(function(e, t) {
        const r = t.host, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_hostname_3d9f22c60dc5bec6 = function() {
      return f(function(e, t) {
        const r = t.hostname, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_port_b8d9a9c4e2b26efa = function() {
      return f(function(e, t) {
        const r = t.port, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_pathname_5449afe3829f96a1 = function() {
      return f(function(e, t) {
        const r = t.pathname, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_search_489f12953342ec1f = function() {
      return f(function(e, t) {
        const r = t.search, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_hash_553098e838e06c1d = function() {
      return f(function(e, t) {
        const r = t.hash, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
        u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
      }, arguments);
    }, n.wbg.__wbg_assign_ab4a69a994878ad9 = function() {
      return f(function(e, t, r) {
        e.assign(i(t, r));
      }, arguments);
    }, n.wbg.__wbg_headers_abb199c3be8d817c = function(e) {
      return e.headers;
    }, n.wbg.__wbg_newwithstrandinit_3fd6fba4083ff2d0 = function() {
      return f(function(e, t, r) {
        return new Request(i(e, t), r);
      }, arguments);
    }, n.wbg.__wbg_instanceof_ResizeObserverEntry_494c663b8cd0cdcf = function(e) {
      let t;
      try {
        t = e instanceof ResizeObserverEntry;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_contentRect_bce644376332c7a5 = function(e) {
      return e.contentRect;
    }, n.wbg.__wbg_contentBoxSize_c6294de1f1ca7e41 = function(e) {
      return e.contentBoxSize;
    }, n.wbg.__wbg_devicePixelContentBoxSize_d5bcdcd5e96671f3 = function(e) {
      return e.devicePixelContentBoxSize;
    }, n.wbg.__wbg_instanceof_Response_849eb93e75734b6e = function(e) {
      let t;
      try {
        t = e instanceof Response;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_url_5f6dc4009ac5f99d = function(e, t) {
      const r = t.url, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_status_61a01141acd3cf74 = function(e) {
      return e.status;
    }, n.wbg.__wbg_ok_38d7c30bbc66719e = function(e) {
      return e.ok;
    }, n.wbg.__wbg_statusText_1e41a5e3986992cd = function(e, t) {
      const r = t.statusText, _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_headers_9620bfada380764a = function(e) {
      return e.headers;
    }, n.wbg.__wbg_body_9545a94f397829db = function(e) {
      const t = e.body;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_arrayBuffer_29931d52c7206b02 = function() {
      return f(function(e) {
        return e.arrayBuffer();
      }, arguments);
    }, n.wbg.__wbg_clipboardData_0427b2003659865a = function(e) {
      const t = e.clipboardData;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_data_1d8005e6d66d881b = function(e, t) {
      const r = t.data;
      var _ = g(r) ? 0 : m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbg_preventDefault_b1a4aafc79409429 = function(e) {
      e.preventDefault();
    }, n.wbg.__wbg_stopPropagation_fa5b666049c9fd02 = function(e) {
      e.stopPropagation();
    }, n.wbg.__wbg_set_cb0e7a5c2dd66afd = function() {
      return f(function(e, t, r, _, c) {
        e.set(i(t, r), i(_, c));
      }, arguments);
    }, n.wbg.__wbg_videoWidth_f0b751704b53672c = function(e) {
      return e.videoWidth;
    }, n.wbg.__wbg_videoHeight_e75550285bbbfdab = function(e) {
      return e.videoHeight;
    }, n.wbg.__wbg_isComposing_71872de364b1e1b7 = function(e) {
      return e.isComposing;
    }, n.wbg.__wbg_clientX_fef6bf7a6bcf41b8 = function(e) {
      return e.clientX;
    }, n.wbg.__wbg_clientY_df42f8fceab3cef2 = function(e) {
      return e.clientY;
    }, n.wbg.__wbg_ctrlKey_008695ce60a588f5 = function(e) {
      return e.ctrlKey;
    }, n.wbg.__wbg_shiftKey_1e76dbfcdd36a4b4 = function(e) {
      return e.shiftKey;
    }, n.wbg.__wbg_altKey_07da841b54bd3ed6 = function(e) {
      return e.altKey;
    }, n.wbg.__wbg_metaKey_86bfd3b0d3a8083f = function(e) {
      return e.metaKey;
    }, n.wbg.__wbg_button_367cdc7303e3cf9b = function(e) {
      return e.button;
    }, n.wbg.__wbg_identifier_02d52b63cc6ddc4d = function(e) {
      return e.identifier;
    }, n.wbg.__wbg_clientX_32cdd4a59d3eff3f = function(e) {
      return e.clientX;
    }, n.wbg.__wbg_clientY_155c09997817066a = function(e) {
      return e.clientY;
    }, n.wbg.__wbg_force_139077aa422a42a5 = function(e) {
      return e.force;
    }, n.wbg.__wbg_framebufferTextureMultiviewOVR_a4eb1a11052508f4 = function(e, t, r, _, c, o, a) {
      e.framebufferTextureMultiviewOVR(t >>> 0, r >>> 0, _, c, o, a);
    }, n.wbg.__wbg_byobRequest_72fca99f9c32c193 = function(e) {
      const t = e.byobRequest;
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_close_184931724d961ccc = function() {
      return f(function(e) {
        e.close();
      }, arguments);
    }, n.wbg.__wbg_new_61d4f20a1c08a45c = function() {
      return f(function(e) {
        return new ResizeObserver(e);
      }, arguments);
    }, n.wbg.__wbg_disconnect_6675f32e2ae8deb7 = function(e) {
      e.disconnect();
    }, n.wbg.__wbg_observe_dc0ebcd59ee7cd17 = function(e, t, r) {
      e.observe(t, r);
    }, n.wbg.__wbg_bufferData_bb9321e8fa042bac = function(e, t, r, _) {
      e.bufferData(t >>> 0, r, _ >>> 0);
    }, n.wbg.__wbg_bufferData_5d1e6b8eaa7d23c8 = function(e, t, r, _) {
      e.bufferData(t >>> 0, r, _ >>> 0);
    }, n.wbg.__wbg_bufferSubData_a6cea5e056662bd7 = function(e, t, r, _) {
      e.bufferSubData(t >>> 0, r, _);
    }, n.wbg.__wbg_compressedTexSubImage2D_db8b170a99900aff = function(e, t, r, _, c, o, a, w, l) {
      e.compressedTexSubImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l);
    }, n.wbg.__wbg_readPixels_551d0505625c865b = function() {
      return f(function(e, t, r, _, c, o, a, w) {
        e.readPixels(t, r, _, c, o >>> 0, a >>> 0, w);
      }, arguments);
    }, n.wbg.__wbg_texImage2D_a14a3c7863e25c89 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p) {
        e.texImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l >>> 0, p);
      }, arguments);
    }, n.wbg.__wbg_texSubImage2D_55a407e48f3a5cb4 = function() {
      return f(function(e, t, r, _, c, o, a, w, l, p) {
        e.texSubImage2D(t >>> 0, r, _, c, o, a, w >>> 0, l >>> 0, p);
      }, arguments);
    }, n.wbg.__wbg_uniform2fv_dcb8b73e2637092a = function(e, t, r, _) {
      e.uniform2fv(t, y(r, _));
    }, n.wbg.__wbg_uniform2iv_fc73855d9dec793a = function(e, t, r, _) {
      e.uniform2iv(t, B(r, _));
    }, n.wbg.__wbg_uniform3fv_3e32c897d3ed1eaa = function(e, t, r, _) {
      e.uniform3fv(t, y(r, _));
    }, n.wbg.__wbg_uniform3iv_2b3fa9d97dff01a2 = function(e, t, r, _) {
      e.uniform3iv(t, B(r, _));
    }, n.wbg.__wbg_uniform4fv_980ce05d950ee599 = function(e, t, r, _) {
      e.uniform4fv(t, y(r, _));
    }, n.wbg.__wbg_uniform4iv_f112dcc4401f5469 = function(e, t, r, _) {
      e.uniform4iv(t, B(r, _));
    }, n.wbg.__wbg_uniformMatrix2fv_4417ed4d88a140be = function(e, t, r, _, c) {
      e.uniformMatrix2fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_uniformMatrix3fv_d46553a1248946b5 = function(e, t, r, _, c) {
      e.uniformMatrix3fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_uniformMatrix4fv_cd46ed81bccb0cb2 = function(e, t, r, _, c) {
      e.uniformMatrix4fv(t, r !== 0, y(_, c));
    }, n.wbg.__wbg_activeTexture_5f084e1b3f14853e = function(e, t) {
      e.activeTexture(t >>> 0);
    }, n.wbg.__wbg_attachShader_6397dc4fd87343d3 = function(e, t, r) {
      e.attachShader(t, r);
    }, n.wbg.__wbg_bindAttribLocation_7ab87f5815dce9f0 = function(e, t, r, _, c) {
      e.bindAttribLocation(t, r >>> 0, i(_, c));
    }, n.wbg.__wbg_bindBuffer_1e5043751efddd4f = function(e, t, r) {
      e.bindBuffer(t >>> 0, r);
    }, n.wbg.__wbg_bindFramebuffer_c301d73a2c2842bb = function(e, t, r) {
      e.bindFramebuffer(t >>> 0, r);
    }, n.wbg.__wbg_bindRenderbuffer_8ec7d02bd60bdfb2 = function(e, t, r) {
      e.bindRenderbuffer(t >>> 0, r);
    }, n.wbg.__wbg_bindTexture_772f5eb022019d87 = function(e, t, r) {
      e.bindTexture(t >>> 0, r);
    }, n.wbg.__wbg_blendColor_f25a274ecd388a1e = function(e, t, r, _, c) {
      e.blendColor(t, r, _, c);
    }, n.wbg.__wbg_blendEquation_a442d97b5c6efedb = function(e, t) {
      e.blendEquation(t >>> 0);
    }, n.wbg.__wbg_blendEquationSeparate_721f30ba584a5233 = function(e, t, r) {
      e.blendEquationSeparate(t >>> 0, r >>> 0);
    }, n.wbg.__wbg_blendFunc_fc4b298f39801a9c = function(e, t, r) {
      e.blendFunc(t >>> 0, r >>> 0);
    }, n.wbg.__wbg_blendFuncSeparate_abe2ad4272c8365e = function(e, t, r, _, c) {
      e.blendFuncSeparate(t >>> 0, r >>> 0, _ >>> 0, c >>> 0);
    }, n.wbg.__wbg_clear_f9731a47df2e70d8 = function(e, t) {
      e.clear(t >>> 0);
    }, n.wbg.__wbg_clearColor_42707553c40e0e0f = function(e, t, r, _, c) {
      e.clearColor(t, r, _, c);
    }, n.wbg.__wbg_clearDepth_42ac48f2ab25c419 = function(e, t) {
      e.clearDepth(t);
    }, n.wbg.__wbg_clearStencil_0f906e2d8b61aa7a = function(e, t) {
      e.clearStencil(t);
    }, n.wbg.__wbg_colorMask_03aa359acc86fd70 = function(e, t, r, _, c) {
      e.colorMask(t !== 0, r !== 0, _ !== 0, c !== 0);
    }, n.wbg.__wbg_compileShader_3af4719dfdb508e3 = function(e, t) {
      e.compileShader(t);
    }, n.wbg.__wbg_copyTexSubImage2D_0e21b1e1089c410a = function(e, t, r, _, c, o, a, w, l) {
      e.copyTexSubImage2D(t >>> 0, r, _, c, o, a, w, l);
    }, n.wbg.__wbg_createBuffer_34e01f5c10929b41 = function(e) {
      const t = e.createBuffer();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createFramebuffer_49ca64e9e1c6f5eb = function(e) {
      const t = e.createFramebuffer();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createProgram_9affbfa62b7b2608 = function(e) {
      const t = e.createProgram();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createRenderbuffer_375d7f4004bc49bd = function(e) {
      const t = e.createRenderbuffer();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_createShader_55ca04b44164bd41 = function(e, t) {
      const r = e.createShader(t >>> 0);
      return g(r) ? 0 : s(r);
    }, n.wbg.__wbg_createTexture_c13c31b2b132c17f = function(e) {
      const t = e.createTexture();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_cullFace_af37bb1c2d22ab73 = function(e, t) {
      e.cullFace(t >>> 0);
    }, n.wbg.__wbg_deleteBuffer_96df38349e3487d2 = function(e, t) {
      e.deleteBuffer(t);
    }, n.wbg.__wbg_deleteFramebuffer_417b62b6156d4894 = function(e, t) {
      e.deleteFramebuffer(t);
    }, n.wbg.__wbg_deleteProgram_641402f7551587d8 = function(e, t) {
      e.deleteProgram(t);
    }, n.wbg.__wbg_deleteRenderbuffer_d3aedb394b1ea546 = function(e, t) {
      e.deleteRenderbuffer(t);
    }, n.wbg.__wbg_deleteShader_e5c778f25b722e68 = function(e, t) {
      e.deleteShader(t);
    }, n.wbg.__wbg_deleteTexture_f89d8e417b156960 = function(e, t) {
      e.deleteTexture(t);
    }, n.wbg.__wbg_depthFunc_1ee4bf1e0127bf7f = function(e, t) {
      e.depthFunc(t >>> 0);
    }, n.wbg.__wbg_depthMask_dd6cd8a9aff90e5c = function(e, t) {
      e.depthMask(t !== 0);
    }, n.wbg.__wbg_depthRange_7e521414b51cf5de = function(e, t, r) {
      e.depthRange(t, r);
    }, n.wbg.__wbg_disable_5dd8c3842de93e92 = function(e, t) {
      e.disable(t >>> 0);
    }, n.wbg.__wbg_disableVertexAttribArray_12bc9adefa738796 = function(e, t) {
      e.disableVertexAttribArray(t >>> 0);
    }, n.wbg.__wbg_drawArrays_f619a26a53ab5ab3 = function(e, t, r, _) {
      e.drawArrays(t >>> 0, r, _);
    }, n.wbg.__wbg_enable_7abe812a71c76206 = function(e, t) {
      e.enable(t >>> 0);
    }, n.wbg.__wbg_enableVertexAttribArray_6d44444aa994f42a = function(e, t) {
      e.enableVertexAttribArray(t >>> 0);
    }, n.wbg.__wbg_framebufferRenderbuffer_e1c9c64aea848b39 = function(e, t, r, _, c) {
      e.framebufferRenderbuffer(t >>> 0, r >>> 0, _ >>> 0, c);
    }, n.wbg.__wbg_framebufferTexture2D_66e1968fd5b7b3e3 = function(e, t, r, _, c, o) {
      e.framebufferTexture2D(t >>> 0, r >>> 0, _ >>> 0, c, o);
    }, n.wbg.__wbg_frontFace_bb8a1ded6f52865e = function(e, t) {
      e.frontFace(t >>> 0);
    }, n.wbg.__wbg_getParameter_a77768abe8a51f24 = function() {
      return f(function(e, t) {
        return e.getParameter(t >>> 0);
      }, arguments);
    }, n.wbg.__wbg_getProgramInfoLog_bf1fba8fa90667c7 = function(e, t, r) {
      const _ = t.getProgramInfoLog(r);
      var c = g(_) ? 0 : m(_, b.__wbindgen_malloc, b.__wbindgen_realloc), o = d;
      u()[e / 4 + 1] = o, u()[e / 4 + 0] = c;
    }, n.wbg.__wbg_getProgramParameter_10c8a43809fb8c2e = function(e, t, r) {
      return e.getProgramParameter(t, r >>> 0);
    }, n.wbg.__wbg_getShaderInfoLog_0262cb299092ce92 = function(e, t, r) {
      const _ = t.getShaderInfoLog(r);
      var c = g(_) ? 0 : m(_, b.__wbindgen_malloc, b.__wbindgen_realloc), o = d;
      u()[e / 4 + 1] = o, u()[e / 4 + 0] = c;
    }, n.wbg.__wbg_getShaderParameter_60b69083e8d662ce = function(e, t, r) {
      return e.getShaderParameter(t, r >>> 0);
    }, n.wbg.__wbg_getUniformLocation_6eedfb513ccce732 = function(e, t, r, _) {
      const c = e.getUniformLocation(t, i(r, _));
      return g(c) ? 0 : s(c);
    }, n.wbg.__wbg_linkProgram_af5fed9dc3f1cdf9 = function(e, t) {
      e.linkProgram(t);
    }, n.wbg.__wbg_pixelStorei_054e50b5fdc17824 = function(e, t, r) {
      e.pixelStorei(t >>> 0, r);
    }, n.wbg.__wbg_polygonOffset_2927e355350d4327 = function(e, t, r) {
      e.polygonOffset(t, r);
    }, n.wbg.__wbg_renderbufferStorage_f41b3c99f6a8f25e = function(e, t, r, _, c) {
      e.renderbufferStorage(t >>> 0, r >>> 0, _, c);
    }, n.wbg.__wbg_scissor_75ba2245d4db0eaf = function(e, t, r, _, c) {
      e.scissor(t, r, _, c);
    }, n.wbg.__wbg_shaderSource_7891a1fcb69a0023 = function(e, t, r, _) {
      e.shaderSource(t, i(r, _));
    }, n.wbg.__wbg_stencilFuncSeparate_a3699f92e69c1494 = function(e, t, r, _, c) {
      e.stencilFuncSeparate(t >>> 0, r >>> 0, _, c >>> 0);
    }, n.wbg.__wbg_stencilMask_c5ad44ea27c5f169 = function(e, t) {
      e.stencilMask(t >>> 0);
    }, n.wbg.__wbg_stencilMaskSeparate_a7830b1e1eabf5bd = function(e, t, r) {
      e.stencilMaskSeparate(t >>> 0, r >>> 0);
    }, n.wbg.__wbg_stencilOpSeparate_321604240216c55c = function(e, t, r, _, c) {
      e.stencilOpSeparate(t >>> 0, r >>> 0, _ >>> 0, c >>> 0);
    }, n.wbg.__wbg_texParameteri_d1035ed45d6c5655 = function(e, t, r, _) {
      e.texParameteri(t >>> 0, r >>> 0, _);
    }, n.wbg.__wbg_uniform1f_8914cb45b3ad5887 = function(e, t, r) {
      e.uniform1f(t, r);
    }, n.wbg.__wbg_uniform1i_badd5ff70c0d30bf = function(e, t, r) {
      e.uniform1i(t, r);
    }, n.wbg.__wbg_uniform4f_fb56c7f4de64dd4c = function(e, t, r, _, c, o) {
      e.uniform4f(t, r, _, c, o);
    }, n.wbg.__wbg_useProgram_c637e43f9cd4c07a = function(e, t) {
      e.useProgram(t);
    }, n.wbg.__wbg_vertexAttribPointer_c25e4c5ed17f8a1d = function(e, t, r, _, c, o, a) {
      e.vertexAttribPointer(t >>> 0, r, _ >>> 0, c !== 0, o, a);
    }, n.wbg.__wbg_viewport_221ade2aef6032c8 = function(e, t, r, _, c) {
      e.viewport(t, r, _, c);
    }, n.wbg.__wbg_getSupportedProfiles_904a0392ad42295b = function(e) {
      const t = e.getSupportedProfiles();
      return g(t) ? 0 : s(t);
    }, n.wbg.__wbg_warn_2a7a92102b6acb7a = function(e, t) {
      console.warn(i(e, t));
    }, n.wbg.__wbg_info_78dce4847f0aad0b = function(e, t) {
      console.info(i(e, t));
    }, n.wbg.__wbg_debug_7bd96b976ecb446b = function(e, t) {
      console.debug(i(e, t));
    }, n.wbg.__wbg_trace_c877763d80e41ee1 = function(e, t) {
      console.trace(i(e, t));
    }, n.wbg.__wbg_performance_e5eb61626698b7a4 = function(e) {
      return e.performance;
    }, n.wbg.__wbg_now_928014da6271b17c = function(e) {
      return e.now();
    }, n.wbg.__wbg_crypto_70a96de3b6b73dac = function(e) {
      return e.crypto;
    }, n.wbg.__wbg_process_dd1577445152112e = function(e) {
      return e.process;
    }, n.wbg.__wbg_versions_58036bec3add9e6f = function(e) {
      return e.versions;
    }, n.wbg.__wbg_node_6a9d28205ed5b0d8 = function(e) {
      return e.node;
    }, n.wbg.__wbg_msCrypto_adbc770ec9eca9c7 = function(e) {
      return e.msCrypto;
    }, n.wbg.__wbg_require_f05d779769764e82 = function() {
      return f(function() {
        return module.require;
      }, arguments);
    }, n.wbg.__wbg_randomFillSync_e950366c42764a07 = function() {
      return f(function(e, t) {
        e.randomFillSync(t);
      }, arguments);
    }, n.wbg.__wbg_getRandomValues_3774744e221a22ad = function() {
      return f(function(e, t) {
        e.getRandomValues(t);
      }, arguments);
    }, n.wbg.__wbg_get_bd8e338fbd5f5cc8 = function(e, t) {
      return e[t >>> 0];
    }, n.wbg.__wbg_length_cd7af8117672b8b8 = function(e) {
      return e.length;
    }, n.wbg.__wbg_new_16b304a2cfa7ff4a = function() {
      return new Array();
    }, n.wbg.__wbg_newnoargs_e258087cd0daa0ea = function(e, t) {
      return new Function(i(e, t));
    }, n.wbg.__wbg_next_40fc327bfc8770e6 = function(e) {
      return e.next;
    }, n.wbg.__wbg_next_196c84450b364254 = function() {
      return f(function(e) {
        return e.next();
      }, arguments);
    }, n.wbg.__wbg_done_298b57d23c0fc80c = function(e) {
      return e.done;
    }, n.wbg.__wbg_value_d93c65011f51a456 = function(e) {
      return e.value;
    }, n.wbg.__wbg_iterator_2cee6dadfd956dfa = function() {
      return Symbol.iterator;
    }, n.wbg.__wbg_get_e3c254076557e348 = function() {
      return f(function(e, t) {
        return Reflect.get(e, t);
      }, arguments);
    }, n.wbg.__wbg_call_27c0f87801dedf93 = function() {
      return f(function(e, t) {
        return e.call(t);
      }, arguments);
    }, n.wbg.__wbg_new_72fb9a18b5ae2624 = function() {
      return new Object();
    }, n.wbg.__wbg_self_ce0dbfc45cf2f5be = function() {
      return f(function() {
        return self.self;
      }, arguments);
    }, n.wbg.__wbg_window_c6fb939a7f436783 = function() {
      return f(function() {
        return window.window;
      }, arguments);
    }, n.wbg.__wbg_globalThis_d1e6af4856ba331b = function() {
      return f(function() {
        return globalThis.globalThis;
      }, arguments);
    }, n.wbg.__wbg_global_207b558942527489 = function() {
      return f(function() {
        return global.global;
      }, arguments);
    }, n.wbg.__wbg_at_c729a14f9fc27c62 = function(e, t) {
      return e.at(t);
    }, n.wbg.__wbg_set_d4638f722068f043 = function(e, t, r) {
      e[t >>> 0] = r;
    }, n.wbg.__wbg_includes_310a37f41280ae42 = function(e, t, r) {
      return e.includes(t, r);
    }, n.wbg.__wbg_isArray_2ab64d95e09ea0ae = function(e) {
      return Array.isArray(e);
    }, n.wbg.__wbg_of_4a2b313a453ec059 = function(e) {
      return Array.of(e);
    }, n.wbg.__wbg_push_a5b05aedc7234f9f = function(e, t) {
      return e.push(t);
    }, n.wbg.__wbg_instanceof_ArrayBuffer_836825be07d4c9d2 = function(e) {
      let t;
      try {
        t = e instanceof ArrayBuffer;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_instanceof_Error_e20bb56fd5591a93 = function(e) {
      let t;
      try {
        t = e instanceof Error;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_new_28c511d9baebfa89 = function(e, t) {
      return new Error(i(e, t));
    }, n.wbg.__wbg_toString_ffe4c9ea3b3532e9 = function(e) {
      return e.toString();
    }, n.wbg.__wbg_call_b3ca7c6051f9bec1 = function() {
      return f(function(e, t, r) {
        return e.call(t, r);
      }, arguments);
    }, n.wbg.__wbg_isSafeInteger_f7b04ef02296c4d2 = function(e) {
      return Number.isSafeInteger(e);
    }, n.wbg.__wbg_getTime_2bc4375165f02d15 = function(e) {
      return e.getTime();
    }, n.wbg.__wbg_getTimezoneOffset_38257122e236c190 = function(e) {
      return e.getTimezoneOffset();
    }, n.wbg.__wbg_new_cf3ec55744a78578 = function(e) {
      return new Date(e);
    }, n.wbg.__wbg_new0_7d84e5b2cd9fdc73 = function() {
      return /* @__PURE__ */ new Date();
    }, n.wbg.__wbg_now_3014639a94423537 = function() {
      return Date.now();
    }, n.wbg.__wbg_instanceof_Object_71ca3c0a59266746 = function(e) {
      let t;
      try {
        t = e instanceof Object;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_entries_95cc2c823b285a09 = function(e) {
      return Object.entries(e);
    }, n.wbg.__wbg_is_010fdc0f4ab96916 = function(e, t) {
      return Object.is(e, t);
    }, n.wbg.__wbg_toString_c816a20ab859d0c1 = function(e) {
      return e.toString();
    }, n.wbg.__wbg_valueOf_a0b7c836f68a054b = function(e) {
      return e.valueOf();
    }, n.wbg.__wbg_instanceof_TypeError_6134172734e39ae0 = function(e) {
      let t;
      try {
        t = e instanceof TypeError;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_new_5dd86ebc917d9f52 = function(e, t) {
      return new TypeError(i(e, t));
    }, n.wbg.__wbg_new_81740750da40724f = function(e, t) {
      try {
        var r = { a: e, b: t }, _ = (o, a) => {
          const w = r.a;
          r.a = 0;
          try {
            return ne(w, r.b, o, a);
          } finally {
            r.a = w;
          }
        };
        return new Promise(_);
      } finally {
        r.a = r.b = 0;
      }
    }, n.wbg.__wbg_resolve_b0083a7967828ec8 = function(e) {
      return Promise.resolve(e);
    }, n.wbg.__wbg_catch_0260e338d10f79ae = function(e, t) {
      return e.catch(t);
    }, n.wbg.__wbg_then_0c86a60e8fcfe9f6 = function(e, t) {
      return e.then(t);
    }, n.wbg.__wbg_then_a73caa9a87991566 = function(e, t, r) {
      return e.then(t, r);
    }, n.wbg.__wbg_buffer_12d079cc21e14bdb = function(e) {
      return e.buffer;
    }, n.wbg.__wbg_newwithbyteoffsetandlength_41559f654c4e743c = function(e, t, r) {
      return new Int8Array(e, t >>> 0, r >>> 0);
    }, n.wbg.__wbg_newwithbyteoffsetandlength_4bea9f904a7e0aef = function(e, t, r) {
      return new Int16Array(e, t >>> 0, r >>> 0);
    }, n.wbg.__wbg_newwithbyteoffsetandlength_425360430a1c8206 = function(e, t, r) {
      return new Int32Array(e, t >>> 0, r >>> 0);
    }, n.wbg.__wbg_newwithbyteoffsetandlength_aa4a17c33a06e5cb = function(e, t, r) {
      return new Uint8Array(e, t >>> 0, r >>> 0);
    }, n.wbg.__wbg_new_63b92bc8671ed464 = function(e) {
      return new Uint8Array(e);
    }, n.wbg.__wbg_set_a47bac70306a19a7 = function(e, t, r) {
      e.set(t, r >>> 0);
    }, n.wbg.__wbg_length_c20a40f15020d68a = function(e) {
      return e.length;
    }, n.wbg.__wbg_newwithbyteoffsetandlength_9fd64654bc0b0817 = function(e, t, r) {
      return new Uint16Array(e, t >>> 0, r >>> 0);
    }, n.wbg.__wbg_newwithbyteoffsetandlength_3125852e5a7fbcff = function(e, t, r) {
      return new Uint32Array(e, t >>> 0, r >>> 0);
    }, n.wbg.__wbg_newwithbyteoffsetandlength_4a659d079a1650e0 = function(e, t, r) {
      return new Float32Array(e, t >>> 0, r >>> 0);
    }, n.wbg.__wbg_instanceof_Uint8Array_2b3bbecd033d19f6 = function(e) {
      let t;
      try {
        t = e instanceof Uint8Array;
      } catch {
        t = !1;
      }
      return t;
    }, n.wbg.__wbg_newwithlength_e9b4878cebadb3d3 = function(e) {
      return new Uint8Array(e >>> 0);
    }, n.wbg.__wbg_buffer_dd7f74bc60f1faab = function(e) {
      return e.buffer;
    }, n.wbg.__wbg_subarray_a1f73cd4b5b42fe1 = function(e, t, r) {
      return e.subarray(t >>> 0, r >>> 0);
    }, n.wbg.__wbg_byteLength_58f7b4fab1919d44 = function(e) {
      return e.byteLength;
    }, n.wbg.__wbg_byteOffset_81d60f7392524f62 = function(e) {
      return e.byteOffset;
    }, n.wbg.__wbg_set_1f9b04f170055d33 = function() {
      return f(function(e, t, r) {
        return Reflect.set(e, t, r);
      }, arguments);
    }, n.wbg.__wbindgen_debug_string = function(e, t) {
      const r = C(t), _ = m(r, b.__wbindgen_malloc, b.__wbindgen_realloc), c = d;
      u()[e / 4 + 1] = c, u()[e / 4 + 0] = _;
    }, n.wbg.__wbindgen_throw = function(e, t) {
      throw new Error(i(e, t));
    }, n.wbg.__wbindgen_memory = function() {
      return b.memory;
    }, n.wbg.__wbindgen_closure_wrapper1420 = function(e, t, r) {
      return x(e, t, 158, K);
    }, n.wbg.__wbindgen_closure_wrapper1422 = function(e, t, r) {
      return x(e, t, 158, Q);
    }, n.wbg.__wbindgen_closure_wrapper5270 = function(e, t, r) {
      return x(e, t, 1810, N);
    }, n.wbg.__wbindgen_closure_wrapper12713 = function(e, t, r) {
      return x(e, t, 5314, W);
    }, n.wbg.__wbindgen_closure_wrapper12715 = function(e, t, r) {
      return x(e, t, 5314, W);
    }, n.wbg.__wbindgen_closure_wrapper12717 = function(e, t, r) {
      return x(e, t, 5314, X);
    }, n.wbg.__wbindgen_closure_wrapper19869 = function(e, t, r) {
      return x(e, t, 8039, U);
    }, n.wbg.__wbindgen_closure_wrapper19871 = function(e, t, r) {
      return x(e, t, 8039, U);
    }, n.wbg.__wbindgen_closure_wrapper28758 = function(e, t, r) {
      return x(e, t, 11635, R);
    }, n.wbg.__wbindgen_closure_wrapper28760 = function(e, t, r) {
      return x(e, t, 11635, R);
    }, n.wbg.__wbindgen_closure_wrapper28762 = function(e, t, r) {
      return x(e, t, 11635, R);
    }, n.wbg.__wbindgen_closure_wrapper28764 = function(e, t, r) {
      return x(e, t, 11635, R);
    }, n.wbg.__wbindgen_closure_wrapper34662 = function(e, t, r) {
      return x(e, t, 14104, Y);
    }, n.wbg.__wbindgen_closure_wrapper35859 = function(e, t, r) {
      return x(e, t, 14829, $);
    }, n.wbg.__wbindgen_closure_wrapper35921 = function(e, t, r) {
      return x(e, t, 14842, Z);
    }, n.wbg.__wbindgen_init_externref_table = function() {
      const e = b.__wbindgen_export_2, t = e.grow(4);
      e.set(0, void 0), e.set(t + 0, void 0), e.set(t + 1, null), e.set(t + 2, !0), e.set(t + 3, !1);
    }, n;
  }
  function q(n, e) {
    return b = n.exports, L.__wbindgen_wasm_module = e, k = null, T = null, P = null, D = null, A = null, b.__wbindgen_start(), b;
  }
  function ge(n) {
    if (b !== void 0)
      return b;
    const e = G();
    n instanceof WebAssembly.Module || (n = new WebAssembly.Module(n));
    const t = new WebAssembly.Instance(n, e);
    return q(t, n);
  }
  async function L(n) {
    if (b !== void 0)
      return b;
    const e = G();
    (typeof n == "string" || typeof Request == "function" && n instanceof Request || typeof URL == "function" && n instanceof URL) && (n = fetch(n));
    const { instance: t, module: r } = await ie(await n, e);
    return q(t, r);
  }
  function we() {
    L.__wbindgen_wasm_module = null, b = null, k = null, T = null, P = null, D = null, A = null;
  }
  return Object.assign(L, { initSync: ge, deinit: we }, I);
}
export {
  se as default
};
