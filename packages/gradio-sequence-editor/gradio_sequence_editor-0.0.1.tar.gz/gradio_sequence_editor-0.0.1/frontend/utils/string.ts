export interface ChainProps {
    name: string | null;
    subName?: string;
    sequence?: string;
    errorMsg?: string;
    singleLimit?: number;
    key?: string;
    jobId?: number;
    canEdit?: boolean;
}

export enum NameRuleEnum {
    NOT_NULL = 'not-null',
    LENGTH_100 = 'length-100',
    NOT_REPEAT = 'not-repeat',
}

export const guid = () => {
    function S4() {
        // eslint-disable-next-line no-bitwise
        return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
    }
    return `${S4() + S4()}-${S4()}-${S4()}-${S4()}-${S4()}${S4()}${S4()}`;
};

export const colorHexToNumber = (color = '#F2F5FA') => {
    if (color.startsWith('#')) {
        color = color.substr(1);
    }
    return parseInt(color, 16);
};

export const colorNumberToHex = (color: number) => {
    return `#${color.toString(16)}`;
};

export const fastaCheck = (fasta: string) => {
    const fastaFileText = fasta.split(/\n|\r/g);
    let sequence: string[] = [];
    if (fastaFileText[0][0] !== '>') return 1;
    for (let i = 1, l = fastaFileText.length; i < l; i++) {
        if (fastaFileText[i][0] === '>') {
            const sequenceText = sequence.join('').trim();
            if (sequenceText === '' || !checkStandardAminoAcids(sequenceText)) {
                return 2;
            }
            sequence = [];
        } else {
            sequence.push(fastaFileText[i]);
        }
    }
    const sequenceText = sequence.join('').trim();
    if (sequenceText === '' || !checkStandardAminoAcids(sequenceText)) {
        return 2;
    }
    return 0;
};

export const checkSequenceName = (input: { name: string; index?: number }, rules: NameRuleEnum[], array: string[]) => {
    return rules.every(rule => {
        if (input.name === null) return true;
        switch (rule) {
            case NameRuleEnum.NOT_NULL:
                return !!input.name;
            case NameRuleEnum.LENGTH_100:
                return input.name.length <= 100;
            case NameRuleEnum.NOT_REPEAT:
                return array.findIndex((name, index) => name === input.name && index !== input.index) === -1;
            default:
                return true;
        }
    });
};

export const createChainDataFromLine = (lines: string[], rules: { limit: number }) => {
    const seqs: ChainProps[] = [];
    lines.forEach(item => {
        if (item.startsWith('>')) {
            seqs.push({
                name: item.slice(1),
                key: guid(),
                sequence: '',
                errorMsg: '',
            });
        } else {
            seqs[seqs.length - 1].sequence += item;
            seqs[seqs.length - 1].errorMsg = checkInputSequence(seqs[seqs.length - 1].sequence!, rules.limit);
        }
    });
    return seqs;
};

export const checkInputSequence = (text: string, limit?: number) => {
    const pureText = text.replace(/[\n\r ]+/g, '');
    if (!pureText) return 'Sequence is empty.';
    // if (pureText.length > (limit ?? 1000)) return ERROR_MSG.ParamIsIllegal('The sequence length', 0, limit ?? 1000);
    if (!checkStandardAminoAcids(pureText)) return 'Please input the standard amino acid.';
};

export const getStringFromChainData = (data: ChainProps[]) => {
    return data
        .map(c => ({
            ...c,
            sequence: c.sequence?.replaceAll(' ', '').replaceAll('\n', ''),
        }))
        .reduce((acc, cur) => {
            const seq = `>${cur.name}\n${cur.sequence}`;
            if (acc === '') {
                return seq;
            }
            return `${acc}\n${seq}`;
        }, '');
};

export const checkStandardAminoAcids = (fasta: string) => {
    return /^[GAVLIFWYDNEKQMSTCPHR\r\n ]+$/.test(fasta);
};

export const numberFormat = (value: number) => {
    const param: {
        value: string | number;
        unit: string;
    } = {
        value,
        unit: '',
    };
    const k = 1000;
    const sizes = ['', 'K', 'M', 'B'];
    let i;
    if (value < k) {
        param.value = value;
        param.unit = '';
    } else {
        i = Math.floor(Math.log(value) / Math.log(k));
        param.value = (value / k ** i).toFixed(0);
        param.unit = sizes[i];
    }
    return `${param.value}${param.unit}`;
};

export const numberThousandsFormat = (num: number) => {
    return num.toFixed(2).replace(/\d+/, n => {
        return n.replace(/(\d)(?=(?:\d{3})+$)/g, '$1,');
    });
};

export const splitFileName = (url: string) => {
    url = url.split('?')[0] || '';
    const arr = url.split(/\/|\\/);
    return arr[arr.length - 1];
};
export const getStandardTypeSymbol = (typeSymbol: string) => {
    if (typeSymbol.length > 2 || typeSymbol.length === 0) {
        return typeSymbol;
    }
    return `${typeSymbol[0].toLocaleUpperCase()}${typeSymbol.length === 2 ? typeSymbol[1].toLocaleLowerCase() : ''}`;
};

export const insertParams = (search: string, key: string, value: string) => {
    key = encodeURIComponent(key);
    value = encodeURIComponent(value);

    // kvp looks like ['key1=value1', 'key2=value2', ...]
    const kvp = search ? search.split('&') : [];
    let i = 0;

    for (; i < kvp.length; i++) {
        if (kvp[i].startsWith(`${key}=`)) {
            const pair = kvp[i].split('=');
            pair[1] = value;
            kvp[i] = pair.join('=');
            break;
        }
    }

    if (i >= kvp.length) {
        kvp[kvp.length] = [key, value].join('=');
    }

    // can return this or...
    const params = kvp.join('&');

    // reload page with new params
    return params;
};

// 对象数组去重
export const uniqueArr = (arr: any[], key?: Function) => {
    if (!key) return [...new Set(arr).values()];

    const obj = arr.reduce(
        (o, e) => {
            o[key(e)] = e;
            return o;
        },
        {} as {
            [propName: string]: any;
        }
    );
    // const obj = arr.reduce((o, e) => ((o[key(e)] = e), o), {});
    const res = Object.values(obj);
    return res;
};

export const JSON_stringify = (o: any) => {
    const cache: any[] = [];
    return JSON.stringify(o, function (key, value) {
        if (typeof value === 'object' && value !== null) {
            if (cache.indexOf(value) !== -1) {
                // 移除
                return 'cached';
            }
            // 收集所有的值
            cache.push(value);
        }
        return value;
    });
};

export const parseMapToObj = (map: Map<string, any>) =>
    Array.from(map).reduce((total, [key, value]) => {
        total[key] = value;
        return total;
    }, {} as { [key: string]: any });

export const parseSetToObj = (set: Set<string>, value: any) =>
    Array.from(set).reduce((total, key) => {
        total[key] = value;
        return total;
    }, {} as { [key: string]: any });

export const splitCsvLine = (line: string) => {
    const res: string[] = [];
    let isStart = false;
    let cache: string[] = [];
    for (let i = 0, l = line.length; i < l; i++) {
        const char = line[i];
        switch (char) {
            case '"':
                isStart = !isStart;
                break;
            case ',':
                if (isStart) cache.push(char);
                else {
                    res.push(cache.join(''));
                    cache = [];
                }
                break;
            default:
                cache.push(char);
                break;
        }
    }
    if (cache.length) {
        res.push(cache.join('').trim());
    }
    return res;
};

export const downloadAsText = (filename: string, text: string, type = 'text/plain') => {
    const element = document.createElement('a');
    element.setAttribute('href', `data:${type};charset=utf-8,${encodeURIComponent(text)}`);
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
};
