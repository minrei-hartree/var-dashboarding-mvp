import useSWR from "swr";
import { ColDef, GetRowIdParams, GridApi, GridOptions } from "ag-grid-enterprise";
import { AgGridReact } from "ag-grid-react";
import { formatContractMonth, formatFinanceNumber } from "@/lib/format";
import { useCallback, useMemo, useState } from "react";

interface DataRow {
  customGroup?: string;
  px_location: number;
  contract_month: string;
  deltaposition: number;
  pnl_vector: number[];
}

const fetcher = (url: string): Promise<DataRow[]> =>
  fetch(url).then((res) => res.json());

function parsePnLVector(vector: string): number[] {
  if (!vector) return [];
  const cleanedVector = vector.replace(/[\[\]]/g, "").trim();
  return cleanedVector.split(",").map(Number);
}

function computeVaR(
  vector: number[],
  lookback: number = 251,
  confidenceLevel: number = 0.05
): number {
  const slicedVector = vector.slice(-lookback);
  const sortedVector = slicedVector.sort((a, b) => a - b);
  const index = Math.floor(sortedVector.length * confidenceLevel);
  return sortedVector[index];
}

const MainGrid = () => {
  const { data, error } = useSWR<DataRow[]>(
    "http://localhost:8000/var/pnl_vectors",
    fetcher
  );
  const [localData, setLocalData] = useState<DataRow[]>([]);

  // Initialize localData when data is fetched
  if (data && localData.length === 0) {
    const groupedData = data.map((row) => {
      if (!row.customGroup) {
        return {...row, customGroup: row.px_location.toString()};
      }
      return row;
    });
    setLocalData(groupedData)
  }

  const getRowId = useCallback((params: GetRowIdParams) => params.data.idx, [])


  const addRowsToGroup = useCallback(
    (groupName: string, selectedNodes: any[]) => {
      if (!localData) return;

      setLocalData((prevData) => {
        const newData = prevData.map((row) => {
          if (selectedNodes.some((node) => node.data === row)) {
            return { ...row, customGroup: groupName };
          }
          return row;
        });
        return newData;
      });
    },
    [localData]
  );

  // Context menu to assign rows to a custom group
  const getContextMenuItems: any = useCallback(
    (params: any) => {
      const selectedNodes = params.api.getSelectedNodes();
      if (selectedNodes.length === 0) return [];

      return [
        {
          name: "Add to Custom Group",
          action: () => {
            const groupName = prompt("Enter a group name:"); // Prompt for group name
            if (groupName) {
              addRowsToGroup(groupName, selectedNodes);
            }
          },
        },
        {
          name: "Ungroup",
          action: () => addRowsToGroup("", selectedNodes), // Remove from groups
        },
        "separator",
        "copy",
        "resetColumns",
      ];
    },
    [addRowsToGroup]
  );

  const autoGroupColumnDef = useMemo(() => {
    return {
      headerName: 'Group',
      field: 'px_location',
      filter: 'agGroupColumnFilter',
      cellStyle: {fontWeight: "500"},
    }
  }, [])

  const columnDefs: ColDef[] = [
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

  const gridOptions: GridOptions = {
    getContextMenuItems,
    suppressContextMenu: false,
    rowSelection: "multiple",
    defaultColDef: {      // Global column configuration
      filter: true,
      sortable: true,
      resizable: true,
      floatingFilter: true,
    }
  };

  if (error) return <div>Error loading data.</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div className="ag-theme-alpine h-full w-full p-10">
      <AgGridReact
        rowData={localData}
        columnDefs={columnDefs}
        gridOptions={gridOptions}
        autoGroupColumnDef={autoGroupColumnDef}
        groupHideParentOfSingleChild={true}
        getRowId={getRowId} // Helps grid re-render fully less
      />
    </div>
  );
};

export default MainGrid;