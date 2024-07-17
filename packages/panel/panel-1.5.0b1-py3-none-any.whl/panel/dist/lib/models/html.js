import { ModelEvent } from "@bokehjs/core/bokeh_events";
import { entries } from "@bokehjs/core/util/object";
import { Markup } from "@bokehjs/models/widgets/markup";
import { PanelMarkupView } from "./layout";
import { serializeEvent } from "./event-to-object";
export class DOMEvent extends ModelEvent {
    node;
    data;
    static __name__ = "DOMEvent";
    constructor(node, data) {
        super();
        this.node = node;
        this.data = data;
    }
    get event_values() {
        return { model: this.origin, node: this.node, data: this.data };
    }
    static {
        this.prototype.event_name = "dom_event";
    }
}
export function html_decode(input) {
    const doc = new DOMParser().parseFromString(input, "text/html");
    return doc.documentElement.textContent;
}
export function run_scripts(node) {
    for (const old_script of node.querySelectorAll("script")) {
        const new_script = document.createElement("script");
        for (const attr of old_script.attributes) {
            new_script.setAttribute(attr.name, attr.value);
        }
        new_script.append(document.createTextNode(old_script.innerHTML));
        const parent_node = old_script.parentNode;
        if (parent_node != null) {
            parent_node.replaceChild(new_script, old_script);
        }
    }
}
export class HTMLView extends PanelMarkupView {
    static __name__ = "HTMLView";
    _event_listeners = new Map();
    connect_signals() {
        super.connect_signals();
        const { text, visible, events } = this.model.properties;
        this.on_change(text, () => {
            const html = this.process_tex();
            this.set_html(html);
        });
        this.on_change(visible, () => {
            if (this.model.visible) {
                this.container.style.visibility = "visible";
            }
        });
        this.on_change(events, () => {
            this._remove_event_listeners();
            this._setup_event_listeners();
        });
    }
    rerender() {
        this.render();
        this.invalidate_layout();
    }
    set_html(html) {
        if (html !== null) {
            this.container.innerHTML = html;
            if (this.model.run_scripts) {
                run_scripts(this.container);
            }
            this._setup_event_listeners();
        }
    }
    render() {
        super.render();
        this.container.style.visibility = "hidden";
        this.shadow_el.appendChild(this.container);
        if (this.provider.status == "failed" || this.provider.status == "loaded") {
            this._has_finished = true;
        }
        const html = this.process_tex();
        this.watch_stylesheets();
        this.set_html(html);
    }
    style_redraw() {
        if (this.model.visible) {
            this.container.style.visibility = "visible";
        }
    }
    process_tex() {
        const decoded = html_decode(this.model.text);
        const text = decoded ?? this.model.text;
        if (this.model.disable_math || !this.contains_tex(text)) {
            return text;
        }
        const tex_parts = this.provider.MathJax.find_tex(text);
        const processed_text = [];
        let last_index = 0;
        for (const part of tex_parts) {
            processed_text.push(text.slice(last_index, part.start.n));
            processed_text.push(this.provider.MathJax.tex2svg(part.math, { display: part.display }).outerHTML);
            last_index = part.end.n;
        }
        if (last_index < text.length) {
            processed_text.push(text.slice(last_index));
        }
        return processed_text.join("");
    }
    contains_tex(html) {
        if (!this.provider.MathJax) {
            return false;
        }
        return this.provider.MathJax.find_tex(html).length > 0;
    }
    _remove_event_listeners() {
        for (const [node, callbacks] of this._event_listeners) {
            const el = document.getElementById(node);
            if (el == null) {
                console.warn(`DOM node '${node}' could not be found. Cannot subscribe to DOM events.`);
                continue;
            }
            for (const [event_name, event_callback] of callbacks) {
                el.removeEventListener(event_name, event_callback);
            }
        }
        this._event_listeners.clear();
    }
    _setup_event_listeners() {
        for (const [node, event_names] of entries(this.model.events)) {
            const el = document.getElementById(node);
            if (el == null) {
                console.warn(`DOM node '${node}' could not be found. Cannot subscribe to DOM events.`);
                continue;
            }
            for (const event_name of event_names) {
                const callback = (event) => {
                    this.model.trigger_event(new DOMEvent(node, serializeEvent(event)));
                };
                el.addEventListener(event_name, callback);
                let callbacks = this._event_listeners.get(node);
                if (callbacks === undefined) {
                    this._event_listeners.set(node, callbacks = new Map());
                }
                callbacks.set(event_name, callback);
            }
        }
    }
}
export class HTML extends Markup {
    static __name__ = "HTML";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.markup";
    static {
        this.prototype.default_view = HTMLView;
        this.define(({ Bool, Str, List, Dict }) => ({
            events: [Dict(List(Str)), {}],
            run_scripts: [Bool, true],
        }));
    }
}
//# sourceMappingURL=html.js.map