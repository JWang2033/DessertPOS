import React, { useEffect, useState } from "react";
import { Table, Button, Typography, Input, Select, message } from "antd";
import { Plus, Eye, Search } from "lucide-react";
import { PurchaseOrder } from "../types";
import { getPurchaseOrderById, getPurchaseOrders } from "../services/api";

import CreateOrderDrawer from "../components/CreateOrderDrawer";
import PurchaseOrderDetailsDrawer from "../components/PurchaseOrderDetailsDrawer";

const { Title } = Typography;

interface ApiPurchaseOrderListItem {
  id: number;
  po_code: string;
  order_date: string;
  store_id: string;
  total_amount: number;
  total_items_count: number;
}

interface ApiPurchaseOrderItem {
  id: number;
  ingredient_id: number;
  ingredient_name: string;
  unit_abbreviation: string;
  quantity: number | string;
  vendor?: string | null;
}

interface ApiPurchaseOrderDetail {
  id: number;
  po_code: string;
  order_date: string;
  store_id: string;
  total_amount: number | string;
  items: ApiPurchaseOrderItem[];
}

const PurchaseManagement: React.FC = () => {
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [selectedPO, setSelectedPO] = useState<PurchaseOrder | null>(null);
  const [detailsDrawerOpen, setDetailsDrawerOpen] = useState(false);
  const [createDrawerOpen, setCreateDrawerOpen] = useState(false);

  const [searchText, setSearchText] = useState("");
  const [sortOrder, setSortOrder] = useState<"desc" | "asc">("desc");

  useEffect(() => {
    let active = true;
    const loadOrders = async () => {
      try {
        const response = await getPurchaseOrders();
        const mapped = (response.data as ApiPurchaseOrderListItem[]).map(
          (order) => ({
            id: order.po_code,
            date: order.order_date,
            storeId: order.store_id,
            totalAmount: Number(order.total_amount || 0),
            status: "Completed",
            items: [],
          }),
        );
        if (active) setPurchaseOrders(mapped);
      } catch {
        if (active) message.error("Failed to fetch purchase orders.");
      }
    };

    loadOrders();
    return () => {
      active = false;
    };
  }, []);

  const handleCreateSuccess = (newPO: PurchaseOrder) => {
    setPurchaseOrders([newPO, ...purchaseOrders]);
    setCreateDrawerOpen(false);
  };

  const handleViewDetails = async (poCode: string) => {
    try {
      const response = await getPurchaseOrderById(poCode);
      const order = response.data as ApiPurchaseOrderDetail;
      const mapped: PurchaseOrder = {
        id: order.po_code,
        date: order.order_date,
        storeId: order.store_id,
        totalAmount: Number(order.total_amount || 0),
        status: "Completed",
        items: (order.items || []).map((item: ApiPurchaseOrderItem, idx) => ({
          key: item.id?.toString() || idx.toString(),
          ingredientId: item.ingredient_id?.toString() || "",
          name: item.ingredient_name,
          quantity: Number(item.quantity),
          unit: item.unit_abbreviation,
          vendor: item.vendor || "",
        })),
      };
      setSelectedPO(mapped);
      setDetailsDrawerOpen(true);
    } catch {
      message.error("Failed to fetch purchase order details.");
    }
  };

  const filteredOrders = purchaseOrders
    .filter(
      (order) =>
        order.id.toLowerCase().includes(searchText.toLowerCase()) ||
        order.storeId.toLowerCase().includes(searchText.toLowerCase()),
    )
    .sort((a, b) => {
      const dateA = new Date(a.date).getTime();
      const dateB = new Date(b.date).getTime();
      return sortOrder === "desc" ? dateB - dateA : dateA - dateB;
    });

  // --- List View Columns ---
  const columns = [
    {
      title: "PO Number",
      dataIndex: "id",
      key: "id",
      render: (text: string) => (
        <span
          className="font-mono font-medium text-blue-600 hover:text-blue-800 cursor-pointer"
          onClick={() => {
            handleViewDetails(text);
          }}
        >
          {text}
        </span>
      ),
    },
    { title: "Date", dataIndex: "date", key: "date" },
    { title: "Store ID", dataIndex: "storeId", key: "storeId" },
    {
      title: "Total Amount",
      dataIndex: "totalAmount",
      key: "totalAmount",
      render: (val: number) => `$${val.toFixed(2)}`,
    },
    {
      title: "Action",
      key: "action",
      render: (_: unknown, record: PurchaseOrder) => (
        <Button
          type="link"
          icon={<Eye size={16} />}
          onClick={() => {
            handleViewDetails(record.id);
          }}
        >
          Details
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Title level={3} style={{ margin: 0 }}>
            Purchase Orders
          </Title>
          <p className="text-gray-500 mt-1">Manage store procurement</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6 space-y-4">
        {/* Toolbar */}
        <div className="flex flex-col md:flex-row justify-between gap-4 items-center">
          <div className="w-full md:w-80">
            <Input
              prefix={<Search size={16} className="text-gray-400" />}
              placeholder="Search PO Number, Store ID..."
              allowClear
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-3 w-full md:w-auto">
            <Select
              value={sortOrder}
              onChange={setSortOrder}
              className="min-w-[160px]"
              options={[
                { value: "desc", label: "Date: Newest First" },
                { value: "asc", label: "Date: Oldest First" },
              ]}
            />
            <Button
              type="primary"
              icon={<Plus size={16} />}
              onClick={() => setCreateDrawerOpen(true)}
              className="bg-blue-600 shadow-sm"
            >
              Create New Order
            </Button>
          </div>
        </div>

        <Table dataSource={filteredOrders} columns={columns} rowKey="id" />
      </div>

      <CreateOrderDrawer
        open={createDrawerOpen}
        onClose={() => setCreateDrawerOpen(false)}
        onSuccess={handleCreateSuccess}
      />

      {/* View Details Drawer */}
      <PurchaseOrderDetailsDrawer
        open={detailsDrawerOpen}
        onClose={() => setDetailsDrawerOpen(false)}
        order={selectedPO}
      />
    </div>
  );
};

export default PurchaseManagement;
