export const parseTime = (timeStr: string): number => {
  if (!timeStr) return 999999;
  if (timeStr.includes("min")) return parseInt(timeStr) || 0;
  if (timeStr.includes("hour")) return (parseInt(timeStr) || 0) * 60;
  if (timeStr.includes("day")) return (parseInt(timeStr) || 0) * 1440;
  return 999999;
};

export const calculateDiff = (actual: number, standard: number): number => {
  if (standard === 0) return 0;
  return ((actual - standard) / standard) * 100;
};
