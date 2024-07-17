import type * as p from "@bokehjs/core/properties";
import { ReactComponent, ReactComponentView } from "./react_component";
declare class AnyWidgetModelAdapter {
    model: AnyWidgetComponent;
    model_changes: any;
    data_changes: any;
    view: AnyWidgetComponentView | null;
    constructor(model: AnyWidgetComponent);
    get(name: any): any;
    set(name: string, value: any): void;
    save_changes(): void;
    on(event: string, cb: () => void): void;
    off(event: string, cb: () => void): void;
}
declare class AnyWidgetAdapter extends AnyWidgetModelAdapter {
    view: AnyWidgetComponentView;
    constructor(view: AnyWidgetComponentView);
    get_child(name: any): HTMLElement | HTMLElement[] | undefined;
}
export declare class AnyWidgetComponentView extends ReactComponentView {
    model: AnyWidgetComponent;
    adapter: AnyWidgetAdapter;
    destroyer: ((props: any) => void) | null;
    initialize(): void;
    remove(): void;
    protected _render_code(): string;
    after_rendered(): void;
}
export declare namespace AnyWidgetComponent {
    type Attrs = p.AttrsOf<Props>;
    type Props = ReactComponent.Props;
}
export interface AnyWidgetComponent extends AnyWidgetComponent.Attrs {
}
export declare class AnyWidgetComponent extends ReactComponent {
    properties: AnyWidgetComponent.Props;
    constructor(attrs?: Partial<AnyWidgetComponent.Attrs>);
    protected _run_initializer(initialize: (props: any) => void): void;
    compile(): string | null;
    static __module__: string;
}
export {};
//# sourceMappingURL=anywidget_component.d.ts.map