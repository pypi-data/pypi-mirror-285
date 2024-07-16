import { guid } from './string'

export interface FileSelectorAttrs {
    multiple?: boolean;
    accept?: string;
    clearFile?: boolean;
}

const copyFileList = (files: FileList) => {
    const fileList = Object.create(null);
    fileList.length = 0;
    fileList.item = (n: string | number) => fileList[n];
    for (let i = 0; i < files.length; i++) {
        fileList[i] = files.item(i)!;
        fileList.length++;
    }
    return fileList;
};

export class FileSelector {
    private inputHtml: HTMLInputElement;

    private triggerId = guid();

    private defaultAttrs: FileSelectorAttrs = {
        multiple: false,
        accept: '*',
        clearFile: true,
    };

    private attrs: FileSelectorAttrs = {
        multiple: false,
        accept: '*',
        clearFile: true,
    };

    private modifyAttrs() {
        const { multiple, accept } = this.attrs;
        if (multiple) {
            this.inputHtml.setAttribute('multiple', 'multiple');
        } else {
            this.inputHtml.removeAttribute('multiple');
        }
        this.inputHtml.setAttribute('accept', accept!);
    }

    setAttrs(attrs: FileSelectorAttrs) {
        this.attrs = Object.assign(this.defaultAttrs, attrs);
        this.modifyAttrs();
    }

    selectFile() {
        this.triggerId = guid();
        const evTriggerId = this.triggerId;
        return new Promise<FileList>(resolve => {
            const onFileChange = () => {
                if (evTriggerId !== this.triggerId) {
                    this.inputHtml.removeEventListener('change', onFileChange);
                    return;
                }
                const { clearFile } = this.attrs;
                const files = copyFileList(this.inputHtml.files!);
                resolve(files);
                if (clearFile) {
                    this.inputHtml!.value = '';
                }
                this.inputHtml.removeEventListener('change', onFileChange);
            };
            this.inputHtml.addEventListener('change', onFileChange);
            this.inputHtml.click();
        });
    }

    constructor() {
        this.inputHtml = document.createElement('input');
        this.inputHtml.setAttribute('type', 'file');
        this.inputHtml.classList.add('hrm-hidden-input');
        this.inputHtml.style="display: none";
        document.body.appendChild(this.inputHtml);
    }
}

export default new FileSelector();
