export function formatContractMonth(dateString: string, useFuturesCode: boolean = false): string {
  if (!dateString) return ""; // Return empty string if dateString is null or undefined

  const date = new Date(dateString);
  const year = date.getFullYear().toString().slice(-2);

  if (useFuturesCode) {
    const month = date.getMonth(); // 0 (January) to 11 (December)
    const monthCodes = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"];
    const monthCode = monthCodes[month];
    return `${monthCode}${year}`;
  }
    const month = date.toLocaleString("default", { month: "short" })
    return `${month} '${year}`;
}

export function formatFinanceNumber(val: number): string {
  const roundedValue = Math.round(val); // Round to the nearest whole number
  const formatted = new Intl.NumberFormat("en-US", {
    style: "decimal",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(Math.abs(roundedValue));

  return roundedValue < 0 ? `(${formatted})` : formatted;
}