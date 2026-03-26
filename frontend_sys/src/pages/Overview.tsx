import React, { useEffect, useState } from "react";
import { Table, Statistic, Row, Col, Typography, Tag, Tabs } from "antd";
import type { ColumnsType } from "antd/es/table";
import { Package, AlertTriangle, CheckCheck } from "lucide-react";
import { InventoryItem } from "../types";
import { parseTime, calculateDiff } from "../utils/inventoryHelpers";
import InventoryToolbar from "../components/InventoryToolbar";
import { getInventory } from "../services/api";

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
  store_id?: string;
}

const Overview: React.FC = () => {
  const [searchText, setSearchText] = useState("");
  const [activeTab, setActiveTab] = useState("ingredients");
  const [inventoryData, setInventoryData] = useState<InventoryItem[]>([]);
  const [storeFilter, setStoreFilter] = useState<string[]>([]);
  const [typeFilter, setTypeFilter] = useState<string[]>([]);
  const [groupBy, setGroupBy] = useState<
    "none" | "store" | "health" | "accuracy"
  >("store");
  const [sortBy, setSortBy] = useState<
    "default" | "updated_desc" | "diff_desc" | "diff_asc"
  >("default");

  const formatLastUpdated = (timestamp: string) => {
    const updated = new Date(timestamp);
    const diffMinutes = Math.max(
      1,
      Math.floor((Date.now() - updated.getTime()) / 60000),
    );
    if (diffMinutes < 60) return `${diffMinutes} mins ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)} hours ago`;
    return `${Math.floor(diffMinutes / 1440)} days ago`;
  };

  useEffect(() => {
    const fetchInventory = async () => {
      try {
        const response = await getInventory();
        const mapped = (response.data as ApiInventoryItem[]).map((item) => ({
          id: item.inventory_id.toString(),
          ingredientId:
            item.item_type === "ingredient"
              ? item.ingredient_id.toString()
              : undefined,
          semiFinishedId:
            item.item_type === "semi_product"
              ? item.ingredient_id?.toString()
              : undefined,
          name: item.ingredient_name,
          type: item.item_type === "semi_product" ? "Semi-Finished" : item.category_name,
          brand: item.brand,
          standardQty: Number(item.standard_qty || 0),
          actualQty: Number(item.actual_qty || 0),
          unit: item.unit_abbreviation,
          store_id: item.store_id || "N/A",
          location: item.location,
          lastUpdated: formatLastUpdated(item.update_time),
          status: item.restock_needed ? "Restock Needed" : "Sufficient",
        }));
        setInventoryData(mapped);
      } catch {
        setInventoryData([]);
      }
    };

    fetchInventory();
  }, []);

  // Filter Data
  const filteredData = inventoryData.filter((item) => {
    const isIngredient =
      activeTab === "ingredients"
        ? item.type !== "Semi-Finished"
        : item.type === "Semi-Finished";
    const matchesSearch = item.name
      .toLowerCase()
      .includes(searchText.toLowerCase());
    const matchesStore =
      storeFilter.length > 0 ? storeFilter.includes(item.store_id) : true;
    const matchesType =
      typeFilter.length > 0 ? typeFilter.includes(item.type) : true;
    return isIngredient && matchesSearch && matchesStore && matchesType;
  });

  // Sort Data
  const sortedData = [...filteredData].sort((a, b) => {
    if (sortBy === "updated_desc") {
      return parseTime(a.lastUpdated) - parseTime(b.lastUpdated); // Smaller minutes = more recent
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

  // Unique Stores for Filter
  const uniqueStores = Array.from(
    new Set(inventoryData.map((i) => i.store_id)),
  ).sort();
  const storeOptions = uniqueStores.map((s) => ({
    value: s,
    label: `Store ${s}`,
  }));

  // Unique Types for Filter (dependent on activeTab)
  const uniqueTypes = Array.from(
    new Set(
      inventoryData
        .filter((item) =>
          activeTab === "ingredients"
            ? item.type !== "Semi-Finished"
            : item.type === "Semi-Finished",
        )
        .map((i) => i.type),
    ),
  ).sort();
  const typeOptions = uniqueTypes.map((t) => ({ value: t, label: t }));

  // Statistics Calculation (Global)
  const totalItems = inventoryData.length;
  const lowStockCount = inventoryData.filter(
    (i) => i.status === "Restock Needed",
  ).length;
  // Mock accuracy calculation
  const accuracy = 98.5;

  const columns: ColumnsType<InventoryItem> = [
    {
      title: "Store ID",
      dataIndex: "store_id",
      key: "store_id",
      width: 120,
      render: (text: string) => <Tag color="geekblue">{text}</Tag>,
      sorter: (a: InventoryItem, b: InventoryItem) =>
        a.store_id.localeCompare(b.store_id),
      // Default sort by store ID to group them visually
      defaultSortOrder: "ascend" as const,
    },
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
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
      width: 140,
      align: "right" as const,
      render: (val: number, record: InventoryItem) => (
        <span className="text-gray-500">
          {val} {record.unit}
        </span>
      ),
    },
    {
      title: "Actual Qty",
      dataIndex: "actualQty",
      key: "actualQty",
      width: 120,
      align: "center" as const,
      render: (val: number, record: InventoryItem) => (
        <span className="font-medium text-gray-800">
          {val} {record.unit}
        </span>
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
      title: "Update Time",
      dataIndex: "lastUpdated",
      key: "lastUpdated",
      width: 150,
      render: (text: string) => (
        <span className="text-xs text-gray-500">{text}</span>
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
      <Title level={3}>Overview</Title>

      <Row gutter={16}>
        <Col span={8}>
          <div className="bg-white rounded-lg shadow-sm p-6 h-full">
            <Statistic
              title="Total Inventory Items (All Stores)"
              value={totalItems}
              prefix={<Package size={20} className="mr-2 text-blue-500" />}
            />
          </div>
        </Col>
        <Col span={8}>
          <div className="bg-white rounded-lg shadow-sm p-6 h-full">
            <Statistic
              title="Global Alerts"
              value={lowStockCount}
              valueStyle={{ color: "#cf1322" }}
              prefix={<AlertTriangle size={20} className="mr-2" />}
              suffix="Items"
            />
          </div>
        </Col>
        <Col span={8}>
          <div className="bg-white rounded-lg shadow-sm p-6 h-full">
            <Statistic
              title="Network Inventory Stock Accuracy"
              value={accuracy}
              precision={1}
              formatter={(value) => (
                <span>
                  {value}
                  <span className="text-sm ml-0.5">%</span>
                </span>
              )}
              prefix={<CheckCheck size={20} className="mr-2 text-green-500" />}
            />
          </div>
        </Col>
      </Row>

      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 font-semibold text-lg">
          Inventory Status Across Network
        </div>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={items}
          className="px-6 pt-2 border-b border-gray-100"
          size="large"
        />
        <div className="p-6 space-y-8">
          {/* Toolbar */}
          <InventoryToolbar
            searchText={searchText}
            onSearchChange={setSearchText}
            filterLabel="Filter"
            locationFilter={storeFilter} // Mapping store to location prop
            onLocationFilterChange={setStoreFilter}
            locationOptions={storeOptions}
            locationPlaceholder="Store"
            typeFilter={typeFilter}
            onTypeFilterChange={setTypeFilter}
            typeOptions={typeOptions}
            groupBy={groupBy}
            onGroupByChange={setGroupBy}
            groupByOptions={[
              { value: "none", label: "Group: None" },
              { value: "store", label: "Group: Store" },
              { value: "health", label: "Group: Health" },
              { value: "accuracy", label: "Group: Accuracy" },
            ]}
            sortBy={sortBy}
            onSortByChange={setSortBy}
            sortByOptions={[
              { value: "default", label: "Sort: Default" },
              { value: "updated_desc", label: "Updated (Newest)" },
              { value: "diff_desc", label: "Diff % (High to Low)" },
              { value: "diff_asc", label: "Diff % (Low to High)" },
            ]}
          />

          {/* Group data dynamically */}
          {Object.entries(
            sortedData.reduce(
              (acc, item) => {
                let key = "";
                if (groupBy === "store") {
                  key = item.store_id;
                } else if (groupBy === "health") {
                  key = item.status;
                } else if (groupBy === "accuracy") {
                  const diff = calculateDiff(item.actualQty, item.standardQty);
                  key = Math.abs(diff) <= 10 ? "Accurate" : "Inaccurate";
                } else {
                  key = "All Inventory";
                }

                if (!acc[key]) acc[key] = [];
                acc[key].push(item);
                return acc;
              },
              {} as Record<string, InventoryItem[]>,
            ),
          )
            .sort(([keyA], [keyB]) => keyA.localeCompare(keyB))
            .map(([groupKey, groupItems]) => (
              <div
                key={groupKey}
                className="border border-gray-200 rounded-lg overflow-hidden"
              >
                <div
                  className={`px-4 py-3 border-b border-gray-200 flex justify-between items-center ${
                    groupBy === "health" && groupKey === "Restock Needed"
                      ? "bg-red-50"
                      : groupBy === "accuracy" && groupKey === "Inaccurate"
                        ? "bg-orange-50"
                        : "bg-gray-50"
                  }`}
                >
                  <h3
                    className={`font-medium ${
                      groupBy === "health" && groupKey === "Restock Needed"
                        ? "text-red-700"
                        : groupBy === "accuracy" && groupKey === "Inaccurate"
                          ? "text-orange-700"
                          : "text-gray-700"
                    }`}
                  >
                    {groupBy === "store" ? `Store ${groupKey}` : groupKey}
                  </h3>
                  <Tag>{groupItems.length} Items</Tag>
                </div>
                <Table
                  columns={
                    columns.filter((col) => {
                      if (groupBy === "store" && col.key === "store_id")
                        return false;
                      if (groupBy === "health" && col.key === "status")
                        return false;
                      // Keep all columns for accuracy to show context, or remove diff if requested. Keeping for now.
                      return true;
                    }) as ColumnsType<InventoryItem>
                  }
                  dataSource={groupItems}
                  rowKey="id"
                  pagination={false}
                  size="small"
                  scroll={{ x: true }}
                />
              </div>
            ))}

          {sortedData.length === 0 && (
            <div className="text-center py-10 text-gray-500">
              No inventory items found matching your filters.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Overview;
