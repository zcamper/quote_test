CREATE TABLE IF NOT EXISTS "equipment_all_types" (
"ADRSCODE" TEXT,
  "CUSTNMBR" TEXT,
  "Equipment_ID" TEXT,
  "Wennsoft_Region" TEXT,
  "Wennsoft_Branch" TEXT,
  "Wennsoft_Master_Equip_ID" TEXT,
  "Manufacturer_ID" TEXT,
  "Equipment_Type" TEXT,
  "Wennsoft_Model_Number" TEXT,
  "Wennsoft_Serial_Number" TEXT,
  "Equip_Description_Long" TEXT,
  "Installed_By_Long_Desc" TEXT,
  "Extended_Warranty_Type" TEXT,
  "Extended_Warr_Expiration" TIMESTAMP,
  "Warranty_Expiration" TIMESTAMP,
  "Install_Date" TIMESTAMP,
  "Inactive_Retired_Flag" INTEGER
);
CREATE TABLE IF NOT EXISTS "equipment_ats" (
"ADRSCODE" TEXT,
  "CUSTNMBR" TEXT,
  "Equipment_ID" TEXT,
  "Wennsoft_Region" TEXT,
  "Wennsoft_Branch" TEXT,
  "Wennsoft_Master_Equip_ID" TEXT,
  "Manufacturer_ID" TEXT,
  "Equipment_Type" TEXT,
  "Wennsoft_Model_Number" TEXT,
  "Wennsoft_Serial_Number" TEXT,
  "Equip_Description_Long" TEXT,
  "Installed_By_Long_Desc" TEXT,
  "Extended_Warranty_Type" TEXT,
  "Extended_Warr_Expiration" TIMESTAMP,
  "Warranty_Expiration" TIMESTAMP,
  "Install_Date" TIMESTAMP,
  "Inactive_Retired_Flag" INTEGER
);
CREATE TABLE IF NOT EXISTS "equipment_generator" (
"ADRSCODE" TEXT,
  "CUSTNMBR" TEXT,
  "Equipment_ID" TEXT,
  "Wennsoft_Region" TEXT,
  "Wennsoft_Branch" TEXT,
  "Wennsoft_Master_Equip_ID" TEXT,
  "Manufacturer_ID" TEXT,
  "Equipment_Type" TEXT,
  "Wennsoft_Model_Number" TEXT,
  "Wennsoft_Serial_Number" TEXT,
  "Equip_Description_Long" TEXT,
  "Installed_By_Long_Desc" TEXT,
  "Extended_Warranty_Type" TEXT,
  "Extended_Warr_Expiration" TIMESTAMP,
  "Warranty_Expiration" TIMESTAMP,
  "Install_Date" TIMESTAMP,
  "Inactive_Retired_Flag" INTEGER
);
CREATE TABLE IF NOT EXISTS "equipment_engine" (
"ADRSCODE" TEXT,
  "CUSTNMBR" TEXT,
  "Equipment_ID" TEXT,
  "Wennsoft_Region" TEXT,
  "Wennsoft_Branch" TEXT,
  "Wennsoft_Master_Equip_ID" TEXT,
  "Manufacturer_ID" TEXT,
  "Equipment_Type" TEXT,
  "Wennsoft_Model_Number" TEXT,
  "Wennsoft_Serial_Number" TEXT,
  "Equip_Description_Long" TEXT,
  "Installed_By_Long_Desc" TEXT,
  "Extended_Warranty_Type" TEXT,
  "Extended_Warr_Expiration" TIMESTAMP,
  "Warranty_Expiration" TIMESTAMP,
  "Install_Date" TIMESTAMP,
  "Inactive_Retired_Flag" INTEGER
);
CREATE TABLE IF NOT EXISTS "sv000123_overhead_groups" (
"Overhead_Group_Code" TEXT,
  "Labor_Group_Name" TEXT,
  "DEPRTMNT" TEXT,
  "JOBTITLE" TEXT,
  "PAYRCORD" TEXT,
  "Billing_Amount" REAL,
  "Billing_Description" TEXT,
  "Wennsoft_Affiliate" TEXT,
  "Wennsoft_Region" TEXT,
  "Wennsoft_Branch" TEXT,
  "USERID" TEXT,
  "Technician_ID" TEXT,
  "Technician_Team" TEXT,
  "User_Define_1" TEXT,
  "User_Define_2" TEXT,
  "USRDAT01" TIMESTAMP,
  "USRDAT02" TIMESTAMP,
  "User_Defined_Dollar_1" REAL,
  "User_Defined_Dollar_2" REAL,
  "User_Def_Integer_1" INTEGER,
  "User_Def_Integer_2" INTEGER,
  "WSReserved_CB1" INTEGER,
  "WSReserved_CB2" INTEGER,
  "DEX_ROW_ID" INTEGER
);
CREATE TABLE IF NOT EXISTS "sv00166_pricing_matrix" (
"Pricing_Matrix_Name" TEXT,
  "WS_Cost_Code" INTEGER,
  "WS_Other_Cost_Sub_Code" INTEGER,
  "Price_Matrix_Entry_1" TEXT,
  "Price_Matrix_Entry_2" TEXT,
  "Price_Matrix_Entry_3" TEXT,
  "Price_Matrix_Entry_4" TEXT,
  "Price_Matrix_Entry_5" TEXT,
  "Price_Matrix_Entry_6" TEXT,
  "Price_Matrix_Entry_7" TEXT,
  "SEQNUMBR" INTEGER,
  "WS_Billing_Method" INTEGER,
  "Billing_Amount" REAL,
  "ITEMDESC" TEXT,
  "Pricing_Markup_Amount" REAL,
  "Pricing_Markup_Percent" INTEGER,
  "Pricing_Amount_1" REAL,
  "Pricing_Amount_2" REAL,
  "WS_Bill_Cost_Code" INTEGER,
  "WS_Bill_Other_Cost_Code" INTEGER,
  "Min_Amount_Total" REAL,
  "Max_Amount_Total" REAL,
  "MODIFDT" TIMESTAMP,
  "Modified_Time" TIMESTAMP,
  "MDFUSRID" TEXT,
  "DEX_ROW_ID" INTEGER
);
CREATE TABLE IF NOT EXISTS "service_call_details" (
"SV00300_Service_Call_ID" TEXT,
  "SV00300_CUSTNMBR" TEXT,
  "SV00300_ADRSCODE" TEXT,
  "SV00300_Bill_Customer_Number" TEXT,
  "SV00200_CUSTNAME" TEXT,
  "SV00200_Labor_Group_Name" TEXT,
  "SV00200_Pricing_Matrix_Name" TEXT,
  "PL_CUSTNAME" TEXT,
  "PL_Labor_Group_Name" TEXT,
  "PL_Pricing_Matrix_Name" TEXT,
  "BillCustomer_CUSTNAME" TEXT,
  "SV00302_Equipment_ID" TEXT,
  "Generator_Equipment_ID" TEXT,
  "Generator_Wennsoft_Model_Number" TEXT,
  "Generator_Wennsoft_Serial_Number" TEXT,
  "Engine_Equipment_ID" TEXT,
  "Engine_Wennsoft_Model_Number" TEXT,
  "Engine_Wennsoft_Serial_Number" TEXT,
  "ATS_Equipment_ID" TEXT,
  "ATS_Wennsoft_Model_Number" TEXT,
  "ATS_Wennsoft_Serial_Number" TEXT,
  "SV00400_Extended_Warr_Expiration" TIMESTAMP,
  "SV00400_Warranty_Expiration" TIMESTAMP,
  "SV00400_Install_Date" TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "sv000805_service_notes_resolution" (
"CUSTNMBR" TEXT,
  "ADRSCODE" TEXT,
  "Service_Call_ID" TEXT,
  "Record_Notes" TEXT,
  "WS_Note_Type" TEXT,
  "Note_Service_Index" TEXT,
  "USERID" TEXT,
  "Technician_ID" TEXT,
  "Technician_Team" TEXT,
  "Note_Author" TEXT
);
CREATE TABLE IF NOT EXISTS "sv000805_service_notes_description" (
"CUSTNMBR" TEXT,
  "ADRSCODE" TEXT,
  "Service_Call_ID" TEXT,
  "Record_Notes" TEXT,
  "WS_Note_Type" TEXT,
  "Note_Service_Index" TEXT,
  "USERID" TEXT,
  "Technician_ID" TEXT,
  "Technician_Team" TEXT,
  "Note_Author" TEXT
);
CREATE TABLE IF NOT EXISTS "iv00102_item_quantity_all" (
"ITEMNMBR" TEXT,
  "LOCNCODE" TEXT,
  "QTYONHND" REAL
);

-- Tables for Inspection Feature
CREATE TABLE IF NOT EXISTS "checklists" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL UNIQUE,
    "description" TEXT,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "inspection_checklist_items" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "checklist_id" INTEGER NOT NULL,
    "item_text" TEXT NOT NULL,
    "category" TEXT,
    "is_required" BOOLEAN NOT NULL DEFAULT 1,
    "display_order" INTEGER,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("checklist_id") REFERENCES "checklists"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "inspections" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "quote_id" TEXT NOT NULL,
    "checklist_id" INTEGER NOT NULL,
    "inspector_name" TEXT,
    "inspection_date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "unit_status" TEXT,
    "repair_quote_needed" BOOLEAN,
    "overall_comments" TEXT,
    "status" TEXT NOT NULL DEFAULT 'Draft', -- e.g., Draft, Submitted
    FOREIGN KEY ("checklist_id") REFERENCES "checklists"("id")
);

CREATE TABLE IF NOT EXISTS "inspection_results" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "inspection_id" INTEGER NOT NULL,
    "checklist_item_id" INTEGER NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'Not Checked', -- e.g., Not Checked, Passed, Failed
    "comments" TEXT,
    FOREIGN KEY ("inspection_id") REFERENCES "inspections"("id") ON DELETE CASCADE,
    FOREIGN KEY ("checklist_item_id") REFERENCES "inspection_checklist_items"("id")
);

CREATE TABLE IF NOT EXISTS "inspection_photos" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "inspection_id" INTEGER NOT NULL,
    "file_path" TEXT NOT NULL,
    "description" TEXT,
    "uploaded_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("inspection_id") REFERENCES "inspections"("id") ON DELETE CASCADE
);
