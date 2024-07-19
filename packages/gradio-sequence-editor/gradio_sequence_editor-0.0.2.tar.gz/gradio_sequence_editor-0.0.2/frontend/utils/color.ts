export const ColorMap: { [key: string]: string } = {
    G: '#f3b228',
    A: '#f3b228',
    V: '#48b596',
    L: '#48b596',
    I: '#48b596',
    F: '#48b596',
    W: '#48b596',
    Y: '#48b596',
    D: '#d06142',
    N: '#a567f9',
    E: '#d06142',
    K: '#0A63D1',
    Q: '#a567f9',
    M: '#48b596',
    S: '#f3b228',
    T: '#f3b228',
    C: '#48b596',
    P: '#48b596',
    H: '#a567f9',
    R: '#0A63D1',
}

export const getSequenceColor = (residue: string) => {
    if (residue.length !== 1) return '#000000';
    return ColorMap[residue.toUpperCase()] ?? '#000000';
}