const {
  SvelteComponent: c,
  append: o,
  attr: _,
  detach: d,
  element: g,
  init: r,
  insert: v,
  noop: f,
  safe_not_equal: y,
  set_data: m,
  text: b,
  toggle_class: u
} = window.__gradio__svelte__internal;
function w(a) {
  let e, n = (
    /*value*/
    (a[0] !== null ? (
      /*value*/
      a[0].toLocaleString()
    ) : "") + ""
  ), i;
  return {
    c() {
      e = g("div"), i = b(n), _(e, "class", "svelte-1gecy8w"), u(
        e,
        "table",
        /*type*/
        a[1] === "table"
      ), u(
        e,
        "gallery",
        /*type*/
        a[1] === "gallery"
      ), u(
        e,
        "selected",
        /*selected*/
        a[2]
      );
    },
    m(l, t) {
      v(l, e, t), o(e, i);
    },
    p(l, [t]) {
      t & /*value*/
      1 && n !== (n = /*value*/
      (l[0] !== null ? (
        /*value*/
        l[0].toLocaleString()
      ) : "") + "") && m(i, n), t & /*type*/
      2 && u(
        e,
        "table",
        /*type*/
        l[1] === "table"
      ), t & /*type*/
      2 && u(
        e,
        "gallery",
        /*type*/
        l[1] === "gallery"
      ), t & /*selected*/
      4 && u(
        e,
        "selected",
        /*selected*/
        l[2]
      );
    },
    i: f,
    o: f,
    d(l) {
      l && d(e);
    }
  };
}
function S(a, e, n) {
  let { value: i } = e, { type: l } = e, { selected: t = !1 } = e;
  return a.$$set = (s) => {
    "value" in s && n(0, i = s.value), "type" in s && n(1, l = s.type), "selected" in s && n(2, t = s.selected);
  }, [i, l, t];
}
class h extends c {
  constructor(e) {
    super(), r(this, e, S, w, y, { value: 0, type: 1, selected: 2 });
  }
}
export {
  h as default
};
