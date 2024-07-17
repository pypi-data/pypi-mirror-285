const {
  SvelteComponent: b,
  add_iframe_resize_listener: y,
  add_render_callback: v,
  append: h,
  attr: m,
  binding_callbacks: w,
  detach: z,
  element: k,
  init: p,
  insert: S,
  noop: f,
  safe_not_equal: q,
  set_data: C,
  text: E,
  toggle_class: r
} = window.__gradio__svelte__internal, { onMount: M } = window.__gradio__svelte__internal;
function P(t) {
  let e, n = (
    /*value*/
    (t[0] ? (
      /*value*/
      t[0]
    ) : "") + ""
  ), _, d;
  return {
    c() {
      e = k("div"), _ = E(n), m(e, "class", "svelte-84cxb8"), v(() => (
        /*div_elementresize_handler*/
        t[5].call(e)
      )), r(
        e,
        "table",
        /*type*/
        t[1] === "table"
      ), r(
        e,
        "gallery",
        /*type*/
        t[1] === "gallery"
      ), r(
        e,
        "selected",
        /*selected*/
        t[2]
      );
    },
    m(l, s) {
      S(l, e, s), h(e, _), d = y(
        e,
        /*div_elementresize_handler*/
        t[5].bind(e)
      ), t[6](e);
    },
    p(l, [s]) {
      s & /*value*/
      1 && n !== (n = /*value*/
      (l[0] ? (
        /*value*/
        l[0]
      ) : "") + "") && C(_, n), s & /*type*/
      2 && r(
        e,
        "table",
        /*type*/
        l[1] === "table"
      ), s & /*type*/
      2 && r(
        e,
        "gallery",
        /*type*/
        l[1] === "gallery"
      ), s & /*selected*/
      4 && r(
        e,
        "selected",
        /*selected*/
        l[2]
      );
    },
    i: f,
    o: f,
    d(l) {
      l && z(e), d(), t[6](null);
    }
  };
}
function W(t, e, n) {
  let { value: _ } = e, { type: d } = e, { selected: l = !1 } = e, s, a;
  function c(i, u) {
    !i || !u || (a.style.setProperty("--local-text-width", `${u < 150 ? u : 200}px`), n(4, a.style.whiteSpace = "unset", a));
  }
  M(() => {
    c(a, s);
  });
  function o() {
    s = this.clientWidth, n(3, s);
  }
  function g(i) {
    w[i ? "unshift" : "push"](() => {
      a = i, n(4, a);
    });
  }
  return t.$$set = (i) => {
    "value" in i && n(0, _ = i.value), "type" in i && n(1, d = i.type), "selected" in i && n(2, l = i.selected);
  }, [_, d, l, s, a, o, g];
}
class j extends b {
  constructor(e) {
    super(), p(this, e, W, P, q, { value: 0, type: 1, selected: 2 });
  }
}
export {
  j as default
};
