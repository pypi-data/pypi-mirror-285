import { JupyterCadDoc } from '@jupytercad/schema';
import { JSONExt } from '@lumino/coreutils';
import { Signal } from '@lumino/signaling';
export class JupyterCadStlDoc extends JupyterCadDoc {
    constructor() {
        super();
        this.editable = false;
        this._sourceObserver = (events) => {
            const changes = [];
            events.forEach(event => {
                event.keys.forEach((change, key) => {
                    changes.push({
                        name: 'Stl File',
                        key: key,
                        newValue: JSONExt.deepCopy(event.target.toJSON())
                    });
                });
            });
            this._objectChanged.emit({ objectChange: changes });
            this._changed.emit({ objectChange: changes });
        };
        this._objectChanged = new Signal(this);
        this._source = this.ydoc.getText('source');
        this._source.observeDeep(this._sourceObserver);
    }
    get version() {
        return '0.1.0';
    }
    get objectsChanged() {
        return this._objectChanged;
    }
    get objects() {
        const source = this._source.toJSON();
        if (!source) {
            return [];
        }
        return [
            {
                name: 'Stl File', // TODO get file name?
                visible: true,
                shape: 'Part::Any',
                parameters: {
                    Content: this._source.toJSON(),
                    Type: 'STL'
                }
            }
        ];
    }
    static create() {
        return new JupyterCadStlDoc();
    }
}
