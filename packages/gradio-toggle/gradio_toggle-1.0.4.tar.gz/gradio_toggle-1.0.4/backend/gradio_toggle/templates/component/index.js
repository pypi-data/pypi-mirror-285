function ue() {
}
function Jt(l, e) {
  return l != l ? e == e : l !== e || l && typeof l == "object" || typeof l == "function";
}
function Qt(l, ...e) {
  if (l == null) {
    for (const n of e)
      n(void 0);
    return ue;
  }
  const t = l.subscribe(...e);
  return t.unsubscribe ? () => t.unsubscribe() : t;
}
function Wt(l) {
  let e;
  return Qt(l, (t) => e = t)(), e;
}
const wt = typeof window < "u";
let Xe = wt ? () => window.performance.now() : () => Date.now(), kt = wt ? (l) => requestAnimationFrame(l) : ue;
const se = /* @__PURE__ */ new Set();
function vt(l) {
  se.forEach((e) => {
    e.c(l) || (se.delete(e), e.f());
  }), se.size !== 0 && kt(vt);
}
function xt(l) {
  let e;
  return se.size === 0 && kt(vt), {
    promise: new Promise((t) => {
      se.add(e = { c: l, f: t });
    }),
    abort() {
      se.delete(e);
    }
  };
}
const le = [];
function pt(l, e = ue) {
  let t;
  const n = /* @__PURE__ */ new Set();
  function i(r) {
    if (Jt(l, r) && (l = r, t)) {
      const a = !le.length;
      for (const o of n)
        o[1](), le.push(o, l);
      if (a) {
        for (let o = 0; o < le.length; o += 2)
          le[o][0](le[o + 1]);
        le.length = 0;
      }
    }
  }
  function f(r) {
    i(r(l));
  }
  function s(r, a = ue) {
    const o = [r, a];
    return n.add(o), n.size === 1 && (t = e(i, f) || ue), r(l), () => {
      n.delete(o), n.size === 0 && t && (t(), t = null);
    };
  }
  return { set: i, update: f, subscribe: s };
}
function Ye(l) {
  return Object.prototype.toString.call(l) === "[object Date]";
}
function Ne(l, e, t, n) {
  if (typeof t == "number" || Ye(t)) {
    const i = n - t, f = (t - e) / (l.dt || 1 / 60), s = l.opts.stiffness * i, r = l.opts.damping * f, a = (s - r) * l.inv_mass, o = (f + a) * l.dt;
    return Math.abs(o) < l.opts.precision && Math.abs(i) < l.opts.precision ? n : (l.settled = !1, Ye(t) ? new Date(t.getTime() + o) : t + o);
  } else {
    if (Array.isArray(t))
      return t.map(
        (i, f) => Ne(l, e[f], t[f], n[f])
      );
    if (typeof t == "object") {
      const i = {};
      for (const f in t)
        i[f] = Ne(l, e[f], t[f], n[f]);
      return i;
    } else
      throw new Error(`Cannot spring ${typeof t} values`);
  }
}
function Ge(l, e = {}) {
  const t = pt(l), { stiffness: n = 0.15, damping: i = 0.8, precision: f = 0.01 } = e;
  let s, r, a, o = l, u = l, m = 1, b = 0, g = !1;
  function v(C, k = {}) {
    u = C;
    const d = a = {};
    return l == null || k.hard || q.stiffness >= 1 && q.damping >= 1 ? (g = !0, s = Xe(), o = C, t.set(l = u), Promise.resolve()) : (k.soft && (b = 1 / ((k.soft === !0 ? 0.5 : +k.soft) * 60), m = 0), r || (s = Xe(), g = !1, r = xt((c) => {
      if (g)
        return g = !1, r = null, !1;
      m = Math.min(m + b, 1);
      const h = {
        inv_mass: m,
        opts: q,
        settled: !0,
        dt: (c - s) * 60 / 1e3
      }, L = Ne(h, o, l, u);
      return s = c, o = l, t.set(l = L), h.settled && (r = null), !h.settled;
    })), new Promise((c) => {
      r.promise.then(() => {
        d === a && c();
      });
    }));
  }
  const q = {
    set: v,
    update: (C, k) => v(C(u, l), k),
    subscribe: t.subscribe,
    stiffness: n,
    damping: i,
    precision: f
  };
  return q;
}
const {
  SvelteComponent: $t,
  assign: el,
  create_slot: tl,
  detach: ll,
  element: nl,
  get_all_dirty_from_scope: il,
  get_slot_changes: fl,
  get_spread_update: sl,
  init: ol,
  insert: al,
  safe_not_equal: rl,
  set_dynamic_element_data: Ke,
  set_style: N,
  toggle_class: P,
  transition_in: yt,
  transition_out: Ct,
  update_slot_base: ul
} = window.__gradio__svelte__internal;
function cl(l) {
  let e, t, n;
  const i = (
    /*#slots*/
    l[18].default
  ), f = tl(
    i,
    l,
    /*$$scope*/
    l[17],
    null
  );
  let s = [
    { "data-testid": (
      /*test_id*/
      l[7]
    ) },
    { id: (
      /*elem_id*/
      l[2]
    ) },
    {
      class: t = "block " + /*elem_classes*/
      l[3].join(" ") + " svelte-nl1om8"
    }
  ], r = {};
  for (let a = 0; a < s.length; a += 1)
    r = el(r, s[a]);
  return {
    c() {
      e = nl(
        /*tag*/
        l[14]
      ), f && f.c(), Ke(
        /*tag*/
        l[14]
      )(e, r), P(
        e,
        "hidden",
        /*visible*/
        l[10] === !1
      ), P(
        e,
        "padded",
        /*padding*/
        l[6]
      ), P(
        e,
        "border_focus",
        /*border_mode*/
        l[5] === "focus"
      ), P(
        e,
        "border_contrast",
        /*border_mode*/
        l[5] === "contrast"
      ), P(e, "hide-container", !/*explicit_call*/
      l[8] && !/*container*/
      l[9]), N(
        e,
        "height",
        /*get_dimension*/
        l[15](
          /*height*/
          l[0]
        )
      ), N(e, "width", typeof /*width*/
      l[1] == "number" ? `calc(min(${/*width*/
      l[1]}px, 100%))` : (
        /*get_dimension*/
        l[15](
          /*width*/
          l[1]
        )
      )), N(
        e,
        "border-style",
        /*variant*/
        l[4]
      ), N(
        e,
        "overflow",
        /*allow_overflow*/
        l[11] ? "visible" : "hidden"
      ), N(
        e,
        "flex-grow",
        /*scale*/
        l[12]
      ), N(e, "min-width", `calc(min(${/*min_width*/
      l[13]}px, 100%))`), N(e, "border-width", "var(--block-border-width)");
    },
    m(a, o) {
      al(a, e, o), f && f.m(e, null), n = !0;
    },
    p(a, o) {
      f && f.p && (!n || o & /*$$scope*/
      131072) && ul(
        f,
        i,
        a,
        /*$$scope*/
        a[17],
        n ? fl(
          i,
          /*$$scope*/
          a[17],
          o,
          null
        ) : il(
          /*$$scope*/
          a[17]
        ),
        null
      ), Ke(
        /*tag*/
        a[14]
      )(e, r = sl(s, [
        (!n || o & /*test_id*/
        128) && { "data-testid": (
          /*test_id*/
          a[7]
        ) },
        (!n || o & /*elem_id*/
        4) && { id: (
          /*elem_id*/
          a[2]
        ) },
        (!n || o & /*elem_classes*/
        8 && t !== (t = "block " + /*elem_classes*/
        a[3].join(" ") + " svelte-nl1om8")) && { class: t }
      ])), P(
        e,
        "hidden",
        /*visible*/
        a[10] === !1
      ), P(
        e,
        "padded",
        /*padding*/
        a[6]
      ), P(
        e,
        "border_focus",
        /*border_mode*/
        a[5] === "focus"
      ), P(
        e,
        "border_contrast",
        /*border_mode*/
        a[5] === "contrast"
      ), P(e, "hide-container", !/*explicit_call*/
      a[8] && !/*container*/
      a[9]), o & /*height*/
      1 && N(
        e,
        "height",
        /*get_dimension*/
        a[15](
          /*height*/
          a[0]
        )
      ), o & /*width*/
      2 && N(e, "width", typeof /*width*/
      a[1] == "number" ? `calc(min(${/*width*/
      a[1]}px, 100%))` : (
        /*get_dimension*/
        a[15](
          /*width*/
          a[1]
        )
      )), o & /*variant*/
      16 && N(
        e,
        "border-style",
        /*variant*/
        a[4]
      ), o & /*allow_overflow*/
      2048 && N(
        e,
        "overflow",
        /*allow_overflow*/
        a[11] ? "visible" : "hidden"
      ), o & /*scale*/
      4096 && N(
        e,
        "flex-grow",
        /*scale*/
        a[12]
      ), o & /*min_width*/
      8192 && N(e, "min-width", `calc(min(${/*min_width*/
      a[13]}px, 100%))`);
    },
    i(a) {
      n || (yt(f, a), n = !0);
    },
    o(a) {
      Ct(f, a), n = !1;
    },
    d(a) {
      a && ll(e), f && f.d(a);
    }
  };
}
function _l(l) {
  let e, t = (
    /*tag*/
    l[14] && cl(l)
  );
  return {
    c() {
      t && t.c();
    },
    m(n, i) {
      t && t.m(n, i), e = !0;
    },
    p(n, [i]) {
      /*tag*/
      n[14] && t.p(n, i);
    },
    i(n) {
      e || (yt(t, n), e = !0);
    },
    o(n) {
      Ct(t, n), e = !1;
    },
    d(n) {
      t && t.d(n);
    }
  };
}
function dl(l, e, t) {
  let { $$slots: n = {}, $$scope: i } = e, { height: f = void 0 } = e, { width: s = void 0 } = e, { elem_id: r = "" } = e, { elem_classes: a = [] } = e, { variant: o = "solid" } = e, { border_mode: u = "base" } = e, { padding: m = !0 } = e, { type: b = "normal" } = e, { test_id: g = void 0 } = e, { explicit_call: v = !1 } = e, { container: q = !0 } = e, { visible: C = !0 } = e, { allow_overflow: k = !0 } = e, { scale: d = null } = e, { min_width: c = 0 } = e, h = b === "fieldset" ? "fieldset" : "div";
  const L = (_) => {
    if (_ !== void 0) {
      if (typeof _ == "number")
        return _ + "px";
      if (typeof _ == "string")
        return _;
    }
  };
  return l.$$set = (_) => {
    "height" in _ && t(0, f = _.height), "width" in _ && t(1, s = _.width), "elem_id" in _ && t(2, r = _.elem_id), "elem_classes" in _ && t(3, a = _.elem_classes), "variant" in _ && t(4, o = _.variant), "border_mode" in _ && t(5, u = _.border_mode), "padding" in _ && t(6, m = _.padding), "type" in _ && t(16, b = _.type), "test_id" in _ && t(7, g = _.test_id), "explicit_call" in _ && t(8, v = _.explicit_call), "container" in _ && t(9, q = _.container), "visible" in _ && t(10, C = _.visible), "allow_overflow" in _ && t(11, k = _.allow_overflow), "scale" in _ && t(12, d = _.scale), "min_width" in _ && t(13, c = _.min_width), "$$scope" in _ && t(17, i = _.$$scope);
  }, [
    f,
    s,
    r,
    a,
    o,
    u,
    m,
    g,
    v,
    q,
    C,
    k,
    d,
    c,
    h,
    L,
    b,
    i,
    n
  ];
}
class ml extends $t {
  constructor(e) {
    super(), ol(this, e, dl, _l, rl, {
      height: 0,
      width: 1,
      elem_id: 2,
      elem_classes: 3,
      variant: 4,
      border_mode: 5,
      padding: 6,
      type: 16,
      test_id: 7,
      explicit_call: 8,
      container: 9,
      visible: 10,
      allow_overflow: 11,
      scale: 12,
      min_width: 13
    });
  }
}
const {
  SvelteComponent: bl,
  append: Te,
  attr: O,
  bubble: gl,
  create_component: hl,
  destroy_component: wl,
  detach: qt,
  element: Ze,
  init: kl,
  insert: Ft,
  listen: vl,
  mount_component: pl,
  safe_not_equal: yl,
  set_data: Cl,
  set_style: ne,
  space: ql,
  text: Fl,
  toggle_class: V,
  transition_in: zl,
  transition_out: Ll
} = window.__gradio__svelte__internal;
function Oe(l) {
  let e, t;
  return {
    c() {
      e = Ze("span"), t = Fl(
        /*label*/
        l[1]
      ), O(e, "class", "svelte-1lrphxw");
    },
    m(n, i) {
      Ft(n, e, i), Te(e, t);
    },
    p(n, i) {
      i & /*label*/
      2 && Cl(
        t,
        /*label*/
        n[1]
      );
    },
    d(n) {
      n && qt(e);
    }
  };
}
function Sl(l) {
  let e, t, n, i, f, s, r, a = (
    /*show_label*/
    l[2] && Oe(l)
  );
  return i = new /*Icon*/
  l[0]({}), {
    c() {
      e = Ze("button"), a && a.c(), t = ql(), n = Ze("div"), hl(i.$$.fragment), O(n, "class", "svelte-1lrphxw"), V(
        n,
        "small",
        /*size*/
        l[4] === "small"
      ), V(
        n,
        "large",
        /*size*/
        l[4] === "large"
      ), V(
        n,
        "medium",
        /*size*/
        l[4] === "medium"
      ), e.disabled = /*disabled*/
      l[7], O(
        e,
        "aria-label",
        /*label*/
        l[1]
      ), O(
        e,
        "aria-haspopup",
        /*hasPopup*/
        l[8]
      ), O(
        e,
        "title",
        /*label*/
        l[1]
      ), O(e, "class", "svelte-1lrphxw"), V(
        e,
        "pending",
        /*pending*/
        l[3]
      ), V(
        e,
        "padded",
        /*padded*/
        l[5]
      ), V(
        e,
        "highlight",
        /*highlight*/
        l[6]
      ), V(
        e,
        "transparent",
        /*transparent*/
        l[9]
      ), ne(e, "color", !/*disabled*/
      l[7] && /*_color*/
      l[12] ? (
        /*_color*/
        l[12]
      ) : "var(--block-label-text-color)"), ne(e, "--bg-color", /*disabled*/
      l[7] ? "auto" : (
        /*background*/
        l[10]
      )), ne(
        e,
        "margin-left",
        /*offset*/
        l[11] + "px"
      );
    },
    m(o, u) {
      Ft(o, e, u), a && a.m(e, null), Te(e, t), Te(e, n), pl(i, n, null), f = !0, s || (r = vl(
        e,
        "click",
        /*click_handler*/
        l[14]
      ), s = !0);
    },
    p(o, [u]) {
      /*show_label*/
      o[2] ? a ? a.p(o, u) : (a = Oe(o), a.c(), a.m(e, t)) : a && (a.d(1), a = null), (!f || u & /*size*/
      16) && V(
        n,
        "small",
        /*size*/
        o[4] === "small"
      ), (!f || u & /*size*/
      16) && V(
        n,
        "large",
        /*size*/
        o[4] === "large"
      ), (!f || u & /*size*/
      16) && V(
        n,
        "medium",
        /*size*/
        o[4] === "medium"
      ), (!f || u & /*disabled*/
      128) && (e.disabled = /*disabled*/
      o[7]), (!f || u & /*label*/
      2) && O(
        e,
        "aria-label",
        /*label*/
        o[1]
      ), (!f || u & /*hasPopup*/
      256) && O(
        e,
        "aria-haspopup",
        /*hasPopup*/
        o[8]
      ), (!f || u & /*label*/
      2) && O(
        e,
        "title",
        /*label*/
        o[1]
      ), (!f || u & /*pending*/
      8) && V(
        e,
        "pending",
        /*pending*/
        o[3]
      ), (!f || u & /*padded*/
      32) && V(
        e,
        "padded",
        /*padded*/
        o[5]
      ), (!f || u & /*highlight*/
      64) && V(
        e,
        "highlight",
        /*highlight*/
        o[6]
      ), (!f || u & /*transparent*/
      512) && V(
        e,
        "transparent",
        /*transparent*/
        o[9]
      ), u & /*disabled, _color*/
      4224 && ne(e, "color", !/*disabled*/
      o[7] && /*_color*/
      o[12] ? (
        /*_color*/
        o[12]
      ) : "var(--block-label-text-color)"), u & /*disabled, background*/
      1152 && ne(e, "--bg-color", /*disabled*/
      o[7] ? "auto" : (
        /*background*/
        o[10]
      )), u & /*offset*/
      2048 && ne(
        e,
        "margin-left",
        /*offset*/
        o[11] + "px"
      );
    },
    i(o) {
      f || (zl(i.$$.fragment, o), f = !0);
    },
    o(o) {
      Ll(i.$$.fragment, o), f = !1;
    },
    d(o) {
      o && qt(e), a && a.d(), wl(i), s = !1, r();
    }
  };
}
function Ml(l, e, t) {
  let n, { Icon: i } = e, { label: f = "" } = e, { show_label: s = !1 } = e, { pending: r = !1 } = e, { size: a = "small" } = e, { padded: o = !0 } = e, { highlight: u = !1 } = e, { disabled: m = !1 } = e, { hasPopup: b = !1 } = e, { color: g = "var(--block-label-text-color)" } = e, { transparent: v = !1 } = e, { background: q = "var(--background-fill-primary)" } = e, { offset: C = 0 } = e;
  function k(d) {
    gl.call(this, l, d);
  }
  return l.$$set = (d) => {
    "Icon" in d && t(0, i = d.Icon), "label" in d && t(1, f = d.label), "show_label" in d && t(2, s = d.show_label), "pending" in d && t(3, r = d.pending), "size" in d && t(4, a = d.size), "padded" in d && t(5, o = d.padded), "highlight" in d && t(6, u = d.highlight), "disabled" in d && t(7, m = d.disabled), "hasPopup" in d && t(8, b = d.hasPopup), "color" in d && t(13, g = d.color), "transparent" in d && t(9, v = d.transparent), "background" in d && t(10, q = d.background), "offset" in d && t(11, C = d.offset);
  }, l.$$.update = () => {
    l.$$.dirty & /*highlight, color*/
    8256 && t(12, n = u ? "var(--color-accent)" : g);
  }, [
    i,
    f,
    s,
    r,
    a,
    o,
    u,
    m,
    b,
    v,
    q,
    C,
    n,
    g,
    k
  ];
}
class Vl extends bl {
  constructor(e) {
    super(), kl(this, e, Ml, Sl, yl, {
      Icon: 0,
      label: 1,
      show_label: 2,
      pending: 3,
      size: 4,
      padded: 5,
      highlight: 6,
      disabled: 7,
      hasPopup: 8,
      color: 13,
      transparent: 9,
      background: 10,
      offset: 11
    });
  }
}
const {
  SvelteComponent: Nl,
  append: Fe,
  attr: D,
  detach: Tl,
  init: Zl,
  insert: jl,
  noop: ze,
  safe_not_equal: Dl,
  set_style: X,
  svg_element: ge
} = window.__gradio__svelte__internal;
function El(l) {
  let e, t, n, i;
  return {
    c() {
      e = ge("svg"), t = ge("g"), n = ge("path"), i = ge("path"), D(n, "d", "M18,6L6.087,17.913"), X(n, "fill", "none"), X(n, "fill-rule", "nonzero"), X(n, "stroke-width", "2px"), D(t, "transform", "matrix(1.14096,-0.140958,-0.140958,1.14096,-0.0559523,0.0559523)"), D(i, "d", "M4.364,4.364L19.636,19.636"), X(i, "fill", "none"), X(i, "fill-rule", "nonzero"), X(i, "stroke-width", "2px"), D(e, "width", "100%"), D(e, "height", "100%"), D(e, "viewBox", "0 0 24 24"), D(e, "version", "1.1"), D(e, "xmlns", "http://www.w3.org/2000/svg"), D(e, "xmlns:xlink", "http://www.w3.org/1999/xlink"), D(e, "xml:space", "preserve"), D(e, "stroke", "currentColor"), X(e, "fill-rule", "evenodd"), X(e, "clip-rule", "evenodd"), X(e, "stroke-linecap", "round"), X(e, "stroke-linejoin", "round");
    },
    m(f, s) {
      jl(f, e, s), Fe(e, t), Fe(t, n), Fe(e, i);
    },
    p: ze,
    i: ze,
    o: ze,
    d(f) {
      f && Tl(e);
    }
  };
}
class Il extends Nl {
  constructor(e) {
    super(), Zl(this, e, null, El, Dl, {});
  }
}
const Bl = [
  { color: "red", primary: 600, secondary: 100 },
  { color: "green", primary: 600, secondary: 100 },
  { color: "blue", primary: 600, secondary: 100 },
  { color: "yellow", primary: 500, secondary: 100 },
  { color: "purple", primary: 600, secondary: 100 },
  { color: "teal", primary: 600, secondary: 100 },
  { color: "orange", primary: 600, secondary: 100 },
  { color: "cyan", primary: 600, secondary: 100 },
  { color: "lime", primary: 500, secondary: 100 },
  { color: "pink", primary: 600, secondary: 100 }
], Re = {
  inherit: "inherit",
  current: "currentColor",
  transparent: "transparent",
  black: "#000",
  white: "#fff",
  slate: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617"
  },
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
    950: "#030712"
  },
  zinc: {
    50: "#fafafa",
    100: "#f4f4f5",
    200: "#e4e4e7",
    300: "#d4d4d8",
    400: "#a1a1aa",
    500: "#71717a",
    600: "#52525b",
    700: "#3f3f46",
    800: "#27272a",
    900: "#18181b",
    950: "#09090b"
  },
  neutral: {
    50: "#fafafa",
    100: "#f5f5f5",
    200: "#e5e5e5",
    300: "#d4d4d4",
    400: "#a3a3a3",
    500: "#737373",
    600: "#525252",
    700: "#404040",
    800: "#262626",
    900: "#171717",
    950: "#0a0a0a"
  },
  stone: {
    50: "#fafaf9",
    100: "#f5f5f4",
    200: "#e7e5e4",
    300: "#d6d3d1",
    400: "#a8a29e",
    500: "#78716c",
    600: "#57534e",
    700: "#44403c",
    800: "#292524",
    900: "#1c1917",
    950: "#0c0a09"
  },
  red: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
    800: "#991b1b",
    900: "#7f1d1d",
    950: "#450a0a"
  },
  orange: {
    50: "#fff7ed",
    100: "#ffedd5",
    200: "#fed7aa",
    300: "#fdba74",
    400: "#fb923c",
    500: "#f97316",
    600: "#ea580c",
    700: "#c2410c",
    800: "#9a3412",
    900: "#7c2d12",
    950: "#431407"
  },
  amber: {
    50: "#fffbeb",
    100: "#fef3c7",
    200: "#fde68a",
    300: "#fcd34d",
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
    800: "#92400e",
    900: "#78350f",
    950: "#451a03"
  },
  yellow: {
    50: "#fefce8",
    100: "#fef9c3",
    200: "#fef08a",
    300: "#fde047",
    400: "#facc15",
    500: "#eab308",
    600: "#ca8a04",
    700: "#a16207",
    800: "#854d0e",
    900: "#713f12",
    950: "#422006"
  },
  lime: {
    50: "#f7fee7",
    100: "#ecfccb",
    200: "#d9f99d",
    300: "#bef264",
    400: "#a3e635",
    500: "#84cc16",
    600: "#65a30d",
    700: "#4d7c0f",
    800: "#3f6212",
    900: "#365314",
    950: "#1a2e05"
  },
  green: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
    800: "#166534",
    900: "#14532d",
    950: "#052e16"
  },
  emerald: {
    50: "#ecfdf5",
    100: "#d1fae5",
    200: "#a7f3d0",
    300: "#6ee7b7",
    400: "#34d399",
    500: "#10b981",
    600: "#059669",
    700: "#047857",
    800: "#065f46",
    900: "#064e3b",
    950: "#022c22"
  },
  teal: {
    50: "#f0fdfa",
    100: "#ccfbf1",
    200: "#99f6e4",
    300: "#5eead4",
    400: "#2dd4bf",
    500: "#14b8a6",
    600: "#0d9488",
    700: "#0f766e",
    800: "#115e59",
    900: "#134e4a",
    950: "#042f2e"
  },
  cyan: {
    50: "#ecfeff",
    100: "#cffafe",
    200: "#a5f3fc",
    300: "#67e8f9",
    400: "#22d3ee",
    500: "#06b6d4",
    600: "#0891b2",
    700: "#0e7490",
    800: "#155e75",
    900: "#164e63",
    950: "#083344"
  },
  sky: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0ea5e9",
    600: "#0284c7",
    700: "#0369a1",
    800: "#075985",
    900: "#0c4a6e",
    950: "#082f49"
  },
  blue: {
    50: "#eff6ff",
    100: "#dbeafe",
    200: "#bfdbfe",
    300: "#93c5fd",
    400: "#60a5fa",
    500: "#3b82f6",
    600: "#2563eb",
    700: "#1d4ed8",
    800: "#1e40af",
    900: "#1e3a8a",
    950: "#172554"
  },
  indigo: {
    50: "#eef2ff",
    100: "#e0e7ff",
    200: "#c7d2fe",
    300: "#a5b4fc",
    400: "#818cf8",
    500: "#6366f1",
    600: "#4f46e5",
    700: "#4338ca",
    800: "#3730a3",
    900: "#312e81",
    950: "#1e1b4b"
  },
  violet: {
    50: "#f5f3ff",
    100: "#ede9fe",
    200: "#ddd6fe",
    300: "#c4b5fd",
    400: "#a78bfa",
    500: "#8b5cf6",
    600: "#7c3aed",
    700: "#6d28d9",
    800: "#5b21b6",
    900: "#4c1d95",
    950: "#2e1065"
  },
  purple: {
    50: "#faf5ff",
    100: "#f3e8ff",
    200: "#e9d5ff",
    300: "#d8b4fe",
    400: "#c084fc",
    500: "#a855f7",
    600: "#9333ea",
    700: "#7e22ce",
    800: "#6b21a8",
    900: "#581c87",
    950: "#3b0764"
  },
  fuchsia: {
    50: "#fdf4ff",
    100: "#fae8ff",
    200: "#f5d0fe",
    300: "#f0abfc",
    400: "#e879f9",
    500: "#d946ef",
    600: "#c026d3",
    700: "#a21caf",
    800: "#86198f",
    900: "#701a75",
    950: "#4a044e"
  },
  pink: {
    50: "#fdf2f8",
    100: "#fce7f3",
    200: "#fbcfe8",
    300: "#f9a8d4",
    400: "#f472b6",
    500: "#ec4899",
    600: "#db2777",
    700: "#be185d",
    800: "#9d174d",
    900: "#831843",
    950: "#500724"
  },
  rose: {
    50: "#fff1f2",
    100: "#ffe4e6",
    200: "#fecdd3",
    300: "#fda4af",
    400: "#fb7185",
    500: "#f43f5e",
    600: "#e11d48",
    700: "#be123c",
    800: "#9f1239",
    900: "#881337",
    950: "#4c0519"
  }
};
Bl.reduce(
  (l, { color: e, primary: t, secondary: n }) => ({
    ...l,
    [e]: {
      primary: Re[e][t],
      secondary: Re[e][n]
    }
  }),
  {}
);
function fe(l) {
  let e = ["", "k", "M", "G", "T", "P", "E", "Z"], t = 0;
  for (; l > 1e3 && t < e.length - 1; )
    l /= 1e3, t++;
  let n = e[t];
  return (Number.isInteger(l) ? l : l.toFixed(1)) + n;
}
const {
  SvelteComponent: Al,
  append: E,
  attr: F,
  component_subscribe: Ue,
  detach: Pl,
  element: Xl,
  init: Yl,
  insert: Gl,
  noop: He,
  safe_not_equal: Kl,
  set_style: he,
  svg_element: I,
  toggle_class: Je
} = window.__gradio__svelte__internal, { onMount: Ol } = window.__gradio__svelte__internal;
function Rl(l) {
  let e, t, n, i, f, s, r, a, o, u, m, b;
  return {
    c() {
      e = Xl("div"), t = I("svg"), n = I("g"), i = I("path"), f = I("path"), s = I("path"), r = I("path"), a = I("g"), o = I("path"), u = I("path"), m = I("path"), b = I("path"), F(i, "d", "M255.926 0.754768L509.702 139.936V221.027L255.926 81.8465V0.754768Z"), F(i, "fill", "#FF7C00"), F(i, "fill-opacity", "0.4"), F(i, "class", "svelte-43sxxs"), F(f, "d", "M509.69 139.936L254.981 279.641V361.255L509.69 221.55V139.936Z"), F(f, "fill", "#FF7C00"), F(f, "class", "svelte-43sxxs"), F(s, "d", "M0.250138 139.937L254.981 279.641V361.255L0.250138 221.55V139.937Z"), F(s, "fill", "#FF7C00"), F(s, "fill-opacity", "0.4"), F(s, "class", "svelte-43sxxs"), F(r, "d", "M255.923 0.232622L0.236328 139.936V221.55L255.923 81.8469V0.232622Z"), F(r, "fill", "#FF7C00"), F(r, "class", "svelte-43sxxs"), he(n, "transform", "translate(" + /*$top*/
      l[1][0] + "px, " + /*$top*/
      l[1][1] + "px)"), F(o, "d", "M255.926 141.5L509.702 280.681V361.773L255.926 222.592V141.5Z"), F(o, "fill", "#FF7C00"), F(o, "fill-opacity", "0.4"), F(o, "class", "svelte-43sxxs"), F(u, "d", "M509.69 280.679L254.981 420.384V501.998L509.69 362.293V280.679Z"), F(u, "fill", "#FF7C00"), F(u, "class", "svelte-43sxxs"), F(m, "d", "M0.250138 280.681L254.981 420.386V502L0.250138 362.295V280.681Z"), F(m, "fill", "#FF7C00"), F(m, "fill-opacity", "0.4"), F(m, "class", "svelte-43sxxs"), F(b, "d", "M255.923 140.977L0.236328 280.68V362.294L255.923 222.591V140.977Z"), F(b, "fill", "#FF7C00"), F(b, "class", "svelte-43sxxs"), he(a, "transform", "translate(" + /*$bottom*/
      l[2][0] + "px, " + /*$bottom*/
      l[2][1] + "px)"), F(t, "viewBox", "-1200 -1200 3000 3000"), F(t, "fill", "none"), F(t, "xmlns", "http://www.w3.org/2000/svg"), F(t, "class", "svelte-43sxxs"), F(e, "class", "svelte-43sxxs"), Je(
        e,
        "margin",
        /*margin*/
        l[0]
      );
    },
    m(g, v) {
      Gl(g, e, v), E(e, t), E(t, n), E(n, i), E(n, f), E(n, s), E(n, r), E(t, a), E(a, o), E(a, u), E(a, m), E(a, b);
    },
    p(g, [v]) {
      v & /*$top*/
      2 && he(n, "transform", "translate(" + /*$top*/
      g[1][0] + "px, " + /*$top*/
      g[1][1] + "px)"), v & /*$bottom*/
      4 && he(a, "transform", "translate(" + /*$bottom*/
      g[2][0] + "px, " + /*$bottom*/
      g[2][1] + "px)"), v & /*margin*/
      1 && Je(
        e,
        "margin",
        /*margin*/
        g[0]
      );
    },
    i: He,
    o: He,
    d(g) {
      g && Pl(e);
    }
  };
}
function Ul(l, e, t) {
  let n, i;
  var f = this && this.__awaiter || function(g, v, q, C) {
    function k(d) {
      return d instanceof q ? d : new q(function(c) {
        c(d);
      });
    }
    return new (q || (q = Promise))(function(d, c) {
      function h(M) {
        try {
          _(C.next(M));
        } catch (K) {
          c(K);
        }
      }
      function L(M) {
        try {
          _(C.throw(M));
        } catch (K) {
          c(K);
        }
      }
      function _(M) {
        M.done ? d(M.value) : k(M.value).then(h, L);
      }
      _((C = C.apply(g, v || [])).next());
    });
  };
  let { margin: s = !0 } = e;
  const r = Ge([0, 0]);
  Ue(l, r, (g) => t(1, n = g));
  const a = Ge([0, 0]);
  Ue(l, a, (g) => t(2, i = g));
  let o;
  function u() {
    return f(this, void 0, void 0, function* () {
      yield Promise.all([r.set([125, 140]), a.set([-125, -140])]), yield Promise.all([r.set([-125, 140]), a.set([125, -140])]), yield Promise.all([r.set([-125, 0]), a.set([125, -0])]), yield Promise.all([r.set([125, 0]), a.set([-125, 0])]);
    });
  }
  function m() {
    return f(this, void 0, void 0, function* () {
      yield u(), o || m();
    });
  }
  function b() {
    return f(this, void 0, void 0, function* () {
      yield Promise.all([r.set([125, 0]), a.set([-125, 0])]), m();
    });
  }
  return Ol(() => (b(), () => o = !0)), l.$$set = (g) => {
    "margin" in g && t(0, s = g.margin);
  }, [s, n, i, r, a];
}
class Hl extends Al {
  constructor(e) {
    super(), Yl(this, e, Ul, Rl, Kl, { margin: 0 });
  }
}
const {
  SvelteComponent: Jl,
  append: x,
  attr: A,
  binding_callbacks: Qe,
  check_outros: je,
  create_component: zt,
  create_slot: Lt,
  destroy_component: St,
  destroy_each: Mt,
  detach: p,
  element: Y,
  empty: oe,
  ensure_array_like: ve,
  get_all_dirty_from_scope: Vt,
  get_slot_changes: Nt,
  group_outros: De,
  init: Ql,
  insert: y,
  mount_component: Tt,
  noop: Ee,
  safe_not_equal: Wl,
  set_data: j,
  set_style: H,
  space: Z,
  text: z,
  toggle_class: T,
  transition_in: B,
  transition_out: G,
  update_slot_base: Zt
} = window.__gradio__svelte__internal, { tick: xl } = window.__gradio__svelte__internal, { onDestroy: $l } = window.__gradio__svelte__internal, { createEventDispatcher: en } = window.__gradio__svelte__internal, tn = (l) => ({}), We = (l) => ({}), ln = (l) => ({}), xe = (l) => ({});
function $e(l, e, t) {
  const n = l.slice();
  return n[41] = e[t], n[43] = t, n;
}
function et(l, e, t) {
  const n = l.slice();
  return n[41] = e[t], n;
}
function nn(l) {
  let e, t, n, i, f = (
    /*i18n*/
    l[1]("common.error") + ""
  ), s, r, a;
  t = new Vl({
    props: {
      Icon: Il,
      label: (
        /*i18n*/
        l[1]("common.clear")
      ),
      disabled: !1
    }
  }), t.$on(
    "click",
    /*click_handler*/
    l[32]
  );
  const o = (
    /*#slots*/
    l[30].error
  ), u = Lt(
    o,
    l,
    /*$$scope*/
    l[29],
    We
  );
  return {
    c() {
      e = Y("div"), zt(t.$$.fragment), n = Z(), i = Y("span"), s = z(f), r = Z(), u && u.c(), A(e, "class", "clear-status svelte-v0wucf"), A(i, "class", "error svelte-v0wucf");
    },
    m(m, b) {
      y(m, e, b), Tt(t, e, null), y(m, n, b), y(m, i, b), x(i, s), y(m, r, b), u && u.m(m, b), a = !0;
    },
    p(m, b) {
      const g = {};
      b[0] & /*i18n*/
      2 && (g.label = /*i18n*/
      m[1]("common.clear")), t.$set(g), (!a || b[0] & /*i18n*/
      2) && f !== (f = /*i18n*/
      m[1]("common.error") + "") && j(s, f), u && u.p && (!a || b[0] & /*$$scope*/
      536870912) && Zt(
        u,
        o,
        m,
        /*$$scope*/
        m[29],
        a ? Nt(
          o,
          /*$$scope*/
          m[29],
          b,
          tn
        ) : Vt(
          /*$$scope*/
          m[29]
        ),
        We
      );
    },
    i(m) {
      a || (B(t.$$.fragment, m), B(u, m), a = !0);
    },
    o(m) {
      G(t.$$.fragment, m), G(u, m), a = !1;
    },
    d(m) {
      m && (p(e), p(n), p(i), p(r)), St(t), u && u.d(m);
    }
  };
}
function fn(l) {
  let e, t, n, i, f, s, r, a, o, u = (
    /*variant*/
    l[8] === "default" && /*show_eta_bar*/
    l[18] && /*show_progress*/
    l[6] === "full" && tt(l)
  );
  function m(c, h) {
    if (
      /*progress*/
      c[7]
    ) return an;
    if (
      /*queue_position*/
      c[2] !== null && /*queue_size*/
      c[3] !== void 0 && /*queue_position*/
      c[2] >= 0
    ) return on;
    if (
      /*queue_position*/
      c[2] === 0
    ) return sn;
  }
  let b = m(l), g = b && b(l), v = (
    /*timer*/
    l[5] && it(l)
  );
  const q = [_n, cn], C = [];
  function k(c, h) {
    return (
      /*last_progress_level*/
      c[15] != null ? 0 : (
        /*show_progress*/
        c[6] === "full" ? 1 : -1
      )
    );
  }
  ~(f = k(l)) && (s = C[f] = q[f](l));
  let d = !/*timer*/
  l[5] && ct(l);
  return {
    c() {
      u && u.c(), e = Z(), t = Y("div"), g && g.c(), n = Z(), v && v.c(), i = Z(), s && s.c(), r = Z(), d && d.c(), a = oe(), A(t, "class", "progress-text svelte-v0wucf"), T(
        t,
        "meta-text-center",
        /*variant*/
        l[8] === "center"
      ), T(
        t,
        "meta-text",
        /*variant*/
        l[8] === "default"
      );
    },
    m(c, h) {
      u && u.m(c, h), y(c, e, h), y(c, t, h), g && g.m(t, null), x(t, n), v && v.m(t, null), y(c, i, h), ~f && C[f].m(c, h), y(c, r, h), d && d.m(c, h), y(c, a, h), o = !0;
    },
    p(c, h) {
      /*variant*/
      c[8] === "default" && /*show_eta_bar*/
      c[18] && /*show_progress*/
      c[6] === "full" ? u ? u.p(c, h) : (u = tt(c), u.c(), u.m(e.parentNode, e)) : u && (u.d(1), u = null), b === (b = m(c)) && g ? g.p(c, h) : (g && g.d(1), g = b && b(c), g && (g.c(), g.m(t, n))), /*timer*/
      c[5] ? v ? v.p(c, h) : (v = it(c), v.c(), v.m(t, null)) : v && (v.d(1), v = null), (!o || h[0] & /*variant*/
      256) && T(
        t,
        "meta-text-center",
        /*variant*/
        c[8] === "center"
      ), (!o || h[0] & /*variant*/
      256) && T(
        t,
        "meta-text",
        /*variant*/
        c[8] === "default"
      );
      let L = f;
      f = k(c), f === L ? ~f && C[f].p(c, h) : (s && (De(), G(C[L], 1, 1, () => {
        C[L] = null;
      }), je()), ~f ? (s = C[f], s ? s.p(c, h) : (s = C[f] = q[f](c), s.c()), B(s, 1), s.m(r.parentNode, r)) : s = null), /*timer*/
      c[5] ? d && (De(), G(d, 1, 1, () => {
        d = null;
      }), je()) : d ? (d.p(c, h), h[0] & /*timer*/
      32 && B(d, 1)) : (d = ct(c), d.c(), B(d, 1), d.m(a.parentNode, a));
    },
    i(c) {
      o || (B(s), B(d), o = !0);
    },
    o(c) {
      G(s), G(d), o = !1;
    },
    d(c) {
      c && (p(e), p(t), p(i), p(r), p(a)), u && u.d(c), g && g.d(), v && v.d(), ~f && C[f].d(c), d && d.d(c);
    }
  };
}
function tt(l) {
  let e, t = `translateX(${/*eta_level*/
  (l[17] || 0) * 100 - 100}%)`;
  return {
    c() {
      e = Y("div"), A(e, "class", "eta-bar svelte-v0wucf"), H(e, "transform", t);
    },
    m(n, i) {
      y(n, e, i);
    },
    p(n, i) {
      i[0] & /*eta_level*/
      131072 && t !== (t = `translateX(${/*eta_level*/
      (n[17] || 0) * 100 - 100}%)`) && H(e, "transform", t);
    },
    d(n) {
      n && p(e);
    }
  };
}
function sn(l) {
  let e;
  return {
    c() {
      e = z("processing |");
    },
    m(t, n) {
      y(t, e, n);
    },
    p: Ee,
    d(t) {
      t && p(e);
    }
  };
}
function on(l) {
  let e, t = (
    /*queue_position*/
    l[2] + 1 + ""
  ), n, i, f, s;
  return {
    c() {
      e = z("queue: "), n = z(t), i = z("/"), f = z(
        /*queue_size*/
        l[3]
      ), s = z(" |");
    },
    m(r, a) {
      y(r, e, a), y(r, n, a), y(r, i, a), y(r, f, a), y(r, s, a);
    },
    p(r, a) {
      a[0] & /*queue_position*/
      4 && t !== (t = /*queue_position*/
      r[2] + 1 + "") && j(n, t), a[0] & /*queue_size*/
      8 && j(
        f,
        /*queue_size*/
        r[3]
      );
    },
    d(r) {
      r && (p(e), p(n), p(i), p(f), p(s));
    }
  };
}
function an(l) {
  let e, t = ve(
    /*progress*/
    l[7]
  ), n = [];
  for (let i = 0; i < t.length; i += 1)
    n[i] = nt(et(l, t, i));
  return {
    c() {
      for (let i = 0; i < n.length; i += 1)
        n[i].c();
      e = oe();
    },
    m(i, f) {
      for (let s = 0; s < n.length; s += 1)
        n[s] && n[s].m(i, f);
      y(i, e, f);
    },
    p(i, f) {
      if (f[0] & /*progress*/
      128) {
        t = ve(
          /*progress*/
          i[7]
        );
        let s;
        for (s = 0; s < t.length; s += 1) {
          const r = et(i, t, s);
          n[s] ? n[s].p(r, f) : (n[s] = nt(r), n[s].c(), n[s].m(e.parentNode, e));
        }
        for (; s < n.length; s += 1)
          n[s].d(1);
        n.length = t.length;
      }
    },
    d(i) {
      i && p(e), Mt(n, i);
    }
  };
}
function lt(l) {
  let e, t = (
    /*p*/
    l[41].unit + ""
  ), n, i, f = " ", s;
  function r(u, m) {
    return (
      /*p*/
      u[41].length != null ? un : rn
    );
  }
  let a = r(l), o = a(l);
  return {
    c() {
      o.c(), e = Z(), n = z(t), i = z(" | "), s = z(f);
    },
    m(u, m) {
      o.m(u, m), y(u, e, m), y(u, n, m), y(u, i, m), y(u, s, m);
    },
    p(u, m) {
      a === (a = r(u)) && o ? o.p(u, m) : (o.d(1), o = a(u), o && (o.c(), o.m(e.parentNode, e))), m[0] & /*progress*/
      128 && t !== (t = /*p*/
      u[41].unit + "") && j(n, t);
    },
    d(u) {
      u && (p(e), p(n), p(i), p(s)), o.d(u);
    }
  };
}
function rn(l) {
  let e = fe(
    /*p*/
    l[41].index || 0
  ) + "", t;
  return {
    c() {
      t = z(e);
    },
    m(n, i) {
      y(n, t, i);
    },
    p(n, i) {
      i[0] & /*progress*/
      128 && e !== (e = fe(
        /*p*/
        n[41].index || 0
      ) + "") && j(t, e);
    },
    d(n) {
      n && p(t);
    }
  };
}
function un(l) {
  let e = fe(
    /*p*/
    l[41].index || 0
  ) + "", t, n, i = fe(
    /*p*/
    l[41].length
  ) + "", f;
  return {
    c() {
      t = z(e), n = z("/"), f = z(i);
    },
    m(s, r) {
      y(s, t, r), y(s, n, r), y(s, f, r);
    },
    p(s, r) {
      r[0] & /*progress*/
      128 && e !== (e = fe(
        /*p*/
        s[41].index || 0
      ) + "") && j(t, e), r[0] & /*progress*/
      128 && i !== (i = fe(
        /*p*/
        s[41].length
      ) + "") && j(f, i);
    },
    d(s) {
      s && (p(t), p(n), p(f));
    }
  };
}
function nt(l) {
  let e, t = (
    /*p*/
    l[41].index != null && lt(l)
  );
  return {
    c() {
      t && t.c(), e = oe();
    },
    m(n, i) {
      t && t.m(n, i), y(n, e, i);
    },
    p(n, i) {
      /*p*/
      n[41].index != null ? t ? t.p(n, i) : (t = lt(n), t.c(), t.m(e.parentNode, e)) : t && (t.d(1), t = null);
    },
    d(n) {
      n && p(e), t && t.d(n);
    }
  };
}
function it(l) {
  let e, t = (
    /*eta*/
    l[0] ? `/${/*formatted_eta*/
    l[19]}` : ""
  ), n, i;
  return {
    c() {
      e = z(
        /*formatted_timer*/
        l[20]
      ), n = z(t), i = z("s");
    },
    m(f, s) {
      y(f, e, s), y(f, n, s), y(f, i, s);
    },
    p(f, s) {
      s[0] & /*formatted_timer*/
      1048576 && j(
        e,
        /*formatted_timer*/
        f[20]
      ), s[0] & /*eta, formatted_eta*/
      524289 && t !== (t = /*eta*/
      f[0] ? `/${/*formatted_eta*/
      f[19]}` : "") && j(n, t);
    },
    d(f) {
      f && (p(e), p(n), p(i));
    }
  };
}
function cn(l) {
  let e, t;
  return e = new Hl({
    props: { margin: (
      /*variant*/
      l[8] === "default"
    ) }
  }), {
    c() {
      zt(e.$$.fragment);
    },
    m(n, i) {
      Tt(e, n, i), t = !0;
    },
    p(n, i) {
      const f = {};
      i[0] & /*variant*/
      256 && (f.margin = /*variant*/
      n[8] === "default"), e.$set(f);
    },
    i(n) {
      t || (B(e.$$.fragment, n), t = !0);
    },
    o(n) {
      G(e.$$.fragment, n), t = !1;
    },
    d(n) {
      St(e, n);
    }
  };
}
function _n(l) {
  let e, t, n, i, f, s = `${/*last_progress_level*/
  l[15] * 100}%`, r = (
    /*progress*/
    l[7] != null && ft(l)
  );
  return {
    c() {
      e = Y("div"), t = Y("div"), r && r.c(), n = Z(), i = Y("div"), f = Y("div"), A(t, "class", "progress-level-inner svelte-v0wucf"), A(f, "class", "progress-bar svelte-v0wucf"), H(f, "width", s), A(i, "class", "progress-bar-wrap svelte-v0wucf"), A(e, "class", "progress-level svelte-v0wucf");
    },
    m(a, o) {
      y(a, e, o), x(e, t), r && r.m(t, null), x(e, n), x(e, i), x(i, f), l[31](f);
    },
    p(a, o) {
      /*progress*/
      a[7] != null ? r ? r.p(a, o) : (r = ft(a), r.c(), r.m(t, null)) : r && (r.d(1), r = null), o[0] & /*last_progress_level*/
      32768 && s !== (s = `${/*last_progress_level*/
      a[15] * 100}%`) && H(f, "width", s);
    },
    i: Ee,
    o: Ee,
    d(a) {
      a && p(e), r && r.d(), l[31](null);
    }
  };
}
function ft(l) {
  let e, t = ve(
    /*progress*/
    l[7]
  ), n = [];
  for (let i = 0; i < t.length; i += 1)
    n[i] = ut($e(l, t, i));
  return {
    c() {
      for (let i = 0; i < n.length; i += 1)
        n[i].c();
      e = oe();
    },
    m(i, f) {
      for (let s = 0; s < n.length; s += 1)
        n[s] && n[s].m(i, f);
      y(i, e, f);
    },
    p(i, f) {
      if (f[0] & /*progress_level, progress*/
      16512) {
        t = ve(
          /*progress*/
          i[7]
        );
        let s;
        for (s = 0; s < t.length; s += 1) {
          const r = $e(i, t, s);
          n[s] ? n[s].p(r, f) : (n[s] = ut(r), n[s].c(), n[s].m(e.parentNode, e));
        }
        for (; s < n.length; s += 1)
          n[s].d(1);
        n.length = t.length;
      }
    },
    d(i) {
      i && p(e), Mt(n, i);
    }
  };
}
function st(l) {
  let e, t, n, i, f = (
    /*i*/
    l[43] !== 0 && dn()
  ), s = (
    /*p*/
    l[41].desc != null && ot(l)
  ), r = (
    /*p*/
    l[41].desc != null && /*progress_level*/
    l[14] && /*progress_level*/
    l[14][
      /*i*/
      l[43]
    ] != null && at()
  ), a = (
    /*progress_level*/
    l[14] != null && rt(l)
  );
  return {
    c() {
      f && f.c(), e = Z(), s && s.c(), t = Z(), r && r.c(), n = Z(), a && a.c(), i = oe();
    },
    m(o, u) {
      f && f.m(o, u), y(o, e, u), s && s.m(o, u), y(o, t, u), r && r.m(o, u), y(o, n, u), a && a.m(o, u), y(o, i, u);
    },
    p(o, u) {
      /*p*/
      o[41].desc != null ? s ? s.p(o, u) : (s = ot(o), s.c(), s.m(t.parentNode, t)) : s && (s.d(1), s = null), /*p*/
      o[41].desc != null && /*progress_level*/
      o[14] && /*progress_level*/
      o[14][
        /*i*/
        o[43]
      ] != null ? r || (r = at(), r.c(), r.m(n.parentNode, n)) : r && (r.d(1), r = null), /*progress_level*/
      o[14] != null ? a ? a.p(o, u) : (a = rt(o), a.c(), a.m(i.parentNode, i)) : a && (a.d(1), a = null);
    },
    d(o) {
      o && (p(e), p(t), p(n), p(i)), f && f.d(o), s && s.d(o), r && r.d(o), a && a.d(o);
    }
  };
}
function dn(l) {
  let e;
  return {
    c() {
      e = z(" /");
    },
    m(t, n) {
      y(t, e, n);
    },
    d(t) {
      t && p(e);
    }
  };
}
function ot(l) {
  let e = (
    /*p*/
    l[41].desc + ""
  ), t;
  return {
    c() {
      t = z(e);
    },
    m(n, i) {
      y(n, t, i);
    },
    p(n, i) {
      i[0] & /*progress*/
      128 && e !== (e = /*p*/
      n[41].desc + "") && j(t, e);
    },
    d(n) {
      n && p(t);
    }
  };
}
function at(l) {
  let e;
  return {
    c() {
      e = z("-");
    },
    m(t, n) {
      y(t, e, n);
    },
    d(t) {
      t && p(e);
    }
  };
}
function rt(l) {
  let e = (100 * /*progress_level*/
  (l[14][
    /*i*/
    l[43]
  ] || 0)).toFixed(1) + "", t, n;
  return {
    c() {
      t = z(e), n = z("%");
    },
    m(i, f) {
      y(i, t, f), y(i, n, f);
    },
    p(i, f) {
      f[0] & /*progress_level*/
      16384 && e !== (e = (100 * /*progress_level*/
      (i[14][
        /*i*/
        i[43]
      ] || 0)).toFixed(1) + "") && j(t, e);
    },
    d(i) {
      i && (p(t), p(n));
    }
  };
}
function ut(l) {
  let e, t = (
    /*p*/
    (l[41].desc != null || /*progress_level*/
    l[14] && /*progress_level*/
    l[14][
      /*i*/
      l[43]
    ] != null) && st(l)
  );
  return {
    c() {
      t && t.c(), e = oe();
    },
    m(n, i) {
      t && t.m(n, i), y(n, e, i);
    },
    p(n, i) {
      /*p*/
      n[41].desc != null || /*progress_level*/
      n[14] && /*progress_level*/
      n[14][
        /*i*/
        n[43]
      ] != null ? t ? t.p(n, i) : (t = st(n), t.c(), t.m(e.parentNode, e)) : t && (t.d(1), t = null);
    },
    d(n) {
      n && p(e), t && t.d(n);
    }
  };
}
function ct(l) {
  let e, t, n, i;
  const f = (
    /*#slots*/
    l[30]["additional-loading-text"]
  ), s = Lt(
    f,
    l,
    /*$$scope*/
    l[29],
    xe
  );
  return {
    c() {
      e = Y("p"), t = z(
        /*loading_text*/
        l[9]
      ), n = Z(), s && s.c(), A(e, "class", "loading svelte-v0wucf");
    },
    m(r, a) {
      y(r, e, a), x(e, t), y(r, n, a), s && s.m(r, a), i = !0;
    },
    p(r, a) {
      (!i || a[0] & /*loading_text*/
      512) && j(
        t,
        /*loading_text*/
        r[9]
      ), s && s.p && (!i || a[0] & /*$$scope*/
      536870912) && Zt(
        s,
        f,
        r,
        /*$$scope*/
        r[29],
        i ? Nt(
          f,
          /*$$scope*/
          r[29],
          a,
          ln
        ) : Vt(
          /*$$scope*/
          r[29]
        ),
        xe
      );
    },
    i(r) {
      i || (B(s, r), i = !0);
    },
    o(r) {
      G(s, r), i = !1;
    },
    d(r) {
      r && (p(e), p(n)), s && s.d(r);
    }
  };
}
function mn(l) {
  let e, t, n, i, f;
  const s = [fn, nn], r = [];
  function a(o, u) {
    return (
      /*status*/
      o[4] === "pending" ? 0 : (
        /*status*/
        o[4] === "error" ? 1 : -1
      )
    );
  }
  return ~(t = a(l)) && (n = r[t] = s[t](l)), {
    c() {
      e = Y("div"), n && n.c(), A(e, "class", i = "wrap " + /*variant*/
      l[8] + " " + /*show_progress*/
      l[6] + " svelte-v0wucf"), T(e, "hide", !/*status*/
      l[4] || /*status*/
      l[4] === "complete" || /*show_progress*/
      l[6] === "hidden"), T(
        e,
        "translucent",
        /*variant*/
        l[8] === "center" && /*status*/
        (l[4] === "pending" || /*status*/
        l[4] === "error") || /*translucent*/
        l[11] || /*show_progress*/
        l[6] === "minimal"
      ), T(
        e,
        "generating",
        /*status*/
        l[4] === "generating" && /*show_progress*/
        l[6] === "full"
      ), T(
        e,
        "border",
        /*border*/
        l[12]
      ), H(
        e,
        "position",
        /*absolute*/
        l[10] ? "absolute" : "static"
      ), H(
        e,
        "padding",
        /*absolute*/
        l[10] ? "0" : "var(--size-8) 0"
      );
    },
    m(o, u) {
      y(o, e, u), ~t && r[t].m(e, null), l[33](e), f = !0;
    },
    p(o, u) {
      let m = t;
      t = a(o), t === m ? ~t && r[t].p(o, u) : (n && (De(), G(r[m], 1, 1, () => {
        r[m] = null;
      }), je()), ~t ? (n = r[t], n ? n.p(o, u) : (n = r[t] = s[t](o), n.c()), B(n, 1), n.m(e, null)) : n = null), (!f || u[0] & /*variant, show_progress*/
      320 && i !== (i = "wrap " + /*variant*/
      o[8] + " " + /*show_progress*/
      o[6] + " svelte-v0wucf")) && A(e, "class", i), (!f || u[0] & /*variant, show_progress, status, show_progress*/
      336) && T(e, "hide", !/*status*/
      o[4] || /*status*/
      o[4] === "complete" || /*show_progress*/
      o[6] === "hidden"), (!f || u[0] & /*variant, show_progress, variant, status, translucent, show_progress*/
      2384) && T(
        e,
        "translucent",
        /*variant*/
        o[8] === "center" && /*status*/
        (o[4] === "pending" || /*status*/
        o[4] === "error") || /*translucent*/
        o[11] || /*show_progress*/
        o[6] === "minimal"
      ), (!f || u[0] & /*variant, show_progress, status, show_progress*/
      336) && T(
        e,
        "generating",
        /*status*/
        o[4] === "generating" && /*show_progress*/
        o[6] === "full"
      ), (!f || u[0] & /*variant, show_progress, border*/
      4416) && T(
        e,
        "border",
        /*border*/
        o[12]
      ), u[0] & /*absolute*/
      1024 && H(
        e,
        "position",
        /*absolute*/
        o[10] ? "absolute" : "static"
      ), u[0] & /*absolute*/
      1024 && H(
        e,
        "padding",
        /*absolute*/
        o[10] ? "0" : "var(--size-8) 0"
      );
    },
    i(o) {
      f || (B(n), f = !0);
    },
    o(o) {
      G(n), f = !1;
    },
    d(o) {
      o && p(e), ~t && r[t].d(), l[33](null);
    }
  };
}
var bn = function(l, e, t, n) {
  function i(f) {
    return f instanceof t ? f : new t(function(s) {
      s(f);
    });
  }
  return new (t || (t = Promise))(function(f, s) {
    function r(u) {
      try {
        o(n.next(u));
      } catch (m) {
        s(m);
      }
    }
    function a(u) {
      try {
        o(n.throw(u));
      } catch (m) {
        s(m);
      }
    }
    function o(u) {
      u.done ? f(u.value) : i(u.value).then(r, a);
    }
    o((n = n.apply(l, e || [])).next());
  });
};
let we = [], Le = !1;
function gn(l) {
  return bn(this, arguments, void 0, function* (e, t = !0) {
    if (!(window.__gradio_mode__ === "website" || window.__gradio_mode__ !== "app" && t !== !0)) {
      if (we.push(e), !Le) Le = !0;
      else return;
      yield xl(), requestAnimationFrame(() => {
        let n = [0, 0];
        for (let i = 0; i < we.length; i++) {
          const s = we[i].getBoundingClientRect();
          (i === 0 || s.top + window.scrollY <= n[0]) && (n[0] = s.top + window.scrollY, n[1] = i);
        }
        window.scrollTo({ top: n[0] - 20, behavior: "smooth" }), Le = !1, we = [];
      });
    }
  });
}
function hn(l, e, t) {
  let n, { $$slots: i = {}, $$scope: f } = e;
  this && this.__awaiter;
  const s = en();
  let { i18n: r } = e, { eta: a = null } = e, { queue_position: o } = e, { queue_size: u } = e, { status: m } = e, { scroll_to_output: b = !1 } = e, { timer: g = !0 } = e, { show_progress: v = "full" } = e, { message: q = null } = e, { progress: C = null } = e, { variant: k = "default" } = e, { loading_text: d = "Loading..." } = e, { absolute: c = !0 } = e, { translucent: h = !1 } = e, { border: L = !1 } = e, { autoscroll: _ } = e, M, K = !1, ce = 0, J = 0, ee = null, te = null, Ie = 0, Q = null, ae, R = null, Be = !0;
  const Xt = () => {
    t(0, a = t(27, ee = t(19, _e = null))), t(25, ce = performance.now()), t(26, J = 0), K = !0, Ae();
  };
  function Ae() {
    requestAnimationFrame(() => {
      t(26, J = (performance.now() - ce) / 1e3), K && Ae();
    });
  }
  function Pe() {
    t(26, J = 0), t(0, a = t(27, ee = t(19, _e = null))), K && (K = !1);
  }
  $l(() => {
    K && Pe();
  });
  let _e = null;
  function Yt(w) {
    Qe[w ? "unshift" : "push"](() => {
      R = w, t(16, R), t(7, C), t(14, Q), t(15, ae);
    });
  }
  const Gt = () => {
    s("clear_status");
  };
  function Kt(w) {
    Qe[w ? "unshift" : "push"](() => {
      M = w, t(13, M);
    });
  }
  return l.$$set = (w) => {
    "i18n" in w && t(1, r = w.i18n), "eta" in w && t(0, a = w.eta), "queue_position" in w && t(2, o = w.queue_position), "queue_size" in w && t(3, u = w.queue_size), "status" in w && t(4, m = w.status), "scroll_to_output" in w && t(22, b = w.scroll_to_output), "timer" in w && t(5, g = w.timer), "show_progress" in w && t(6, v = w.show_progress), "message" in w && t(23, q = w.message), "progress" in w && t(7, C = w.progress), "variant" in w && t(8, k = w.variant), "loading_text" in w && t(9, d = w.loading_text), "absolute" in w && t(10, c = w.absolute), "translucent" in w && t(11, h = w.translucent), "border" in w && t(12, L = w.border), "autoscroll" in w && t(24, _ = w.autoscroll), "$$scope" in w && t(29, f = w.$$scope);
  }, l.$$.update = () => {
    l.$$.dirty[0] & /*eta, old_eta, timer_start, eta_from_start*/
    436207617 && (a === null && t(0, a = ee), a != null && ee !== a && (t(28, te = (performance.now() - ce) / 1e3 + a), t(19, _e = te.toFixed(1)), t(27, ee = a))), l.$$.dirty[0] & /*eta_from_start, timer_diff*/
    335544320 && t(17, Ie = te === null || te <= 0 || !J ? null : Math.min(J / te, 1)), l.$$.dirty[0] & /*progress*/
    128 && C != null && t(18, Be = !1), l.$$.dirty[0] & /*progress, progress_level, progress_bar, last_progress_level*/
    114816 && (C != null ? t(14, Q = C.map((w) => {
      if (w.index != null && w.length != null)
        return w.index / w.length;
      if (w.progress != null)
        return w.progress;
    })) : t(14, Q = null), Q ? (t(15, ae = Q[Q.length - 1]), R && (ae === 0 ? t(16, R.style.transition = "0", R) : t(16, R.style.transition = "150ms", R))) : t(15, ae = void 0)), l.$$.dirty[0] & /*status*/
    16 && (m === "pending" ? Xt() : Pe()), l.$$.dirty[0] & /*el, scroll_to_output, status, autoscroll*/
    20979728 && M && b && (m === "pending" || m === "complete") && gn(M, _), l.$$.dirty[0] & /*status, message*/
    8388624, l.$$.dirty[0] & /*timer_diff*/
    67108864 && t(20, n = J.toFixed(1));
  }, [
    a,
    r,
    o,
    u,
    m,
    g,
    v,
    C,
    k,
    d,
    c,
    h,
    L,
    M,
    Q,
    ae,
    R,
    Ie,
    Be,
    _e,
    n,
    s,
    b,
    q,
    _,
    ce,
    J,
    ee,
    te,
    f,
    i,
    Yt,
    Gt,
    Kt
  ];
}
class wn extends Jl {
  constructor(e) {
    super(), Ql(
      this,
      e,
      hn,
      mn,
      Wl,
      {
        i18n: 1,
        eta: 0,
        queue_position: 2,
        queue_size: 3,
        status: 4,
        scroll_to_output: 22,
        timer: 5,
        show_progress: 6,
        message: 23,
        progress: 7,
        variant: 8,
        loading_text: 9,
        absolute: 10,
        translucent: 11,
        border: 12,
        autoscroll: 24
      },
      null,
      [-1, -1]
    );
  }
}
const {
  SvelteComponent: kn,
  append: ke,
  attr: ie,
  detach: vn,
  element: Se,
  init: pn,
  insert: yn,
  listen: Me,
  noop: _t,
  run_all: Cn,
  safe_not_equal: qn,
  set_data: Fn,
  space: zn,
  text: Ln,
  toggle_class: dt
} = window.__gradio__svelte__internal, { createEventDispatcher: Sn } = window.__gradio__svelte__internal;
function Mn(l) {
  let e, t, n, i, f, s, r;
  return {
    c() {
      e = Se("label"), t = Se("input"), n = zn(), i = Se("span"), f = Ln(
        /*label*/
        l[1]
      ), t.disabled = /*disabled*/
      l[2], ie(t, "type", "checkbox"), ie(t, "name", "test"), ie(t, "data-testid", "checkbox"), ie(t, "class", "svelte-15y2hcz"), ie(i, "class", "ml-2 svelte-15y2hcz"), ie(e, "class", "svelte-15y2hcz"), dt(
        e,
        "disabled",
        /*disabled*/
        l[2]
      );
    },
    m(a, o) {
      yn(a, e, o), ke(e, t), t.checked = /*value*/
      l[0], ke(e, n), ke(e, i), ke(i, f), s || (r = [
        Me(
          t,
          "change",
          /*input_change_handler*/
          l[6]
        ),
        Me(
          t,
          "keydown",
          /*handle_enter*/
          l[3]
        ),
        Me(
          t,
          "input",
          /*handle_input*/
          l[4]
        )
      ], s = !0);
    },
    p(a, [o]) {
      o & /*disabled*/
      4 && (t.disabled = /*disabled*/
      a[2]), o & /*value*/
      1 && (t.checked = /*value*/
      a[0]), o & /*label*/
      2 && Fn(
        f,
        /*label*/
        a[1]
      ), o & /*disabled*/
      4 && dt(
        e,
        "disabled",
        /*disabled*/
        a[2]
      );
    },
    i: _t,
    o: _t,
    d(a) {
      a && vn(e), s = !1, Cn(r);
    }
  };
}
function Vn(l, e, t) {
  let n;
  var i = this && this.__awaiter || function(b, g, v, q) {
    function C(k) {
      return k instanceof v ? k : new v(function(d) {
        d(k);
      });
    }
    return new (v || (v = Promise))(function(k, d) {
      function c(_) {
        try {
          L(q.next(_));
        } catch (M) {
          d(M);
        }
      }
      function h(_) {
        try {
          L(q.throw(_));
        } catch (M) {
          d(M);
        }
      }
      function L(_) {
        _.done ? k(_.value) : C(_.value).then(c, h);
      }
      L((q = q.apply(b, g || [])).next());
    });
  };
  let { value: f = !1 } = e, { label: s = "Checkbox" } = e, { interactive: r } = e;
  const a = Sn();
  function o(b) {
    return i(this, void 0, void 0, function* () {
      b.key === "Enter" && (t(0, f = !f), a("select", {
        index: 0,
        value: b.currentTarget.checked,
        selected: b.currentTarget.checked
      }));
    });
  }
  function u(b) {
    return i(this, void 0, void 0, function* () {
      t(0, f = b.currentTarget.checked), a("select", {
        index: 0,
        value: b.currentTarget.checked,
        selected: b.currentTarget.checked
      });
    });
  }
  function m() {
    f = this.checked, t(0, f);
  }
  return l.$$set = (b) => {
    "value" in b && t(0, f = b.value), "label" in b && t(1, s = b.label), "interactive" in b && t(5, r = b.interactive);
  }, l.$$.update = () => {
    l.$$.dirty & /*value*/
    1 && a("change", f), l.$$.dirty & /*interactive*/
    32 && t(2, n = !r);
  }, [
    f,
    s,
    n,
    o,
    u,
    r,
    m
  ];
}
class Gn extends kn {
  constructor(e) {
    super(), pn(this, e, Vn, Mn, qn, { value: 0, label: 1, interactive: 5 });
  }
}
const {
  SvelteComponent: Nn,
  append: U,
  assign: Tn,
  attr: S,
  create_component: jt,
  destroy_component: Dt,
  detach: pe,
  element: $,
  get_spread_object: Zn,
  get_spread_update: jn,
  init: Dn,
  insert: ye,
  listen: mt,
  mount_component: Et,
  run_all: En,
  safe_not_equal: In,
  set_data: It,
  set_style: bt,
  space: Ve,
  text: Bt,
  transition_in: At,
  transition_out: Pt
} = window.__gradio__svelte__internal, { afterUpdate: Bn, onMount: An } = window.__gradio__svelte__internal;
function gt(l) {
  let e, t;
  return {
    c() {
      e = $("div"), t = Bt(
        /*label*/
        l[1]
      ), S(e, "class", "block-label svelte-1iucwgs"), S(
        e,
        "for",
        /*elem_id*/
        l[10]
      );
    },
    m(n, i) {
      ye(n, e, i), U(e, t);
    },
    p(n, i) {
      i & /*label*/
      2 && It(
        t,
        /*label*/
        n[1]
      ), i & /*elem_id*/
      1024 && S(
        e,
        "for",
        /*elem_id*/
        n[10]
      );
    },
    d(n) {
      n && pe(e);
    }
  };
}
function ht(l) {
  let e, t, n;
  return {
    c() {
      e = $("div"), t = $("div"), n = Bt(
        /*info*/
        l[4]
      ), S(t, "class", "block-info svelte-1iucwgs"), S(e, "id", "info"), S(e, "class", "block-label-container");
    },
    m(i, f) {
      ye(i, e, f), U(e, t), U(t, n);
    },
    p(i, f) {
      f & /*info*/
      16 && It(
        n,
        /*info*/
        i[4]
      );
    },
    d(i) {
      i && pe(e);
    }
  };
}
function Pn(l) {
  let e, t, n, i, f, s, r, a, o, u, m, b, g, v;
  const q = [
    {
      autoscroll: (
        /*gradio*/
        l[13].autoscroll
      )
    },
    { i18n: (
      /*gradio*/
      l[13].i18n
    ) },
    /*loading_status*/
    l[12]
  ];
  let C = {};
  for (let c = 0; c < q.length; c += 1)
    C = Tn(C, q[c]);
  e = new wn({ props: C }), e.$on(
    "clear_status",
    /*clear_status_handler*/
    l[17]
  );
  let k = (
    /*show_label*/
    l[2] && gt(l)
  ), d = (
    /*info*/
    l[4] && ht(l)
  );
  return {
    c() {
      jt(e.$$.fragment), t = Ve(), n = $("div"), i = $("div"), k && k.c(), f = Ve(), s = $("div"), r = $("div"), m = Ve(), d && d.c(), S(r, "class", "toggle-knob svelte-1iucwgs"), S(
        s,
        "id",
        /*elem_id*/
        l[10]
      ), S(s, "class", a = "toggle " + /*value*/
      (l[0] ? "active" : "") + " " + /*interactive*/
      (l[9] ? "" : "non-interactive") + " svelte-1iucwgs"), S(s, "tabindex", o = /*interactive*/
      l[9] ? "0" : "-1"), S(s, "role", "switch"), S(s, "aria-checked", u = /*value*/
      l[0].toString()), S(
        s,
        "aria-label",
        /*label*/
        l[1]
      ), bt(
        s,
        "--toggle-background-color",
        /*value*/
        l[0] ? (
          /*color*/
          l[5]
        ) : "var(--border-color-primary)"
      ), S(i, "class", "container svelte-1iucwgs"), S(n, "class", "block-component");
    },
    m(c, h) {
      Et(e, c, h), ye(c, t, h), ye(c, n, h), U(n, i), k && k.m(i, null), U(i, f), U(i, s), U(s, r), U(n, m), d && d.m(n, null), b = !0, g || (v = [
        mt(
          s,
          "click",
          /*handleChange*/
          l[14]
        ),
        mt(
          s,
          "keydown",
          /*handleKeydown*/
          l[15]
        )
      ], g = !0);
    },
    p(c, h) {
      const L = h & /*gradio, loading_status*/
      12288 ? jn(q, [
        h & /*gradio*/
        8192 && {
          autoscroll: (
            /*gradio*/
            c[13].autoscroll
          )
        },
        h & /*gradio*/
        8192 && { i18n: (
          /*gradio*/
          c[13].i18n
        ) },
        h & /*loading_status*/
        4096 && Zn(
          /*loading_status*/
          c[12]
        )
      ]) : {};
      e.$set(L), /*show_label*/
      c[2] ? k ? k.p(c, h) : (k = gt(c), k.c(), k.m(i, f)) : k && (k.d(1), k = null), (!b || h & /*elem_id*/
      1024) && S(
        s,
        "id",
        /*elem_id*/
        c[10]
      ), (!b || h & /*value, interactive*/
      513 && a !== (a = "toggle " + /*value*/
      (c[0] ? "active" : "") + " " + /*interactive*/
      (c[9] ? "" : "non-interactive") + " svelte-1iucwgs")) && S(s, "class", a), (!b || h & /*interactive*/
      512 && o !== (o = /*interactive*/
      c[9] ? "0" : "-1")) && S(s, "tabindex", o), (!b || h & /*value*/
      1 && u !== (u = /*value*/
      c[0].toString())) && S(s, "aria-checked", u), (!b || h & /*label*/
      2) && S(
        s,
        "aria-label",
        /*label*/
        c[1]
      ), (!b || h & /*value, color*/
      33) && bt(
        s,
        "--toggle-background-color",
        /*value*/
        c[0] ? (
          /*color*/
          c[5]
        ) : "var(--border-color-primary)"
      ), /*info*/
      c[4] ? d ? d.p(c, h) : (d = ht(c), d.c(), d.m(n, null)) : d && (d.d(1), d = null);
    },
    i(c) {
      b || (At(e.$$.fragment, c), b = !0);
    },
    o(c) {
      Pt(e.$$.fragment, c), b = !1;
    },
    d(c) {
      c && (pe(t), pe(n)), Dt(e, c), k && k.d(), d && d.d(), g = !1, En(v);
    }
  };
}
function Xn(l) {
  let e, t;
  return e = new ml({
    props: {
      visible: (
        /*visible*/
        l[3]
      ),
      elem_id: (
        /*elem_id*/
        l[10]
      ),
      elem_classes: (
        /*elem_classes*/
        l[11]
      ),
      container: (
        /*container*/
        l[6]
      ),
      scale: (
        /*scale*/
        l[7]
      ),
      min_width: (
        /*min_width*/
        l[8]
      ),
      $$slots: { default: [Pn] },
      $$scope: { ctx: l }
    }
  }), {
    c() {
      jt(e.$$.fragment);
    },
    m(n, i) {
      Et(e, n, i), t = !0;
    },
    p(n, [i]) {
      const f = {};
      i & /*visible*/
      8 && (f.visible = /*visible*/
      n[3]), i & /*elem_id*/
      1024 && (f.elem_id = /*elem_id*/
      n[10]), i & /*elem_classes*/
      2048 && (f.elem_classes = /*elem_classes*/
      n[11]), i & /*container*/
      64 && (f.container = /*container*/
      n[6]), i & /*scale*/
      128 && (f.scale = /*scale*/
      n[7]), i & /*min_width*/
      256 && (f.min_width = /*min_width*/
      n[8]), i & /*$$scope, info, elem_id, value, interactive, label, color, show_label, gradio, loading_status*/
      538167 && (f.$$scope = { dirty: i, ctx: n }), e.$set(f);
    },
    i(n) {
      t || (At(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Pt(e.$$.fragment, n), t = !1;
    },
    d(n) {
      Dt(e, n);
    }
  };
}
function Yn(l, e, t) {
  let { value: n = !1 } = e, { label: i = "Toggle" } = e, { show_label: f = !0 } = e, { visible: s = !0 } = e, { info: r = void 0 } = e, { color: a = "var(--checkbox-background-color-selected)" } = e, { container: o = !0 } = e, { scale: u = null } = e, { min_width: m = void 0 } = e, { interactive: b = !0 } = e, { elem_id: g = "" } = e, { elem_classes: v = [] } = e, { value_is_output: q = !1 } = e, { loading_status: C } = e, { gradio: k } = e;
  const d = pt(n);
  function c() {
    b && (d.update((_) => !_), k.dispatch("change"), q || k.dispatch("input"));
  }
  function h(_) {
    b && (_.key === "Enter" || _.key === " ") && (_.preventDefault(), c());
  }
  Bn(() => {
    t(16, q = !1);
  }), An(() => {
    d.set(n);
  });
  const L = () => k.dispatch("clear_status", C);
  return l.$$set = (_) => {
    "value" in _ && t(0, n = _.value), "label" in _ && t(1, i = _.label), "show_label" in _ && t(2, f = _.show_label), "visible" in _ && t(3, s = _.visible), "info" in _ && t(4, r = _.info), "color" in _ && t(5, a = _.color), "container" in _ && t(6, o = _.container), "scale" in _ && t(7, u = _.scale), "min_width" in _ && t(8, m = _.min_width), "interactive" in _ && t(9, b = _.interactive), "elem_id" in _ && t(10, g = _.elem_id), "elem_classes" in _ && t(11, v = _.elem_classes), "value_is_output" in _ && t(16, q = _.value_is_output), "loading_status" in _ && t(12, C = _.loading_status), "gradio" in _ && t(13, k = _.gradio);
  }, l.$$.update = () => {
    l.$$.dirty & /*value*/
    1 && Wt(d) !== n && d.set(n);
  }, d.subscribe((_) => {
    t(0, n = _);
  }), [
    n,
    i,
    f,
    s,
    r,
    a,
    o,
    u,
    m,
    b,
    g,
    v,
    C,
    k,
    c,
    h,
    q,
    L
  ];
}
class Kn extends Nn {
  constructor(e) {
    super(), Dn(this, e, Yn, Xn, In, {
      value: 0,
      label: 1,
      show_label: 2,
      visible: 3,
      info: 4,
      color: 5,
      container: 6,
      scale: 7,
      min_width: 8,
      interactive: 9,
      elem_id: 10,
      elem_classes: 11,
      value_is_output: 16,
      loading_status: 12,
      gradio: 13
    });
  }
}
export {
  Gn as BaseCheckbox,
  Kn as default
};
