import React from "react";
import { Drawer, Divider } from "antd";
import { PurchaseOrder } from "../types";

interface PurchaseOrderDetailsDrawerProps {
  open: boolean;
  onClose: () => void;
  order: PurchaseOrder | null;
}

const PurchaseOrderDetailsDrawer: React.FC<PurchaseOrderDetailsDrawerProps> = ({
  open,
  onClose,
  order,
}) => {
  return (
    <Drawer
      title={
        <div>
          <div className="text-sm text-gray-500 font-normal">Order Details</div>
          <div className="font-mono text-lg">{order?.id}</div>
        </div>
      }
      open={open}
      onClose={onClose}
      width={500}
    >
      {order && (
        <div className="space-y-6">
          <div className="flex justify-between items-center bg-gray-50 p-4 rounded-lg border border-gray-100">
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                Store
              </div>
              <div className="font-medium">{order.storeId}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                Order Date
              </div>
              <div className="font-medium">{order.date}</div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-800 mb-3 flex items-center justify-between">
              <span>Items Ordered</span>
              <span className="text-xs font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                {order.items?.length || 0} items
              </span>
            </h4>

            {!order.items || order.items.length === 0 ? (
              <div className="text-gray-500 text-center py-8 bg-gray-50 rounded italic border border-dashed border-gray-200">
                No items in this order
              </div>
            ) : (
              <div className="space-y-2">
                {order.items.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-start text-sm p-3 bg-white border border-gray-100 rounded-lg hover:border-gray-300 transition-colors"
                  >
                    <div>
                      <div className="font-medium text-gray-900">
                        {item.name}
                      </div>
                      <div className="text-xs text-gray-400 mt-0.5">
                        {item.vendor || "No vendor specified"}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-gray-800">
                        {item.quantity}{" "}
                        <span className="text-gray-500 text-xs font-normal">
                          {item.unit}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <Divider />

          <div className="flex justify-between items-end">
            <span className="text-gray-500">Estimated Total</span>
            <span className="text-2xl font-bold tracking-tight">
              ${order.totalAmount?.toFixed(2) || "0.00"}
            </span>
          </div>
        </div>
      )}
    </Drawer>
  );
};

export default PurchaseOrderDetailsDrawer;
