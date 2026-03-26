import React from "react";
import { Table, Button, Space } from "antd";
import { Edit, Trash2 } from "lucide-react";
import { Ingredient } from "../types";

interface Props {
  dataSource: Ingredient[];
}

const IngredientTable: React.FC<Props> = ({ dataSource }) => {
  const ingredientColumns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      width: 220,
      render: (text: string) => (
        <span className="font-semibold text-gray-800">{text}</span>
      ),
    },
    {
      title: "Type",
      dataIndex: "type",
      key: "type",
      width: 150,
      render: (text: string) => (
        <span className="text-gray-500 text-xs">{text}</span>
      ),
    },
    {
      title: "Brand",
      dataIndex: "brand",
      key: "brand",
      render: (text: string) => (
        <span className="text-gray-500 text-xs">{text || "--"}</span>
      ),
    },
    {
      title: "Threshold",
      key: "threshold",
      render: (record: Ingredient) =>
        record.threshold_amount ? (
          <div className="px-2 py-0.5 rounded-sm bg-green-50 text-green-600 border border-green-200 text-xs inline-block">
            {record.threshold_amount} {record.threshold_unit}
          </div>
        ) : (
          <span className="text-gray-300 italic text-xs">Not Set</span>
        ),
    },
    {
      title: "Allergens",
      dataIndex: "allergens",
      key: "allergens",
      render: (allergens: string[]) => (
        <div className="flex flex-wrap gap-1.5 items-center min-h-[22px]">
          {allergens && allergens.length > 0 ? (
            allergens.map((a) => (
              <span
                key={a}
                className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-red-50 text-red-500 border border-red-100"
              >
                {a}
              </span>
            ))
          ) : (
            <span className="text-gray-300 italic text-xs px-1">None</span>
          )}
        </div>
      ),
    },
    {
      title: "Actions",
      key: "actions",
      width: 100,
      align: "center" as const,
      render: () => (
        <Space size={4}>
          <Button
            type="text"
            size="small"
            icon={<Edit size={16} />}
            className="text-[#1890ff] hover:bg-blue-50 flex items-center justify-center"
          />
          <Button
            type="text"
            size="small"
            icon={<Trash2 size={16} />}
            className="text-red-500 hover:bg-red-50 flex items-center justify-center"
          />
        </Space>
      ),
    },
  ];

  return (
    <Table
      dataSource={dataSource}
      columns={ingredientColumns}
      rowKey="id"
      pagination={{ pageSize: 8, showSizeChanger: false }}
    />
  );
};

export default IngredientTable;
