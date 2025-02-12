import useSWR from "swr";
import { ColDef, GetRowIdParams, GridApi, GridOptions } from "ag-grid-enterprise";
import { AgGridReact } from "ag-grid-react";
import { formatContractMonth, formatFinanceNumber } from "@/lib/format";
import { useCallback, useMemo, useState } from "react";
import { computeVaR, parsePnLVector } from "@/lib/utils";

interface DataRow {
  customGroup?: string;
  px_location: number;
  contract_month: string;
  deltaposition: number;
  pnl_vector: number[];
}

export const columnDefs: ColDef[] = [
    // {
    //   headerName: "PX Location",
    //   field: "px_location",
    //   cellStyle: { fontWeight: "500" },
    // },
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
        if (params.node.group) {
          return formatFinanceNumber(params.value);
        }
        const vector = parsePnLVector(params.value);
        return formatFinanceNumber(computeVaR(vector));
      },
      aggFunc: (params) => {
        const allVectors = params.values.map((v: string) => parsePnLVector(v));
        const summedPnL = allVectors.reduce((acc, curr) => {
          if (acc.length === 0) return [...curr];
          return acc.map((value, index) => value + (curr[index] || 0));
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