import React from "react";
import { Table, Button, Space } from "antd";
import { Edit, Trash2 } from "lucide-react";
import { IngredientRef, SemiFinishedProduct } from "../types";

interface Props {
  dataSource: SemiFinishedProduct[];
}

const SemiFinishedTable: React.FC<Props> = ({ dataSource }) => {
  const semiFinishedColumns = [
    {
      title: "Product Name",
      dataIndex: "name",
      key: "name",
      width: 250,
      render: (text: string) => (
        <span className="font-semibold text-gray-800">{text}</span>
      ),
    },
    {
      title: "Prep Time",
      dataIndex: "prepTime",
      key: "prepTime",
      render: (time: number) => <span className="text-gray-600">{time}h</span>,
    },
    {
      title: "Ingredients Summary",
      dataIndex: "ingredients",
      key: "ingredients",
      render: (ingredients: IngredientRef[]) => {
        const firstThree = ingredients
          .slice(0, 3)
          .map((i) => i.name)
          .join(", ");
        const remaining = ingredients.length - 3;
        return (
          <span className="text-gray-500 text-sm">
            {firstThree}
            {remaining > 0 && (
              <span className="bg-gray-100 text-gray-600 text-xs px-1.5 py-0.5 rounded ml-1">
                +{remaining} more
              </span>
            )}
          </span>
        );
      },
    },
    {
      title: "Allergens",
      key: "allergens",
      render: (record: SemiFinishedProduct) => {
        // Collect unique allergens from all ingredients
        const allAllergens = new Set<string>();
        record.ingredients.forEach((ing) => {
          if (ing.allergens) ing.allergens.forEach((a) => allAllergens.add(a));
        });
        const tags = Array.from(allAllergens);

        return (
          <div className="flex flex-wrap gap-1.5 items-center min-h-[22px]">
            {tags.length > 0 ? (
              tags.map((a) => (
                <span
                  key={a}
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-orange-50 text-orange-600 border border-orange-100 uppercase font-semibold"
                >
                  {a}
                </span>
              ))
            ) : (
              <span className="text-gray-300 italic text-xs px-1">None</span>
            )}
          </div>
        );
      },
    },
    {
      title: "Threshold",
      key: "threshold",
      render: (record: SemiFinishedProduct) => (
        <div className="px-2 py-0.5 rounded-sm bg-green-50 text-green-600 border border-green-200 text-xs inline-block">
          {record.threshold_amount} {record.threshold_unit}
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

  const expandedRowRender = (record: SemiFinishedProduct) => {
    const subColumns = [
      { title: "Component Ingredient", dataIndex: "name", key: "name" },
      {
        title: "Quantity",
        dataIndex: "quantity",
        key: "quantity",
        width: 100,
        render: (val: number) => val.toFixed(2),
      },
      {
        title: "Unit",
        dataIndex: "unit",
        key: "unit",
        width: 80,
        align: "center" as const,
      },
    ];

    return (
      <Table
        columns={subColumns}
        dataSource={record.ingredients}
        pagination={false}
        size="small"
        rowKey="name"
        className="bg-gray-50 rounded-md border border-gray-100 m-2"
      />
    );
  };

  return (
    <Table
      dataSource={dataSource}
      columns={semiFinishedColumns}
      rowKey="id"
      pagination={{ pageSize: 8, showSizeChanger: false }}
      expandable={{
        expandedRowRender,
        expandRowByClick: true,
      }}
    />
  );
};

export default SemiFinishedTable;
