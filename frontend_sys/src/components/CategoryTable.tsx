import React from "react";
import { Table, Button, Space, Tag } from "antd";
import { Edit, Trash2 } from "lucide-react";
import { Category } from "../types";

interface Props {
  dataSource: Category[];
}

const CategoryTable: React.FC<Props> = ({ dataSource }) => {
  const categoryColumns = [
    {
      title: "Category Name",
      dataIndex: "name",
      key: "name",
      width: 250,
      render: (text: string) => (
        <span className="font-semibold text-gray-800">{text}</span>
      ),
    },
    {
      title: "Allowed Units",
      dataIndex: "allowedUnits",
      key: "allowedUnits",
      render: (units: string[]) => (
        <div className="flex flex-wrap gap-1.5">
          {units.map((u) => (
            <Tag
              key={u}
              color="blue"
              className="mr-0 rounded-sm px-2 text-xs border border-blue-200 bg-blue-50 text-blue-700"
            >
              {u}
            </Tag>
          ))}
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
      columns={categoryColumns}
      rowKey="id"
      pagination={{ pageSize: 8, showSizeChanger: false }}
    />
  );
};

export default CategoryTable;
