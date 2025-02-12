"use client";

import React from "react";

import { ModuleRegistry } from "ag-grid-community";
import { AllEnterpriseModule, LicenseManager } from "ag-grid-enterprise";
import MainGrid from "@/components/MainGrid";

ModuleRegistry.registerModules([AllEnterpriseModule]);
LicenseManager.setLicenseKey("");

export default function Home() {

  return (
    <div className="h-screen w-screen flex justify-center">
      <MainGrid />
    </div>
  );
};