import useSWR from "swr";
import { ColDef, GetRowIdParams, GridApi, GridOptions } from "ag-grid-enterprise";
import { AgGridReact } from "ag-grid-react";
import { formatContractMonth, formatFinanceNumber } from "@/lib/format";
import { useCallback, useMemo, useState } from "react";
import { computeVaR, parsePnLVector } from "@/lib/utils";

export interface DataRow {
  customGroup?: string;
  px_location: string;
  contract_month: string;
  deltaposition: number;
  pnl_vector: number[];
  idx: string;
}


export const columnDefs: ColDef[] = [
    {
      headerName: "Contract Month",
      field: "contract_month",
      valueFormatter: (params) => {
        return params.value === "2006-06-01" // Equity
          ? ""
          : formatContractMonth(params.value);
      },
    },
    {
      headerName: "Delta Position",
      field: "deltaposition",
      valueFormatter: (params) => {
        return formatFinanceNumber(params.value);
      },
      aggFunc: (params) => {
        return params.values.reduce((v, s) => v + s, 0);
      },
    },
    {
      headerName: "1Y VaR",
      field: "pnl_vector",
      valueFormatter: (params) => {
        if (params.node.group) { // already VaR
          return formatFinanceNumber(params.value);
        } // raw pnl vector
        return formatFinanceNumber(computeVaR(params.value));
      },
      aggFunc: (params) => {
        // const allVectors = params.values.map((v: string) => parsePnLVector(v));
        const summedPnL = params.values.reduce((acc, curr) => {
          if (acc.length === 0) return [...curr];
          return acc.map((value: number, index: number) => value + (curr[index] || 0));
        }, []);
        return computeVaR(summedPnL);
      },
    },
    {
      headerName: "Custom Group",
      field: "customGroup",
      rowGroup: true,
      hide: true,
    },
  ];