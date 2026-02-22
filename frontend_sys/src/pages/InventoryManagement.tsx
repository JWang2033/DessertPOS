import React, { useState, useMemo, useEffect } from "react";
import {
  Table,
  InputNumber,
  Tag,
  Select,
  message,
  Tabs,
  Typography,
} from "antd";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { getInventory, updateInventory, getUnits } from "../services/api";
import { InventoryItem, Unit } from "../types";
import { calculateDiff } from "../utils/inventoryHelpers";
import InventoryToolbar from "../components/InventoryToolbar";

dayjs.extend(relativeTime);

const { Title } = Typography;

interface ApiInventoryItem {
  inventory_id: number;
  ingredient_id?: number;
  ingredient_name: string;
  category_name?: string;
  brand?: string | null;
  standard_qty?: number | string | null;
  actual_qty?: number | string | null;
  unit_abbreviation: string;
  location: string;
  update_time: string;
  restock_needed: boolean;
  item_type: "ingredient" | "semi_product";
}

const InventoryManagement: React.FC = () => {
  const [data, setData] = useState<InventoryItem[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState("");
  const [locationFilter, setLocationFilter] = useState<string[]>([]);
  const [typeFilter, setTypeFilter] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState("ingredients");
  const [groupBy, setGroupBy] = useState<
    "none" | "location" | "health" | "accuracy"
  >("none");
  const [sortBy, setSortBy] = useState<
    "default" | "updated_desc" | "diff_desc" | "diff_asc"
  >("default");

  useEffect(() => {
    fetchInventory();
    fetchUnits();
  }, []); // Fetch on initial component mount

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const response = await getInventory();
      // Map backend data to frontend InventoryItem type
      const transformedData = (response.data as ApiInventoryItem[]).map(
        (item): InventoryItem => ({
        id: item.inventory_id.toString(),
        ingredientId:
          item.item_type === "ingredient" && item.ingredient_id
            ? item.ingredient_id.toString()
            : undefined,
        semiFinishedId:
          item.item_type === "semi_product" && item.ingredient_id
            ? item.ingredient_id.toString()
            : undefined,
        name: item.ingredient_name,
        type:
          item.item_type === "semi_product"
            ? "Semi-Finished"
            : item.category_name || "",
        brand: item.brand || undefined,
        standardQty: Number(item.standard_qty || 0),
        actualQty: Number(item.actual_qty || 0),
        unit: item.unit_abbreviation,
        store_id: "N/A", // Backend doesn't provide this yet, so hardcode or hide
        location: item.location,
        lastUpdated: item.update_time,
        status: item.restock_needed ? "Restock Needed" : "Sufficient",
      }),
      );
      setData(transformedData);
    } catch {
      message.error("Failed to fetch inventory data.");
    } finally {
      setLoading(false);
    }
  };

  const fetchUnits = async () => {
    try {
      const response = await getUnits();
      // The backend returns Unit objects with {id, name, abbreviation}
      // The frontend `types.ts` expects {id, name, abbreviation}
      // So a direct mapping is fine.
      setUnits(response.data);
    } catch {
      message.error("Failed to fetch units.");
    }
  };

  // Get unique existing locations for dropdown from live data
  const uniqueLocations = useMemo(() => {
    return Array.from(new Set(data.map((i) => i.location))).sort();
  }, [data]);

  const locationOptions = uniqueLocations.map((l) => ({ value: l, label: l }));
  const unitOptions = units.map((u) => ({
    value: u.abbreviation,
    label: u.abbreviation,
  }));

  // Unique Types for Filter (dependent on activeTab) from live data
  const uniqueTypes = Array.from(
    new Set(
      data
        .filter((item) =>
          activeTab === "ingredients"
            ? item.type !== "Semi-Finished"
            : item.type === "Semi-Finished",
        )
        .map((i) => i.type),
    ),
  ).sort();
  const typeOptions = uniqueTypes.map((t) => ({ value: t, label: t }));

  // Handle actual quantity change and save to backend
  const handleQuantityChange = async (value: number | null, id: string) => {
    if (value === null) return;

    const originalData = [...data];
    const itemToUpdate = data.find((item) => item.id === id);
    if (!itemToUpdate) return;

    // Optimistic UI update
    setData((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, actualQty: value, lastUpdated: new Date().toISOString() } : item
      )
    );

    try {
      await updateInventory(parseInt(id, 10), { actual_qty: value });
      message.success("Quantity saved to backend!");
      // Optionally, refetch to ensure data consistency
      // fetchInventory();
    } catch {
      message.error("Failed to update quantity.");
      setData(originalData); // Revert on failure
    }
  };

  // These handlers are now informational as the backend doesn't support these updates yet
  const handleUnitChange = (value: string, id: string) => {
    void value;
    void id;
    message.info("Changing the unit of an existing inventory item is not supported.");
  };

  const handleLocationChange = (value: string, id: string) => {
    void value;
    void id;
    message.info("Changing location is not yet supported by the backend.");
  };

  const filteredData = data.filter((item) => {
    const isCorrectType =
      activeTab === "ingredients"
        ? item.type !== "Semi-Finished"
        : item.type === "Semi-Finished";
    const matchesSearch = item.name
      .toLowerCase()
      .includes(searchText.toLowerCase());
    const matchesLocation =
      locationFilter.length > 0 ? locationFilter.includes(item.location) : true;
    const matchesType =
      typeFilter.length > 0 ? typeFilter.includes(item.type) : true;
    return isCorrectType && matchesSearch && matchesLocation && matchesType;
  });

  // Sort Data
  const sortedData = [...filteredData].sort((a, b) => {
    if (sortBy === "updated_desc") {
      return new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime();
    }
    if (sortBy === "diff_desc") {
      const diffA = calculateDiff(a.actualQty, a.standardQty);
      const diffB = calculateDiff(b.actualQty, b.standardQty);
      return diffB - diffA;
    }
    if (sortBy === "diff_asc") {
      const diffA = calculateDiff(a.actualQty, a.standardQty);
      const diffB = calculateDiff(b.actualQty, b.standardQty);
      return diffA - diffB;
    }
    return 0;
  });

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      fixed: "left" as const,
      width: 260,
      render: (text: string, record: InventoryItem) => (
        <div>
          <div className="font-bold text-gray-800">{text}</div>
          {activeTab === "ingredients" && (
            <div className="text-xs text-gray-400">{record.brand}</div>
          )}
        </div>
      ),
    },
    ...(activeTab === "ingredients"
      ? [
          {
            title: "Type",
            dataIndex: "type",
            key: "type",
            width: 100,
            render: (text: string) => <Tag>{text}</Tag>,
          },
        ]
      : []),
    {
      title: "Expected Qty",
      dataIndex: "standardQty",
      key: "standardQty",
      width: 160,
      align: "right" as const,
      render: (val: number, record: InventoryItem) => (
        <span className="text-gray-500">
          {val.toFixed(2)} {record.unit}
        </span>
      ),
    },
    {
      title: "Actual Qty",
      dataIndex: "actualQty",
      key: "actualQty",
      width: 220,
      align: "left" as const,
      render: (val: number, record: InventoryItem) => (
        <InputNumber
          min={0}
          value={val}
          onChange={(v) => handleQuantityChange(v, record.id)}
          className="w-full"
          addonAfter={
            <Select
              value={record.unit}
              onChange={(u) => handleUnitChange(u, record.id)}
              options={unitOptions}
              className="w-[80px]"
              variant="borderless"
              size="small"
              dropdownMatchSelectWidth={false}
              disabled // Disable unit changes on existing items
            />
          }
        />
      ),
    },
    {
      title: "Diff %",
      key: "diff",
      width: 80,
      render: (_: unknown, record: InventoryItem) => {
        const diff = calculateDiff(record.actualQty, record.standardQty);
        const color = diff < -20 ? "red" : diff < 0 ? "orange" : "green";
        return (
          <span style={{ color }} className="font-medium">
            {diff > 0 ? "+" : ""}
            {diff.toFixed(1)}%
          </span>
        );
      },
    },
    {
      title: "Location",
      dataIndex: "location",
      key: "location",
      width: 140,
      render: (loc: string, record: InventoryItem) => (
        <Select
          value={loc}
          className="w-full"
          onChange={(v) => handleLocationChange(v, record.id)}
          options={locationOptions}
          showSearch
          disabled // Disable location changes for now
        />
      ),
    },
    {
      title: "Update Time",
      dataIndex: "lastUpdated",
      key: "lastUpdated",
      width: 150,
      render: (text: string) => (
        <span className="text-xs text-gray-500">{dayjs(text).fromNow()}</span>
      ),
    },
    {
      title: "Health",
      dataIndex: "status",
      key: "status",
      fixed: "right" as const,
      width: 110,
      render: (status: string) => (
        <Tag color={status === "Sufficient" ? "success" : "error"}>
          {status === "Sufficient" ? "Sufficient" : "Restock"}
        </Tag>
      ),
    },
  ];

  const items = [
    {
      key: "ingredients",
      label: "Ingredients",
    },
    {
      key: "semifinished",
      label: "Semi-Finished Products",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Title level={3} style={{ margin: 0 }}>
            Inventory Management
          </Title>
          <p className="text-gray-500 mt-1">
            Track and manage stock levels for ingredients and semi-finished products.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6 space-y-4">
        <InventoryToolbar
          searchText={searchText}
          onSearchChange={setSearchText}
          locationFilter={locationFilter}
          onLocationFilterChange={setLocationFilter}
          locationOptions={locationOptions}
          typeFilter={typeFilter}
          onTypeFilterChange={setTypeFilter}
          typeOptions={typeOptions}
          groupBy={groupBy}
          onGroupByChange={(value) =>
            setGroupBy(value as "none" | "location" | "health" | "accuracy")
          }
          sortBy={sortBy}
          onSortByChange={(value) =>
            setSortBy(
              value as "default" | "updated_desc" | "diff_desc" | "diff_asc",
            )
          }
          // These are hardcoded for now as they are not part of the current backend logic
          groupByOptions={[
            { value: "none", label: "None" },
            { value: "location", label: "Location" },
            { value: "health", label: "Health" },
            { value: "accuracy", label: "Accuracy" },
          ]}
          sortByOptions={[
            { value: "default", label: "Default" },
            { value: "updated_desc", label: "Last Updated" },
            { value: "diff_desc", label: "Diff % (High-Low)" },
            { value: "diff_asc", label: "Diff % (Low-High)" },
          ]}
        />

        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={items}
          className="mb-[-1px]"
        />

        <Table
          columns={columns}
          dataSource={sortedData}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1300 }}
          pagination={{ pageSize: 10 }}
        />
      </div>
    </div>
  );
};

export default InventoryManagement;
