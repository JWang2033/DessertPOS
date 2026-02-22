import React, { useRef, useState } from "react";
import {
  Drawer,
  Button,
  Input,
  Select,
  InputNumber,
  Space,
  message,
} from "antd";
import { Trash2, PlusCircle } from "lucide-react";
import { Ingredient, Category, Unit } from "../types";
import { mockAllergens } from "../services/mockData";

interface Props {
  open: boolean;
  onCancel: () => void;
  onSuccess: (data: Partial<Ingredient>[]) => void;
  categories: Category[];
  units: Unit[];
}

interface BatchIngredient {
  key: string;
  name: string;
  type: string;
  brand: string;
  threshold_amount?: number;
  threshold_unit: string;
  allergens: string[];
}

const BatchIngredientsModal: React.FC<Props> = ({
  open,
  onCancel,
  onSuccess,
  categories,
  units,
}) => {
  const rowKeyRef = useRef(1);
  const createRowKey = () => `row-${rowKeyRef.current++}`;
  const createEmptyRow = (key: string): BatchIngredient => ({
    key,
    name: "",
    type: "",
    brand: "",
    threshold_amount: undefined,
    threshold_unit: "kg",
    allergens: [],
  });
  const [rows, setRows] = useState<BatchIngredient[]>([
    createEmptyRow("row-0"),
  ]);

  const addRow = () => {
    setRows([
      ...rows,
      createEmptyRow(createRowKey()),
    ]);
  };

  const removeRow = (key: string) => {
    if (rows.length > 1) {
      setRows(rows.filter((r) => r.key !== key));
    } else {
      message.warning("At least one row is required.");
    }
  };

  const updateRow = (
    key: string,
    field: keyof BatchIngredient,
    value: BatchIngredient[keyof BatchIngredient],
  ) => {
    setRows(rows.map((r) => (r.key === key ? { ...r, [field]: value } : r)));
  };

  const handleSubmit = () => {
    const invalid = rows.some((item) => !item.name || !item.type);
    if (invalid) {
      message.error("Name and Type are required for all ingredients.");
      return;
    }

    // Convert to partial ingredients for parent
    const dataToSubmit = rows.map((item) => ({
      name: item.name,
      type: item.type,
      brand: item.brand,
      threshold_amount: item.threshold_amount,
      threshold_unit: item.threshold_unit,
      allergens: item.allergens,
    }));

    onSuccess(dataToSubmit);
    setRows([createEmptyRow(createRowKey())]);
  };

  const gridTemplate = "1.5fr 1.2fr 1.2fr 0.8fr 0.8fr 0.8fr 1.5fr 50px";

  return (
    <Drawer
      title={
        <div className="flex justify-between items-center pr-8">
          <span>Batch Create Ingredients</span>
        </div>
      }
      placement="bottom"
      height="96%"
      onClose={onCancel}
      open={open}
      styles={{ body: { padding: 0 } }}
      footer={
        <div className="flex justify-between items-center">
          <Button type="link" onClick={onCancel} className="text-gray-500">
            Cancel
          </Button>
          <Space>
            <Button onClick={onCancel}>Cancel</Button>
            <Button type="primary" onClick={handleSubmit}>
              Submit All
            </Button>
          </Space>
        </div>
      }
    >
      <div className="h-full bg-white overflow-auto">
        <div className="p-6 pb-20">
          <div
            className="grid gap-4 bg-gray-50 px-4 py-3 border-y border-gray-100 font-semibold text-xs text-gray-600 uppercase tracking-wide items-center sticky top-0 z-10 shadow-sm"
            style={{ gridTemplateColumns: gridTemplate }}
          >
            <div>
              Name <span className="text-red-500">*</span>
            </div>
            <div>
              Type <span className="text-red-500">*</span>
            </div>
            <div>Brand</div>
            <div>Threshold</div>
            <div>Unit</div>
            <div>View</div>
            <div>Allergens</div>
            <div className="text-center">Action</div>
          </div>

          <div>
            {rows.map((row) => (
              <div
                key={row.key}
                className="grid gap-4 px-4 py-3 border-b border-gray-100 items-center hover:bg-blue-50/30 transition-colors"
                style={{ gridTemplateColumns: gridTemplate }}
              >
                <Input
                  placeholder="Name"
                  value={row.name}
                  onChange={(e) => updateRow(row.key, "name", e.target.value)}
                  size="small"
                />
                <Select
                  placeholder="Select"
                  className="w-full"
                  size="small"
                  value={row.type || null}
                  onChange={(val) => updateRow(row.key, "type", val)}
                  options={categories.map((c) => ({
                    value: c.name,
                    label: c.name,
                  }))}
                />
                <Input
                  placeholder="Brand"
                  value={row.brand}
                  onChange={(e) => updateRow(row.key, "brand", e.target.value)}
                  size="small"
                />
                <InputNumber
                  placeholder="0"
                  className="w-full"
                  size="small"
                  min={0}
                  value={row.threshold_amount}
                  onChange={(val) =>
                    updateRow(row.key, "threshold_amount", val)
                  }
                />
                <Select
                  value={row.threshold_unit}
                  className="w-full"
                  size="small"
                  onChange={(val) => updateRow(row.key, "threshold_unit", val)}
                  options={units.map((u) => ({
                    value: u.abbreviation,
                    label: u.abbreviation,
                  }))}
                />
                <div className="bg-gray-100 text-gray-500 text-xs px-2 py-1 rounded h-6 flex items-center truncate">
                  {row.threshold_amount
                    ? `${row.threshold_amount} ${row.threshold_unit}`
                    : "-"}
                </div>
                <Select
                  mode="multiple"
                  placeholder="Select"
                  value={row.allergens}
                  onChange={(val) => updateRow(row.key, "allergens", val)}
                  size="small"
                  className="w-full"
                  maxTagCount="responsive"
                  options={mockAllergens}
                />
                <div className="flex justify-center">
                  <button
                    onClick={() => removeRow(row.key)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4">
            <Button
              type="dashed"
              block
              onClick={addRow}
              icon={<PlusCircle size={16} />}
              className="text-[#1890ff] border-blue-200 bg-blue-50/50"
            >
              Add New Ingredient
            </Button>
          </div>
        </div>
      </div>
    </Drawer>
  );
};

export default BatchIngredientsModal;
