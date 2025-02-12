import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function parsePnLVector(vector: string): number[] {
  if (!vector) return [];
  const cleanedVector = vector.replace(/[\[\]]/g, "").trim();
  return cleanedVector.split(",").map(Number);
}

export function computeVaR(
  vector: number[],
  lookback: number = 251,
  confidenceLevel: number = 0.05
): number {
  const slicedVector = vector.slice(-lookback);
  const sortedVector = slicedVector.sort((a, b) => a - b);
  const index = Math.floor(sortedVector.length * confidenceLevel);
  return sortedVector[index];
}
