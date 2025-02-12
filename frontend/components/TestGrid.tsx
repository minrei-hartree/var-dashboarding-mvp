import useSWR from "swr";
import { ColDef } from "ag-grid-enterprise";
import { AgGridReact } from "ag-grid-react";

interface DataRow {
  id: number;
  name: string;
  value: number;
}

const fetcher = (url: string): Promise<DataRow[]> =>
  fetch(url).then((res) => res.json());

const TestGrid = () => {
  const { data, error } = useSWR<DataRow[]>("http://localhost:8000/var/test", fetcher);

  if (error) return <div>Error loading data.</div>;
  if (!data) return <div>Loading...</div>;

  const columnDefs: ColDef[] = [
    { headerName: "ID", field: "id" },
    { headerName: "Name", field: "name" },
    { headerName: "Value", field: "value" },
  ];

  return (
      <div className="ag-theme-alpine h-full w-full p-10">
        <AgGridReact
          rowData={data} columnDefs={columnDefs}
        />
      </div>
  )
}

export default TestGrid