import useSWR from "swr";
import { ColDef, colorSchemeDark, colorSchemeDarkBlue, colorSchemeDarkWarm, colorSchemeLightCold, GetRowIdParams, GridApi, GridOptions, themeBalham } from "ag-grid-enterprise";
import { AgGridReact } from "ag-grid-react";
import { formatContractMonth, formatFinanceNumber } from "@/lib/format";
import { useCallback, useEffect, useMemo, useState } from "react";
import { columnDefs, DataRow } from "@/lib/gridDefs";
import GridToolbar from "./GridToolbar";
import { Button } from "@/components/ui/button"
import TraderSelection from "./TraderSelection";
import useTraderPnlVectors from "@/hooks/useTraderPnlVectors";


type GroupCache = {
  [key: string]: string
}

const MainGrid = () => {
  const { pnlVectors: data, isLoading } = useTraderPnlVectors()
  const [localData, setLocalData] = useState<DataRow[]>([]);
  const [customGroupCache, setCustomGroupCache] = useState<GroupCache>({});

  // Initialize localData when data is fetched
  useEffect(() => {
    if (data) {
      const groupedData = data.map((row) => {
        return {
          ...row,
          customGroup: customGroupCache[row.idx] || row.px_location
        }
      });
      setLocalData(groupedData)
    }
  }, [data, isLoading])

  const getRowId = useCallback((params: GetRowIdParams) => params.data.idx, [])

  const groupByPxLocation = useCallback(() => {
    const groupedData = localData.map((row) => {
      return {
        ...row,
        customGroup: customGroupCache[row.idx] || row.px_location
      }
    });
    setLocalData(groupedData)
  }, [localData, customGroupCache]);

  const groupByContractMonth = useCallback(() => {
    const groupedData = localData.map((row) => {
      return {
        ...row,
        customGroup: customGroupCache[row.idx] || formatContractMonth(row.contract_month)
      }
    })
    setLocalData(groupedData)
  }, [localData, customGroupCache])

  const addRowsToGroup = useCallback(
    (groupName: string, selectedNodes: any[]) => {
      if (!localData) return;

      setLocalData((prevData) => {
        const updatedCacheEntries: Array<{ idx: string; group: string }> = []
        const newData = prevData.map((row) => {
          if (selectedNodes.some((node) => node.data === row)) {
            updatedCacheEntries.push({ idx: row.idx, group: groupName })
            return { ...row, customGroup: groupName };
          }
          return row;
        });

        setCustomGroupCache((prevCache) => {
          const newCache = { ...prevCache }
          updatedCacheEntries.forEach((entry) => {
            newCache[entry.idx] = entry.group
          })
          return newCache
        })

        return newData
      });
    },
    [localData]
  );

  const logCache = () => { console.log(customGroupCache) }

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
      cellStyle: { fontWeight: "500" },
      minWidth: 400,
    }
  }, [])


  const gridOptions: GridOptions = {
    theme: themeBalham.withPart(colorSchemeLightCold),
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

  return (
    <div className="h-full w-full p-10 flex flex-col gap-4">
      {/* <GridToolbar /> */}
      <div className="flex gap-4">
        <TraderSelection />
        <Button variant="outline" onClick={groupByPxLocation}>group by px location</Button>
        <Button variant="outline" onClick={groupByContractMonth}>group by contract month</Button>
        <Button variant="outline" onClick={logCache}>LOG GROUP CACHE</Button>
      </div>
      <AgGridReact
        loading={isLoading}
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