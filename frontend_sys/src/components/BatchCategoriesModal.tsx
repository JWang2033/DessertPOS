import React, { useRef, useState } from "react";
import { Drawer, Button, Input, Select, Space, message } from "antd";
import { Trash2, PlusCircle } from "lucide-react";
import { Unit } from "../types";

interface Props {
  open: boolean;
  onCancel: () => void;
  onSuccess: (data: BatchCategoryPayload[]) => void;
  units: Unit[];
}

interface BatchCategory {
  key: string;
  name: string;
  allowedUnits: string[];
}

interface BatchCategoryPayload {
  name: string;
  allowedUnits: string[];
}

const BatchCategoriesModal: React.FC<Props> = ({
  open,
  onCancel,
  onSuccess,
  units,
}) => {
  const rowKeyRef = useRef(1);
  const createRowKey = () => `row-${rowKeyRef.current++}`;
  const createEmptyRow = (key: string): BatchCategory => ({
    key,
    name: "",
    allowedUnits: [],
  });
  const [rows, setRows] = useState<BatchCategory[]>([
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
    field: keyof BatchCategory,
    value: BatchCategory[keyof BatchCategory],
  ) => {
    setRows(rows.map((r) => (r.key === key ? { ...r, [field]: value } : r)));
  };

  const handleSubmit = () => {
    const invalid = rows.some(
      (item) => !item.name || item.allowedUnits.length === 0,
    );
    if (invalid) {
      message.error(
        "Name and at least one Unit are required for all categories.",
      );
      return;
    }

    const dataToSubmit: BatchCategoryPayload[] = rows.map((item) => ({
      name: item.name,
      allowedUnits: item.allowedUnits,
    }));

    onSuccess(dataToSubmit);
    setRows([createEmptyRow(createRowKey())]);
  };

  const gridTemplate = "1.5fr 2fr 50px";

  return (
    <Drawer
      title={
        <div className="flex justify-between items-center pr-8">
          <span>Batch Create Categories</span>
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
              Allowed Units <span className="text-red-500">*</span>
            </div>
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
                  placeholder="Category Name"
                  value={row.name}
                  onChange={(e) => updateRow(row.key, "name", e.target.value)}
                  size="small"
                />
                <Select
                  mode="multiple"
                  placeholder="Select Allowed Units"
                  className="w-full"
                  size="small"
                  value={row.allowedUnits}
                  onChange={(val) => updateRow(row.key, "allowedUnits", val)}
                  options={units.map((u) => ({
                    value: u.abbreviation,
                    label: `${u.name} (${u.abbreviation})`,
                  }))}
                  maxTagCount="responsive"
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
              Add New Category
            </Button>
          </div>
        </div>
      </div>
    </Drawer>
  );
};

export default BatchCategoriesModal;
