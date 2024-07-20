import { IJCadObject, IJcadObjectDocChange, IJupyterCadDoc, JupyterCadDoc } from '@jupytercad/schema';
import { ISignal } from '@lumino/signaling';
export declare class JupyterCadStlDoc extends JupyterCadDoc {
    constructor();
    get version(): string;
    get objectsChanged(): ISignal<IJupyterCadDoc, IJcadObjectDocChange>;
    get objects(): Array<IJCadObject>;
    static create(): JupyterCadStlDoc;
    editable: boolean;
    private _sourceObserver;
    private _source;
    private _objectChanged;
}
