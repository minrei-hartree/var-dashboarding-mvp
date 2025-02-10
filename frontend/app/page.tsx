"use client";

import React from "react";
import useSWR from "swr";
import { AgGridReact } from "ag-grid-react";
import { ColDef } from "ag-grid-enterprise";

import { ModuleRegistry } from "ag-grid-community";
import { AllEnterpriseModule, LicenseManager } from "ag-grid-enterprise";

ModuleRegistry.registerModules([AllEnterpriseModule]);
// LicenseManager.setLicenseKey("Using_this_{AG_Charts_and_AG_Grid}_Enterprise_key_{AG-963284}_in_excess_of_the_licence_granted_is_not_permitted___Please_report_misuse_to_legal@ag-grid.com___For_help_with_changing_this_key_please_contact_info@ag-grid.com___{AcmeCorp}_is_granted_a_{Single_Application}_Developer_License_for_the_application_{AcmeApp}_only_for_{1}_Front-End_JavaScript_developer___All_Front-End_JavaScript_developers_working_on_{AcmeApp}_need_to_be_licensed___{AcmeApp}_has_been_granted_a_Deployment_License_Add-on_for_{1}_Production_Environment___This_key_works_with_{AG_Charts_and_AG_Grid}_Enterprise_versions_released_before_{04_May_2024}____[v3]_[0102]_4F37JqkNmUUpwds1nG==WwlRFepEGJshElLJE3uKnQ6vcbwTaJF6");
LicenseManager.setLicenseKey("LICENSE_KEY_HERE");

// Define the data type interface
interface DataRow {
  id: number;
  name: string;
  value: number;
}

// Create a typed fetcher function
const fetcher = (url: string): Promise<DataRow[]> =>
  fetch(url).then((res) => res.json());

export default function Home() {
  const { data, error } = useSWR<DataRow[]>("http://localhost:8000/var/test", fetcher);

  if (error) return <div>Error loading data.</div>;
  if (!data) return <div>Loading...</div>;

  const columnDefs: ColDef[] = [
    { headerName: "ID", field: "id" },
    { headerName: "Name", field: "name" },
    { headerName: "Value", field: "value" },
  ];

  return (
    <div className="ag-theme-alpine" style={{ height: 400, width: 600 }}>
      <AgGridReact rowData={data} columnDefs={columnDefs} />
    </div>
  );
};