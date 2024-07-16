import fileSelector from "./fileSelector";

export const manualSelectFiles = async (fileTypes: string[], multiple = false) => {
    const accept = fileTypes.length > 0 ? fileTypes.map(type => `.${type}`).join(',') : undefined;
    fileSelector.setAttrs({ accept, multiple });
    const fileList = await fileSelector.selectFile();
    const files = Array.from(fileList).filter(file => file !== null) as File[];
    return files;
};