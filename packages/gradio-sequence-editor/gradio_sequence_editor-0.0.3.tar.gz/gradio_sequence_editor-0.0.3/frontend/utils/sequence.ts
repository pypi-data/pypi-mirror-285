export const AminoAcidSet = new Set([
    "A",
    "R",
    "N",
    "D",
    "C",
    "Q",
    "E",
    "G",
    "H",
    "I",
    "L",
    "K",
    "M",
    "F",
    "P",
    "S",
    "T",
    "W",
    "Y",
    "V"
]);
export const AcidAttrMap = new Map([
    ['Y', 'TYR'],
    ['A', 'ALA'],
    ['V', 'VAL'],
    ['L', 'LEU'],
    ['I', 'ILE'],
    ['F', 'PHE'],
    ['W', 'TRP'],
    ['M', 'MET'],
    ['C', 'CYS'],
    ['P', 'PRO'],
    ['N', 'ASN'],
    ['Q', 'GLN'],
    ['S', 'SER'],
    ['T', 'THR'],
    ['K', 'LYS'],
    ['H', 'HIS'],
    ['R', 'ARG'],
    ['D', 'ASP'],
    ['E', 'GLU'],
    ['G', 'GLY'],
]);
// 定义疏水性指数表
export const HydrophobicityIndex: { [key: string]: number } = {
    'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5, 'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2,
    'I': 4.5, 'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6, 'S': -0.8, 'T': -0.7, 'W': -0.9,
    'Y': -1.3, 'V': 4.2
};

export const calcTotalHydrophobicity = (sequence: string) => {
    // 计算总疏水性
    let res = 0;
    for (let i = 0; i < sequence.length; i++) {
        const residue = sequence[i];
        res += HydrophobicityIndex[residue] ?? 1;
    }
    // 计算平均疏水性
    return (res / sequence.length).toFixed(2);
}

export const Polarity: { [key: string]: number } = {
    'A': 8.1, 'R': 10.5, 'N': 11.6, 'D': 13.0, 'C': 5.5,
    'Q': 10.5, 'E': 12.3, 'G': 9.0, 'H': 10.4, 'I': 5.2,
    'L': 4.9, 'K': 11.3, 'M': 5.7, 'F': 5.2, 'P': 8.0,
    'S': 9.2, 'T': 8.6, 'W': 5.4, 'Y': 6.2, 'V': 5.9
}

export const Bulkiness: { [key: string]: number } = {
    'A': 11.5, 'R': 14.3, 'N': 12.0, 'D': 11.7, 'C': 13.5,
    'Q': 14.0, 'E': 13.6, 'G': 3.4, 'H': 13.7, 'I': 21.4,
    'L': 21.4, 'K': 15.7, 'M': 16.3, 'F': 19.8, 'P': 17.4,
    'S': 9.2, 'T': 15.2, 'W': 21.7, 'Y': 18.0, 'V': 21.6
}

export const AminoAcidWeight: { [key: string]: number } = {
    'A': 89.09, 'R': 174.20, 'N': 132.12, 'D': 133.10, 'C': 121.16,
    'Q': 146.15, 'E': 147.13, 'G': 75.07, 'H': 155.16, 'I': 131.18,
    'L': 131.18, 'K': 146.19, 'M': 149.21, 'F': 165.19, 'P': 115.13,
    'S': 105.09, 'T': 119.12, 'W': 204.23, 'Y': 181.19, 'V': 117.15
}

export const calcSequenceWeight = (sequence: string) => {
    let molecularWeight = 0;

    // Calculate total molecular weight
    for (let i = 0; i < sequence.length; i++) {
        let aa = sequence[i].toUpperCase(); // Convert to uppercase for case insensitivity
        if (AminoAcidWeight[aa]) {
            molecularWeight += AminoAcidWeight[aa];
        } else {
            // Handle unknown amino acids or non-amino acid characters
            console.warn('Unknown amino acid or character: ' + aa);
        }
    }

    // Convert molecular weight to kDa (kilodaltons)
    let molecularWeightInKDa = molecularWeight / 1000;

    return molecularWeightInKDa.toFixed(2);
}

export const pKa: { [key: string]: number } = {
    'C': 8.18, 'D': 3.86, 'E': 4.25, 'H': 6.00, 'K': 10.53,
    'R': 12.48, 'Y': 10.07, 'A': 2.34, 'N': 8.80, 'Q': 5.65,
    'G': 2.34, 'I': 2.36, 'L': 2.36, 'M': 2.28, 'F': 2.58,
    'P': 1.99, 'S': 2.21, 'T': 2.09, 'V': 2.32, 'W': 3.78
};

const calculateCharge = (sequence: string, pH: number) => {
    // Define pKa values for ionizable groups

    let positiveCharge = 0;
    let negativeCharge = 0;

    for (let i = 0; i < sequence.length; i++) {
        let aa = sequence[i].toUpperCase();
        if (pKa[aa]) {
            let pKaValue = pKa[aa];
            let ratio = Math.pow(10, pH - pKaValue);
            positiveCharge += 1 / (1 + ratio);
            negativeCharge += ratio / (1 + ratio);
        }
    }

    let netCharge = positiveCharge - negativeCharge;
    return netCharge;
}

export const calcSequencePl = (sequence: string) => {
    let pH = 7.0; // Initial guess for pH (neutral pH)
    let charge = calculateCharge(sequence, pH);

    // Iteratively find the pH at which the net charge is closest to zero
    const tolerance = 0.01; // Desired precision
    let iterations = 0;
    const maxIterations = 100;
    while (Math.abs(charge) > tolerance && iterations < maxIterations) {
        pH += charge > 0 ? 0.5 : -0.5; // Adjust pH based on charge
        charge = calculateCharge(sequence, pH);
        iterations++;
    }

    return pH.toFixed(2); // Return pI rounded to 2 decimal places
}
