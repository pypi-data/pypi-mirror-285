export function extRemoverCorrector(stringToBeCorrected: string): string {
     return stringToBeCorrected.replace(/\.[^/.]+$/, "").replace(/[ ._]/g, "-");
};