import React, { useState } from "react";
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
import { Ingredient, SemiFinishedProduct, IngredientRef, Unit } from "../types";

interface Props {
  open: boolean;
  onCancel: () => void;
  onSuccess: (data: SemiFinishedProduct) => void;
  ingredients: Ingredient[];
  units: Unit[];
}

const CreateSemiFinishedModal: React.FC<Props> = ({
  open,
  onCancel,
  onSuccess,
  ingredients,
  units,
}) => {
  const [name, setName] = useState("");
  const [prepTime, setPrepTime] = useState<number | null>(null);
  const [thresholdAmount, setThresholdAmount] = useState<number | null>(null);
  const [thresholdUnit, setThresholdUnit] = useState("kg");

  const [productIngredients, setProductIngredients] = useState<
    Partial<IngredientRef>[]
  >([
    { name: "", quantity: 0, unit: "kg" },
    { name: "", quantity: 0, unit: "kg" }, // At least two
  ]);

  const resetForm = () => {
    setName("");
    setPrepTime(null);
    setThresholdAmount(null);
    setThresholdUnit("kg");
    setProductIngredients([
      { name: "", quantity: 0, unit: "kg" },
      { name: "", quantity: 0, unit: "kg" },
    ]);
  };

  const handleAddIngredient = () => {
    setProductIngredients([
      ...productIngredients,
      { name: "", quantity: 0, unit: "kg" },
    ]);
  };

  const handleRemoveIngredient = (index: number) => {
    if (productIngredients.length > 2) {
      const newIngredients = [...productIngredients];
      newIngredients.splice(index, 1);
      setProductIngredients(newIngredients);
    } else {
      message.warning("At least two ingredients are required.");
    }
  };

  const updateIngredient = (
    index: number,
    field: keyof IngredientRef,
    value: IngredientRef[keyof IngredientRef],
  ) => {
    const newIngredients = [...productIngredients];
    newIngredients[index] = { ...newIngredients[index], [field]: value };
    // If name changes, try to find allergens/unit from mock list
    if (field === "name") {
      const found = ingredients.find((i) => i.name === value);
      if (found) {
        newIngredients[index].ingredientId = found.id;
        // Optional: Pre-fill unit if we had it in ingredient definition, but we don't strictly enforce it here
        if (found.allergens) {
          newIngredients[index].allergens = found.allergens;
        }
      }
    }
    setProductIngredients(newIngredients);
  };

  const handleSubmit = () => {
    if (!name || prepTime === null) {
      message.error("Please fill in all required fields.");
      return;
    }

    const invalidIngredients = productIngredients.some(
      (i) => !i.name || !i.quantity,
    );
    if (invalidIngredients) {
      message.error("Please ensure all ingredients have a name and quantity.");
      return;
    }

    const newProduct: SemiFinishedProduct = {
      id: Math.random().toString(36).substr(2, 9),
      name,
      prepTime: prepTime,
      threshold_amount: thresholdAmount ? thresholdAmount : 0,
      threshold_unit: thresholdUnit,
      ingredients: productIngredients as IngredientRef[],
    };

    onSuccess(newProduct);
    resetForm();
  };

  // Header for the ingredient table
  const gridTemplate = "2fr 1fr 1fr 40px";

  return (
    <Drawer
      title={
        <div className="flex justify-between items-center pr-8">
          <span>Create Semi-Finished Product</span>
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
              Create Product
            </Button>
          </Space>
        </div>
      }
    >
      <div className="h-full bg-white overflow-auto max-w-3xl mx-auto border-x border-gray-100 shadow-sm">
        <div className="p-8 pb-20">
          {/* Main Product Details */}
          <div className="mb-8 grid grid-cols-2 gap-6">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Product Name <span className="text-red-500">*</span>
              </label>
              <Input
                placeholder="e.g. Tonkotsu Broth Base"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prep Time (Hours) <span className="text-red-500">*</span>
              </label>
              <InputNumber
                className="w-full"
                placeholder="e.g. 12"
                min={0}
                value={prepTime}
                onChange={(val) => setPrepTime(val)}
              />
            </div>

            <div className="flex gap-2">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Threshold Amount{" "}
                </label>
                <InputNumber
                  className="w-full"
                  placeholder="e.g. 20"
                  min={0}
                  value={thresholdAmount}
                  onChange={(val) => setThresholdAmount(val)}
                />
              </div>
              <div className="w-24">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Unit
                </label>
                <Select
                  className="w-full"
                  value={thresholdUnit}
                  onChange={setThresholdUnit}
                  options={units.map((u) => ({
                    label: u.abbreviation,
                    value: u.abbreviation,
                  }))}
                />
              </div>
            </div>
          </div>

          {/* Ingredients Section */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-800">
                Ingredients
              </h3>
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                Minimum 2 items required
              </span>
            </div>

            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <div
                className="grid bg-gray-50 px-4 py-3 border-b border-gray-200 font-semibold text-xs text-gray-600 uppercase tracking-wide"
                style={{ gridTemplateColumns: gridTemplate }}
              >
                <div>Ingredient Name</div>
                <div>Quantity</div>
                <div>Unit</div>
                <div className="text-center"></div>
              </div>

              <div className="divide-y divide-gray-100">
                {productIngredients.map((ing, index) => (
                  <div
                    key={index}
                    className="grid px-4 py-3 items-center gap-3 hover:bg-gray-50/50 transition-colors"
                    style={{ gridTemplateColumns: gridTemplate }}
                  >
                    <Select
                      showSearch
                      placeholder="Select Ingredient"
                      className="w-full"
                      value={ing.name ? ing.name : undefined}
                      onChange={(val) => updateIngredient(index, "name", val)}
                      options={ingredients.map((i) => ({
                        value: i.name,
                        label: i.name,
                      }))}
                    />
                    <InputNumber
                      className="w-full"
                      placeholder="0"
                      min={0}
                      value={ing.quantity}
                      onChange={(val) =>
                        updateIngredient(index, "quantity", val)
                      }
                    />
                    <Select
                      className="w-full"
                      value={ing.unit}
                      onChange={(val) => updateIngredient(index, "unit", val)}
                      options={units.map((u) => ({
                        value: u.abbreviation,
                        label: u.abbreviation,
                      }))}
                    />
                    <div className="flex justify-center">
                      <button
                        onClick={() => handleRemoveIngredient(index)}
                        className={`p-1 rounded hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors ${productIngredients.length <= 2 ? "opacity-50 cursor-not-allowed" : ""}`}
                        disabled={productIngredients.length <= 2}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Button
              type="dashed"
              block
              onClick={handleAddIngredient}
              icon={<PlusCircle size={16} />}
              className="mt-4 py-4 text-[#1890ff] border-blue-200 bg-blue-50/30 font-medium"
            >
              Add Another Ingredient
            </Button>
          </div>
        </div>
      </div>
    </Drawer>
  );
};

export default CreateSemiFinishedModal;
